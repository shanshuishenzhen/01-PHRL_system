import json
import os
import random
import pandas as pd
import sys
import sqlite3
import uuid
from datetime import datetime

# 添加题库管理模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'question_bank_web'))

# 尝试导入题库管理模块的数据库模型
try:
    from models import QuestionBank, Question
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    DB_INTEGRATION_AVAILABLE = True
except ImportError:
    print("警告: 无法导入题库管理模块，将使用文件模式")
    DB_INTEGRATION_AVAILABLE = False

def get_question_bank_db_session():
    """获取题库管理模块的数据库会话"""
    if not DB_INTEGRATION_AVAILABLE:
        return None

    try:
        # 题库管理模块的数据库路径（使用正确的数据库文件名）
        db_path = os.path.join(os.path.dirname(__file__), '..', 'question_bank_web', 'questions.db')
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"连接题库数据库失败: {e}")
        return None

def save_to_question_bank_db(bank_name, questions):
    """将题目保存到题库管理模块的数据库"""
    if not DB_INTEGRATION_AVAILABLE:
        return False, "数据库集成不可用"

    session = get_question_bank_db_session()
    if not session:
        return False, "无法连接到题库数据库"

    try:
        # 查找或创建题库
        question_bank = session.query(QuestionBank).filter_by(name=bank_name).first()
        if not question_bank:
            question_bank = QuestionBank(name=bank_name)
            session.add(question_bank)
            session.flush()  # 获取ID
        else:
            # 删除现有题目（如果是替换模式）
            session.query(Question).filter_by(question_bank_id=question_bank.id).delete()

        # 添加新题目
        for q in questions:
            # 处理选项数据结构
            options = q.get('options', [])
            option_a = option_b = option_c = option_d = ''

            if isinstance(options, list):
                # 选项是列表格式 [{"key": "A", "text": "..."}, ...]
                for opt in options:
                    if opt.get('key') == 'A':
                        option_a = opt.get('text', '')
                    elif opt.get('key') == 'B':
                        option_b = opt.get('text', '')
                    elif opt.get('key') == 'C':
                        option_c = opt.get('text', '')
                    elif opt.get('key') == 'D':
                        option_d = opt.get('text', '')
            elif isinstance(options, dict):
                # 选项是字典格式 {"A": "...", "B": "..."}
                option_a = options.get('A', '')
                option_b = options.get('B', '')
                option_c = options.get('C', '')
                option_d = options.get('D', '')

            # 生成唯一的题目ID，格式为：原ID#题库UUID
            unique_question_id = f"{q['id']}#{question_bank.id}"

            question = Question(
                id=unique_question_id,
                question_type_code=q['type'],
                stem=q['stem'],
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=q['answer'],
                difficulty_code='3',  # 默认中等难度
                question_bank_id=question_bank.id,
                created_at=datetime.utcnow()
            )
            session.add(question)

        session.commit()
        return True, f"成功保存到题库: {bank_name}"

    except Exception as e:
        session.rollback()
        return False, f"保存到数据库失败: {e}"
    finally:
        session.close()

def generate_question(q_type, k_code_l3, parallel_seq, question_seq, question_type_name):
    """生成单个虚拟题目的JSON对象。"""
    # 定义question_id
    question_id = f"{q_type}-{k_code_l3}-{parallel_seq:03d}-{question_seq:03d}"
    
    question_stem = f"这是一道关于知识点 {k_code_l3} 的{question_type_name}。ID: {question_id}"
    options = []
    if q_type in ['B', 'G']: # 单选/多选
        options = [
            {"key": "A", "text": f"选项A for {question_id}"},
            {"key": "B", "text": f"选项B for {question_id}"},
            {"key": "C", "text": f"选项C for {question_id}"},
            {"key": "D", "text": f"选项D for {question_id}"}
        ]
    
    answer_map = {'G': "A,B", 'C': "正确"}
    answer = answer_map.get(q_type, "A")

    return {
        "id": question_id,
        "type": q_type,
        "type_name": question_type_name,
        "knowledge_point_l1": k_code_l3.split('-')[0],
        "knowledge_point_l2": "-".join(k_code_l3.split('-')[:2]),
        "knowledge_point_l3": k_code_l3,
        "knowledge_point_parallel": f"{k_code_l3}-{parallel_seq:03d}",
        "stem": question_stem,
        "options": options,
        "answer": answer,
        "explanation": f"这是对题目 {question_id} 的详细解析。",
        "difficulty": round(random.uniform(0.2, 0.8), 2),
        "score": 1 if q_type in ['B', 'C'] else 2
    }

