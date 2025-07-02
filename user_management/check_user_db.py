import sqlite3
import os

# 连接到数据库
db_path = 'f:\\01-PHRL_system\\user_management\\users.db'

if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 检查表结构
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print("\n表结构:")
for col in columns:
    print(f"  {col['name']} ({col['type']})")

# 检查记录数
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"\n总记录数: {count}")

# 检查前5条记录
cursor.execute("SELECT * FROM users LIMIT 5")
users = cursor.fetchall()
print("\n前5条用户记录:")
for user in users:
    print(f"  ID: {user['id']}, 用户名: {user['username']}, 身份证号: {user['ID']}")

# 检查有身份证号的用户数量
cursor.execute("SELECT COUNT(*) FROM users WHERE ID IS NOT NULL AND ID != ''")
id_card_count = cursor.fetchone()[0]
print(f"\n有身份证号的用户数: {id_card_count}")

# 检查身份证号示例
cursor.execute("SELECT ID FROM users WHERE ID IS NOT NULL AND ID != '' LIMIT 3")
id_cards = cursor.fetchall()
print("\n身份证号示例:")
for id_card in id_cards:
    print(f"  {id_card['ID']}")

conn.close()