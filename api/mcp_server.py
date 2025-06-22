from mcp.server.fastmcp import FastMCP
# -*- coding: utf-8 -*- 
from dotenv import load_dotenv
import os
import logging
import json
from article_generator import ArticleGenerator

# 加载环境变量
load_dotenv()
# 紀錄程式執行狀況
# 配置日誌記錄器
logging.basicConfig(
    level=logging.INFO, # 設置日誌級別 INFO
    format='%(asctime)s - %(levelname)s - %(message)s' # 日誌格式
)

logger = logging.getLogger(__name__)


article_generator = ArticleGenerator()


mcp = FastMCP('ToolServer')

@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers."""
    logger.info(f"The add method is called: a={a}, b={b}")
    return a + b

@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    logger.info(f"The multiply method is called: a={a}, b={b}")
    return a * b

@mcp.tool()
async def get_weather(location: str) -> dict:
    """Get weather information for a specific location."""
    logger.info(f"The get_weather method is called: location={location}")
    # Simulate fetching weather data
    weather_data = {
        "location": location,
        "temperature": "22°C",
        "condition": "Sunny"
    }
    return weather_data


@mcp.tool("summarize_meeting", description="輸入會議記錄，透過 Selenium 自動生成會議摘要文章，輸入文字後會自動操作瀏覽器並回傳結果。")
async def summarize_meeting(text: str) -> dict:
    """
    文章摘要生成工具
    
    透過 Selenium 自動操作瀏覽器打開 Google Notebook LM，生成精煉的技術會議摘要。
    支援多次重試與錯誤處理，輸入為純文字。
    
    Parameters:
    - text: 要生成文章的文字內容
    
    Returns:
    - dict 格式的結果，包含生成狀態與訊息
    """
    
    is_success = article_generator.summarize_meeting(text)
    if not is_success:
        return {"status": "failed", "message": "摘要生成失敗"}
    is_success = article_generator.convert_to_markdown_from_openai()
    return {"status": "success" if is_success else "failed"}

if __name__ == "__main__":
    # 啟動 MCP 服務
    mcp.run(transport="streamable-http")
