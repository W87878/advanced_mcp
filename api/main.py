from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
from mcp_client import MCPClient
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    server_script_path: str = "/Users/steve.wang/Downloads/AI_FastAPI_MCP/mcp_server.py"
    mcp_tool_url: str = "http://localhost:8000/mcp"  # HTTP MCP 工具 URL

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to manage MCP client connection."""
    # 指定 HTTP 模式
    client = MCPClient(mode="streamable_http", server_path_or_url=settings.mcp_tool_url)
    try:
        connected = await client.connect_to_server()
        if not connected:
            raise HTTPException(status_code=500, detail="Failed to connect to MCP server")
        app.state.client = client
        yield
    except Exception as e:
        print(f"Error during lifespan: {e}")
        raise e
    finally:
        await client.cleanup()

       
app = FastAPI(title='MCP Client API', lifespan=lifespan)

# ADD CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str  

class Message(BaseModel):
    role: str
    content: str

class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]
    
    
@app.post("/query")
async def query(request: QueryRequest):
    """Process a query and return the response."""
    client: MCPClient = app.state.client
    try:
        messages = await client.process_query(request.query)
        print("== messages ===")
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                content = msg["content"]
                print("assistant content:", repr(content))  # <-- 這行
        # ... 你的原本邏輯
        # 回傳最後一個 assistant 的回答
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                content = msg["content"]
                if isinstance(content, str):
                    cleaned = content.strip()
                    # 如果尾巴有多餘 undefined，清理掉（可依需要擴充）
                    if cleaned.endswith("undefined"):
                        cleaned = cleaned[:-len("undefined")].strip()
                    return {"answer": cleaned}
                elif isinstance(content, list):
                    # 過濾 None 或空字串，並轉成字串後 join
                    filtered = [str(c).strip() for c in content if c and str(c).strip() and str(c) != "undefined"]
                    return {"answer": " ".join(filtered)}
                else:
                    return {"answer": str(content).strip()}
        return {"answer": "沒有回覆內容。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8001, reload=True)
