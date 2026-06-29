import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 获取当前脚本（base.py）所在目录的绝对路径
current_script_dir = os.path.dirname(os.path.abspath(__file__))  # 如 /home/hqyj_ai/ai_rag/db_server
# 2. 拼接 db_server/data/info.db 的绝对路径（无需依赖运行目录）
db_dir = os.path.join(current_script_dir, "data")  # 拼接 data 目录：/home/hqyj_ai/ai_rag/db_server/data
os.makedirs(db_dir, exist_ok=True)  # 确保 data 目录存在（不存在则自动创建）
db_path = os.path.join(db_dir, "info.db")  # 完整数据库路径：/home/hqyj_ai/ai_rag/db_server/data/info.db

# 3. 创建数据库引擎（使用绝对路径）
engine = create_engine(f'sqlite:///{db_path}', echo=True)

# 创建基类，所有模型都继承自这个基类
Base = declarative_base()

class Kb(Base):
    # 表名
    __tablename__ = 'kb_table'
    # 定义表中的列，包括类型，约束，字段说明
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')# 主键
    kb_name = Column(String(50), comment="名称")
    kb_info = Column(String(255), comment='简介')

    # 返回一个字符串，用于表示对象的字符串表示形式，当打印或查看对象时，会调用这个方法来获取对象的字符串表示
    def __repr__(self):
        return f"<Kb(id='{self.id}', kb_name='{self.kb_name}', kb_info='{self.kb_info}')>"
    
# 创建所有表， 第一次执行创建表，如果表结构已经存在，再次执行这行代码不会对数据库产生任何影响，不会重新重复创建已经存在的表
# 如果模型改变，增加列，修改列，修改列的类型或约束，再次执行会更新
Base.metadata.create_all(engine)



# 创建会话
# sessionmaker用于创建会话工厂（Session Factory），会话工厂可以生成多个会话实例，都绑定到同一个数据库引擎（engine）
# 通过这个会话工厂创建的会话实例都可以使用这个引擎与数据库进行交互
Session = sessionmaker(bind=engine)
# 这个会话实例是应用程序与数据库之间交互的接口
# 提供了执行数据库操作的方法，添加数据、查询数据、提交事务、回滚事务，方便操作数据库中的表和数据
session = Session()