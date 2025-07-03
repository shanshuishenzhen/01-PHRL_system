#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理修复测试脚本

测试题库管理模块的启动和运行状态
"""

import os
import sys
import time
import socket
import subprocess
import requests
from pathlib import Path

def check_service_running(port):
    """检查服务是否在指定端口运行"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"检查端口 {port} 时出错: {e}")
        return False

def test_flask_app_directly():
    """直接测试Flask应用启动"""
    print("\n🧪 直接测试Flask应用启动...")
    
    # 检查文件是否存在
    app_path = Path("question_bank_web/app.py")
    run_path = Path("question_bank_web/run.py")
    
    if not app_path.exists():
        print("❌ Flask应用文件不存在: question_bank_web/app.py")
        return False
    
    if not run_path.exists():
        print("❌ 启动脚本不存在: question_bank_web/run.py")
        return False
    
    print("✅ Flask应用文件存在")
    print("✅ 启动脚本存在")
    
    # 测试静默启动
    try:
        print("🚀 测试静默启动...")
        
        env = os.environ.copy()
        env['FLASK_SILENT'] = '1'
        
        if os.name == 'nt':  # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                [sys.executable, "run.py", "--silent"],
                cwd="question_bank_web",
                env=env,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, "run.py", "--silent"],
                cwd="question_bank_web",
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print(f"✅ 进程已启动，PID: {process.pid}")
        
        # 等待服务启动
        max_wait = 15
        for i in range(max_wait):
            time.sleep(1)
            if check_service_running(5000):
                print(f"✅ 服务启动成功，耗时 {i+1} 秒")
                
                # 测试HTTP请求
                try:
                    response = requests.get("http://127.0.0.1:5000", timeout=5)
                    if response.status_code == 200:
                        print("✅ HTTP请求成功，服务正常运行")
                    else:
                        print(f"⚠️ HTTP请求返回状态码: {response.status_code}")
                except Exception as e:
                    print(f"❌ HTTP请求失败: {e}")
                
                # 终止进程
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print("✅ 进程已正常终止")
                except Exception as e:
                    print(f"⚠️ 终止进程时出错: {e}")
                    try:
                        process.kill()
                        print("✅ 进程已强制终止")
                    except:
                        pass
                
                return True
        
        print(f"❌ 服务启动超时（{max_wait}秒）")
        
        # 检查进程输出
        try:
            stdout, stderr = process.communicate(timeout=1)
            if stdout:
                print(f"进程输出: {stdout.decode('utf-8', errors='ignore')}")
            if stderr:
                print(f"进程错误: {stderr.decode('utf-8', errors='ignore')}")
        except:
            pass
        
        # 终止进程
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass
        
        return False
        
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️ 测试数据库连接...")
    
    try:
        # 切换到题库管理目录
        original_cwd = os.getcwd()
        os.chdir("question_bank_web")
        
        # 导入并测试数据库连接
        sys.path.insert(0, os.getcwd())
        from models import Base, Question
        from sqlalchemy import create_engine
        
        # 测试数据库连接
        DATABASE_URL = 'sqlite:///local_dev.db'
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            print("✅ 数据库连接成功")
            
            # 检查表是否存在
            Base.metadata.create_all(engine)
            print("✅ 数据库表创建/验证成功")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        os.chdir(original_cwd)
        if os.getcwd() in sys.path:
            sys.path.remove(os.getcwd())

def test_dependencies():
    """测试依赖项"""
    print("\n📦 测试依赖项...")
    
    required_packages = [
        'flask',
        'sqlalchemy',
        'pandas',
        'openpyxl',
        'flask_cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖项: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖项已安装")
    return True

def main():
    """主函数"""
    print("🔧 题库管理修复测试")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("question_bank_web"):
        print("❌ 当前目录不是项目根目录，请在项目根目录运行此脚本")
        return
    
    # 运行测试
    tests = [
        ("依赖项检查", test_dependencies),
        ("数据库连接", test_database_connection),
        ("Flask应用启动", test_flask_app_directly)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试 {test_name} 时发生异常: {e}")
            results[test_name] = False
    
    # 总结
    print("\n" + "=" * 50)
    print("🎯 测试结果总结:")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！题库管理模块应该可以正常启动。")
        print("\n💡 使用建议:")
        print("1. 在主控台中点击'题库管理'按钮")
        print("2. 等待15秒让服务完全启动")
        print("3. 浏览器应该自动打开 http://127.0.0.1:5000")
    else:
        print("❌ 部分测试失败，请检查上述错误信息。")
        print("\n🔧 修复建议:")
        print("1. 安装缺失的依赖项")
        print("2. 检查数据库文件权限")
        print("3. 确保端口5000未被占用")

if __name__ == "__main__":
    main()
