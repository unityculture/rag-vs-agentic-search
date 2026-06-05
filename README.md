# RAG vs. Agentic Search — 教學 Demo

同一份產品說明書 PDF，並排比較兩種「幫 LLM 找 context」的方式：

- **① 向量檢索 RAG（PostgreSQL + pgvector）**：把 PDF 切 chunk、算 embedding、存進向量資料庫；查詢時找語意最相近的片段。
- **② Agentic search**：不靠向量庫。讓一個會推理的 agent 自己用工具（列檔 / grep / 讀整份）一步步把答案找出來。

兩邊都用同一顆 LLM 生成最終答案，差別只在「怎麼把 context 找出來」。畫面會把每一步流程畫給你看。

> 產品資料為 demo 用**虛構**說明書（電烤盤 / 循環扇 / 行動電源），非真實規格。

---

## 🚀 最快開始：把這件事交給 Claude Code

這個 repo 設計成**讓 AI agent 幫你裝好跑起來**。你幾乎不用懂技術：

1. 用 Claude Code 開啟這個資料夾。
2. 把這句話貼給它：

   > **「請照 README 把這個 demo 在我電腦上跑起來。過程需要權限時我會按允許。」**

3. 過程中需要你的地方只有三個：
   - **按「允許」** 讓它執行安裝指令。
   - **第一次開 Docker Desktop**：它會請你開啟 Docker，可能要你同意一次授權 / 輸入電腦密碼，並讓 Docker 保持開著。
   - **貼上 API key**：把老師私下給你的那串貼上即可。
4. 最後它會打開瀏覽器，demo 就跑起來了。

下面是給 agent 看的細節，你不用讀。

---

## 🤖 給 AI Agent 的 Onboarding SOP（跨平台）

> 目標：在使用者**最少介入**下，把 demo 從零跑到能在瀏覽器操作。
> 這個 demo 用 **Docker** 跑 PostgreSQL + pgvector，所以 **Mac / Windows 都能用同一套**。

**步驟 0 — 先判斷作業系統**（macOS 還是 Windows），下面指令分流。

### 1. 確保 Docker Desktop 已安裝並在執行
Docker 是唯一需要使用者稍微配合的部分（GUI app）。請盡量代勞：

- **macOS**：
  ```bash
  brew install --cask docker     # 沒有 brew 就引導使用者到 https://brew.sh，或到 docker.com 下載
  open -a Docker                 # 啟動 Docker Desktop
  ```
- **Windows（PowerShell）**：
  ```powershell
  winget install -e --id Docker.DockerDesktop
  # 裝完通常要登出/重開機讓 WSL2 生效，再從開始選單啟動 Docker Desktop
  ```
- **等 daemon 真的起來**（很重要，剛開 Docker 要幾秒）：重試 `docker info` 直到成功為止。
- 第一次啟動 Docker Desktop 會要使用者**同意授權 / 輸入電腦密碼**，這步請使用者本人點。

### 2. 確保 uv（Python 環境管理）
- **macOS**：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Windows**：`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
- 裝完若 `uv` 找不到，請開新終端或把 uv 的安裝路徑加進 PATH。

### 3. 設定 API key
- 把 `.env.example` 複製成 `.env`。
- **向使用者詢問老師提供的 OpenAI API key**，填進 `.env` 的 `OPENAI_API_KEY=` 後面（`.env` 已 gitignore，安全）。

### 4. 啟動資料庫 + 匯入 + 開 UI
```bash
docker compose up -d            # 起 PostgreSQL + pgvector，等它 healthy
uv sync                         # 安裝 Python 套件
uv run python ingest.py         # PDF → chunk → embedding → 寫進 pgvector
uv run streamlit run app.py     # 開 UI，瀏覽器會自動打開
```

### 遇到問題
- `Cannot connect to the Docker daemon` → Docker Desktop 沒開或還沒起來。執行 `open -a Docker`（Mac）/ 開啟 Docker Desktop，等 `docker info` 成功再重試。
- 沒有 Homebrew（Mac）→ 引導使用者到 <https://brew.sh> 或 <https://www.docker.com/products/docker-desktop/> 安裝（這步需本人操作）。
- port 5433 被占用 → 改 `docker-compose.yml` 的 `"5433:5432"` 左邊那個埠，並同步改 `.env` 的 `PGPORT`。
- ingest 報 OpenAI 錯誤 → 多半是 key 沒填或無效，回到第 3 步。

---

## 🧩 手動步驟（不想用 agent 的話）

```bash
docker compose up -d            # 起 pgvector（需先安裝並開啟 Docker Desktop）
uv sync
uv run python ingest.py
uv run streamlit run app.py
```

需求：**Docker Desktop + uv + 老師提供的 OpenAI API key**（Mac / Windows 皆可）。

---

## 📁 檔案說明

| 檔案 | 作用 |
|------|------|
| `docker-compose.yml` | 用 Docker 跑 PostgreSQL + pgvector（pgvector/pgvector:pg17） |
| `gen_samples.py` | 產生 3 份中文產品說明書 PDF（已附在 `data/pdfs/`，通常不用跑） |
| `core.py` | 讀 PDF、切 chunk、呼叫 OpenAI embedding / chat |
| `db.py` | 資料庫連線與 schema |
| `ingest.py` | PDF → chunk → embedding → 寫進 pgvector |
| `rag_pgvector.py` | 方式①：向量檢索 |
| `rag_agentic.py` | 方式②：agent 用 grep / read 工具找 |
| `app.py` | Streamlit UI（兩種方式並排，逐步呈現流程） |

---

## 🔐 安全

- `.env`（含 API key）已列入 `.gitignore`，**不會進 git**。repo 裡的 `.env.example` 的 key 欄位是空的。
- API key 由**老師私下提供**，請勿貼到任何會上傳的檔案或公開場合。
- 課程結束後，老師會 rotate（作廢並更換）這把教學用 key。
