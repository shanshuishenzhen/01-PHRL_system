#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试生成单一题库功能
"""

import os
import sys
import pandas as pd
sys.path.append('developer_tools')

from question_bank_generator import generate_from_excel

def test_single_bank_generation():
    """测试生成单一题库功能"""
    print("🏗️ 测试生成单一题库功能")
    print("=" * 60)
    
    # 1. 创建保卫管理员模板
    template_path = 'test_template_security.xlsx'
    output_path = 'question_bank_web/questions_sample.xlsx'
    
    # 创建保卫管理员（三级）理论题库模板
    data = {
        '题库名称': ['保卫管理员（三级）理论'] + [''] * 22,
        '1级代码': ['A'] + [''] * 7 + ['B'] + [''] * 5 + ['C'] + [''] * 4 + ['D'] + [''] * 3,
        '1级比重(%)': [20] + [''] * 7 + [10] + [''] * 5 + [45] + [''] * 4 + [25] + [''] * 3,
        '2级代码': ['A-A'] + [''] * 1 + ['A-B'] + [''] * 5 + ['B-A'] + [''] * 1 + ['B-B'] + [''] * 1 + ['B-C'] + [''] * 1 + ['C-A'] + [''] * 2 + ['C-B'] + [''] * 1 + ['D-A'] + [''] * 1 + ['D-B'] + [''] * 1,
        '2级比重(%)': [5] + [''] * 1 + [15] + [''] * 5 + [4] + [''] * 1 + [3] + [''] * 1 + [3] + [''] * 1 + [25] + [''] * 2 + [20] + [''] * 1 + [12] + [''] * 1 + [13] + [''] * 1,
        '3级代码': ['A-A-A', 'A-A-B', 'A-B-A', 'A-B-B', 'A-B-C', 'A-B-D', 'A-B-E', 'A-B-F', 'B-A-A', 'B-A-B', 'B-B-A', 'B-B-B', 'B-C-A', 'B-C-B', 'C-A-A', 'C-A-B', 'C-A-C', 'C-B-A', 'C-B-B', 'D-A-A', 'D-A-B', 'D-B-A', 'D-B-B'],
        '3级比重(%)': [2.5, 2.5, 2, 3, 2, 3, 1, 4, 2, 2, 2, 1, 1, 2, 7, 8, 10, 10, 10, 6, 6, 6, 7],
        '知识点数量': [4, 5, 8, 7, 6, 5, 7, 5, 2, 4, 5, 8, 9, 7, 5, 2, 4, 5, 8, 9, 5, 8, 9],
        'B(单选题)': [10, 20, 15, 20, 10, 20, 15, 20, 20, 15, 20, 10, 20, 15, 20, 15, 15, 20, 10, 20, 15, 20, 20],
        'G(多选题)': [10, 20, 15, 20, 10, 20, 15, 20, 20, 15, 20, 10, 20, 15, 20, 15, 15, 20, 10, 20, 15, 20, 20],
        'C(判断题)': [8, 18, 13, 18, 8, 18, 13, 18, 18, 13, 18, 8, 18, 13, 18, 13, 13, 18, 8, 18, 13, 18, 18],
        'T(填空题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
        'D(简答题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
        'U(计算题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
        'W(论述题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
        'E(案例分析题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
        'F(组合题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15]
    }
    
    try:
        # 创建模板文件
        df = pd.DataFrame(data)
        df.to_excel(template_path, index=False)
        print(f"✅ 创建模板文件: {template_path}")
        
        # 生成题库（覆盖模式）
        print(f"\n📥 生成题库...")
        total_questions, bank_name, db_success = generate_from_excel(template_path, output_path, append_mode=False)
        
        print(f"\n生成结果:")
        print(f"  题库名称: {bank_name}")
        print(f"  题目数量: {total_questions}")
        print(f"  数据库同步: {'成功' if db_success else '失败'}")
        
        # 验证生成的Excel文件
        if os.path.exists(output_path):
            df_output = pd.read_excel(output_path)
            unique_banks = df_output['题库名称'].unique() if '题库名称' in df_output.columns else []
            
            print(f"\n📊 Excel文件验证:")
            print(f"  文件路径: {output_path}")
            print(f"  总题目数: {len(df_output)}")
            print(f"  题库数量: {len(unique_banks)}")
            print(f"  题库列表: {list(unique_banks)}")
            
            # 检查是否只有一个题库
            if len(unique_banks) == 1 and unique_banks[0] == bank_name:
                print(f"  ✅ 验证通过：只包含一个题库 '{bank_name}'")
            else:
                print(f"  ❌ 验证失败：包含多个题库或题库名称不匹配")
        
        # 验证数据库状态
        if db_success:
            import sqlite3
            db_path = 'question_bank_web/questions.db'
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM questions")
                question_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM question_banks")
                bank_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT name FROM question_banks")
                bank_names = [row[0] for row in cursor.fetchall()]
                
                print(f"\n🗄️ 数据库验证:")
                print(f"  题目总数: {question_count}")
                print(f"  题库总数: {bank_count}")
                print(f"  题库列表: {bank_names}")
                
                # 检查是否只有一个题库
                if bank_count == 1 and len(bank_names) == 1 and bank_names[0] == bank_name:
                    print(f"  ✅ 验证通过：数据库只包含一个题库 '{bank_name}'")
                else:
                    print(f"  ❌ 验证失败：数据库包含多个题库或题库名称不匹配")
                
                conn.close()
        
        # 清理临时文件
        if os.path.exists(template_path):
            os.remove(template_path)
            print(f"\n🧹 已清理临时文件: {template_path}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_single_bank_generation()
    print("\n🎯 单一题库生成测试完成！")
