import json
import os
import random
import pandas as pd

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

def generate_from_excel(excel_path, output_path):
    """
    从指定的Excel模板文件生成题库，并保存为Excel格式。
    """
    def handle_excel_upload(self, file_path='case_001.xlsx'):
        """处理新规则模板的上传"""
        df = pd.read_excel(os.path.join('developer_tools', 'case_001.xlsx'))

    # 数据预处理：向前填充合并的单元格
    # 注意：pandas读取时，合并单元格只有左上角有值，其他为空。向前填充可以补全这些值。
    df['1级代码'] = df['1级代码'].ffill()
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
    os.makedirs(output_dir, exist_ok=True)
    
    # 将生成的题目转换为Excel格式
    # 准备数据框架
    data = []
    bank_name = "样例题库"
    
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
            '题型代码': f"{q.get('type', '')}（{q.get('type_name', '').replace('组合题', '综合题') if q.get('type', '') == 'F' else q.get('type_name', '')}）",  # 修改为正确的格式
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
    
    # 创建DataFrame并导出为Excel
    df_output = pd.DataFrame(data)
    df_output.to_excel(output_path, index=False)
    
    # 同时保存一份JSON格式作为备份
    json_path = output_path.replace('.xlsx', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({"questions": all_questions}, f, ensure_ascii=False, indent=2)
    
    # 返回生成的题目总数
    total_questions = len(all_questions)

    return total_questions

if __name__ == '__main__':
    # 用于直接测试脚本
    excel_file = os.path.join(os.path.dirname(__file__), '样例题组题规则模板.xlsx')
    output_file = os.path.join(os.path.dirname(__file__), '..', 'question_bank_web', 'questions_sample.xlsx')
    
    if os.path.exists(excel_file):
        try:
            total_generated = generate_from_excel(excel_file, output_file)
            print(f"测试生成成功！共 {total_generated} 道题目。")
            print(f"文件已保存至: {output_file}")
        except Exception as e:
            print(f"测试生成失败: {e}")
    else:
        print(f"错误: 模板文件不存在于 {excel_file}")
