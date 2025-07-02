import sqlite3
import os

def migrate_id_to_id_card():
    """将数据库中的ID字段数据迁移到id_card字段"""
    db_path = 'user_management/users.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表结构，确认ID字段是否存在
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'ID' not in column_names:
            print("ID字段不存在，可能已经完成迁移")
            return
        
        # 添加id_card字段（如果不存在）
        if 'id_card' not in column_names:
            print("添加id_card字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN id_card TEXT")
            conn.commit()
            print("id_card字段添加成功")
        
        # 获取所有用户数据
        cursor.execute("SELECT id, ID FROM users")
        users = cursor.fetchall()
        
        # 更新id_card字段
        for user_id, id_card in users:
            cursor.execute("UPDATE users SET id_card = ? WHERE id = ?", (id_card, user_id))
        
        conn.commit()
        print(f"成功将{len(users)}个用户的ID字段数据迁移到id_card字段")
        
        # 创建临时表，不包含ID字段
        cursor.execute('''
            CREATE TABLE users_new (
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
                created_at TEXT NOT NULL
            )
        ''')
        
        # 将数据从原表复制到新表
        cursor.execute('''
            INSERT INTO users_new 
            SELECT id, id_card, username, password, role, status, real_name, email, phone, department, created_at 
            FROM users
        ''')
        
        # 删除原表，重命名新表
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        conn.commit()
        print("成功移除ID字段，迁移完成")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"迁移过程中发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_id_to_id_card()