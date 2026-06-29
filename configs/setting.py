import os

from dotenv import load_dotenv

load_dotenv()

# 知识库信息数据库路径
SQLALCHEMY_DATABASE = './db/server/data'

SQLALCHEMY_DATABASE_URI = 'sqlite:///./db_server/data/info.db'


KB_DIR = './knowledgebases'


FILE_STORAGE_DIR = './data'

embedding_model_path = './models/AI-ModelScope/bge-large-zh-v1___5'



TEMP_FILE_STORAGE_DIR = './temp/data'


chat_model_name = 'Qwen/Qwen2.5-7B-Instruct'
api_key = os.getenv('SILICONFLOW_API_KEY', '')
base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')

TIME_OUT = 60

MEDIA_DIR = './temp/medias'
