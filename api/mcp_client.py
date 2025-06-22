from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from contextlib import AsyncExitStack
import os
from utils.logger import logger
from datetime import datetime
import json
import traceback
import copy


def get_env_int(key: str, default: int) -> int:
    val = os.getenv(key)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default

def get_env_float(key: str, default: float) -> float:
    val = os.getenv(key)
    try:
        return float(val) if val is not None else default
    except ValueError:
        return default


class MCPClient:
    def __init__(self, mode=os.getenv("MCP_MODE", "stdio"), server_path_or_url=None):
        self.mode = mode  # "stdio" or "sse" or "streamable_http"
        self.server_path_or_url = server_path_or_url
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = None
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=get_env_float("TEMPERATURE", 0.3),
            max_tokens=get_env_int("MAX_TOKENS", 1000),
            request_timeout=get_env_int("REQUEST_TIMEOUT", 60),
            streaming=False,
        )
        self.tools = []
        self.messages = []
        self.logger = logger

    async def connect_to_server(self):
        try:
            if self.mode == "stdio":
                command = "python" if self.server_path_or_url.endswith(".py") else "node"
                server_params = StdioServerParameters(
                    command=command,
                    args=[self.server_path_or_url],
                    env=None
                )
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                self.stdio, self.write = stdio_transport
                self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
                await self.session.initialize()
            elif self.mode == "sse":
                self.client = MultiServerMCPClient({
                    "tool_server": {
                        "url": self.server_path_or_url,
                        "transport": "sse",
                    }
                })
                self.session = self.client  # 統一命名給後續使用
            elif self.mode == "streamable_http":
                self.client = MultiServerMCPClient({
                    "tool_server": {
                        "url": self.server_path_or_url,
                        "transport": "streamable_http",
                    }
                })
                self.session = self.client  # 統一命名給後續使用
            else:
                raise ValueError("Unsupported mode. Use 'stdio' or 'http'.")

            self.logger.info("Connected to MCP server")

            mcp_tools = await self.get_mcp_tools()
            def clean_schema(schema):
                if schema is None:
                    return {}
                if not isinstance(schema, dict):
                    # 如果不是 dict（可能是 function），就不處理，直接返回空 dict 或原值（視情況）
                    return {}
                cleaned = copy.deepcopy(schema)
                keys_to_remove = []
                for k, v in cleaned.items():
                    if callable(v):
                        keys_to_remove.append(k)
                for k in keys_to_remove:
                    cleaned.pop(k)
                return cleaned

            # 修改 tools 初始化：
            self.tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": clean_schema(getattr(tool, "json_schema", None) or getattr(tool, "schema", None))
                    }
                }
                for tool in mcp_tools
            ]
            self.logger.info(f"Loaded tools: {[t['function']['name'] for t in self.tools]}")
            return True

        except Exception as e:
            self.logger.error(f"Error connecting to MCP server: {e}")
            traceback.print_exc()
            raise

    async def get_mcp_tools(self):
        try:
            if self.mode == "stdio":
                response = await self.session.list_tools()
                return response.tools
            elif self.mode == "sse" or self.mode == "streamable_http":
                tools = await self.session.get_tools()
                return tools
            else:
                raise ValueError(f"Unknown mode {self.mode} for getting tools")
        except Exception as e:
            self.logger.error(f"Error fetching MCP tools: {e}")
            traceback.print_exc()
            raise

    def serialize_tool_result(self, obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        if isinstance(obj, list):
            return [self.serialize_tool_result(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self.serialize_tool_result(value) for key, value in obj.items()}
        if type(obj).__name__ == "TextContent" and hasattr(obj, "text"):
            return obj.text
        if hasattr(obj, "to_dict"):
            return self.serialize_tool_result(obj.to_dict())
        if hasattr(obj, "__dict__"):
            return self.serialize_tool_result(vars(obj))
        return str(obj)

    async def process_query(self, query: str):
        try:
            self.logger.info(f"Processing query: {query}")
            self.messages = [{"role": "user", "content": query}]
            MAX_ITERATIONS = get_env_int("MAX_ITERATIONS", 5)

            for _ in range(MAX_ITERATIONS):
                response = await self.call_llm()
                self.logger.info(f"LLM response: {response}")

                content = response.get("content", "")
                if content.strip():
                    self.messages.append({"role": "assistant", "content": content})
                    await self.log_conversation()
                    break
                
                tool_calls = response.get("tool_calls", [])
                if tool_calls:
                    for call in tool_calls:
                        func = call.get("function", {})
                        tool_name = func.get("name")
                        args_json = func.get("arguments", "{}")
                        tool_args = json.loads(args_json)
                        if self.mode == "stdio" or self.mode == "streamable_http" or self.mode == "sse":
                            async with self.client.session("tool_server") as session:
                                result = await session.call_tool(tool_name, tool_args)
                        else:
                            raise ValueError(f"Unknown mode {self.mode}")
                        tool_result = result.result if hasattr(result, "result") else result
                        tool_result_str = json.dumps(self.serialize_tool_result(tool_result), ensure_ascii=False)
                        self.messages.append({"role": "user", "content": f"Tool {tool_name} result:\n{tool_result_str}"})
                    await self.log_conversation()
                    continue
                break
            else:
                self.messages.append({"role": "assistant", "content": "Error: exceeded maximum reasoning steps."})

            return self.messages

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise

    async def call_llm(self):
        formatted_messages = []
        for msg in self.messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "tool":
                formatted_messages.append(ToolMessage(content=msg["content"], tool_call_id=msg["tool_call_id"]))

        response = await self.llm.ainvoke(
            formatted_messages,
            tools=self.tools,
            tool_choice="auto"
        )
        return {
            "content": response.content if hasattr(response, "content") else "",
            "tool_calls": response.additional_kwargs.get("tool_calls", [])
        }

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            self.logger.info("Disconnected.")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    async def log_conversation(self):
        try:
            os.makedirs("conversations", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join("conversations", f"conversation_{timestamp}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Logged to {path}")
        except Exception as e:
            self.logger.error(f"Logging error: {e}")
