import sqlite3
import os
import json
from datetime import datetime

def recreate_database():
    """重新创建数据库并导入用户数据"""
    db_path = 'user_management/users.db'
    json_path = 'user_management/users.json'
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_path):
        print(f"用户数据文件不存在: {json_path}")
        return
    
    # 如果数据库文件存在，先删除
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"已删除旧数据库文件: {db_path}")
        except Exception as e:
            print(f"删除旧数据库文件失败: {e}")
            return
    
    # 创建新数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                id_card TEXT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                real_name TEXT,
                email TEXT,
                phone TEXT,
                department TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        ''')
        conn.commit()
        print("创建新数据库表结构成功")
        
        # 从JSON导入用户数据
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        users = data.get('users', [])
        if not users:
            print("JSON文件中没有用户数据")
            return
        
        for user in users:
            try:
                # 准备用户数据
                user_id = user.get('id')
                id_card = user.get('ID', '')  # 从JSON中的ID字段获取身份证号
                username = user.get('username', '')
                password = user.get('password', user.get('password_hash', '123456'))
                role = user.get('role', 'student')
                status = user.get('status', 'active')
                real_name = user.get('real_name', '')
                email = user.get('email', '')
                phone = user.get('phone', '')
                department = user.get('department', '')
                created_at = user.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                updated_at = user.get('updated_at', created_at)
                
                # 插入用户数据
                cursor.execute("""
                    INSERT INTO users (id, id_card, username, password, role, status, real_name, email, phone, department, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, id_card, username, password, role, status, real_name, email, phone, department, created_at, updated_at))
                
            except sqlite3.IntegrityError:
                print(f"跳过重复用户: {username}")
            except Exception as e:
                print(f"导入用户 {username} 时出错: {e}")
        
        conn.commit()
        print(f"成功从JSON导入用户数据")
        
        # 检查导入结果
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"导入用户总数: {count}")
        
        # 检查身份证号
        cursor.execute("SELECT COUNT(*) FROM users WHERE id_card IS NOT NULL AND id_card != ''")
        id_card_count = cursor.fetchone()[0]
        print(f"有身份证号的用户数: {id_card_count}")
        
        # 显示身份证号示例
        if id_card_count > 0:
            print("\n=== 身份证号示例 ===")
            cursor.execute("SELECT id_card FROM users WHERE id_card IS NOT NULL AND id_card != '' LIMIT 5")
            id_cards = cursor.fetchall()
            for i, id_card in enumerate(id_cards):
                print(f"示例{i+1}: {id_card[0]}")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"数据库操作错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    recreate_database()