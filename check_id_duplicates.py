#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查样例Excel文件中的ID重复情况
"""

import pandas as pd
import os

def check_id_duplicates():
    """检查样例Excel文件中的ID重复情况"""
    print("🔍 检查样例Excel文件中的ID重复情况")
    print("=" * 60)
    
    excel_file = 'question_bank_web/questions_sample.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ 样例Excel文件不存在: {excel_file}")
        return
    
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file)
        print(f"✅ 成功读取Excel文件: {excel_file}")
        print(f"总行数: {len(df)}")
        
        # 检查ID重复情况
        id_counts = df['ID'].value_counts()
        duplicated_ids = id_counts[id_counts > 1]
        
        print(f"\n📊 ID重复统计:")
        print(f"  唯一ID数量: {len(id_counts)}")
        print(f"  重复ID数量: {len(duplicated_ids)}")
        print(f"  总行数: {len(df)}")
        
        if len(duplicated_ids) > 0:
            print(f"\n🔍 重复ID详情（前10个）:")
            for i, (id_val, count) in enumerate(duplicated_ids.head(10).items()):
                print(f"  {i+1}. ID: {id_val} -> 出现 {count} 次")
                
                # 显示这个ID对应的题库名称
                rows_with_id = df[df['ID'] == id_val]
                banks = rows_with_id['题库名称'].unique()
                print(f"      题库: {', '.join(banks)}")
        
        # 检查是否每个重复ID都分别属于两个不同的题库
        print(f"\n🔍 分析重复ID的题库分布:")
        sample_duplicated_ids = duplicated_ids.head(5).index
        
        for id_val in sample_duplicated_ids:
            rows_with_id = df[df['ID'] == id_val]
            banks = rows_with_id['题库名称'].unique()
            print(f"  ID {id_val}:")
            for bank in banks:
                count = len(rows_with_id[rows_with_id['题库名称'] == bank])
                print(f"    - {bank}: {count} 次")
        
        # 验证假设：每个ID在每个题库中只出现一次
        print(f"\n🧪 验证假设：每个ID在每个题库中只出现一次")
        all_valid = True
        for id_val in sample_duplicated_ids:
            rows_with_id = df[df['ID'] == id_val]
            for bank in rows_with_id['题库名称'].unique():
                count = len(rows_with_id[rows_with_id['题库名称'] == bank])
                if count != 1:
                    print(f"  ❌ ID {id_val} 在题库 '{bank}' 中出现 {count} 次")
                    all_valid = False
        
        if all_valid:
            print(f"  ✅ 验证通过：每个ID在每个题库中都只出现一次")
            print(f"  💡 结论：这是两个独立的题库，使用了相同的ID编码系统")
        
    except Exception as e:
        print(f"❌ 读取Excel文件时发生错误: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_id_duplicates()
    print("\n🎯 检查完成！")
