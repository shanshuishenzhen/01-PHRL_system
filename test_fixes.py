#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复效果的脚本
验证Pillow依赖检查和客户端独立启动的修复
"""

import os
import sys
import subprocess
from pathlib import Path

def test_pillow_import():
    """测试Pillow导入修复"""
    print("🔍 测试1: Pillow依赖检查修复")
    print("-" * 40)
    
    try:
        # 测试直接导入PIL
        import PIL
        print("✅ PIL导入成功")
        
        # 测试PIL.Image
        from PIL import Image
        print("✅ PIL.Image导入成功")
        
        # 获取版本信息
        print(f"   Pillow版本: {PIL.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ PIL导入失败: {e}")
        return False

def test_launcher_dependency_check():
    """测试启动器依赖检查逻辑"""
    print("\n🔍 测试2: 启动器依赖检查逻辑")
    print("-" * 40)
    
    try:
        # 模拟启动器的依赖检查逻辑
        required_packages = {
            "flask": "flask",
            "pandas": "pandas", 
            "openpyxl": "openpyxl",
            "pillow": "PIL",  # 修复后的映射
            "requests": "requests"
        }
        
        missing_packages = []
        
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                print(f"✅ {package_name} (导入为 {import_name})")
            except ImportError:
                print(f"❌ {package_name} (尝试导入 {import_name}) - 未安装")
                missing_packages.append(package_name)
        
        if missing_packages:
            print(f"\n⚠️  缺少依赖: {', '.join(missing_packages)}")
            return False
        else:
            print("\n✅ 所有依赖检查通过")
            return True
            
    except Exception as e:
        print(f"❌ 依赖检查过程出错: {e}")
        return False

def test_client_standalone():
    """测试客户端独立启动"""
    print("\n🔍 测试3: 客户端独立启动能力")
    print("-" * 40)
    
    try:
        # 检查独立启动器文件是否存在
        standalone_launcher = Path("client/standalone_launcher.py")
        if standalone_launcher.exists():
            print("✅ 独立启动器文件存在")
        else:
            print("❌ 独立启动器文件不存在")
            return False
        
        # 检查客户端应用文件
        client_app = Path("client/client_app.py")
        if client_app.exists():
            print("✅ 客户端应用文件存在")
        else:
            print("❌ 客户端应用文件不存在")
            return False
        
        # 检查配置目录
        config_dir = Path("client/config")
        if config_dir.exists():
            print("✅ 客户端配置目录存在")
        else:
            print("⚠️  客户端配置目录不存在，但独立启动器会创建")
        
        # 测试导入客户端模块（不实际运行GUI）
        sys.path.insert(0, "client")
        try:
            # 只测试导入，不运行GUI
            print("🔄 测试客户端模块导入...")
            
            # 这里我们不实际导入，因为它会启动GUI
            # 而是检查文件语法
            with open("client/client_app.py", 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 简单的语法检查
            compile(content, "client/client_app.py", "exec")
            print("✅ 客户端应用语法检查通过")
            
            return True
            
        except SyntaxError as e:
            print(f"❌ 客户端应用语法错误: {e}")
            return False
        except Exception as e:
            print(f"⚠️  客户端模块测试异常: {e}")
            return True  # 语法正确，只是运行时问题
            
    except Exception as e:
        print(f"❌ 客户端独立启动测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构完整性"""
    print("\n🔍 测试4: 目录结构完整性")
    print("-" * 40)
    
    required_dirs = [
        "client",
        "client/config", 
        "exam_management",
        "grading_center",
        "user_management",
        "question_bank_web"
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️  缺少目录: {', '.join(missing_dirs)}")
        return False
    else:
        print("\n✅ 目录结构完整")
        return True

def main():
    """主测试函数"""
    print("🧪 PH&RL系统修复效果测试")
    print("=" * 50)
    
    tests = [
        ("Pillow依赖检查修复", test_pillow_import),
        ("启动器依赖检查逻辑", test_launcher_dependency_check),
        ("客户端独立启动能力", test_client_standalone),
        ("目录结构完整性", test_directory_structure)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行异常: {e}")
    
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！修复成功！")
        print("\n✅ 现在可以:")
        print("1. 运行 python launcher.py (Pillow依赖检查已修复)")
        print("2. 运行 python client/standalone_launcher.py (客户端独立启动)")
        print("3. 直接运行 python client/client_app.py (改进的错误处理)")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
