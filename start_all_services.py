#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动所有服务的脚本
包括题库管理、阅卷中心、成绩门户
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from datetime import datetime

def print_banner():
    """打印启动横幅"""
    print("=" * 80)
    print("🎯 考试系统完整服务启动器")
    print("=" * 80)
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def start_service(name, command, cwd, port):
    """启动单个服务"""
    def run_service():
        try:
            print(f"🚀 启动 {name}...")
            os.chdir(cwd)
            subprocess.run(command, shell=True, check=True)
        except Exception as e:
            print(f"❌ {name} 启动失败: {e}")
    
    # 在后台线程中启动服务
    thread = threading.Thread(target=run_service, daemon=True)
    thread.start()
    
    # 等待服务启动
    print(f"   ⏳ 等待 {name} 启动...")
    time.sleep(3)
    
    # 检查服务状态
    try:
        import requests
        response = requests.get(f"http://localhost:{port}", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ {name} 启动成功 (端口 {port})")
            return True
        else:
            print(f"   ❌ {name} 响应异常")
            return False
    except Exception as e:
        print(f"   ❌ {name} 连接失败: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    required_modules = ['flask', 'flask_cors', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ 缺少依赖模块: {', '.join(missing_modules)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    print("   ✅ 所有依赖已满足")
    return True

def check_files():
    """检查必要文件"""
    print("\n📁 检查必要文件...")
    
    required_files = [
        'question_bank_web/app.py',
        'grading_center/grading_api.py',
        'grade_portal/grade_portal.py',
        'client_fixed.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ 缺少必要文件，无法启动")
        return False
    
    print("   ✅ 所有必要文件存在")
    return True

def start_all_services():
    """启动所有服务"""
    print("\n🚀 启动所有服务...")
    print("-" * 50)
    
    services = [
        {
            'name': '题库管理系统',
            'command': 'python app.py',
            'cwd': 'question_bank_web',
            'port': 5000,
            'url': 'http://localhost:5000'
        },
        {
            'name': '阅卷中心',
            'command': 'python grading_api.py',
            'cwd': 'grading_center',
            'port': 5002,
            'url': 'http://localhost:5002'
        },
        {
            'name': '成绩门户',
            'command': 'python grade_portal.py',
            'cwd': 'grade_portal',
            'port': 5003,
            'url': 'http://localhost:5003'
        }
    ]
    
    started_services = []
    
    for service in services:
        success = start_service(
            service['name'],
            service['command'],
            service['cwd'],
            service['port']
        )
        
        if success:
            started_services.append(service)
        
        # 切换回根目录
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    return started_services

def show_service_info(services):
    """显示服务信息"""
    print("\n🌐 服务访问地址:")
    print("-" * 50)
    
    for service in services:
        print(f"   {service['name']}: {service['url']}")
    
    print(f"\n🖥️ 客户端启动:")
    print(f"   python client_fixed.py")
    
    print(f"\n📖 使用说明:")
    print(f"   1. 题库管理系统 - 管理试卷和题目")
    print(f"   2. 客户端 - 学生答题")
    print(f"   3. 阅卷中心 - 自动阅卷和成绩统计")
    print(f"   4. 成绩门户 - 成绩查询和发布")
    
    print(f"\n🔑 默认账号:")
    print(f"   成绩门户教师: admin/123456")
    print(f"   成绩门户学生: student/123456")

def open_browsers(services):
    """打开浏览器"""
    print(f"\n🌐 打开浏览器...")
    
    try:
        # 打开成绩门户（主要入口）
        webbrowser.open('http://localhost:5003')
        print(f"   ✅ 已打开成绩门户")
        
        time.sleep(2)
        
        # 打开阅卷中心
        webbrowser.open('http://localhost:5002')
        print(f"   ✅ 已打开阅卷中心")
        
    except Exception as e:
        print(f"   ⚠️ 自动打开浏览器失败: {e}")
        print(f"   请手动访问上述地址")

def test_complete_workflow():
    """测试完整工作流程"""
    print(f"\n🧪 完整工作流程测试:")
    print("-" * 50)
    
    print(f"1. 启动客户端进行答题:")
    print(f"   python client_fixed.py")
    print(f"   - 答题完成后会自动提交到阅卷中心")
    
    print(f"\n2. 查看阅卷结果:")
    print(f"   访问 http://localhost:5002")
    print(f"   - 查看自动阅卷结果和成绩统计")
    
    print(f"\n3. 发布和查询成绩:")
    print(f"   访问 http://localhost:5003")
    print(f"   - 教师登录发布成绩")
    print(f"   - 学生登录查询成绩")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查文件
    if not check_files():
        return
    
    # 启动所有服务
    started_services = start_all_services()
    
    if not started_services:
        print("\n❌ 没有服务启动成功")
        return
    
    # 显示服务信息
    show_service_info(started_services)
    
    # 打开浏览器
    open_browsers(started_services)
    
    # 显示测试说明
    test_complete_workflow()
    
    print(f"\n🎉 系统启动完成！")
    print(f"\n💡 提示:")
    print(f"   - 所有服务都在后台运行")
    print(f"   - 按 Ctrl+C 退出")
    print(f"   - 建议按照工作流程测试完整功能")
    
    try:
        # 保持脚本运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n👋 系统关闭")
        print(f"感谢使用考试系统！")

if __name__ == "__main__":
    main()
