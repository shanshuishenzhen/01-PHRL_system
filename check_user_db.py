# -*- coding: utf-8 -*-
import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join('user_management', 'users.db')

def check_database():
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取表结构
    print("=== 数据库表结构 ===")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    table_schema = cursor.fetchone()
    if table_schema:
        print(table_schema[0])
    else:
        print("users表不存在")
    
    # 获取记录数
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"\n=== 用户记录数: {count} ===")
    
    # 获取前5条记录
    print("\n=== 前5条用户记录 ===")
    cursor.execute("SELECT id, ID, username, real_name, department FROM users LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, 身份证号: {row[1]}, 用户名: {row[2]}, 姓名: {row[3]}, 部门: {row[4]}")
    
    # 检查ID字段是否有数据
    cursor.execute("SELECT COUNT(*) FROM users WHERE ID IS NOT NULL AND ID != ''")
    id_count = cursor.fetchone()[0]
    print(f"\n=== 有身份证号的用户数: {id_count} ===")
    
    # 如果有身份证号，显示几个例子
    if id_count > 0:
        print("\n=== 身份证号示例 ===")
        cursor.execute("SELECT ID FROM users WHERE ID IS NOT NULL AND ID != '' LIMIT 5")
        id_samples = cursor.fetchall()
        for idx, sample in enumerate(id_samples):
            print(f"示例{idx+1}: {sample[0]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()