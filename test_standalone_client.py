#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试独立客户端功能
"""

import requests
import json
import time
import subprocess
import sys
import os

def test_server_connection():
    """测试服务器连接"""
    print("🌐 测试服务器连接")
    print("-" * 40)
    
    try:
        # 测试健康检查
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def test_login_api():
    """测试登录API"""
    print("\n🔐 测试登录API")
    print("-" * 40)
    
    try:
        # 测试正确登录
        login_data = {
            "username": "919662422786147946",
            "password": "password123"
        }
        
        response = requests.post("http://127.0.0.1:5000/api/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 登录API正常")
                print(f"   用户信息: {result.get('user_info')}")
                return result.get('user_info')
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return None
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 登录API测试失败: {e}")
        return None

def test_exam_api(user_info):
    """测试考试API"""
    print("\n📝 测试考试API")
    print("-" * 40)
    
    if not user_info:
        print("❌ 需要用户信息")
        return False
    
    try:
        user_id = user_info['id']
        
        # 获取考试列表
        response = requests.get(f"http://127.0.0.1:5000/api/exams/user/{user_id}", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            exams = result.get('exams', [])
            print(f"✅ 获取考试列表成功，共 {len(exams)} 个考试")
            
            if exams:
                # 测试获取考试详情
                exam_id = exams[0]['id']
                detail_response = requests.get(f"http://127.0.0.1:5000/api/exams/{exam_id}", timeout=5)
                
                if detail_response.status_code == 200:
                    exam_details = detail_response.json()
                    questions = exam_details.get('questions', [])
                    print(f"✅ 获取考试详情成功，共 {len(questions)} 道题目")
                    
                    # 显示题目类型统计
                    type_count = {}
                    for q in questions:
                        q_type = q.get('type', 'unknown')
                        type_count[q_type] = type_count.get(q_type, 0) + 1
                    
                    print("   题目类型统计:")
                    for q_type, count in type_count.items():
                        print(f"      {q_type}: {count}题")
                    
                    return True
                else:
                    print(f"❌ 获取考试详情失败: {detail_response.status_code}")
                    return False
            else:
                print("⚠️ 没有可用考试")
                return True
        else:
            print(f"❌ 获取考试列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 考试API测试失败: {e}")
        return False

def test_submit_api(user_info):
    """测试提交API"""
    print("\n📤 测试提交API")
    print("-" * 40)
    
    if not user_info:
        print("❌ 需要用户信息")
        return False
    
    try:
        # 模拟答案数据
        test_answers = {
            "q1": "Windows",
            "q2": ["Python", "Java"],
            "q3": "正确",
            "q4": "硬盘",
            "q5": "计算机网络是指将多台计算机连接起来进行通信和资源共享的系统。"
        }
        
        submit_data = {
            "user_id": user_info['id'],
            "answers": test_answers,
            "submit_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        response = requests.post("http://127.0.0.1:5000/api/exams/exam_001/submit", 
                               json=submit_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 答案提交成功")
                print(f"   得分: {result.get('score')}")
                print(f"   答题数: {result.get('answered_questions')}/{result.get('total_questions')}")
                return True
            else:
                print(f"❌ 提交失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 提交请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 提交API测试失败: {e}")
        return False

def check_standalone_client():
    """检查独立客户端文件"""
    print("\n📁 检查独立客户端文件")
    print("-" * 40)
    
    files_to_check = [
        "standalone_client.py",
        "mock_server.py"
    ]
    
    all_exist = True
    for file_name in files_to_check:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            print(f"✅ {file_name} ({size} bytes)")
        else:
            print(f"❌ {file_name} 不存在")
            all_exist = False
    
    return all_exist

def test_config_generation():
    """测试配置文件生成"""
    print("\n⚙️ 测试配置文件生成")
    print("-" * 40)
    
    try:
        # 导入配置类
        sys.path.append('.')
        from standalone_client import StandaloneClientConfig
        
        # 创建配置实例
        config = StandaloneClientConfig()
        
        print("✅ 配置类导入成功")
        print(f"   服务器URL: {config.get_server_url()}")
        print(f"   客户端名称: {config.config['client']['name']}")
        print(f"   版本: {config.config['client']['version']}")
        
        # 检查配置文件是否生成
        if os.path.exists('client_config.json'):
            print("✅ 配置文件已生成")
            return True
        else:
            print("❌ 配置文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 独立客户端功能测试")
    print("=" * 60)
    
    # 检查文件
    files_ok = check_standalone_client()
    
    # 测试配置
    config_ok = test_config_generation()
    
    # 测试服务器连接
    server_ok = test_server_connection()
    
    if server_ok:
        # 测试API
        user_info = test_login_api()
        exam_ok = test_exam_api(user_info)
        submit_ok = test_submit_api(user_info)
    else:
        print("\n⚠️ 服务器未启动，跳过API测试")
        print("   请先运行: python mock_server.py")
        exam_ok = False
        submit_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 测试结果总结")
    print("=" * 60)
    print(f"📁 文件检查: {'✅ 通过' if files_ok else '❌ 失败'}")
    print(f"⚙️ 配置生成: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"🌐 服务器连接: {'✅ 通过' if server_ok else '❌ 失败'}")
    print(f"📝 考试API: {'✅ 通过' if exam_ok else '❌ 失败'}")
    print(f"📤 提交API: {'✅ 通过' if submit_ok else '❌ 失败'}")
    
    all_passed = all([files_ok, config_ok, server_ok, exam_ok, submit_ok])
    
    if all_passed:
        print("\n🎉 所有测试通过！独立客户端可以正常使用")
        print("\n📋 使用说明:")
        print("1. 启动服务器: python mock_server.py")
        print("2. 启动客户端: python standalone_client.py")
        print("3. 使用测试账号登录:")
        print("   用户名: 919662422786147946")
        print("   密码: password123")
    else:
        print("\n❌ 部分测试失败，请检查问题")
    
    return all_passed

if __name__ == "__main__":
    main()