def generate_from_excel(excel_path, output_path, append_mode=False):
    """
    从指定的Excel模板文件生成题库，并保存为Excel格式。

    Args:
        excel_path: Excel模板文件路径
        output_path: 输出文件路径
        append_mode: 是否为追加模式，True表示追加到现有题库，False表示覆盖
    """
    # 读取Excel文件
    try:
        # 使用openpyxl引擎并指定编码处理
        df = pd.read_excel(excel_path, engine='openpyxl')
    except Exception as e:
        raise Exception(f"读取Excel文件失败: {e}")

    # 数据预处理：向前填充合并的单元格
    # 注意：pandas读取时，合并单元格只有左上角有值，其他为空。向前填充可以补全这些值。
    if '1级代码' in df.columns:
        df['1级代码'] = df['1级代码'].ffill()
    if '2级代码' in df.columns:
        df['2级代码'] = df['2级代码'].ffill()

    # 识别所有题型列，例如 'B(单选题)'
    question_type_cols = {}
    for col in df.columns:
        # 只识别符合题型格式的列名：单个字母后跟括号内容
        if '(' in col and ')' in col and len(col.split('(')[0].strip()) == 1:
            question_type_cols[col] = col.split('(')[1].replace(')', '')

        # 将所有题目数量相关的列中的空值(NaN)替换为0，防止int()转换错误
        numeric_cols = ['知识点数量'] + list(question_type_cols.keys())
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)

    all_questions = []
    
    # 逐行处理三级知识点
    for index, row in df.iterrows():
        # 跳过没有三级代码的行，这些通常是由于合并单元格产生的空行
        k_code_l3_val = df.loc[index, '3级代码']
        if pd.isna(k_code_l3_val):
            continue
        k_code_l3 = str(k_code_l3_val)

        num_parallel_points = int(df.loc[index, '知识点数量'])

        # 为每种题型生成题目
        for col_name, type_name in question_type_cols.items():
            q_type = col_name.split('(')[0]
            max_questions_per_point = int(df.loc[index, col_name])
            
            # 根据新规则生成
            for i in range(num_parallel_points):
                parallel_seq = i + 1
                for j in range(max_questions_per_point):
                    question_seq = j + 1
                    question = generate_question(q_type, k_code_l3, parallel_seq, question_seq, type_name)
                    all_questions.append(question)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:  # 只有当目录不为空时才创建
        os.makedirs(output_dir, exist_ok=True)
    
    # 从Excel模板中提取题库名称
    bank_name = "样例题库"  # 默认名称
    if '题库名称' in df.columns:
        # 获取第一个非空的题库名称
        for idx, row in df.iterrows():
            if pd.notna(row.get('题库名称', '')) and str(row.get('题库名称', '')).strip():
                original_name = str(row.get('题库名称', '')).strip()
                # 如果原名称不包含"样例题库"，则添加后缀
                if "样例题库" not in original_name:
                    bank_name = f"{original_name}样例题库"
                else:
                    bank_name = original_name
                break

    print(f"将生成题库: {bank_name}")

    # 将生成的题目转换为Excel格式
    # 准备数据框架
    data = []
    
    for q in all_questions:
        # 处理选项，将选项对象转换为字符串
        options = q.get("options", [])
        option_a = next((opt['text'] for opt in options if opt['key'] == 'A'), "")
        option_b = next((opt['text'] for opt in options if opt['key'] == 'B'), "")
        option_c = next((opt['text'] for opt in options if opt['key'] == 'C'), "")
        option_d = next((opt['text'] for opt in options if opt['key'] == 'D'), "")
        option_e = ""
        
        # 创建行数据
        # 在生成行数据时，检查并修改题型名称
        row = {
            '题库名称': bank_name,
            'ID': q.get("id", ""),
            '序号': "",  # 添加序号字段
            '认定点代码': "-".join(q.get("id", "").split("-")[1:4]) + "-" + q.get("id", "").split("-")[4],  # 从ID中提取认定点代码
            '题型代码': f"{q.get('type', '')}（{q.get('type_name', '').replace('组合题', '综合题')}）",  # 修改为正确的格式
            '题号': "",
            '试题（题干）': q.get("stem", ""),
            '试题（选项A）': option_a,
            '试题（选项B）': option_b,
            '试题（选项C）': option_c,
            '试题（选项D）': option_d,
            '试题（选项E）': option_e,
            '【图】及位置': "",
            '正确答案': q.get("answer", ""),
            '难度代码': f"{'1（很简单）' if float(q.get('difficulty', 0.5)) < 0.2 else '2（简单）' if float(q.get('difficulty', 0.5)) < 0.4 else '3（中等）' if float(q.get('difficulty', 0.5)) < 0.6 else '4（困难）' if float(q.get('difficulty', 0.5)) < 0.8 else '5（很难）'}",
            '一致性代码': "3（中等）",  # 添加一致性代码字段
            '解析': q.get("explanation", "")
        }
        data.append(row)
    
    # 处理增量模式
    if append_mode and os.path.exists(output_path):
        try:
            # 读取现有的Excel文件
            existing_df = pd.read_excel(output_path)

            # 检查是否已存在相同题库名称的题目
            existing_bank_names = existing_df['题库名称'].unique() if '题库名称' in existing_df.columns else []

            if bank_name in existing_bank_names:
                # 如果题库名称已存在，过滤掉重复的题库
                existing_df = existing_df[existing_df['题库名称'] != bank_name]
                print(f"检测到重复题库名称 '{bank_name}'，将替换现有题库")

            # 合并新旧数据
            new_df = pd.DataFrame(data)
            df_output = pd.concat([existing_df, new_df], ignore_index=True)

            print(f"追加模式: 保留了 {len(existing_df)} 个现有题目，新增 {len(new_df)} 个题目")

        except Exception as e:
            print(f"读取现有文件失败，将创建新文件: {e}")
            df_output = pd.DataFrame(data)
    else:
        # 覆盖模式或文件不存在
        print(f"覆盖模式: 将创建包含 {len(data)} 个题目的新文件")
        df_output = pd.DataFrame(data)

    # 导出为Excel，使用openpyxl引擎并处理编码
    try:
        df_output.to_excel(output_path, index=False, engine='openpyxl')
    except UnicodeEncodeError as e:
        # 如果遇到编码错误，尝试清理数据中的特殊字符
        print("警告: 检测到编码问题，正在清理数据")
        for col in df_output.columns:
            if df_output[col].dtype == 'object':  # 字符串列
                df_output[col] = df_output[col].astype(str).apply(
                    lambda x: x.encode('utf-8', errors='ignore').decode('utf-8') if isinstance(x, str) else x
                )
        df_output.to_excel(output_path, index=False, engine='openpyxl')

    # 保存到题库管理模块的数据库
    db_success = False
    db_message = ""
    if DB_INTEGRATION_AVAILABLE:
        db_success, db_message = save_to_question_bank_db(bank_name, all_questions)
        if db_success:
            print(f"[成功] {db_message}")
        else:
            print(f"[警告] {db_message}")

    # 同时保存一份JSON格式作为备份
    json_path = output_path.replace('.xlsx', '.json')
    backup_data = {
        "bank_name": bank_name,
        "questions": all_questions,
        "generation_time": pd.Timestamp.now().isoformat(),
        "append_mode": append_mode,
        "db_saved": db_success,
        "db_message": db_message
    }
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
    except UnicodeEncodeError as e:
        print("警告: JSON保存编码问题，使用ASCII模式")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=True, indent=2)

    # 返回生成的题目总数、题库名称和数据库保存状态
    total_questions = len(all_questions)
    return total_questions, bank_name, db_success

