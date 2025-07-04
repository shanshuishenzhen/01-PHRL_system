#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试清理样例题库功能
"""

import os
import sys
import sqlite3

def test_clear_samples():
    """测试清理样例题库功能"""
    print("🧹 测试清理样例题库功能")
    print("=" * 60)
    
    # 1. 删除样例Excel文件
    sample_file = 'question_bank_web/questions_sample.xlsx'
    if os.path.exists(sample_file):
        try:
            os.remove(sample_file)
            print(f"✅ 已删除样例Excel文件: {sample_file}")
        except Exception as e:
            print(f"❌ 删除样例Excel文件失败: {e}")
    else:
        print(f"ℹ️ 样例Excel文件不存在: {sample_file}")
    
    # 2. 清理数据库中的样例题库数据
    db_path = 'question_bank_web/questions.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查看清理前的状态
            cursor.execute("SELECT COUNT(*) FROM questions")
            question_count_before = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM question_banks")
            bank_count_before = cursor.fetchone()[0]
            
            cursor.execute("SELECT id, name FROM question_banks WHERE name LIKE '%样例题库%'")
            sample_banks = cursor.fetchall()
            
            print(f"清理前状态:")
            print(f"  题目总数: {question_count_before}")
            print(f"  题库总数: {bank_count_before}")
            print(f"  样例题库数: {len(sample_banks)}")
            
            if sample_banks:
                print(f"  样例题库列表:")
                for bank_id, bank_name in sample_banks:
                    cursor.execute("SELECT COUNT(*) FROM questions WHERE question_bank_id = ?", (bank_id,))
                    question_count = cursor.fetchone()[0]
                    print(f"    - {bank_name} (ID: {bank_id}, 题目数: {question_count})")
            
            # 执行清理
            cursor.execute("DELETE FROM questions WHERE question_bank_id IN (SELECT id FROM question_banks WHERE name LIKE '%样例题库%')")
            deleted_questions = cursor.rowcount
            
            cursor.execute("DELETE FROM question_banks WHERE name LIKE '%样例题库%'")
            deleted_banks = cursor.rowcount
            
            conn.commit()
            
            # 查看清理后的状态
            cursor.execute("SELECT COUNT(*) FROM questions")
            question_count_after = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM question_banks")
            bank_count_after = cursor.fetchone()[0]
            
            print(f"\n清理结果:")
            print(f"  删除题目数: {deleted_questions}")
            print(f"  删除题库数: {deleted_banks}")
            
            print(f"\n清理后状态:")
            print(f"  题目总数: {question_count_after}")
            print(f"  题库总数: {bank_count_after}")
            
            conn.close()
            print(f"✅ 数据库清理完成")
            
        except Exception as e:
            print(f"❌ 数据库清理失败: {e}")
    else:
        print(f"ℹ️ 数据库文件不存在: {db_path}")

if __name__ == "__main__":
    test_clear_samples()
    print("\n🎯 清理测试完成！")
