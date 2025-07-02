import pandas as pd
import os
import datetime
import time  # 添加time模块导入
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from models import Question, QuestionBank

EXPECTED_COLUMNS = [
    'ID', '序号', '认定点代码', '题型代码', '题号', '试题（题干）',
    '试题（选项A）', '试题（选项B）', '试题（选项C）', '试题（选项D）', '试题（选项E）',
    '【图】及位置', '正确答案', '难度代码', '一致性代码', '解析'
]

def parse_question_id(id_str):
    """
    解析题目ID字符串，返回结构化数据
    新格式：题型代码-一级代码-二级代码-三级代码-知识点代码-顺序号
    例如：B-A-B-C-001-002
    """
    parts = str(id_str).split('-')
    if len(parts) != 6:
        raise ValueError(f"ID格式错误: {id_str}. 应为'题型代码-一级代码-二级代码-三级代码-知识点代码-顺序号'格式")
    return {
        "question_type_code": parts[0],
        "level1_code": parts[1],
        "level2_code": parts[2],
        "level3_code": parts[3],
        "knowledge_point": parts[4],
        "sequence": parts[5],
        "full_id": id_str
    }

def import_questions_from_excel(filepath, db_session):
    """从Excel文件导入题目"""
    try:
        df = pd.read_excel(filepath, dtype=str)
        df = df.fillna('')
    except FileNotFoundError:
        return [], [{"type": "file", "message": f"文件未找到: {filepath}"}]
    except Exception as e:
        return [], [{"type": "file", "message": f"读取Excel文件错误: {e}"}]

    # 验证列
    if not all(col in df.columns for col in ['ID', '题库名称', '题型代码', '试题（题干）', '正确答案', '难度代码']):
        missing = [col for col in ['ID', '题库名称', '题型代码', '试题（题干）', '正确答案', '难度代码'] if col not in df.columns]
        return [], [{"type": "validation", "message": f"Excel文件缺少核心列: {', '.join(missing)}"}]

    questions_to_add = []
    detailed_errors = []
    bank_cache = {} # 题库名称到ID的缓存

    # 1. 查数据库已存在ID
    try:
        db_existing_ids = set([row[0] for row in db_session.execute(text('SELECT id FROM questions')).fetchall()])
    except Exception:
        db_existing_ids = set()

    # 2. Excel内部和数据库冲突自动修正ID
    seen_ids = set(db_existing_ids)
    for index, row in df.iterrows():
        orig_id = str(row.get('ID', '')).strip()
        bank_name = str(row.get('题库名称', '')).strip()
        new_id = orig_id
        suffix = bank_name[:4] if bank_name else 'BK'
        seq = 1
        while new_id in seen_ids:
            new_id = f"{orig_id}_{suffix}{seq}"
            seq += 1
        df.at[index, 'ID'] = new_id
        seen_ids.add(new_id)

    # 3. 自动同步题库表
    all_bank_names = set(str(row.get('题库名称', '')).strip() for _, row in df.iterrows() if str(row.get('题库名称', '')).strip())
    if all_bank_names:
        try:
            existing_banks = db_session.query(QuestionBank).filter(QuestionBank.name.in_(all_bank_names)).all()
            existing_bank_names = {b.name for b in existing_banks}
            bank_cache = {b.name: b.id for b in existing_banks}

            for bank_name in all_bank_names:
                if bank_name and bank_name not in existing_bank_names:
                    new_bank = QuestionBank(name=bank_name)
                    db_session.add(new_bank)
                    db_session.flush() # 刷新以获取ID
                    bank_cache[bank_name] = new_bank.id
                    existing_bank_names.add(bank_name)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            # 不能因为题库同步失败就停止，但要记录错误
            detailed_errors.append({"type": "db_sync", "message": f"同步题库表失败: {e}"})

    for index, row in df.iterrows():
        row_num = index + 2
        try:
            # 数据验证和转换
            question_id_str = str(row['ID']).strip()
            bank_name = str(row.get('题库名称', '')).strip()

            if not question_id_str or not bank_name:
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": "ID和题库名称不能为空"
                })
                continue
            
            # 从缓存获取 bank_id
            bank_id = bank_cache.get(bank_name)
            if not bank_id:
                # 如果缓存没有，可能意味着题库同步失败，跳过此行
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": f"无法找到或创建题库 '{bank_name}'"
                })
                continue
            
            # 验证题型代码 - 支持国家标准格式
            valid_question_types = {
                'B（单选题）', 'G（多选题）', 'C（判断题）', 'T（填空题）', 
                'D（简答题）', 'U（计算题）', 'W（论述题）', 'E（案例分析题）', 'F（综合题）'
            }
            question_type = str(row.get('题型代码', '')).strip()
            if question_type not in valid_question_types:
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": f"无效的题型代码 '{question_type}'，应为: B（单选题）、G（多选题）、C（判断题）等"
                })
                continue

            # 验证难度代码 - 支持国家标准格式
            valid_difficulty_codes = {
                '1（很简单）', '2（简单）', '3（中等）', '4（困难）', '5（很难）'
            }
            difficulty_code = str(row.get('难度代码', '')).strip()
            if difficulty_code not in valid_difficulty_codes:
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": f"无效的难度代码 '{difficulty_code}'，应为: 1（很简单）、2（简单）、3（中等）、4（困难）、5（很难）"
                })
                continue

            # 验证一致性代码 - 支持国家标准格式
            valid_consistency_codes = {
                '1（很低）', '2（低）', '3（中等）', '4（高）', '5（很高）'
            }
            consistency_code = str(row.get('一致性代码', '')).strip()
            if consistency_code not in valid_consistency_codes:
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": f"无效的一致性代码 '{consistency_code}'，应为: 1（很低）、2（低）、3（中等）、4（高）、5（很高）"
                })
                continue

            # 创建问题数据
            question_data = {
                'id': question_id_str,
                'question_bank_id': bank_id, # 使用外键ID
                'question_type_code': question_type,
                'question_number': str(row.get('题号', '')).strip(),
                'stem': str(row.get('试题（题干）', '')).strip(),
                'option_a': str(row.get('试题（选项A）', '')).strip(),
                'option_b': str(row.get('试题（选项B）', '')).strip(),
                'option_c': str(row.get('试题（选项C）', '')).strip(),
                'option_d': str(row.get('试题（选项D）', '')).strip(),
                'option_e': str(row.get('试题（选项E）', '')).strip(),
                'image_info': str(row.get('【图】及位置', '')).strip(),
                'correct_answer': str(row.get('正确答案', '')).strip(),
                'difficulty_code': difficulty_code,
                'consistency_code': consistency_code,
                'analysis': str(row.get('解析', '')).strip(),
            }

            # 必填字段验证
            if not question_data['stem']:
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": "题干不能为空"
                })
                continue
                
            if not question_data['correct_answer']:
                detailed_errors.append({
                    "row": row_num,
                    "id": question_id_str,
                    "type": "validation",
                    "message": "正确答案不能为空"
                })
                continue

            questions_to_add.append(question_data)
            print(f"实际插入ID: {question_id_str}")

        except ValueError as ve:
            detailed_errors.append({
                "row": row_num,
                "id": question_id_str,
                "type": "parsing",
                "message": f"解析ID错误: {ve}"
            })
        except Exception as e:
            detailed_errors.append({
                "row": row_num,
                "id": question_id_str,
                "type": "unknown",
                "message": f"未知错误: {e}"
            })

    # 打印错误摘要
    if detailed_errors:
        print("\n--- 导入错误摘要 ---")
        for error in detailed_errors:
            print(f"第 {error['row']} 行 (ID: {error['id']}): {error['message']}")
    
    # 批处理插入数据库
    if questions_to_add:
        try:
            db_session.bulk_insert_mappings(Question, questions_to_add)
            db_session.commit()
            print(f"成功提交 {len(questions_to_add)} 条新题目到数据库。")
        except Exception as e:
            db_session.rollback()
            print(f"数据库提交失败: {e}")
            detailed_errors.append({"type": "db_commit", "message": f"数据库提交失败: {e}"})
            # 如果提交失败，清空成功列表
            questions_to_add = []

    return questions_to_add, detailed_errors

