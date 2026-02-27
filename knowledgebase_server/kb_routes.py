from langchain_community.retrievers import BM25Retriever
import os
import shutil
from db_server.base import session
from db_server.knowledge_base_respository import add_kb_to_db, del_kb_from_db, list_kb_from_db

from typing import List
import jieba
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.retrievers import EnsembleRetriever

from loader.loader import data_loader
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import HTTPException,APIRouter,Body,UploadFile,File,Form
from configs.setting import KB_DIR,FILE_STORAGE_DIR
from configs.setting import api_key,base_url

kbapp = APIRouter(prefix="/kbs", tags=['knowledge management'])

if not os.path.exists(KB_DIR):
    os.makedirs(KB_DIR)
    
class CustomEmbeddingModel(Embeddings):
    def __init__(self,model,model_name):
        self.model = model
        self.model_name = model_name
    def embed_documents(self, texts):
        return [self.model.client.create(model=self.model_name,input=text).data[0].embedding for text in texts]
    def embed_query(self, text):
        return self.model.client.create(model=self.model_name,input=text).data[0].embedding

embedding = OpenAIEmbeddings(
    api_key= api_key,
    base_url = base_url
)
embedding_model = CustomEmbeddingModel(embedding,"BAAI/bge-large-zh-v1.5")


@kbapp.post("/create_kb")
async def create_kb(
    kb_name: str = Body(..., description='知识库名称'),
    kb_info: str = Body("", description='知识库描述'),
):
    kb_path = os.path.join(KB_DIR,f"{kb_name}.faiss")

    if os.path.exists(kb_path):
        raise HTTPException(status_code=400,detail="知识库已存在")
    doc = Document(page_content='init',metadata={})
    vector_store = FAISS.from_documents([doc],embedding_model,normalize_L2=True)
    ids = list(vector_store.docstore._dict.keys())
    vector_store.delete(ids)
    vector_store.save_local(kb_path)
    add_kb_to_db(session,kb_name,kb_info)
    return {'message':f"知识库'{kb_name}'创建成功！"}


@kbapp.delete("/delete_kb")
async def delete_kb(kb_name: str):
    kb_path = os.path.join(KB_DIR,f"{kb_name}.faiss")
    kb_files_path = os.path.join(FILE_STORAGE_DIR,kb_name)
    if not os.path.exists(kb_path):
        raise HTTPException(status_code=404,detail="Database not found")
    shutil.rmtree(kb_path)
    if os.path.exists(kb_files_path):
        shutil.rmtree(kb_files_path)
    
    del_kb_from_db(session, kb_name)
    return {'message':f"Database'{kb_name}'删除成功！"}

@kbapp.get("/list_kbs")
async def list_kbs():
    kb_list = list_kb_from_db(session)
    result = [kb['kb_name'] for kb in kb_list]
    return result

@kbapp.post('/upload_docs')
async def upload_docs(
    files:List[UploadFile] = File(...),
    kb_name:str = Form(...,description='知识库名称'),
    chunk_size: int = Form(128,description='知识库单段文本最大长度'), 
    chunk_overlap :int = Form(20,description='知识库相邻文本重合长度'),
):

    kb_path = os.path.join(KB_DIR,f"{kb_name}.faiss")
    kb_file_storage_path = os.path.join(FILE_STORAGE_DIR,kb_name)

    if not os.path.exists(kb_path):
        raise HTTPException(status_code=404,detail="Database not found")
    
    os.makedirs(kb_file_storage_path,exist_ok=True)
    updated_file = []
    for file in files:
        file_path = os.path.join(kb_file_storage_path,file.filename)
        file_content = file.file.read()

        with open(file_path,'wb') as f:
            f.write(file_content)

        loader = data_loader().get_loader(file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap,separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            "，",
            "。",
            ""
        ],)
        chunks = text_splitter.split_documents(docs)
        vectorstore = FAISS.load_local(kb_path,embedding_model,allow_dangerous_deserialization=True)

        vectorstore.add_documents(chunks)
        vectorstore.save_local(kb_path)
        updated_file.append(file.filename)

    return {"message":f"File'{updated_file}'added to database '{kb_name}'successfully"}


# 在tools/knowledge_search.py文件中调用
@kbapp.post("/search_kb")
async def search_db(
    kb_name: str = Body(..., description="知识库名称"),
    query: str = Body(..., description="问题")
):
    kb_path = os.path.join(KB_DIR, f"{kb_name}.faiss")

    if not os.path.exists(kb_path):
        raise HTTPException(status_code=404, detail="Database not found")
    
    vector_store = FAISS.load_local(kb_path, embedding_model, allow_dangerous_deserialization=True)
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k":2})
    docs = list(vector_store.docstore._dict.values())
    bm25_retriever = BM25Retriever.from_documents(
        docs,
        preprocess_func=jieba.lcut_for_search
    )
    bm25_retriever.k = 2
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],weights=[0.5,0.5]
    )
    contexts = ensemble_retriever.invoke(query)
    contexts = {
        "results":[{"sources": context.metadata.get("sources",""),"page_contents":context.page_content} for context in contexts]
    }
    return contexts