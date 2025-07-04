#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查样例Excel文件中的题库名称分布
"""

import pandas as pd
import os

def check_sample_banks():
    """检查样例Excel文件中的题库名称分布"""
    print("🔍 检查样例Excel文件中的题库名称分布")
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
        
        # 检查题库名称列
        if '题库名称' not in df.columns:
            print(f"❌ Excel文件中没有'题库名称'列")
            print(f"可用列: {list(df.columns)}")
            return
        
        # 统计题库名称分布
        bank_counts = df['题库名称'].value_counts()
        print(f"\n📊 题库名称分布:")
        for bank_name, count in bank_counts.items():
            print(f"  {bank_name}: {count} 个题目")
        
        print(f"\n📈 统计摘要:")
        print(f"  不同题库数量: {len(bank_counts)}")
        print(f"  总题目数量: {len(df)}")
        
        # 显示前几个题目的题库名称
        print(f"\n📋 前10个题目的题库名称:")
        for i, (idx, row) in enumerate(df.head(10).iterrows()):
            print(f"  {i+1}. ID: {row.get('ID', 'N/A')} -> 题库: {row.get('题库名称', 'N/A')}")
        
        # 检查是否有空的题库名称
        empty_banks = df[df['题库名称'].isna() | (df['题库名称'] == '')].shape[0]
        if empty_banks > 0:
            print(f"\n⚠️ 发现 {empty_banks} 个题目没有题库名称")
        
    except Exception as e:
        print(f"❌ 读取Excel文件时发生错误: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_sample_banks()
    print("\n🎯 检查完成！")
