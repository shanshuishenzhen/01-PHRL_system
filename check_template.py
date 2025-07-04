#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查模板内容
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'question_bank_web'))

def check_template():
    """检查模板内容"""
    print("🔍 检查模板内容")
    print("=" * 50)
    
    try:
        from app import index_template
        
        # 检查关键元素
        checks = [
            ("题库选择器", "bank-select" in index_template),
            ("题目标题区域", "question-header" in index_template),
            ("题库选择器样式", "bank-selector" in index_template),
            ("筛选函数", "filterByBank" in index_template),
            ("题库数量显示", "banks_with_count" in index_template),
            ("筛选统计", "filtered_total" in index_template),
        ]
        
        for name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {name}: {'存在' if result else '不存在'}")
        
        # 输出模板的关键部分
        print("\n📄 模板关键部分:")
        
        if "bank-select" in index_template:
            start = index_template.find('<select id="bank-select"')
            if start != -1:
                end = index_template.find('</select>', start) + 9
                print("题库选择器HTML:")
                print(index_template[start:end])
        
        if "question-header" in index_template:
            start = index_template.find('<div class="question-header"')
            if start != -1:
                end = index_template.find('</div>', start) + 6
                print("\n题目标题区域HTML:")
                print(index_template[start:end])
        
        return True
        
    except Exception as e:
        print(f"❌ 检查模板失败: {e}")
        return False

def main():
    """主函数"""
    check_template()

if __name__ == '__main__':
    main()
