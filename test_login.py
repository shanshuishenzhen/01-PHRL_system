#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的登录测试脚本
"""

import sys
import os

# 添加client目录到路径
sys.path.append('client')

try:
    import api
    
    print("🔐 测试用户登录功能")
    print("=" * 40)
    
    test_users = [
        ("student", "123456"),
        ("test", "123"),
        ("admin", "123456")
    ]
    
    for username, password in test_users:
        print(f"\n测试用户: {username}")
        print("-" * 20)
        
        try:
            result = api.login(username, password)
            print(f"登录结果: {result}")
            
            if result:
                print(f"✅ 登录成功!")
                print(f"   用户ID: {result.get('id')}")
                print(f"   用户名: {result.get('username')}")
                print(f"   角色: {result.get('role')}")
                print(f"   真实姓名: {result.get('real_name')}")
            else:
                print(f"❌ 登录失败!")
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
    
    print("\n" + "=" * 40)
    print("登录测试完成")
    
except ImportError as e:
    print(f"❌ 无法导入API模块: {e}")
    sys.exit(1)
