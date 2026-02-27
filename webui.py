import uuid
import gradio as gr
import requests

from webui.chat_with_agent_api import chat_with_backend
from webui.knowledgebase_api import create_kb, delete_kb, list_kbs,update, upload_docs

# backend_url = "http://127.0.0.1:6605/chatbot/chat"
def on_app_load():
    session_id = str(uuid.uuid4())
    return session_id


# 使用gradio.Blocks创建一个块，并设置可以填充高度和宽度
with gr.Blocks(fill_width=True, fill_height=True) as demo:
    session_state = gr.State(value=on_app_load)
    # 创建一个标签页
    with gr.Tab(" 🤖 聊天机器人"):
        # 添加标题
        gr.Markdown("## 🤖 聊天机器人")

        # 创建一个行布局
        with gr.Row():
            # 创建一个左侧的列布局
            with gr.Column(scale=1, variant="panel") as sidebar_left:
                sys_prompt = gr.Textbox(label="系统提示词", value="You are a helpful assistant")
                # gradio有属性history存储历史，所以不用我们自定义
                history_len = gr.Slider(minimum=1, maximum=10, value=1, label="保留历史消息的数量")
                temperature = gr.Slider(minimum=0.01, maximum=2.0, value=0.5, step=0.01, label="temperature")
                top_p = gr.Slider(minimum=0.01, maximum=1.0, value=0.5, step=0.01, label="top_p")
                max_tokens = gr.Slider(minimum=64, maximum=512, value=512, step=8, label="max_tokens")
                stream = gr.Checkbox(label="stream", value=True)
            # 创建右侧的列布局，设置比例为10
            with gr.Column(scale=10) as main:
                # 创建聊天机器人的聊天界面，高度为500px
                chatbot = gr.Chatbot(type="messages", height=500)
                # 创建chatinterface，用于处理聊天的逻辑.fn中设置的是和fastapi交互的函数
                iface = gr.ChatInterface(fn=chat_with_backend,
                                multimodal=True,
                                type="messages",
                                theme='soft',
                                chatbot=chatbot,
                                additional_inputs=[
                                    sys_prompt,
                                    history_len,
                                    temperature,
                                    top_p,
                                    max_tokens,
                                    stream,
                                    session_state,
                                ])        
                # iface.launch() 

    with gr.Tab("知识库管理"):
        gr.Markdown("## 📚 知识库管理")
        with gr.Row():
            kb_name = gr.Textbox(label="知识库名称", placeholder="请输入知识库名称")
        with gr.Row():
            kb_info = gr.Textbox(label="知识库描述", placeholder="请输入描述")
        with gr.Row():
            # 隐藏的消息框，用于显示操作结果
            message_box = gr.Markdown(visible=False)
        with gr.Row():
            create_button = gr.Button("创建知识库")
            delete_button = gr.Button("删除知识库")

        with gr.Row():
            kb_name_select = gr.Dropdown(label="选择知识库", choices=[], interactive=True )

        

        with gr.Row():
            file_uploaded = gr.Files(label="已选择的文件",visible=False)
        with gr.Row():
            file_upload = gr.Files(label="选择文件")
        with gr.Row():
            chunk_size = gr.Number(label="知识库单段文本创建最大长度",value=128,minimum=1,maximum=800)
            chunk_overlap = gr.Number(label="知识库相邻文本重合程度",value=20,minimum=0,maximum=400)
        with gr.Row():
            upload_button = gr.Button('上传并向量化')
        with gr.Row():
            upload_message_box = gr.Markdown(visible=False)

        demo.load(
                    fn=list_kbs,
                    outputs=kb_name_select,
                    queue=True  # 确保在界面渲染完成后执行
                )

        create_button.click(create_kb, [kb_name, kb_info], [message_box, kb_name, kb_info]).then(fn=list_kbs,outputs=kb_name_select)
        delete_button.click(delete_kb, [kb_name_select], [message_box, kb_name]).then(fn=list_kbs, outputs=kb_name_select)

        file_upload.upload(fn=update,inputs=[file_upload],outputs=[file_uploaded,file_upload])
        upload_button.click(upload_docs,[kb_name_select,file_uploaded,chunk_size,chunk_overlap],[upload_message_box,file_uploaded])

# demo启动，点击运行就可以看到
demo.launch()