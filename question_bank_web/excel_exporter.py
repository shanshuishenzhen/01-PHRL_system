import pandas as pd
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Question, QuestionBank

def export_questions_to_excel(questions, output_path, bank_name="样例题库"):
    """
    将题目列表导出为Excel文件
    """
    # 准备数据框架
    data = []
    for q in questions:
        # 处理选项，将选项对象转换为字符串
        options = q.get("options", [])
        option_a = next((opt['text'] for opt in options if opt['key'] == 'A'), "")
        option_b = next((opt['text'] for opt in options if opt['key'] == 'B'), "")
        option_c = next((opt['text'] for opt in options if opt['key'] == 'C'), "")
        option_d = next((opt['text'] for opt in options if opt['key'] == 'D'), "")
        option_e = next((opt['text'] for opt in options if opt['key'] == 'E'), "")
        
        # 创建行数据
        row = {
            'ID': q.get("id", ""),
            '题库名称': bank_name,
            '题型代码': q.get("type_name", ""),
            '题号': "",
            '试题（题干）': q.get("stem", ""),
            '试题（选项A）': option_a,
            '试题（选项B）': option_b,
            '试题（选项C）': option_c,
            '试题（选项D）': option_d,
            '试题（选项E）': option_e,
            '【图】及位置': "",
            '正确答案': q.get("answer", ""),
            '难度代码': f"{int(float(q.get('difficulty', 0.5))*5)}（{'很简单' if float(q.get('difficulty', 0.5)) < 0.2 else '简单' if float(q.get('difficulty', 0.5)) < 0.4 else '中等' if float(q.get('difficulty', 0.5)) < 0.6 else '困难' if float(q.get('difficulty', 0.5)) < 0.8 else '很难'}）",
            '一致性代码': "3（中等）",
            '解析': q.get("explanation", "")
        }
        data.append(row)
    
    # 创建DataFrame并导出为Excel
    df = pd.DataFrame(data)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 写入Excel文件
    df.to_excel(output_path, index=False)
    
    return len(data)

def export_db_questions_to_excel(db_session, output_path, bank_name=None):
    """
    从数据库导出题目到Excel文件
    """
    # 查询题目
    query = db_session.query(Question)
    if bank_name:
        bank = db_session.query(QuestionBank).filter_by(name=bank_name).first()
        if bank:
            query = query.filter_by(question_bank_id=bank.id)
    
    questions = query.all()
    
    # 准备数据框架
    data = []
    for q in questions:
        # 创建行数据
        row = {
            'ID': q.id,
            '题库名称': q.question_bank.name if q.question_bank else "",
            '题型代码': q.question_type_code,
            '题号': q.question_number,
            '试题（题干）': q.stem,
            '试题（选项A）': q.option_a,
            '试题（选项B）': q.option_b,
            '试题（选项C）': q.option_c,
            '试题（选项D）': q.option_d,
            '试题（选项E）': q.option_e,
            '【图】及位置': q.image_info,
            '正确答案': q.correct_answer,
            '难度代码': q.difficulty_code,
            '一致性代码': q.consistency_code,
            '解析': q.analysis
        }
        data.append(row)
    
    # 创建DataFrame并导出为Excel
    df = pd.DataFrame(data)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 写入Excel文件
    df.to_excel(output_path, index=False)
    
    return len(data)

if __name__ == '__main__':
    # 用于直接测试此脚本
    DATABASE_URL = 'sqlite:///local_dev.db'
    EXCEL_FILE_PATH = 'questions_export.xlsx'
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("开始导出题目到Excel...")
        count = export_db_questions_to_excel(db, EXCEL_FILE_PATH)
        print(f"导出完成。共导出 {count} 道题目到 {EXCEL_FILE_PATH}")
    finally:
        db.close()