import requests
import json

backend_url = "http://127.0.0.1:6605/chatbot/chat"

def chat_with_backend(prompt, history, sys_prompt, history_len, temperature, top_p, max_tokens, stream,session_id ):
    files = [('files',(open(file_path,'rb'))) for file_path in prompt['files']]
    if prompt['files'] != []:
        query = f"{prompt['text']}\n" + ''.join(prompt['files'][0])
    else:
        query = f"{prompt['text']}\n"
    data = {
        "query": query,
        "sys_prompt": sys_prompt,
        "history_len": history_len,
        "history": [str(h) for h in history],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        'session_id':session_id        
    }
    # # 发送请求到 FastAPI 后端
    # response = requests.post(backend_url, json=data, stream=True)
    # if response.status_code == 200:
    #     # 接收所有chunks的内容
    #     chunks = ""
    #     if stream:
    #         for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    #             chunks += chunk
    #             yield chunks
    #     else:
    #         for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    #             chunks += chunk
    #         yield chunks
    try:
        response = requests.post(backend_url, data=data, stream=True, files=files or None)
        response.raise_for_status()
        
        full_answer = ""
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                try:
                    # 解析每个 JSON chunk，提取 answer 字段
                    chunk_data = json.loads(chunk)
                    answer_part = chunk_data.get("answer", "")
                    full_answer += answer_part
                    if stream:
                        yield full_answer  # 流式返回累积的答案
                except json.JSONDecodeError:
                    print(f"无效的 JSON chunk: {chunk}")
        if not stream:
            yield full_answer  # 非流式返回完整答案
            
    except Exception as e:
        yield f"请求错误: {str(e)}"