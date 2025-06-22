
# 📄 MCP Meeting Summary System

此專案結合前端與後端，實現一套基於 AI 與多工具協同的會議摘要及問答系統。
前端搭配 React + Tailwind UI，後端使用 FastAPI + MCP 架構，支援串接 OpenAI 與 Selenium 自動生成會議摘要，提供高品質 Markdown 報告。

---

## 🛠 專案結構

```
.
📁 api/
  ├── main.py              # FastAPI 入口點 + MCPClient
  ├── mcp_server.py        # MCP 工具伺服器 (summarize_meeting add multiply等工具)
  ├── article_generator.py # Selenium + OpenAI 摘要核心邏輯
📁 frontend/
  └── src/
      ├── components/ # 前端元件
      │   └── ui/   # UI 元件
      │       - button.tsx # 按鈕元件
      │       - textarea.tsx # 文本輸入元件
      │       - card.tsx # 卡片元件
      ├── frontend.tsx  # 主要入口與介面元件
      ├── main.tsx    # 前端入口點
      ├── vite.config.ts # Vite 配置（含別名設定）
      └── tailwind.config.js # Tailwind CSS 設定
📁 api/utils/
  └── logger.py  # 日誌紀錄工具
├── transcripts/           # 儲存逐字稿與 Markdown 摘要
├── api/.env               # 儲存 OpenAI API Key（已被 .gitignore 忽略）
├── pyproject.toml         # Python 專案設定檔   
├── README.md              # 本說明文件
```

---

## 🧑‍💻 安裝方式（建議使用 [`uv`](https://github.com/astral-sh/uv)）

```bash
# 安裝依賴（建議使用 uv）
uv pip install -r pyproject.toml
# 或使用 install 命令
uv pip install .
# 或使用 requirements.txt（如果你有產生的話）
uv pip install -r requirements.txt
```

---

## 後端 (backend)

### ✅ 啟動 MCP 工具伺服器 - MODE 預設為 `streamable-http`

```bash
cd api
uv run ./mcp_server.py
```
確保該檔案有註冊 @mcp.tool("summarize_meeting") 等功能，並支援 streamable-http, sse, stdio。

### ✅ 啟動 MCP Agent 問答介面

```bash
cd api
uv run ./main.py
```

## 前端 (frontend)
```bash
- 使用 React + Vite 快速開發
- Tailwind CSS 設計 UI，包含 Button、Textarea、Card 等自訂元件
- Framer Motion 實現平滑動畫與互動體驗
- 功能：輸入問題或逐字稿，呼叫後端 API，顯示智能摘要或回答，並用打字機效果呈現結果
```

### 啟動方式
```bash
cd front
npm install
npm run dev
```
預設會在 http://localhost:5173 啟動開發伺服器。


### API 文件
| 欄位    | 型別     | 說明           |
| ----- | ------ | ------------ |
| query | string | 使用者輸入內容，如逐字稿 |
```
POST http://localhost:8001/query
{
  "query": "請幫我分析這份逐字稿內容..."
}
```
回傳
```json
{
  "answer": "技術討論要點\n- ..."
}
```


---

## 🧙‍♂️ 功能特色
- 🧠 多步推理 Agent：透過 GPT 工具選擇功能，自動呼叫 summarize_meeting 工具。
- 🕸 Selenium 操作 Notebook LM：用真實瀏覽器生成摘要。
- 📝 OpenAI Markdown 重整摘要：轉為結構化會議紀錄。
- 📦 支援 HTTP / SSE / Stdio 模式 MCP Client

---

## 🔐 .env 設定
建立 `.env` 檔案，內容如下：

```env
OPENAI_API_KEY=your_key_here
MCP_MODE=streamable-http, sse, stdio
MAX_ITERATIONS=your_max_iterations_here
MAX_TOKENS=your_max_tokens_here
TEMPERATURE=your_temperature_here
REQUEST_TIMEOUT=your_timeout_here
MODEL=your_model_here
USER_DATA_DIR=your_data_dir_here
PROFILE_DIRECTORY=your_profile_directory_here
DIR=your_directory_here
MAX_INPUT_LENGTH=your_max_length_here
```

或直接在 CLI 中執行：
```bash
export OPENAI_API_KEY=your_key_here
export MCP_MODE=streamable-http, sse, stdio
export MAX_ITERATIONS=your_max_iterations_here
export MAX_TOKENS=your_max_tokens_here
export TEMPERATURE=your_temperature_here
export REQUEST_TIMEOUT=your_timeout_here
export MODEL=your_model_here
export USER_DATA_DIR=your_data_dir_here
export PROFILE_DIRECTORY=your_profile_directory_here
export DIR=your_directory_here
export MAX_INPUT_LENGTH=your_max_length_here
```
---

## 📎 TODO / 延伸規劃

- [ ] 整合新聞、論文與部落格自動爬取模組
- [ ] 支援一鍵生成分析摘要與可視化報表
- [ ] MCP 工具可串接更多分析模組（如 trend 分析、風險評估）

---

## 📜 License

MIT License

## 聯絡作者
Steve Wang | 2025