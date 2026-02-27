import json
import os
import requests
import gradio as gr

base_url = "http://127.0.0.1:6605"

def create_kb(kb_name, kb_info):
    # 定义API的URL
    url = base_url + "/kbs/create_kb"
    # 定义请求数据
    data = {
        "kb_name": kb_name,
        "kb_info": kb_info,
    }
    # 发送POST请求
    try:
        response = requests.post(url, json=data)
        print("原始响应内容:", response.text)  # 新增调试代码
        # 检查响应状态码
        if response.status_code == 200:
            return gr.update(value="创建成功！", visible=True), gr.update(value=""), gr.update(value=""), gr.update(value="")
        else:
            return gr.update(value=f"创建失败：{response.json().get('detail', '')}", visible=True), gr.update(value=""), gr.update(
                value="")
    except Exception as e:
        return gr.update(value=f"请求失败：{e}", visible=True), gr.update(value=""), gr.update(value="")


def delete_kb(kb_name):
    kb_name = kb_name.split(" | ")[0].strip()
    # 定义API的URL
    url = base_url + "/kbs/delete_kb"
    # 发送POST请求
    try:
        response = requests.delete(url, params={"kb_name": kb_name})
        # 检查响应状态码
        if response.status_code == 200:
            return gr.update(value="删除成功！", visible=True), gr.update(value="")
        else:
            return gr.update(value=f"删除失败：{response.json().get('detail', '')}", visible=True), gr.update(value="")
    except Exception as e:
        return gr.update(value=f"请求失败：{e}", visible=True), gr.update(value="")


def list_kbs():
    # 定义API的URL
    list_kbs_url = base_url + "/kbs/list_kbs"  # 请确保端口和路径正确
    # 发送GET请求
    response = requests.get(list_kbs_url)
    # 检查响应状态码并打印结果
    if response.status_code == 200:
        kb_list = response.json()  # 解析JSON格式的kb_name       
        print("========================", response)
        print("========================", kb_list)
        return gr.update(choices=kb_list, value=kb_list[0] if kb_list else None )
    else:
        return gr.update(choices=[])
    
selected_files =[]
def update(file):
    if file:
        for f in file:
            if f not in selected_files:
                selected_files.append(f)
    return gr.update(value=selected_files,visible=True),gr.update(value=[])

def upload_docs(kb_name_upload,file_upload,chunk_size,chunk_overlap):
    upload_docs_url = base_url + '/kbs/upload_docs'
    files = [('files',(open(file_path,'rb'))) for file_path in file_upload if os.path.getsize(file_path) >0]
    if not files:
        return gr.update(value=f"上传所有文件，全部内容为空",visible=True),gr.update(value=[],visible=False)
    
    data = {
        'kb_name' : kb_name_upload,
        'chunk_size':chunk_size,
        'chunk_overlap':chunk_overlap
    }
    global selected_files
    selected_files = []
    try:
        response = requests.post(upload_docs_url,files=files,data=data)

        if response.status_code==200:
            return gr.update(value='文件上传成功',visible=True),gr.update(value=[],visible=False)
        else:
            return gr.update(value=f"文件上传失败，状态码:{response.status_code},错误信息：{response.json().get('detail','')}",visible=True),gr.update(value=[],visible=False)
    except Exception as e :
        return gr.update(value=f"请求失败：{e}",visible=True),gr.update(value=[],visible=False)