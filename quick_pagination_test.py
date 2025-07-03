#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速分页功能测试脚本

简单测试修复后的分页API端点
"""

import requests
import json

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:5000"
    
    print("🔍 测试题库管理模块分页功能修复")
    print("=" * 50)
    
    # 测试主要API端点
    endpoints = [
        {
            'url': f"{base_url}/api/questions",
            'params': {'offset': 0, 'limit': 5},
            'name': '题目列表API (Bootstrap Table格式)'
        },
        {
            'url': f"{base_url}/api/knowledge-tree",
            'params': {},
            'name': '知识点树API'
        },
        {
            'url': f"{base_url}/api/question-types",
            'params': {},
            'name': '题型列表API'
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 测试: {endpoint['name']}")
        print(f"🌐 URL: {endpoint['url']}")
        
        try:
            response = requests.get(endpoint['url'], params=endpoint['params'], timeout=10)
            print(f"📊 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if endpoint['name'].startswith('题目列表'):
                    # 检查Bootstrap Table格式
                    if 'total' in data and 'rows' in data:
                        print(f"✅ 数据格式正确 - 总数: {data['total']}, 返回: {len(data['rows'])}条")
                        
                        # 显示第一个题目的信息
                        if data['rows']:
                            first_q = data['rows'][0]
                            print(f"📝 示例题目: {first_q.get('id', 'N/A')} - {first_q.get('stem', 'N/A')[:50]}...")
                    else:
                        print(f"❌ 数据格式错误: {list(data.keys())}")
                
                elif endpoint['name'].startswith('知识点树'):
                    if isinstance(data, dict):
                        print(f"✅ 知识点树格式正确 - 一级知识点数量: {len(data)}")
                        if data:
                            first_l1 = list(data.keys())[0]
                            print(f"📚 示例一级知识点: {first_l1}")
                    else:
                        print(f"❌ 知识点树格式错误")
                
                elif endpoint['name'].startswith('题型列表'):
                    if isinstance(data, list):
                        print(f"✅ 题型列表格式正确 - 题型数量: {len(data)}")
                        for qt in data[:3]:  # 显示前3个题型
                            print(f"🏷️ {qt.get('code', 'N/A')}: {qt.get('name', 'N/A')}")
                    else:
                        print(f"❌ 题型列表格式错误")
                        
            else:
                print(f"❌ 请求失败: {response.status_code}")
                if response.text:
                    print(f"错误信息: {response.text[:200]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ 连接失败: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成！")
    print("\n💡 如果所有API都正常，请在浏览器中访问:")
    print(f"   {base_url}")
    print("   检查分页功能是否正常工作")

def test_pagination_parameters():
    """测试分页参数"""
    base_url = "http://localhost:5000/api/questions"
    
    print("\n📄 测试分页参数...")
    
    test_cases = [
        {'offset': 0, 'limit': 5, 'desc': '第1页，每页5条'},
        {'offset': 5, 'limit': 5, 'desc': '第2页，每页5条'},
        {'offset': 0, 'limit': 10, 'desc': '第1页，每页10条'},
    ]
    
    for case in test_cases:
        try:
            response = requests.get(base_url, params=case, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'total' in data and 'rows' in data:
                    print(f"✅ {case['desc']}: 返回 {len(data['rows'])} 条记录")
                else:
                    print(f"❌ {case['desc']}: 数据格式错误")
            else:
                print(f"❌ {case['desc']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {case['desc']}: {e}")

def test_search_and_filter():
    """测试搜索和过滤功能"""
    base_url = "http://localhost:5000/api/questions"
    
    print("\n🔍 测试搜索和过滤功能...")
    
    test_cases = [
        {'offset': 0, 'limit': 5, 'search': 'A', 'desc': '搜索包含A的题目'},
        {'offset': 0, 'limit': 5, 'type': 'B', 'desc': '过滤单选题'},
        {'offset': 0, 'limit': 5, 'type': 'C', 'desc': '过滤判断题'},
    ]
    
    for case in test_cases:
        try:
            response = requests.get(base_url, params=case, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'total' in data and 'rows' in data:
                    print(f"✅ {case['desc']}: 找到 {data['total']} 条记录，返回 {len(data['rows'])} 条")
                else:
                    print(f"❌ {case['desc']}: 数据格式错误")
            else:
                print(f"❌ {case['desc']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {case['desc']}: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_pagination_parameters()
    test_search_and_filter()
    
    print("\n🌐 手动测试建议:")
    print("1. 在浏览器中打开: http://localhost:5000")
    print("2. 检查题目列表是否显示")
    print("3. 测试分页控件（页码、每页数量选择）")
    print("4. 测试搜索框和题型过滤器")
    print("5. 测试左侧知识点树导航")
    print("6. 检查是否有JavaScript错误（F12开发者工具）")
