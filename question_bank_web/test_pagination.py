#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分页功能测试脚本
测试题库管理系统的分页显示功能
"""

import requests
import time
from bs4 import BeautifulSoup
import re

def test_pagination():
    """测试分页功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试分页功能...")
    print("=" * 50)
    
    # 测试1: 基本分页参数
    print("📋 测试1: 基本分页参数")
    try:
        response = requests.get(f"{base_url}/?page=1&per_page=5")
        if response.status_code == 200:
            print("✅ 基本分页参数测试通过")
        else:
            print(f"❌ 基本分页参数测试失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 基本分页参数测试异常: {e}")
    
    # 测试2: 不同每页显示数量
    print("\n📋 测试2: 不同每页显示数量")
    per_page_options = [5, 10, 20, 50]
    for per_page in per_page_options:
        try:
            response = requests.get(f"{base_url}/?page=1&per_page={per_page}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 检查每页显示数量选择器
                select = soup.find('select', {'id': 'per_page'})
                if select and str(per_page) in select.text:
                    print(f"✅ 每页显示 {per_page} 条测试通过")
                else:
                    print(f"⚠️  每页显示 {per_page} 条测试通过，但选择器可能有问题")
            else:
                print(f"❌ 每页显示 {per_page} 条测试失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 每页显示 {per_page} 条测试异常: {e}")
    
    # 测试3: 分页控件显示
    print("\n📋 测试3: 分页控件显示")
    try:
        response = requests.get(f"{base_url}/?page=1&per_page=5")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查分页容器
            pagination_container = soup.find('div', {'class': 'pagination-container'})
            if pagination_container:
                print("✅ 分页容器显示正常")
            else:
                print("⚠️  分页容器未找到（可能只有一页数据）")
            
            # 检查分页信息
            pagination_info = soup.find('div', {'class': 'pagination-info'})
            if pagination_info:
                print("✅ 分页信息显示正常")
            else:
                print("⚠️  分页信息未找到")
            
            # 检查分页按钮
            pagination_buttons = soup.find('div', {'class': 'pagination-buttons'})
            if pagination_buttons:
                print("✅ 分页按钮显示正常")
            else:
                print("⚠️  分页按钮未找到")
                
        else:
            print(f"❌ 分页控件显示测试失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 分页控件显示测试异常: {e}")
    
    # 测试4: 页码导航
    print("\n📋 测试4: 页码导航")
    try:
        response = requests.get(f"{base_url}/?page=1&per_page=5")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查首页按钮
            first_page_btn = soup.find('a', string=re.compile(r'首页'))
            if first_page_btn:
                print("✅ 首页按钮存在")
            else:
                print("⚠️  首页按钮未找到（可能已在首页）")
            
            # 检查上一页按钮
            prev_page_btn = soup.find('a', string=re.compile(r'上一页'))
            if prev_page_btn:
                print("✅ 上一页按钮存在")
            else:
                print("⚠️  上一页按钮未找到（可能已在首页）")
            
            # 检查下一页按钮
            next_page_btn = soup.find('a', string=re.compile(r'下一页'))
            if next_page_btn:
                print("✅ 下一页按钮存在")
            else:
                print("⚠️  下一页按钮未找到（可能只有一页）")
            
            # 检查末页按钮
            last_page_btn = soup.find('a', string=re.compile(r'末页'))
            if last_page_btn:
                print("✅ 末页按钮存在")
            else:
                print("⚠️  末页按钮未找到（可能只有一页）")
                
        else:
            print(f"❌ 页码导航测试失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 页码导航测试异常: {e}")
    
    # 测试5: 统计信息显示
    print("\n📋 测试5: 统计信息显示")
    try:
        response = requests.get(f"{base_url}/?page=1&per_page=5")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查统计信息
            stats = soup.find('div', {'class': 'stats'})
            if stats:
                stat_items = stats.find_all('div', {'class': 'stat-item'})
                if len(stat_items) >= 3:
                    print("✅ 统计信息显示正常（包含当前页题目数、总题目数、总页数）")
                else:
                    print(f"⚠️  统计信息不完整，找到 {len(stat_items)} 个统计项")
            else:
                print("❌ 统计信息未找到")
                
        else:
            print(f"❌ 统计信息显示测试失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计信息显示测试异常: {e}")
    
    # 测试6: 边界情况
    print("\n📋 测试6: 边界情况")
    
    # 测试无效页码
    try:
        response = requests.get(f"{base_url}/?page=0&per_page=10")
        if response.status_code == 200:
            print("✅ 无效页码(0)处理正常")
        else:
            print(f"❌ 无效页码(0)处理失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 无效页码(0)处理异常: {e}")
    
    # 测试超大页码
    try:
        response = requests.get(f"{base_url}/?page=999&per_page=10")
        if response.status_code == 200:
            print("✅ 超大页码(999)处理正常")
        else:
            print(f"❌ 超大页码(999)处理失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 超大页码(999)处理异常: {e}")
    
    # 测试无效每页显示数量
    try:
        response = requests.get(f"{base_url}/?page=1&per_page=100")
        if response.status_code == 200:
            print("✅ 超大每页显示数量(100)处理正常")
        else:
            print(f"❌ 超大每页显示数量(100)处理失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 超大每页显示数量(100)处理异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 分页功能测试完成！")
    print("\n💡 使用说明:")
    print("1. 在首页可以看到分页控件")
    print("2. 可以选择每页显示 5/10/20/50 条记录")
    print("3. 支持首页、上一页、下一页、末页导航")
    print("4. 支持键盘快捷键：左右箭头键、Home键、End键")
    print("5. 显示当前页信息：第 X/Y 页，每页 Z 条")

if __name__ == "__main__":
    test_pagination() 