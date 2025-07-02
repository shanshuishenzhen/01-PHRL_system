import sqlite3
import os

def check_db_structure():
    """检查数据库表结构和数据"""
    db_path = 'user_management/users.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表结构
        print("=== 表结构 ===")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col[1]} ({col[2]})" + (" PRIMARY KEY" if col[5] else ""))
        
        # 检查记录数
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\n=== 记录数 ===")
        print(f"用户总数: {count}")
        
        # 检查前5条记录
        print("\n=== 前5条记录 ===")
        cursor.execute("SELECT id, id_card, username, real_name FROM users LIMIT 5")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user[0]}, 身份证号: {user[1]}, 用户名: {user[2]}, 姓名: {user[3]}")
        
        # 检查身份证号
        cursor.execute("SELECT COUNT(*) FROM users WHERE id_card IS NOT NULL AND id_card != ''")
        id_card_count = cursor.fetchone()[0]
        print(f"\n=== 身份证号统计 ===")
        print(f"有身份证号的用户数: {id_card_count}")
        
        # 显示身份证号示例
        if id_card_count > 0:
            print("\n=== 身份证号示例 ===")
            cursor.execute("SELECT id_card FROM users WHERE id_card IS NOT NULL AND id_card != '' LIMIT 5")
            id_cards = cursor.fetchall()
            for i, id_card in enumerate(id_cards):
                print(f"示例{i+1}: {id_card[0]}")
        
    except sqlite3.Error as e:
        print(f"查询过程中发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_structure()