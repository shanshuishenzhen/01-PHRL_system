import sqlite3

conn = sqlite3.connect('d:\\01-PHRL_system\\question_bank_web\\local_dev.db')
cursor = conn.cursor()

# 查询题库列表
cursor.execute('SELECT name FROM question_banks')
banks = cursor.fetchall()
print('题库列表:')
for bank in banks:
    print(bank[0])

# 查询保卫管理员（三级）理论题库中的各题型题目数量
bank_name = '保卫管理员（三级）理论'
print(f'\n{bank_name}题库中各题型题目数量:')
for qtype in ['B', 'G', 'C', 'T', 'D', 'U', 'W', 'E', 'F']:
    cursor.execute(f"SELECT COUNT(*) FROM questions q JOIN question_banks b ON q.question_bank_id = b.id WHERE b.name = '{bank_name}' AND q.question_type_code = '{qtype}'")
    count = cursor.fetchone()[0]
    print(f'题型 {qtype}: {count} 道题')

conn.close()