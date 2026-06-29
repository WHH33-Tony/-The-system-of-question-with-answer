# 智能问答系统

基于 **Gradio + FastAPI + LangChain Agent + RAG** 的智能问答演示项目。支持流式对话、本地知识库检索、网页搜索、天气查询、代码执行等能力。

> 本项目为学习/演示用途的原型，非生产级系统。

**GitHub 仓库：** [WHH33-Tony/-The-system-of-question-with-answer](https://github.com/WHH33-Tony/-The-system-of-question-with-answer)

## 功能特性

### 聊天机器人

- 流式对话，支持多轮历史
- 可调参数：系统提示词、temperature、top_p、max_tokens、历史轮数
- 支持在对话中上传文件，作为临时上下文参与回答
- 基于 ReAct Agent，自动选择并调用工具

### Agent 工具

| 工具 | 说明 |
|------|------|
| `knowledge_search` | 检索本地知识库（FAISS + BM25 混合检索） |
| `web_search` | 通过 SerpAPI 进行百度网页搜索 |
| `weather check` | 查询指定城市实时天气（心知天气 API） |
| `get_time` | 获取当前时间 |
| `code_interpreter` | 执行 Python 代码并返回结果/图片 |

### 知识库管理

- 创建 / 删除 / 列出知识库
- 上传文档并向量化入库
- 支持格式：`.txt`、`.pdf`、`.md`、`.csv`
- 检索策略：向量检索（FAISS）+ 关键词检索（BM25）混合

## 技术架构

```
Gradio 前端 (webui.py)
        ↓ HTTP
FastAPI 后端 (app_server.py :6605)
   ├── /chatbot/chat   → LangChain ReAct Agent
   └── /kbs/*          → 知识库 CRUD + 检索
        ↓
SQLite（知识库元数据）+ FAISS（向量索引）+ 本地文件存储
        ↓
SiliconFlow API（大模型 + Embedding）
```

## 环境要求

- Python 3.10+
- 需准备以下 API Key（见「配置说明」）：
  - **SiliconFlow**：大语言模型与 Embedding（必需）
  - **SerpAPI**：网页搜索（可选，不使用 web_search 工具时可不配）
  - **心知天气**：天气查询（可选）
  - **CodeBox**：代码解释器（可选，本地模式）

## 安装

```bash
git clone https://github.com/WHH33-Tony/-The-system-of-question-with-answer.git
cd -The-system-of-question-with-answer

# 建议使用虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install fastapi uvicorn gradio requests sqlalchemy python-dotenv \
    langchain langchain-openai langchain-community \
    faiss-cpu jieba pydantic codeboxapi \
    pypdf unstructured python-docx pymupdf modelscope

cp .env.example .env   # Windows 可手动复制后编辑
```

> 建议后续补充 `requirements.txt` 并锁定版本，便于复现环境。

## 配置说明

编辑 `configs/setting.py`：

| 配置项 | 说明 |
|--------|------|
| `api_key` | SiliconFlow API Key |
| `base_url` | SiliconFlow API 地址 |
| `chat_model_name` | 对话模型，默认 `Qwen/Qwen2.5-7B-Instruct` |
| `KB_DIR` | FAISS 索引存储目录 |
| `FILE_STORAGE_DIR` | 知识库原始文件目录 |
| `TEMP_FILE_STORAGE_DIR` | 对话临时上传文件目录 |

其他 Key 位于对应工具文件中：

- 网页搜索：`tools/web_search.py`
- 天气查询：`tools/weather_check.py`

复制 `.env.example` 为 `.env` 并填入各 API Key 后即可使用。

## 启动方式

需要同时运行后端和前端（两个终端）：

**终端 1 — 启动 FastAPI 后端**

```bash
python app_server.py
# 默认地址: http://127.0.0.1:6605
```

**终端 2 — 启动 Gradio 前端**

```bash
python webui.py
# 浏览器打开 Gradio 显示的本地地址（通常 http://127.0.0.1:7860）
```

## 使用指南

### 1. 管理知识库

1. 打开「知识库管理」标签页
2. 输入名称和描述，点击「创建知识库」
3. 选择知识库，上传文档，设置分块参数后点击「上传并向量化」

### 2. 开始对话

1. 打开「聊天机器人」标签页
2. 按需调整系统提示词和模型参数
3. 输入问题；Agent 会根据问题自动选择工具
4. 若需基于某知识库回答，请在问题中说明知识库名称，或确保 Agent 调用 `knowledge_search`（输入格式：`知识库名,问题`）

### 3. 对话中上传文件

支持在聊天界面直接上传文件，内容会作为临时文档上下文传入 Agent，不会写入持久知识库。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/chatbot/chat` | 流式对话（Form 表单，支持文件上传） |
| POST | `/kbs/create_kb` | 创建知识库 |
| DELETE | `/kbs/delete_kb` | 删除知识库 |
| GET | `/kbs/list_kbs` | 列出所有知识库 |
| POST | `/kbs/upload_docs` | 上传文档并向量化 |
| POST | `/kbs/search_kb` | 检索指定知识库 |

## 项目结构

```
├── app_server.py          # FastAPI 入口
├── webui.py               # Gradio 前端入口
├── chat/                  # 对话路由与 Agent 逻辑
├── knowledgebase_server/  # 知识库 API
├── tools/                 # Agent 工具集
├── db_server/             # SQLite 元数据
├── loader/                # 文档加载器
├── configs/               # 配置与 Prompt 模板
├── data/                  # 知识库原始文件
├── knowledgebases/        # FAISS 向量索引（运行时生成）
└── temp/                  # 临时文件与媒体输出
```

## 已知限制

- **无用户系统**：无登录、权限、多租户隔离
- **知识库检索非全自动**：Agent 需主动调用 `knowledge_search`，并指定知识库名称
- **无外部学术库集成**：不支持知网、万方等；网页搜索仅为通用搜索引擎
- **Prompt 策略**：当前默认 Prompt 未强制「本地知识库优先」（见 `configs/prompt.py` 注释版本）
- **无自动化测试与 CI**：仅含零散测试脚本

## 后续规划

- [ ] 添加 `requirements.txt` 与 Docker 部署
- [ ] 支持跨知识库自动检索
- [ ] 切换/启用「本地知识库优先」Prompt 策略
- [ ] 用户认证与对话历史持久化

## License

待定
