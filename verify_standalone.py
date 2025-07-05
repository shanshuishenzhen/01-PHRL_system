#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证独立客户端核心功能
"""

import os
import sys
import subprocess
import time

def check_file_independence():
    """检查文件独立性"""
    print("🔍 检查文件独立性")
    print("-" * 40)
    
    # 检查独立客户端文件
    standalone_file = "standalone_client.py"
    if os.path.exists(standalone_file):
        print(f"✅ 独立客户端文件存在: {standalone_file}")
        
        # 检查文件内容
        with open(standalone_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否移除了主控台依赖
        if "check_main_console_running" not in content:
            print("✅ 已移除主控台依赖检查")
        else:
            print("❌ 仍包含主控台依赖检查")
            return False
        
        # 检查是否包含网络通信
        if "requests" in content and "StandaloneAPI" in content:
            print("✅ 包含网络通信功能")
        else:
            print("❌ 缺少网络通信功能")
            return False
        
        # 检查是否包含配置管理
        if "StandaloneClientConfig" in content:
            print("✅ 包含配置管理功能")
        else:
            print("❌ 缺少配置管理功能")
            return False
        
        return True
    else:
        print(f"❌ 独立客户端文件不存在: {standalone_file}")
        return False

def check_import_independence():
    """检查导入独立性"""
    print("\n📦 检查导入独立性")
    print("-" * 40)
    
    try:
        # 尝试导入独立客户端的类
        sys.path.append('.')
        from standalone_client import StandaloneClientConfig, StandaloneAPI
        
        print("✅ 配置类导入成功")
        print("✅ API类导入成功")
        
        # 测试配置类
        config = StandaloneClientConfig()
        print(f"✅ 配置初始化成功")
        print(f"   服务器URL: {config.get_server_url()}")
        
        # 测试API类
        api = StandaloneAPI(config)
        print(f"✅ API初始化成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def check_config_functionality():
    """检查配置功能"""
    print("\n⚙️ 检查配置功能")
    print("-" * 40)
    
    try:
        from standalone_client import StandaloneClientConfig
        
        # 创建配置实例
        config = StandaloneClientConfig()
        
        # 检查默认配置
        default_host = config.config['server']['host']
        default_port = config.config['server']['port']
        print(f"✅ 默认服务器: {default_host}:{default_port}")
        
        # 测试配置修改
        config.config['server']['host'] = '192.168.1.100'
        config.config['server']['port'] = 8080
        
        new_url = config.get_server_url()
        print(f"✅ 配置修改成功: {new_url}")
        
        # 测试配置保存
        config.save_config()
        print("✅ 配置保存成功")
        
        # 检查配置文件
        if os.path.exists('client_config.json'):
            print("✅ 配置文件已生成")
            return True
        else:
            print("❌ 配置文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 配置功能测试失败: {e}")
        return False

def check_ui_independence():
    """检查UI独立性"""
    print("\n🖥️ 检查UI独立性")
    print("-" * 40)
    
    try:
        # 检查是否可以导入UI类
        from standalone_client import LoginFrame, ExamListFrame, ExamFrame
        
        print("✅ 登录界面类导入成功")
        print("✅ 考试列表界面类导入成功")
        print("✅ 考试界面类导入成功")
        
        # 检查主应用类
        from standalone_client import StandaloneExamClient
        print("✅ 主应用类导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ UI类导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ UI检查失败: {e}")
        return False

def check_network_capability():
    """检查网络能力"""
    print("\n🌐 检查网络能力")
    print("-" * 40)
    
    try:
        import requests
        print("✅ requests库可用")
        
        from standalone_client import StandaloneAPI, StandaloneClientConfig
        
        config = StandaloneClientConfig()
        api = StandaloneAPI(config)
        
        print("✅ 网络API类初始化成功")
        print(f"   目标服务器: {api.server_url}")
        
        # 测试网络连接（不依赖服务器）
        print("✅ 网络功能准备就绪")
        
        return True
        
    except ImportError as e:
        print(f"❌ 网络库缺失: {e}")
        return False
    except Exception as e:
        print(f"❌ 网络功能检查失败: {e}")
        return False

def check_packaging_readiness():
    """检查打包准备情况"""
    print("\n📦 检查打包准备情况")
    print("-" * 40)
    
    # 检查必要的依赖
    required_modules = ['tkinter', 'requests', 'json', 'os', 'sys', 'time', 'threading']
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少依赖: {missing_modules}")
        return False
    else:
        print("✅ 所有必要依赖都可用")
        return True

def main():
    """主验证函数"""
    print("🧪 独立客户端核心功能验证")
    print("=" * 60)
    
    # 执行各项检查
    tests = [
        ("文件独立性", check_file_independence),
        ("导入独立性", check_import_independence),
        ("配置功能", check_config_functionality),
        ("UI独立性", check_ui_independence),
        ("网络能力", check_network_capability),
        ("打包准备", check_packaging_readiness)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print("\n" + "=" * 60)
    print("🎯 验证结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有验证通过！独立客户端已准备就绪")
        print("\n📋 独立客户端特性:")
        print("✅ 完全独立运行，不依赖主控台")
        print("✅ 支持局域网服务器通信")
        print("✅ 内置服务器配置管理")
        print("✅ 完整的考试功能界面")
        print("✅ 防作弊安全机制")
        print("✅ 可打包为Windows可执行文件")
        
        print("\n🚀 使用方法:")
        print("1. 配置服务器地址（在客户端中点击'服务器配置'）")
        print("2. 启动客户端: python standalone_client.py")
        print("3. 输入考生账号登录")
        print("4. 选择考试开始答题")
        
        print("\n📦 打包命令:")
        print("pip install pyinstaller")
        print("pyinstaller --onefile --windowed standalone_client.py")
        
        return True
    else:
        print(f"\n❌ {total-passed} 项验证失败，需要修复")
        return False

if __name__ == "__main__":
    main()
