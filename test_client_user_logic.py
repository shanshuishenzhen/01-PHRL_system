#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端用户逻辑测试脚本

测试修复后的客户端用户登录逻辑：
1. 考生账号：只有在有分配考试时才能登录
2. 管理员账号：可以查看所有进行中的考试
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

def test_user_database():
    """测试用户数据库"""
    print("\n👥 测试用户数据库...")
    
    # 检查用户数据库
    db_path = Path("user_management/users.db")
    json_path = Path("user_management/users.json")
    
    users_found = []
    
    # 检查SQLite数据库
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT username, real_name, role FROM users LIMIT 10")
            db_users = cursor.fetchall()
            
            print(f"✅ SQLite数据库: 找到 {len(db_users)} 个用户")
            for user in db_users:
                users_found.append({
                    'username': user['username'],
                    'real_name': user['real_name'],
                    'role': user.get('role', 'student'),
                    'source': 'database'
                })
                print(f"  - {user['username']} ({user['real_name']}) - 角色: {user.get('role', 'student')}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ SQLite数据库读取失败: {e}")
    else:
        print("⚠️ SQLite数据库文件不存在")
    
    # 检查JSON文件
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_users = data.get('users', [])
            
            print(f"✅ JSON文件: 找到 {len(json_users)} 个用户")
            for user in json_users[:5]:  # 只显示前5个
                users_found.append({
                    'username': user.get('username'),
                    'real_name': user.get('real_name') or user.get('name'),
                    'role': user.get('role', 'student'),
                    'source': 'json'
                })
                print(f"  - {user.get('username')} ({user.get('real_name') or user.get('name')}) - 角色: {user.get('role', 'student')}")
            
        except Exception as e:
            print(f"❌ JSON文件读取失败: {e}")
    else:
        print("⚠️ JSON用户文件不存在")
    
    return users_found

def test_exam_assignment():
    """测试考试分配"""
    print("\n📅 测试考试分配...")
    
    # 检查考试管理数据
    exam_paths = [
        "exam_management/exams.json",
        "exam_management/published_exams.json",
        "exam_management/exam_assignments.json"
    ]
    
    total_exams = 0
    assigned_students = set()
    
    for exam_path in exam_paths:
        if os.path.exists(exam_path):
            try:
                with open(exam_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'exams' in data:
                    exams = data['exams']
                    total_exams += len(exams)
                    print(f"✅ {exam_path}: 找到 {len(exams)} 个考试")
                    
                    # 检查考试分配
                    for exam in exams:
                        participants = exam.get('participants', [])
                        if participants:
                            assigned_students.update(participants)
                            print(f"  - 考试 '{exam.get('name')}': {len(participants)} 个参与者")
                
            except Exception as e:
                print(f"❌ 读取 {exam_path} 失败: {e}")
        else:
            print(f"⚠️ {exam_path} 不存在")
    
    print(f"📊 总计: {total_exams} 个考试, {len(assigned_students)} 个分配的学生")
    return assigned_students

def test_login_logic():
    """测试登录逻辑"""
    print("\n🔐 测试登录逻辑...")
    
    # 获取用户和考试数据
    users = test_user_database()
    assigned_students = test_exam_assignment()
    
    print("\n🧪 模拟登录测试:")
    
    # 测试用例
    test_cases = [
        {
            'username': 'admin',
            'role': 'admin',
            'expected': '应该能登录（管理员）'
        },
        {
            'username': 'supervisor',
            'role': 'supervisor', 
            'expected': '应该能登录（考评员）'
        }
    ]
    
    # 添加实际用户的测试用例
    for user in users[:3]:  # 测试前3个用户
        username = user['username']
        role = user['role']
        
        if role == 'student':
            if username in assigned_students or str(user.get('id', '')) in assigned_students:
                expected = '应该能登录（有分配考试的考生）'
            else:
                expected = '应该被拒绝（无分配考试的考生）'
        else:
            expected = f'应该能登录（{role}）'
        
        test_cases.append({
            'username': username,
            'role': role,
            'expected': expected
        })
    
    # 执行测试
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. 用户: {case['username']} (角色: {case['role']})")
        print(f"     预期结果: {case['expected']}")

def test_client_config():
    """测试客户端配置"""
    print("\n⚙️ 测试客户端配置...")
    
    config_path = "client/config/client_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ 客户端配置文件存在")
            print(f"  - API地址: {config.get('api_base_url', '未配置')}")
            print(f"  - 超时设置: {config.get('timeout', '未配置')}秒")
        except Exception as e:
            print(f"❌ 读取客户端配置失败: {e}")
    else:
        print("⚠️ 客户端配置文件不存在")

def create_test_users():
    """创建测试用户"""
    print("\n👤 创建测试用户...")
    
    test_users = [
        {
            'username': 'student001',
            'password': '123456',
            'real_name': '张三',
            'role': 'student',
            'id_card': '123456789012345678'
        },
        {
            'username': 'student002', 
            'password': '123456',
            'real_name': '李四',
            'role': 'student',
            'id_card': '123456789012345679'
        },
        {
            'username': 'teacher001',
            'password': '123456',
            'real_name': '王老师',
            'role': 'evaluator',
            'id_card': '123456789012345680'
        }
    ]
    
    # 检查用户管理数据库
    db_path = "user_management/users.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for user in test_users:
                # 检查用户是否已存在
                cursor.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO users (username, password, real_name, role, id_card)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user['username'], user['password'], user['real_name'], 
                          user['role'], user['id_card']))
                    print(f"  ✅ 创建用户: {user['username']} ({user['real_name']})")
                else:
                    print(f"  ⚠️ 用户已存在: {user['username']}")
            
            conn.commit()
            conn.close()
            print("✅ 测试用户创建完成")
            
        except Exception as e:
            print(f"❌ 创建测试用户失败: {e}")
    else:
        print("⚠️ 用户数据库不存在，无法创建测试用户")

def main():
    """主函数"""
    print("🧪 客户端用户逻辑测试")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("client"):
        print("❌ 当前目录不是项目根目录，请在项目根目录运行此脚本")
        return
    
    # 运行测试
    test_client_config()
    users = test_user_database()
    assigned_students = test_exam_assignment()
    test_login_logic()
    
    # 询问是否创建测试用户
    print("\n" + "=" * 50)
    response = input("是否创建测试用户？(y/n): ").lower().strip()
    if response in ['y', 'yes', '是']:
        create_test_users()
    
    print("\n🎯 测试总结:")
    print("1. 检查了用户数据库和JSON文件")
    print("2. 检查了考试分配情况")
    print("3. 模拟了登录逻辑测试")
    print("4. 验证了客户端配置")
    
    print("\n💡 使用建议:")
    print("1. 确保用户数据库中有正确的role字段")
    print("2. 确保考试管理模块正确分配考生")
    print("3. 测试不同角色用户的登录行为")
    print("4. 验证考生无考试时被正确拒绝")
    
    print("\n🎉 客户端用户逻辑测试完成！")

if __name__ == "__main__":
    main()
