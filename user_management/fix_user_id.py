import sqlite3
import random
import os

def generate_id_card():
    """生成18位随机身份证号"""
    return ''.join([str(random.randint(0, 9)) for _ in range(18)])

def fix_user_id_cards():
    """修复用户身份证号"""
    db_path = 'f:\\01-PHRL_system\\user_management\\users.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有用户
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    update_count = 0
    for user in users:
        # 生成新的18位身份证号
        new_id_card = generate_id_card()
        
        # 更新用户的身份证号
        cursor.execute("UPDATE users SET ID = ? WHERE id = ?", (new_id_card, user['id']))
        update_count += 1
    
    conn.commit()
    
    # 验证更新结果
    cursor.execute("SELECT COUNT(*) FROM users WHERE length(ID) = 18")
    id_card_count = cursor.fetchone()[0]
    
    # 获取几个示例
    cursor.execute("SELECT ID FROM users WHERE length(ID) = 18 LIMIT 3")
    id_cards = cursor.fetchall()
    id_card_examples = [card['ID'] for card in id_cards]
    
    conn.close()
    
    print(f"已更新 {update_count} 个用户的身份证号")
    print(f"有 {id_card_count} 个用户有18位身份证号")
    print(f"身份证号示例: {', '.join(id_card_examples)}")
    
    return update_count > 0

if __name__ == "__main__":
    if fix_user_id_cards():
        print("身份证号修复完成，请重新启动用户管理系统查看效果。")
    else:
        print("身份证号修复失败。")