import sqlite3
import pandas as pd

# 连接数据库
conn = sqlite3.connect('d:\\01-PHRL_system\\question_bank_web\\local_dev.db')
cursor = conn.cursor()

# 查询题库列表
cursor.execute('SELECT id, name FROM question_banks')
banks = cursor.fetchall()
print('题库列表:')
for bank_id, bank_name in banks:
    print(f"ID: {bank_id}, 名称: {bank_name}")

# 查询保卫管理员（三级）理论题库的ID
cursor.execute("SELECT id FROM question_banks WHERE name = '保卫管理员（三级）理论'")
bank_id = cursor.fetchone()
if bank_id:
    bank_id = bank_id[0]
    print(f"\n保卫管理员（三级）理论题库ID: {bank_id}")
    
    # 查询该题库中的题目数量
    cursor.execute(f"SELECT COUNT(*) FROM questions WHERE question_bank_id = '{bank_id}'")
    total_count = cursor.fetchone()[0]
    print(f"题库中总题目数量: {total_count}")
    
    # 查询各题型的题目数量
    cursor.execute(f"SELECT question_type_code, COUNT(*) FROM questions WHERE question_bank_id = '{bank_id}' GROUP BY question_type_code")
    type_counts = cursor.fetchall()
    print("各题型数量:")
    for qtype, count in type_counts:
        print(f"题型 {qtype}: {count} 道题")
    
    # 查询B类型题目的详细信息
    cursor.execute(f"SELECT id, stem, question_type_code FROM questions WHERE question_bank_id = '{bank_id}' AND question_type_code = 'B' LIMIT 5")
    b_questions = cursor.fetchall()
    print("\nB类型题目示例:")
    for q_id, stem, qtype in b_questions:
        print(f"ID: {q_id}, 题型: {qtype}, 题干: {stem[:50]}...")
else:
    print("未找到'保卫管理员（三级）理论'题库")

# 检查xlsx文件中的题型配置
try:
    print("\n检查xlsx文件中的题型配置:")
    df = pd.read_excel('d:\\01-PHRL_system\\question_bank_web\\uploads\\xlsx', sheet_name='题型分布')
    print(df)
except Exception as e:
    print(f"读取xlsx文件失败: {e}")

conn.close()