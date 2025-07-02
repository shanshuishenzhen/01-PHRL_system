# -*- coding: utf-8 -*-
import sqlite3
import os
import random

# 数据库文件路径
DB_PATH = os.path.join('user_management', 'users.db')

def generate_id_card():
    """生成18位随机身份证号"""
    return ''.join([str(random.randint(0, 9)) for _ in range(18)])

def fix_user_id_cards():
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有用户
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    
    updated_count = 0
    for user in users:
        user_id = user[0]
        id_card = generate_id_card()
        
        try:
            cursor.execute("UPDATE users SET ID = ? WHERE id = ?", (id_card, user_id))
            updated_count += 1
        except sqlite3.Error as e:
            print(f"更新用户 {user_id} 时出错: {e}")
    
    conn.commit()
    print(f"成功更新 {updated_count} 个用户的身份证号")
    
    # 验证更新
    cursor.execute("SELECT COUNT(*) FROM users WHERE length(ID) = 18")
    count = cursor.fetchone()[0]
    print(f"现在有 {count} 个用户的身份证号是18位")
    
    # 显示几个例子
    cursor.execute("SELECT id, ID, username FROM users WHERE length(ID) = 18 LIMIT 5")
    samples = cursor.fetchall()
    print("\n=== 更新后的身份证号示例 ===")
    for sample in samples:
        print(f"用户ID: {sample[0]}, 用户名: {sample[2]}, 身份证号: {sample[1]}")
    
    conn.close()

if __name__ == "__main__":
    fix_user_id_cards()