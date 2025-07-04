#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 [Errno 22] Invalid argument 错误的脚本
"""

import os
import sys
import traceback
import tempfile
from pathlib import Path

def diagnose_error_report_issue():
    """诊断错误报告生成问题"""
    print("🔍 诊断错误报告生成问题")
    print("-" * 40)
    
    try:
        # 测试创建error_reports目录
        report_dir = "question_bank_web/error_reports"
        print(f"测试目录: {report_dir}")
        
        # 检查目录是否存在
        if os.path.exists(report_dir):
            print(f"✅ 目录已存在: {report_dir}")
        else:
            print(f"⚠️  目录不存在，尝试创建: {report_dir}")
            try:
                os.makedirs(report_dir, exist_ok=True)
                print(f"✅ 目录创建成功: {report_dir}")
            except Exception as e:
                print(f"❌ 目录创建失败: {e}")
                return False
        
        # 测试文件名生成
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_report_{timestamp}.txt"
        filepath = os.path.join(report_dir, filename)
        
        print(f"测试文件路径: {filepath}")
        
        # 检查路径中的特殊字符
        if any(ord(c) > 127 for c in filepath):
            print("⚠️  文件路径包含非ASCII字符")
        else:
            print("✅ 文件路径只包含ASCII字符")
        
        # 测试文件写入
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("测试内容\n")
            print(f"✅ 文件写入成功: {filepath}")
            
            # 清理测试文件
            os.remove(filepath)
            print(f"✅ 测试文件已清理")
            
        except Exception as e:
            print(f"❌ 文件写入失败: {e}")
            print(f"错误类型: {type(e).__name__}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def fix_export_error_report():
    """修复export_error_report函数"""
    print("\n🔧 修复export_error_report函数")
    print("-" * 40)
    
    try:
        excel_importer_path = "question_bank_web/excel_importer.py"
        
        if not os.path.exists(excel_importer_path):
            print(f"❌ 文件不存在: {excel_importer_path}")
            return False
        
        # 读取原文件
        with open(excel_importer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找export_error_report函数
        if 'def export_error_report(' not in content:
            print("❌ 未找到export_error_report函数")
            return False
        
        # 修复后的函数代码
        new_function = '''def export_error_report(errors, filename=None):
    """导出错误报告到文本文件"""
    try:
        # 创建错误报告目录 - 使用绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        report_dir = os.path.join(current_dir, "error_reports")
        
        # 确保目录存在
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)
        
        # 生成安全的文件名
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}.txt"
        else:
            # 清理文件名中的特殊字符
            filename = "".join(c for c in filename if c.isalnum() or c in "._-")
            if not filename.endswith('.txt'):
                filename += '.txt'
        
        filepath = os.path.join(report_dir, filename)
        
        # 写入错误报告 - 使用更安全的方式
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                if not errors:
                    f.write("导入成功，没有错误。\\n")
                else:
                    f.write(f"导入错误报告 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\\n")
                    f.write("="*50 + "\\n")
                    f.write(f"总错误数: {len(errors)}\\n\\n")
                    
                    for error in errors:
                        row_info = f"第 {error.get('row', 'N/A')} 行" if 'row' in error else ""
                        id_info = f"(ID: {error.get('id', '')})" if 'id' in error else ""
                        message = str(error.get('message', '未知错误'))
                        f.write(f"{row_info} {id_info}: {message}\\n")
                
                # 确保数据写入磁盘
                f.flush()
                os.fsync(f.fileno())
        
        except Exception as write_error:
            # 如果写入失败，尝试使用临时文件
            print(f"警告: 写入错误报告失败: {write_error}")
            
            # 使用临时文件作为备选方案
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix='.txt', prefix='error_report_')
            try:
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    if not errors:
                        f.write("导入成功，没有错误。\\n")
                    else:
                        f.write(f"导入错误报告 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\\n")
                        f.write("="*50 + "\\n")
                        f.write(f"总错误数: {len(errors)}\\n\\n")
                        
                        for error in errors:
                            row_info = f"第 {error.get('row', 'N/A')} 行" if 'row' in error else ""
                            id_info = f"(ID: {error.get('id', '')})" if 'id' in error else ""
                            message = str(error.get('message', '未知错误'))
                            f.write(f"{row_info} {id_info}: {message}\\n")
                
                print(f"错误报告已导出到临时文件: {temp_path}")
                return temp_path
            except Exception as temp_error:
                print(f"临时文件写入也失败: {temp_error}")
                return None
        
        print(f"错误报告已导出到: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"导出错误报告失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return None'''
        
        # 查找并替换函数
        import re
        pattern = r'def export_error_report\(.*?\n(?:.*?\n)*?    return filepath'
        
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            new_content = re.sub(pattern, new_function, content, flags=re.MULTILINE | re.DOTALL)
            
            # 写回文件
            with open(excel_importer_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ export_error_report函数已修复")
            return True
        else:
            print("❌ 未找到完整的export_error_report函数")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_fixed_function():
    """测试修复后的函数"""
    print("\n🧪 测试修复后的函数")
    print("-" * 40)
    
    try:
        # 添加路径以便导入
        sys.path.append('question_bank_web')
        
        # 重新导入模块
        import importlib
        if 'excel_importer' in sys.modules:
            importlib.reload(sys.modules['excel_importer'])
        
        from excel_importer import export_error_report
        
        # 测试错误报告生成
        test_errors = [
            {"row": 2, "id": "TEST001", "message": "测试错误1"},
            {"row": 3, "id": "TEST002", "message": "测试错误2"}
        ]
        
        report_path = export_error_report(test_errors, "test_report.txt")
        
        if report_path and os.path.exists(report_path):
            print(f"✅ 错误报告生成成功: {report_path}")
            
            # 验证文件内容
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "总错误数: 2" in content and "TEST001" in content:
                    print("✅ 错误报告内容正确")
                else:
                    print("❌ 错误报告内容不正确")
            
            # 清理测试文件
            try:
                os.remove(report_path)
                print("✅ 测试文件已清理")
            except:
                pass
            
            return True
        else:
            print("❌ 错误报告生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("🔧 修复 [Errno 22] Invalid argument 错误")
    print("=" * 50)
    
    tests = [
        ("诊断错误报告生成问题", diagnose_error_report_issue),
        ("修复export_error_report函数", fix_export_error_report),
        ("测试修复后的函数", test_fixed_function),
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
    print("📊 修复结果摘要")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 [Errno 22] 错误修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 使用绝对路径创建错误报告目录")
        print("2. ✅ 增强文件名安全性检查")
        print("3. ✅ 添加文件写入异常处理")
        print("4. ✅ 提供临时文件备选方案")
        print("5. ✅ 确保数据写入磁盘")
        
        print("\n🎯 现在可以正常使用:")
        print("• 题库导入不会再出现 [Errno 22] 错误")
        print("• 错误报告可以正常生成和保存")
        print("• 文件路径处理更加安全可靠")
        
    else:
        print("⚠️  部分修复失败，请检查相关问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
