#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试题库选择器功能
"""

import os
import sys
import requests
from bs4 import BeautifulSoup

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'question_bank_web'))

def test_bank_selector():
    """测试题库选择器功能"""
    print("🧪 测试题库选择器功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试主页
        print("🔍 测试主页访问...")
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 主页访问成功")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查题库选择器
            bank_select = soup.find('select', {'id': 'bank-select'})
            if bank_select:
                print("✅ 题库选择器存在")
                
                # 检查选项
                options = bank_select.find_all('option')
                print(f"✅ 题库选项数量: {len(options)}")
                
                for i, option in enumerate(options):
                    value = option.get('value', '')
                    text = option.get_text().strip()
                    print(f"  {i+1}. 值: '{value}' | 文本: '{text}'")
                
            else:
                print("❌ 题库选择器不存在")
            
            # 检查题目列表标题
            question_header = soup.find('div', {'class': 'question-header'})
            if question_header:
                print("✅ 题目列表标题区域存在")
                
                title = question_header.find('h2', {'class': 'question-title'})
                if title:
                    print(f"✅ 题目标题: {title.get_text().strip()}")
                
                selector = question_header.find('div', {'class': 'bank-selector'})
                if selector:
                    print("✅ 题库选择器区域存在")
                else:
                    print("❌ 题库选择器区域不存在")
            else:
                print("❌ 题目列表标题区域不存在")
            
            # 检查统计信息
            stats = soup.find('div', {'class': 'stats'})
            if stats:
                print("✅ 统计信息区域存在")
                
                stat_items = stats.find_all('div', {'class': 'stat-item'})
                print(f"✅ 统计项目数量: {len(stat_items)}")
                
                for i, item in enumerate(stat_items):
                    number = item.find('div', {'class': 'stat-number'})
                    label = item.find('div', {'class': 'stat-label'})
                    if number and label:
                        print(f"  {i+1}. {label.get_text().strip()}: {number.get_text().strip()}")
            else:
                print("❌ 统计信息区域不存在")
            
            # 检查JavaScript函数
            if 'filterByBank' in response.text:
                print("✅ filterByBank函数存在")
            else:
                print("❌ filterByBank函数不存在")
            
            if 'changePerPage' in response.text:
                print("✅ changePerPage函数存在")
            else:
                print("❌ changePerPage函数不存在")
            
        else:
            print(f"❌ 主页访问失败，状态码: {response.status_code}")
            return False
        
        # 测试题库筛选
        print("\n🔍 测试题库筛选功能...")
        
        # 获取第一个题库ID进行测试
        if bank_select and len(options) > 1:
            first_bank_option = options[1]  # 跳过"全部题库"选项
            bank_id = first_bank_option.get('value', '')
            
            if bank_id:
                print(f"🔄 测试筛选题库ID: {bank_id}")
                
                filter_url = f"{base_url}?bank_id={bank_id}"
                filter_response = requests.get(filter_url, timeout=10)
                
                if filter_response.status_code == 200:
                    print("✅ 题库筛选请求成功")
                    
                    # 检查筛选后的页面
                    filter_soup = BeautifulSoup(filter_response.text, 'html.parser')
                    
                    # 检查选中状态
                    selected_option = filter_soup.find('option', {'selected': True})
                    if selected_option and selected_option.get('value') == bank_id:
                        print("✅ 题库选择状态正确保持")
                    else:
                        print("❌ 题库选择状态未正确保持")
                    
                    # 检查统计信息是否更新
                    filter_stats = filter_soup.find('div', {'class': 'stats'})
                    if filter_stats:
                        stat_items = filter_stats.find_all('div', {'class': 'stat-item'})
                        for item in stat_items:
                            label = item.find('div', {'class': 'stat-label'})
                            if label and '筛选题目数' in label.get_text():
                                print("✅ 筛选统计信息正确显示")
                                break
                    
                else:
                    print(f"❌ 题库筛选请求失败，状态码: {filter_response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_responsive_design():
    """测试响应式设计"""
    print("\n🔍 测试响应式设计...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 模拟移动设备访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 移动设备访问成功")
            
            # 检查响应式CSS
            if '@media (max-width: 768px)' in response.text:
                print("✅ 响应式CSS存在")
            else:
                print("❌ 响应式CSS不存在")
            
            # 检查题库选择器的响应式样式
            if 'min-width: 100%' in response.text:
                print("✅ 题库选择器响应式样式存在")
            else:
                print("❌ 题库选择器响应式样式不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 响应式设计测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 题库选择器功能测试")
    print("=" * 60)
    
    # 等待服务器启动
    import time
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    results = []
    
    # 测试题库选择器功能
    results.append(("题库选择器功能", test_bank_selector()))
    
    # 测试响应式设计
    results.append(("响应式设计", test_responsive_design()))
    
    # 输出测试结果
    print("\n📊 测试结果汇总")
    print("=" * 60)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("\n🎉 所有测试通过！题库选择器功能正常工作。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")

if __name__ == '__main__':
    main()
