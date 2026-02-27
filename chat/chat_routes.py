import sys
import os

# # 1. 获取当前文件（tool_select.py）的绝对路径
# current_file = os.path.abspath(__file__)
# # 2. 获取当前文件所在目录（即 ai_rag/tools/）
# tools_dir = os.path.dirname(current_file)
# # 3. 获取项目根目录（即 ai_rag/，tools_dir 的父目录）
# project_root = os.path.dirname(tools_dir)
# # 4. 将项目根目录加入 Python 搜索路径
# sys.path.append(project_root)

# # 之后再导入 tools 下的模块（此时 Python 能在 ai_rag/ 下找到 tools 包）
from tools.code_interpreter import code_interpreter
from tools.weather_check import weather_check
# ... 其他 tools 模块的导入


import os
import json
import asyncio
from ast import literal_eval
from tools.tool_select import tools
from configs.prompt import PROMPT_TEMPLATES
from fastapi.responses import StreamingResponse
from typing import AsyncIterable, List
from fastapi import APIRouter, Form, UploadFile
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent,AgentExecutor
from langchain.prompts import SystemMessagePromptTemplate,HumanMessagePromptTemplate
from utils.callback import CustomAsyncIteratorCallbackHandler
from db_server.base import session
from db_server.knowledge_base_respository import list_kb_from_db
from tools.code_interpreter import code_interpreter
from utils.load_docs import get_file_content
from configs.setting import TIME_OUT, api_key,chat_model_name,base_url
from fastapi.responses import StreamingResponse
from configs.setting import TEMP_FILE_STORAGE_DIR



chatbot_app = APIRouter(prefix="/chatbot", tags=["chatbot management"])
def files_rag(files,uuid):
    kb_file_storage_path = os.path.join(TEMP_FILE_STORAGE_DIR,uuid)
    result = []
    os.makedirs(kb_file_storage_path,exist_ok=True)
    if files:
        for file in files:
            file_path = os.path.join(kb_file_storage_path,file.filename)

            with open(file_path,'wb') as f:
                f.write(file.file.read())

    for filename in os.listdir(kb_file_storage_path):
        file_path = os.path.join(kb_file_storage_path,filename)
        if os.path.isfile(file_path):
            file_content = get_file_content(file_path)

            result.append(f"document:.{file_path}\ncontent:{file_content}\n")
    return "".join(result)


# 定义路由，实现接口对接
# Body从请求体中提取数据
# app = FastAPI()
# chatbot_app = APIRouter(prefix="/chatbot", tags=["chatbot management"])
# messages = []
# api_key = 'sk-talrfpdubittuoctscpxqyuhotkkqgcmuxrxxlmmhkqpzlxd'
# base_url = 'https://api.siliconflow.cn/v1'

# aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)


@chatbot_app.post("/chat")
async def chat(
        files:List[UploadFile] = None,
        query: str = Form(..., description="用户输入"),  # ...必须输入
        sys_prompt: str = Form("You are a helpful assistant.", description="系统提示"),
        history_len: int = Form(-1, description="保留历史消息的数量"),
        history: List[str] = Form([], description="历史对话"),
        temperature: float = Form(0.7, description="LLM采样温度"),
        top_p: float = Form(0.7, description="LLM采样概率"),
        max_tokens: int = Form(100, description="LLM最大token数配置"),
        session_id: str =Form(None,description="会话标识"), 
):
    
    documents = files_rag(files,session_id)
    history = [literal_eval(item) for item in history]
    histories = ""
    if history_len > 0:
        history = history[-2 * history_len:]
    for msg in history:
        role = msg.get('role')
        content = msg.get('content')
        histories += f"{role}:{content}\n\n"
    async def agent_chat_iterator() -> AsyncIterable[str]:
        callback = CustomAsyncIteratorCallbackHandler()
        callbacks = [callback]

        chat_model = ChatOpenAI(
            model=chat_model_name,
            api_key= api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
            callbacks=callbacks
        )
        system_prompt = SystemMessagePromptTemplate.from_template(
            sys_prompt
        )
        human_prompt = HumanMessagePromptTemplate.from_template(
            PROMPT_TEMPLATES['agent']
        )
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt,human_prompt])
        agent = create_react_agent(chat_model,tools,chat_prompt,stop_sequence=["\nObserv"])
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
        )
        knowledgebases = list_kb_from_db(session)
        kbs = "".join([f"{kb['kb_name']} - {kb['kb_info']} \n" for kb in knowledgebases])
        code_interpreter.output_files,code_interpreter.output_codes = "",""

        task = asyncio.create_task(
            agent_executor.acall(
                inputs={"input":query,"history":histories,"knowledgebases":kbs,"documents":documents})
        )
        async for token in callback.aiter():
            response_data = {
                "answer":token,
            }
            yield json.dumps(response_data).encode("utf-8")
        await asyncio.wait_for(task,TIME_OUT)
        output_files,output_codes = code_interpreter.get_outputs()
        if output_files:
            yield json.dumps({"answer":f"\n\n{output_codes}\n\n![](http://localhost:6605{output_files})"}).encode('utf-8')
        else:
            yield json.dumps({'answer':f"\n\n{output_codes}"}).encode('utf-8')

    # 返回 StreamingResponse，以流的形式发送数据。流式响应fastapi的客户端
    return StreamingResponse(agent_chat_iterator(), media_type="application/plain")