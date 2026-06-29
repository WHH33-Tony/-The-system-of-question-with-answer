from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db_server.base import Kb, session

def add_kb_to_db(session:Session, kb_name:str, kb_info:str):
    print("[数据库] 准备写入：", kb_name, kb_info)
    try:
        # 查询是否存在相同名称的kb_name，ilike代表不区分大小写的模糊匹配

        #     更灵活，可写复杂条件，如 >=, ilike, or_
        kb = session.query(Kb).filter(Kb.kb_name.ilike(kb_name)).first()
        if not kb:
            # 如果不存在，创建新的kb_name
            kb = Kb(kb_name=kb_name, kb_info=kb_info)
            session.add(kb)
            session.commit() 
            result = f"Kb '{kb_name}' created successfully."
        else:
            result = f"Kb '{kb_name}' already exist."
    except IntegrityError as e:
        session.rollback()
        result = f"IntegrityError: {e}"
        
    except Exception as e:
        session.rollback()
        result = f"An error occurred: {e}"
    return result 


def del_kb_from_db(session: Session, kb_name: str):
    print("[DB] 准备删除：", kb_name) 
    try:
        # 查询是否存在指定名称的kb_name

        # 简洁，关键字参数，适合“=”匹配
        kb_to_delete = session.query(Kb).filter_by(kb_name=kb_name).first()

        if kb_to_delete:
            # 如果存在，删除kb_name
            session.delete(kb_to_delete)
            session.commit()
            result = f"Kb '{kb_name}' deleted successfully."
        else:
            result = f"Kb '{kb_name}' does not exist."
    except IntegrityError as e:
        session.rollback()
        result = f"IntegrityError: {e}"
    except Exception as e:
        session.rollback()
        result = f"An error occurred: {e}"
    return result 

def list_kb_from_db(session: Session):
    # 查找所有
    all_kbs = session.query(Kb).all()
    # 将结果转换为列表
    kbs_list = [
        {
            "id": kb.id,
            "kb_name": kb.kb_name,
            "kb_info": kb.kb_info,
        }
        for kb in all_kbs
    ]
    return kbs_list