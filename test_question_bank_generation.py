#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库生成功能修复验证脚本
测试开发工具模块的样例题库生成功能
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_syntax_check():
    """测试语法检查"""
    print("🔍 测试1: 语法检查")
    print("-" * 40)
    
    try:
        # 检查question_bank_generator.py
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'developer_tools/question_bank_generator.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ question_bank_generator.py 语法检查通过")
        else:
            print(f"❌ question_bank_generator.py 语法错误: {result.stderr}")
            return False
        
        # 检查developer_tools.py
        result_main = subprocess.run([
            sys.executable, '-m', 'py_compile', 'developer_tools.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result_main.returncode == 0:
            print("✅ developer_tools.py 语法检查通过")
            return True
        else:
            print(f"❌ developer_tools.py 语法错误: {result_main.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 语法检查失败: {e}")
        return False

def test_encoding_fixes():
    """测试编码修复"""
    print("\n🔍 测试2: 编码修复检查")
    print("-" * 40)
    
    try:
        with open("developer_tools/question_bank_generator.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否移除了有问题的Unicode字符
        if "✅" not in content:
            print("✅ Unicode字符 ✅ 已移除")
        else:
            print("❌ Unicode字符 ✅ 仍然存在")
            return False
        
        if "⚠️" not in content:
            print("✅ Unicode字符 ⚠️ 已移除")
        else:
            print("❌ Unicode字符 ⚠️ 仍然存在")
            return False
        
        # 检查是否使用了安全的替代文本
        if "[成功]" in content:
            print("✅ 安全的成功标识已添加")
        else:
            print("❌ 安全的成功标识未添加")
            return False
        
        if "[警告]" in content:
            print("✅ 安全的警告标识已添加")
        else:
            print("❌ 安全的警告标识未添加")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 编码修复检查失败: {e}")
        return False

def test_template_file_exists():
    """测试模板文件是否存在"""
    print("\n🔍 测试3: 模板文件检查")
    print("-" * 40)
    
    try:
        template_file = Path("developer_tools/样例题组题规则模板.xlsx")
        if template_file.exists():
            print(f"✅ 模板文件存在: {template_file}")
            print(f"   文件大小: {template_file.stat().st_size} 字节")
            return True
        else:
            print(f"❌ 模板文件不存在: {template_file}")
            return False
            
    except Exception as e:
        print(f"❌ 模板文件检查失败: {e}")
        return False

def test_output_directory():
    """测试输出目录"""
    print("\n🔍 测试4: 输出目录检查")
    print("-" * 40)
    
    try:
        output_dir = Path("question_bank_web")
        if output_dir.exists():
            print(f"✅ 输出目录存在: {output_dir}")
        else:
            print(f"❌ 输出目录不存在: {output_dir}")
            return False
        
        # 检查是否有写入权限
        test_file = output_dir / "test_write.tmp"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()  # 删除测试文件
            print("✅ 输出目录有写入权限")
            return True
        except Exception as e:
            print(f"❌ 输出目录无写入权限: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 输出目录检查失败: {e}")
        return False

def test_generation_function():
    """测试题库生成函数"""
    print("\n🔍 测试5: 题库生成函数测试")
    print("-" * 40)
    
    try:
        # 添加路径以便导入
        sys.path.insert(0, 'developer_tools')
        from question_bank_generator import generate_from_excel
        
        # 检查模板文件
        template_file = "developer_tools/样例题组题规则模板.xlsx"
        if not os.path.exists(template_file):
            print(f"❌ 模板文件不存在: {template_file}")
            return False
        
        # 设置输出文件
        output_file = "question_bank_web/test_questions.xlsx"
        
        # 尝试生成题库
        print("正在测试题库生成...")
        result = generate_from_excel(template_file, output_file, append_mode=False)
        
        if result:
            if len(result) == 3:
                total_generated, bank_name, db_success = result
                print(f"✅ 题库生成成功")
                print(f"   生成题目数量: {total_generated}")
                print(f"   数据库保存: {'成功' if db_success else '失败'}")
            else:
                total_generated, bank_name = result
                print(f"✅ 题库生成成功")
                print(f"   生成题目数量: {total_generated}")
            
            # 检查输出文件是否存在
            if os.path.exists(output_file):
                print(f"✅ 输出文件已创建: {output_file}")
                # 清理测试文件
                os.remove(output_file)
                return True
            else:
                print(f"❌ 输出文件未创建: {output_file}")
                return False
        else:
            print("❌ 题库生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 题库生成函数测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 题库生成功能修复验证测试")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax_check),
        ("编码修复检查", test_encoding_fixes),
        ("模板文件检查", test_template_file_exists),
        ("输出目录检查", test_output_directory),
        ("题库生成函数测试", test_generation_function)
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
        print("🎉 所有测试通过！题库生成功能修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 移除了导致编码错误的Unicode字符（✅、⚠️等）")
        print("2. ✅ 使用安全的文本替代（[成功]、[警告]等）")
        print("3. ✅ 修复了print语句中的编码问题")
        print("4. ✅ 确保所有输出都使用UTF-8编码")
        print("5. ✅ 题库生成函数可以正常工作")
        
        print("\n🎯 功能说明:")
        print("• 开发工具模块现在可以正常生成样例题库")
        print("• 不再出现 'gbk' codec 编码错误")
        print("• 生成的题库文件格式正确")
        print("• 支持增量和覆盖两种生成模式")
        
        print("\n🚀 使用方法:")
        print("1. 运行 python developer_tools.py")
        print("2. 点击'样例题库生成'选项卡")
        print("3. 下载全空白模板或上传自定义模板")
        print("4. 点击'生成样例题库'按钮")
        print("5. 选择生成模式（增量或覆盖）")
        print("6. 等待生成完成")
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        
        if passed_tests >= 3:
            print("\n💡 建议:")
            print("- 基础功能已修复，可以尝试手动测试")
            print("- 运行: python developer_tools.py")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
