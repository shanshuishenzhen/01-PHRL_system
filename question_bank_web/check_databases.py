#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database(db_file):
    """检查数据库文件"""
    if not os.path.exists(db_file):
        print(f"{db_file} 不存在")
        return False
    
    print(f"=== 检查 {db_file} ===")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"表: {[t[0] for t in tables]}")
        
        if ('questions',) in tables:
            # 查看题目总数
            cursor.execute('SELECT COUNT(*) FROM questions')
            count = cursor.fetchone()[0]
            print(f"题目数量: {count}")
            
            if count > 0:
                # 查看题型统计
                cursor.execute('SELECT question_type_code, COUNT(*) FROM questions GROUP BY question_type_code ORDER BY question_type_code')
                types = cursor.fetchall()
                print("题型统计:")
                for t in types:
                    print(f"  {t[0]}: {t[1]}")
                
                # 检查B型题
                cursor.execute("SELECT COUNT(*) FROM questions WHERE question_type_code = 'B'")
                b_count = cursor.fetchone()[0]
                print(f"B型题数量: {b_count}")
                
                return b_count > 0
        
        conn.close()
        return False
        
    except Exception as e:
        print(f"检查 {db_file} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("数据库检查工具")
    print("=" * 50)
    
    db_files = ['question_bank.db', 'questions.db', 'local_dev.db']
    
    valid_db = None
    for db_file in db_files:
        if check_database(db_file):
            valid_db = db_file
            break
        print()
    
    if valid_db:
        print(f"✅ 找到有效数据库: {valid_db}")
        
        # 检查app.py中使用的数据库配置
        print("\n检查app.py中的数据库配置...")
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'sqlite:///question_bank.db' in content:
                    print("app.py使用: sqlite:///question_bank.db")
                elif 'sqlite:///questions.db' in content:
                    print("app.py使用: sqlite:///questions.db")
                elif 'sqlite:///local_dev.db' in content:
                    print("app.py使用: sqlite:///local_dev.db")
                else:
                    print("未找到明确的数据库配置")
        except Exception as e:
            print(f"检查app.py失败: {e}")
    else:
        print("❌ 没有找到有效的数据库文件")
        print("建议：")
        print("1. 重新导入题库数据")
        print("2. 检查数据库初始化脚本")
        print("3. 确认数据库文件路径")

if __name__ == "__main__":
    main()
