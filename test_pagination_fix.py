#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理模块分页功能测试脚本

测试修复后的分页功能，包括：
1. API端点数据格式
2. Bootstrap Table分页
3. 搜索和过滤功能
4. 知识点树结构
"""

import sys
import os
import unittest
import requests
import json
import time
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

class TestPaginationFix(unittest.TestCase):
    """分页功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.api_url = f"{self.base_url}/api"
        
        # 检查服务是否运行
        try:
            response = requests.get(self.base_url, timeout=5)
            self.server_running = response.status_code == 200
        except:
            self.server_running = False
    
    def test_api_questions_format(self):
        """测试题目API的数据格式"""
        if not self.server_running:
            self.skipTest("题库管理服务未运行")
        
        try:
            # 测试基本API调用
            response = requests.get(f"{self.api_url}/questions", params={
                'offset': 0,
                'limit': 10
            })
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            
            # 检查Bootstrap Table期望的数据格式
            self.assertIn('total', data)
            self.assertIn('rows', data)
            self.assertIsInstance(data['total'], int)
            self.assertIsInstance(data['rows'], list)
            
            # 检查题目数据结构
            if data['rows']:
                question = data['rows'][0]
                self.assertIn('id', question)
                self.assertIn('type_name', question)
                self.assertIn('stem', question)
                
            print(f"✅ API格式测试通过 - 总数: {data['total']}, 返回: {len(data['rows'])}条")
            
        except Exception as e:
            self.fail(f"API格式测试失败: {e}")
    
    def test_pagination_parameters(self):
        """测试分页参数"""
        if not self.server_running:
            self.skipTest("题库管理服务未运行")
        
        try:
            # 测试不同的分页参数
            test_cases = [
                {'offset': 0, 'limit': 5},
                {'offset': 5, 'limit': 10},
                {'offset': 0, 'limit': 20}
            ]
            
            for params in test_cases:
                response = requests.get(f"{self.api_url}/questions", params=params)
                self.assertEqual(response.status_code, 200)
                
                data = response.json()
                self.assertLessEqual(len(data['rows']), params['limit'])
                
                print(f"✅ 分页参数测试通过 - offset: {params['offset']}, limit: {params['limit']}, 返回: {len(data['rows'])}条")
            
        except Exception as e:
            self.fail(f"分页参数测试失败: {e}")
    
    def test_search_functionality(self):
        """测试搜索功能"""
        if not self.server_running:
            self.skipTest("题库管理服务未运行")
        
        try:
            # 测试搜索功能
            response = requests.get(f"{self.api_url}/questions", params={
                'offset': 0,
                'limit': 10,
                'search': 'A'  # 搜索包含A的题目
            })
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('total', data)
            self.assertIn('rows', data)
            
            print(f"✅ 搜索功能测试通过 - 搜索'A'结果: {data['total']}条")
            
        except Exception as e:
            self.fail(f"搜索功能测试失败: {e}")
    
    def test_type_filter(self):
        """测试题型过滤"""
        if not self.server_running:
            self.skipTest("题库管理服务未运行")
        
        try:
            # 测试题型过滤
            response = requests.get(f"{self.api_url}/questions", params={
                'offset': 0,
                'limit': 10,
                'type': 'B'  # 过滤单选题
            })
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            
            # 检查返回的题目是否都是指定题型
            for question in data['rows']:
                if 'question_type_code' in question:
                    self.assertEqual(question['question_type_code'], 'B')
            
            print(f"✅ 题型过滤测试通过 - 单选题数量: {data['total']}条")
            
        except Exception as e:
            self.fail(f"题型过滤测试失败: {e}")
    
    def test_knowledge_tree_api(self):
        """测试知识点树API"""
        if not self.server_running:
            self.skipTest("题库管理服务未运行")
        
        try:
            response = requests.get(f"{self.api_url}/knowledge-tree")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIsInstance(data, dict)
            
            print(f"✅ 知识点树API测试通过 - 一级知识点数量: {len(data)}")
            
            # 打印知识点结构示例
            if data:
                first_l1 = list(data.keys())[0]
                print(f"   示例一级知识点: {first_l1}")
                if data[first_l1]:
                    first_l2 = list(data[first_l1].keys())[0]
                    print(f"   示例二级知识点: {first_l2}")
                    if data[first_l1][first_l2]:
                        first_l3 = data[first_l1][first_l2][0]
                        print(f"   示例三级知识点: {first_l3}")
            
        except Exception as e:
            self.fail(f"知识点树API测试失败: {e}")
    
    def test_question_types_api(self):
        """测试题型API"""
        if not self.server_running:
            self.skipTest("题库管理服务未运行")
        
        try:
            response = requests.get(f"{self.api_url}/question-types")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIsInstance(data, list)
            
            # 检查题型数据结构
            if data:
                question_type = data[0]
                self.assertIn('code', question_type)
                self.assertIn('name', question_type)
            
            print(f"✅ 题型API测试通过 - 题型数量: {len(data)}")
            
            # 打印题型列表
            for qt in data:
                print(f"   {qt['code']}: {qt['name']}")
            
        except Exception as e:
            self.fail(f"题型API测试失败: {e}")

def run_manual_test():
    """运行手动测试"""
    print("\n🌐 开始手动测试...")
    
    try:
        base_url = "http://localhost:5000"
        
        # 检查服务状态
        try:
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                print("✅ 题库管理服务正在运行")
                print(f"🌐 访问地址: {base_url}")
                print("📋 请在浏览器中测试以下功能:")
                print("   1. 页面加载和题目列表显示")
                print("   2. 分页控件（页码、每页显示数量）")
                print("   3. 搜索功能（输入关键词搜索）")
                print("   4. 题型过滤（下拉选择题型）")
                print("   5. 知识点树导航（左侧知识点点击）")
                print("   6. 重置过滤器（点击'全部知识点'）")
            else:
                print(f"⚠️ 服务响应异常，状态码: {response.status_code}")
        except requests.exceptions.RequestException:
            print("❌ 题库管理服务未运行")
            print("💡 请先启动服务: python question_bank_web/app.py")
        
        print("\n✅ 手动测试指导完成")
        
    except Exception as e:
        print(f"❌ 手动测试失败: {e}")

def check_server_status():
    """检查服务器状态"""
    print("\n🔍 检查服务器状态...")
    
    try:
        base_url = "http://localhost:5000"
        
        # 检查主页
        try:
            response = requests.get(base_url, timeout=5)
            print(f"主页状态: {response.status_code}")
        except:
            print("主页状态: 无法连接")
        
        # 检查API端点
        api_endpoints = [
            "/api/questions",
            "/api/knowledge-tree", 
            "/api/question-types"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"{endpoint}: {response.status_code}")
            except:
                print(f"{endpoint}: 无法连接")
        
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")

def main():
    """主函数"""
    print("📄 题库管理模块分页功能测试")
    print("=" * 50)
    
    # 检查服务器状态
    check_server_status()
    
    # 运行单元测试
    print("\n🧪 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 询问是否运行手动测试
    print("\n" + "=" * 50)
    response = input("是否查看手动测试指导？(y/n): ").lower().strip()
    
    if response in ['y', 'yes', '是']:
        run_manual_test()
    else:
        print("跳过手动测试指导")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
