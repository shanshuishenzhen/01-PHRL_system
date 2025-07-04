#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, get_question_type_info
import re

def debug_question_types():
    with app.test_client() as client:
        response = client.get('/')
        content = response.data.decode('utf-8')
        
        print('=== 调试题型显示 ===')
        print(f'页面状态: {response.status_code}')
        print(f'页面长度: {len(content)}')
        
        # 查找题型相关的HTML
        print('\n=== 查找题型标签 ===')
        type_badges = re.findall(r'<div class="question-type-badge[^"]*"[^>]*>([^<]*)</div>', content)
        print(f'找到 {len(type_badges)} 个题型标签:')
        for i, badge in enumerate(type_badges[:10]):  # 只显示前10个
            print(f'  {i+1}: "{badge.strip()}"')
        
        # 查找题型相关的class
        print('\n=== 查找题型样式类 ===')
        type_classes = re.findall(r'question-type-badge ([^"]*)"', content)
        print(f'找到 {len(type_classes)} 个题型样式:')
        for i, cls in enumerate(set(type_classes[:10])):  # 去重并显示前10个
            print(f'  {i+1}: "{cls}"')
        
        # 检查函数调用
        print('\n=== 检查模板函数调用 ===')
        func_calls = re.findall(r'get_question_type_info\([^)]*\)', content)
        print(f'找到 {len(func_calls)} 个函数调用:')
        for i, call in enumerate(func_calls[:5]):  # 只显示前5个
            print(f'  {i+1}: {call}')

        # 更精确地查找题型标签
        print('\n=== 精确查找题型标签 ===')
        # 查找卡片视图中的题型
        card_types = re.findall(r'<div class="question-type-badge[^"]*"[^>]*>\s*([^<\s]+)\s*</div>', content, re.MULTILINE)
        print(f'卡片视图题型 ({len(card_types)}个):')
        for i, t in enumerate(set(card_types)):
            print(f'  {i+1}: "{t}"')

        # 查找表格视图中的题型
        table_types = re.findall(r'<span class="type-badge-small[^"]*"[^>]*>\s*([^<\s]+)\s*</span>', content, re.MULTILINE)
        print(f'表格视图题型 ({len(table_types)}个):')
        for i, t in enumerate(set(table_types)):
            print(f'  {i+1}: "{t}"')
        
        # 查找具体的题型文本
        print('\n=== 查找题型文本 ===')
        type_texts = ['单选题', '多选题', '判断题', '简答题', '案例分析题']
        for text in type_texts:
            count = content.count(text)
            print(f'  "{text}": {count} 次')

if __name__ == '__main__':
    debug_question_types()