def export_error_report(errors, filename=None):
    """导出错误报告到文本文件"""
    # 创建错误报告目录
    report_dir = "error_reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    # 生成文件名
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_report_{timestamp}.txt"
    
    filepath = os.path.join(report_dir, filename)
    
    # 写入错误报告
    with open(filepath, 'w', encoding='utf-8') as f:
        if not errors:
            f.write("导入成功，没有错误。\n")
        else:
            f.write(f"导入错误报告 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write("="*50 + "\n")
            f.write(f"总错误数: {len(errors)}\n\n")
            
            for error in errors:
                row_info = f"第 {error.get('row', 'N/A')} 行" if 'row' in error else ""
                id_info = f"(ID: {error.get('id', '')})" if 'id' in error else ""
                f.write(f"{row_info} {id_info}: {error['message']}\n")
    
    print(f"\n错误报告已导出到: {filepath}")
    return filepath

def main():
    # 用于直接运行此脚本进行测试
    
    # 1. 设置数据库连接
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///local_dev.db')
    if not DATABASE_URL:
        print("错误：DATABASE_URL 环境变量未设置。")
        exit()
        
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    print("\n--- 导入问题测试 ---")
    try:
        imported_qs, import_errors = import_questions_from_excel('dummy_questions.xlsx', db_session)
        
        # 导出错误报告
        if import_errors:
            error_file = export_error_report(import_errors)
            print(f"\n发现导入错误，详情请查看: {error_file}")

        # 打印结果
        if imported_qs:
            print(f"\n--- 导入成功 ---")
            print(f"成功导入 {len(imported_qs)} 个问题。")
    finally:
        db_session.close()

if __name__ == "__main__":
    main()
