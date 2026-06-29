from fastapi import FastAPI
from chat.chat_routes import chatbot_app
from knowledgebase_server.kb_routes import kbapp
from fastapi.middleware.cors import CORSMiddleware


import os
import sys

# 获取当前脚本所在目录的绝对路径（假设app_server.py在项目根目录下）
root_dir = os.path.dirname(os.path.abspath(__file__))
# 把根目录加入模块搜索路径
sys.path.append(root_dir)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定 ["http://localhost:7860"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chatbot_app)

app.include_router(kbapp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_server:app", host="127.0.0.1", port=6605, log_level="info", reload=True)