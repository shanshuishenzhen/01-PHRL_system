#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组题功能测试脚本
测试试卷生成功能
"""

import requests
import time
from bs4 import BeautifulSoup
import re

def test_paper_generation():
    """测试组题功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试组题功能...")
    print("=" * 50)
    
    # 测试1: 试卷列表页面
    print("📋 测试1: 试卷列表页面")
    try:
        response = requests.get(f"{base_url}/papers")
        if response.status_code == 200:
            print("✅ 试卷列表页面访问正常")
        else:
            print(f"❌ 试卷列表页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 试卷列表页面访问异常: {e}")
    
    # 测试2: 快速生成页面
    print("\n📋 测试2: 快速生成页面")
    try:
        response = requests.get(f"{base_url}/quick-generate")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查表单元素
            form = soup.find('form')
            if form:
                print("✅ 快速生成表单存在")
            else:
                print("❌ 快速生成表单未找到")
            
            # 检查难度选择
            difficulty_options = soup.find_all('input', {'name': 'difficulty_distribution'})
            if len(difficulty_options) >= 3:
                print("✅ 难度分布选项完整")
            else:
                print(f"⚠️  难度分布选项不完整，找到 {len(difficulty_options)} 个")
                
        else:
            print(f"❌ 快速生成页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 快速生成页面访问异常: {e}")
    
    # 测试3: 自定义组题页面
    print("\n📋 测试3: 自定义组题页面")
    try:
        response = requests.get(f"{base_url}/generate-paper")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查表单元素
            form = soup.find('form')
            if form:
                print("✅ 自定义组题表单存在")
            else:
                print("❌ 自定义组题表单未找到")
            
            # 检查规则容器
            rules_container = soup.find('div', {'class': 'rules-container'})
            if rules_container:
                print("✅ 组题规则容器存在")
            else:
                print("❌ 组题规则容器未找到")
                
        else:
            print(f"❌ 自定义组题页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 自定义组题页面访问异常: {e}")
    
    # 测试4: 快速生成试卷
    print("\n📋 测试4: 快速生成试卷")
    try:
        test_paper_name = f"测试试卷_{int(time.time())}"
        data = {
            'paper_name': test_paper_name,
            'difficulty_distribution': 'balanced'
        }
        
        response = requests.post(f"{base_url}/quick-generate", data=data)
        if response.status_code == 302:  # 重定向到试卷详情页
            print("✅ 快速生成试卷成功")
            
            # 获取重定向的URL
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print(f"✅ 重定向到: {redirect_url}")
                
                # 访问试卷详情页
                detail_response = requests.get(f"{base_url}{redirect_url}")
                if detail_response.status_code == 200:
                    print("✅ 试卷详情页访问正常")
                    
                    # 检查试卷信息
                    soup = BeautifulSoup(detail_response.text, 'html.parser')
                    paper_title = soup.find('div', {'class': 'paper-title'})
                    if paper_title and test_paper_name in paper_title.text:
                        print("✅ 试卷名称显示正确")
                    else:
                        print("⚠️  试卷名称显示可能有问题")
                        
                else:
                    print(f"❌ 试卷详情页访问失败: {detail_response.status_code}")
        else:
            print(f"❌ 快速生成试卷失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 快速生成试卷异常: {e}")
    
    # 测试5: 自定义组题
    print("\n📋 测试5: 自定义组题")
    try:
        test_paper_name = f"自定义试卷_{int(time.time())}"
        data = {
            'paper_name': test_paper_name,
            'paper_description': '这是一个测试用的自定义试卷',
            'total_score': '100',
            'duration': '120',
            'difficulty_level': '中等',
            'rule_count': '2',
            'rule_0_type': 'B',
            'rule_0_difficulty': '3',
            'rule_0_count': '5',
            'rule_0_score': '4.0',
            'rule_0_section': '单选题',
            'rule_1_type': 'C',
            'rule_1_difficulty': '3',
            'rule_1_count': '3',
            'rule_1_score': '2.0',
            'rule_1_section': '判断题'
        }
        
        response = requests.post(f"{base_url}/generate-paper", data=data)
        if response.status_code == 302:  # 重定向到试卷详情页
            print("✅ 自定义组题成功")
            
            # 获取重定向的URL
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print(f"✅ 重定向到: {redirect_url}")
                
                # 访问试卷详情页
                detail_response = requests.get(f"{base_url}{redirect_url}")
                if detail_response.status_code == 200:
                    print("✅ 自定义试卷详情页访问正常")
                    
                    # 检查试卷信息
                    soup = BeautifulSoup(detail_response.text, 'html.parser')
                    paper_title = soup.find('div', {'class': 'paper-title'})
                    if paper_title and test_paper_name in paper_title.text:
                        print("✅ 自定义试卷名称显示正确")
                    else:
                        print("⚠️  自定义试卷名称显示可能有问题")
                        
                    # 检查题目数量
                    stat_cards = soup.find_all('div', {'class': 'stat-card'})
                    if stat_cards:
                        print("✅ 试卷统计信息显示正常")
                    else:
                        print("⚠️  试卷统计信息显示可能有问题")
                        
                else:
                    print(f"❌ 自定义试卷详情页访问失败: {detail_response.status_code}")
        else:
            print(f"❌ 自定义组题失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 自定义组题异常: {e}")
    
    # 测试6: 试卷导出功能
    print("\n📋 测试6: 试卷导出功能")
    try:
        # 先获取试卷列表
        response = requests.get(f"{base_url}/papers")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找第一个试卷的导出链接
            export_links = soup.find_all('a', href=re.compile(r'/paper/.*/export'))
            if export_links:
                export_url = export_links[0]['href']
                print(f"✅ 找到导出链接: {export_url}")
                
                # 测试导出
                export_response = requests.get(f"{base_url}{export_url}")
                if export_response.status_code == 200:
                    print("✅ 试卷导出成功")
                    
                    # 检查文件内容
                    content = export_response.text
                    if '试卷名称' in content and '题目列表' in content:
                        print("✅ 导出文件内容格式正确")
                    else:
                        print("⚠️  导出文件内容格式可能有问题")
                else:
                    print(f"❌ 试卷导出失败: {export_response.status_code}")
            else:
                print("⚠️  未找到可导出的试卷")
        else:
            print(f"❌ 获取试卷列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 试卷导出功能异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 组题功能测试完成！")
    print("\n💡 功能说明:")
    print("1. 快速生成：一键生成标准试卷")
    print("2. 自定义组题：按规则精确控制试卷内容")
    print("3. 试卷管理：查看、导出、删除试卷")
    print("4. 支持多种题型和难度分布")
    print("5. 试卷统计和导出功能")

if __name__ == "__main__":
    test_paper_generation() 