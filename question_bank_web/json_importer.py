import json
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from models import Question, QuestionBank

def import_questions_from_json(json_path, db_session, bank_name="样例题库"):
    """
    从指定的JSON文件导入题目到数据库。
    """
    # 1. 加载JSON文件
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_questions_from_json = data.get("questions", [])
    except FileNotFoundError:
        print(f"错误: JSON文件未找到 at {json_path}")
        return 0, 1 # 0 成功, 1 失败
    except json.JSONDecodeError:
        print(f"错误: JSON文件格式无效 at {json_path}")
        return 0, 1

    if not all_questions_from_json:
        print("信息: JSON文件中没有题目，无需导入。")
        return 0, 0

    # 2. 自动同步题库表，确保"样例题库"存在
    try:
        bank = db_session.query(QuestionBank).filter_by(name=bank_name).first()
        if not bank:
            bank = QuestionBank(name=bank_name)
            db_session.add(bank)
            db_session.commit()
        bank_id = bank.id
    except Exception as e:
        db_session.rollback()
        print(f"错误: 同步题库失败: {e}")
        return 0, 1
    
    # 3. 准备要插入的数据
    questions_to_add = []
    existing_ids = {row[0] for row in db_session.query(Question.id).all()}

    for q_data in all_questions_from_json:
        question_id = q_data.get("id")
        if question_id in existing_ids:
            continue # 如果ID已存在，则跳过

        # 字段映射：将JSON字段映射到数据库模型字段
        mapped_data = {
            'id': question_id,
            'question_bank_id': bank_id,
            'question_type_code': q_data.get("type_name", ""),
            'stem': q_data.get("stem", ""),
            'option_a': next((opt['text'] for opt in q_data.get("options", []) if opt['key'] == 'A'), ""),
            'option_b': next((opt['text'] for opt in q_data.get("options", []) if opt['key'] == 'B'), ""),
            'option_c': next((opt['text'] for opt in q_data.get("options", []) if opt['key'] == 'C'), ""),
            'option_d': next((opt['text'] for opt in q_data.get("options", []) if opt['key'] == 'D'), ""),
            'correct_answer': q_data.get("answer", ""),
            'analysis': q_data.get("explanation", ""),
            'difficulty_code': str(q_data.get("difficulty", "3")), # 默认为中等
            # 以下字段在我们的JSON中没有，使用默认值或留空
            'question_number': "", 
            'option_e': "",
            'image_info': "",
            'consistency_code': "3（中等）" # 默认为中等
        }
        questions_to_add.append(mapped_data)

    # 4. 批量插入数据库
    if questions_to_add:
        try:
            db_session.bulk_insert_mappings(Question, questions_to_add)
            db_session.commit()
            print(f"成功导入 {len(questions_to_add)} 条新题目到数据库。")
            return len(questions_to_add), 0
        except Exception as e:
            db_session.rollback()
            print(f"数据库提交失败: {e}")
            return 0, len(questions_to_add)
    else:
        print("信息: 没有新的题目需要导入。")
        return 0, 0

if __name__ == '__main__':
    # 用于直接测试此脚本
    DATABASE_URL = 'sqlite:///local_dev.db'
    JSON_FILE_PATH = 'questions_sample.json'

    if not os.path.exists(JSON_FILE_PATH):
        print(f"测试失败: 请确保 '{JSON_FILE_PATH}' 文件存在于当前目录。")
    else:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("开始从JSON导入题目...")
        success_count, fail_count = import_questions_from_json(JSON_FILE_PATH, db)
        print(f"\n导入完成。成功: {success_count}, 失败/跳过: {fail_count}")
        
        db.close() 