def run_validation(blueprint_path, generated_path):
    """运行题库生成验证"""
    try:
        from question_bank_validator import QuestionBankValidator

        validator = QuestionBankValidator()
        validation_result = validator.validate_generated_bank(
            blueprint_path, generated_path, "validation_reports"
        )

        print(f"\n{'='*50}")
        print("题库生成自动验证结果")
        print(f"{'='*50}")
        print(f"验证状态: {'✓ 通过' if validation_result['is_valid'] else '✗ 失败'}")
        print(f"准确率: {validation_result['accuracy_rate']:.2%}")
        print(f"期望题目数: {validation_result['total_questions_expected']}")
        print(f"实际题目数: {validation_result['total_questions_generated']}")
        print(f"验证报告: {validation_result['report_path']}")

        if validation_result['errors']:
            print(f"\n发现 {len(validation_result['errors'])} 个错误:")
            for i, error in enumerate(validation_result['errors'][:5], 1):
                print(f"  {i}. {error}")
            if len(validation_result['errors']) > 5:
                print(f"  ... 还有 {len(validation_result['errors']) - 5} 个错误，详见报告")

        return validation_result['is_valid']

    except ImportError:
        print("\n警告: 验证模块不可用，跳过自动验证")
        return None
    except Exception as e:
        print(f"\n验证过程出错: {e}")
        return False

if __name__ == '__main__':
    # 用于直接测试脚本
    excel_file = os.path.join(os.path.dirname(__file__), '样例题组题规则模板.xlsx')
    output_file = os.path.join(os.path.dirname(__file__), '..', 'question_bank_web', 'questions_sample.xlsx')
    blueprint_file = os.path.join(os.path.dirname(__file__), 'question_bank_blueprint.json')

    if os.path.exists(excel_file):
        try:
            result = generate_from_excel(excel_file, output_file)
            if len(result) == 3:
                total_generated, bank_name, db_success = result
                print(f"测试生成成功！共 {total_generated} 道题目。")
                print(f"文件已保存至: {output_file}")
                print(f"数据库保存: {'成功' if db_success else '失败'}")

                # 自动运行验证
                if os.path.exists(blueprint_file):
                    json_output = output_file.replace('.xlsx', '.json')
                    if os.path.exists(json_output):
                        validation_passed = run_validation(blueprint_file, json_output)
                        if validation_passed is True:
                            print("\n🎉 题库生成和验证全部通过！")
                        elif validation_passed is False:
                            print("\n⚠️ 题库生成完成，但验证发现问题，请查看验证报告")
                    else:
                        print(f"\n警告: JSON备份文件不存在，跳过验证: {json_output}")
                else:
                    print(f"\n警告: 蓝图文件不存在，跳过验证: {blueprint_file}")

            else:
                # 兼容旧版本返回值
                total_generated, bank_name = result
                print(f"测试生成成功！共 {total_generated} 道题目。")
                print(f"文件已保存至: {output_file}")
        except Exception as e:
            print(f"测试生成失败: {e}")
    else:
        print("错误: 模板文件不存在")
