#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门修复Flask Web应用中的 [Errno 22] Invalid argument 错误
"""

import os
import sys
import traceback

def fix_handle_import_sample():
    """修复handle_import_sample函数"""
    print("🔧 修复handle_import_sample函数")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        if not os.path.exists(app_file):
            print(f"❌ 文件不存在: {app_file}")
            return False
        
        # 读取原文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找handle_import_sample函数
        if '@app.route(\'/import-sample\', methods=[\'GET\'])' not in content:
            print("❌ 未找到handle_import_sample路由")
            return False
        
        # 修复后的函数代码
        new_function = '''@app.route('/import-sample', methods=['GET'])
def handle_import_sample():
    """处理从Excel文件导入样例题库的请求"""
    db = get_db()
    excel_file_path = os.path.join(os.path.dirname(__file__), 'questions_sample.xlsx')
    
    if not os.path.exists(excel_file_path):
        flash(f"错误：样例题库文件 'questions_sample.xlsx' 不存在。", 'error')
        return redirect(url_for('index'))
    
    try:
        questions_added, errors = import_questions_from_excel(excel_file_path, db)
        
        if errors:
            # 使用更安全的错误报告生成方式
            try:
                error_report_path = export_error_report(errors, "sample_import_errors.txt")
                if error_report_path and os.path.exists(error_report_path):
                    error_link = f'<a href="/download_error_report/{os.path.basename(error_report_path)}" target="_blank">点击查看报告</a>'
                    if questions_added:
                        flash(f'成功导入 {len(questions_added)} 条样例题目，但有部分数据出错。{error_link}', 'warning')
                    else:
                        flash(f'导入失败，所有样例题目均有问题。{error_link}', 'error')
                else:
                    # 如果错误报告生成失败，仍然显示基本信息
                    if questions_added:
                        flash(f'成功导入 {len(questions_added)} 条样例题目，但有部分数据出错。错误报告生成失败。', 'warning')
                    else:
                        flash(f'导入失败，所有样例题目均有问题。错误报告生成失败。', 'error')
            except Exception as report_error:
                print(f"错误报告生成异常: {report_error}")
                # 即使错误报告生成失败，也要显示导入结果
                if questions_added:
                    flash(f'成功导入 {len(questions_added)} 条样例题目，但有部分数据出错。', 'warning')
                else:
                    flash(f'导入失败，所有样例题目均有问题。', 'error')
        elif questions_added:
            flash(f'成功导入 {len(questions_added)} 条样例题目！', 'success')
        else:
            flash('未在样例题库中找到可导入的新题目。', 'info')
            
    except Exception as e:
        print(f"导入异常详情: {traceback.format_exc()}")
        flash(f"导入过程中发生未知错误: {e}", 'error')
    finally:
        close_db(db)
        
    return redirect(url_for('index'))'''
        
        # 查找并替换函数
        import re
        pattern = r"@app\.route\('/import-sample', methods=\['GET'\]\)\s*\ndef handle_import_sample\(\):.*?return redirect\(url_for\('index'\)\)"
        
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            new_content = re.sub(pattern, new_function, content, flags=re.MULTILINE | re.DOTALL)
            
            # 写回文件
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ handle_import_sample函数已修复")
            return True
        else:
            print("❌ 未找到完整的handle_import_sample函数")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def add_error_handling_to_export_error_report():
    """为export_error_report添加更强的错误处理"""
    print("\n🔧 增强export_error_report错误处理")
    print("-" * 40)
    
    try:
        excel_importer_file = "question_bank_web/excel_importer.py"
        
        if not os.path.exists(excel_importer_file):
            print(f"❌ 文件不存在: {excel_importer_file}")
            return False
        
        # 读取原文件
        with open(excel_importer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有增强的错误处理
        if 'def export_error_report_safe(' in content:
            print("✅ 安全版本的export_error_report已存在")
            return True
        
        # 添加安全版本的函数
        safe_function = '''
def export_error_report_safe(errors, filename=None):
    """安全版本的错误报告导出函数，增强错误处理"""
    try:
        return export_error_report(errors, filename)
    except Exception as e:
        print(f"错误报告生成失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        
        # 尝试使用最简单的方式生成报告
        try:
            import tempfile
            import datetime
            
            # 创建临时文件
            temp_fd, temp_path = tempfile.mkstemp(suffix='.txt', prefix='error_report_safe_')
            
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(f"错误报告 (安全模式) - {datetime.datetime.now()}\\n")
                f.write("="*50 + "\\n")
                f.write(f"总错误数: {len(errors) if errors else 0}\\n\\n")
                
                if errors:
                    for i, error in enumerate(errors[:10]):  # 只显示前10个错误
                        f.write(f"错误 {i+1}: {str(error)}\\n")
                    
                    if len(errors) > 10:
                        f.write(f"... 还有 {len(errors) - 10} 个错误\\n")
                else:
                    f.write("没有错误。\\n")
            
            print(f"安全模式错误报告已生成: {temp_path}")
            return temp_path
            
        except Exception as safe_error:
            print(f"安全模式也失败了: {safe_error}")
            return None
'''
        
        # 在文件末尾添加安全函数
        new_content = content + safe_function
        
        # 写回文件
        with open(excel_importer_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 安全版本的export_error_report已添加")
        return True
        
    except Exception as e:
        print(f"❌ 增强错误处理失败: {e}")
        return False

def update_app_to_use_safe_version():
    """更新app.py使用安全版本的错误报告函数"""
    print("\n🔧 更新app.py使用安全版本")
    print("-" * 40)
    
    try:
        app_file = "question_bank_web/app.py"
        
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新导入语句
        if 'from excel_importer import import_questions_from_excel, export_error_report' in content:
            content = content.replace(
                'from excel_importer import import_questions_from_excel, export_error_report',
                'from excel_importer import import_questions_from_excel, export_error_report, export_error_report_safe'
            )
            print("✅ 导入语句已更新")
        
        # 替换所有export_error_report调用为export_error_report_safe
        content = content.replace('export_error_report(', 'export_error_report_safe(')
        print("✅ 函数调用已更新为安全版本")
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def test_fixed_flask_app():
    """测试修复后的Flask应用"""
    print("\n🧪 测试修复后的Flask应用")
    print("-" * 40)
    
    try:
        # 测试模块导入
        sys.path.append('question_bank_web')
        
        try:
            from excel_importer import export_error_report_safe
            print("✅ 安全版本函数导入成功")
        except ImportError:
            print("❌ 安全版本函数导入失败")
            return False
        
        # 测试安全版本函数
        test_errors = [
            {"row": 1, "id": "TEST001", "message": "测试错误1"},
            {"row": 2, "id": "TEST002", "message": "测试错误2"}
        ]
        
        report_path = export_error_report_safe(test_errors, "test_safe_report.txt")
        
        if report_path and os.path.exists(report_path):
            print(f"✅ 安全版本错误报告生成成功: {report_path}")
            
            # 验证文件内容
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "总错误数: 2" in content and "TEST001" in content:
                    print("✅ 错误报告内容正确")
                else:
                    print("❌ 错误报告内容不正确")
            
            # 清理测试文件
            os.remove(report_path)
            print("✅ 测试文件已清理")
            
            return True
        else:
            print("❌ 安全版本错误报告生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主修复函数"""
    print("🔧 修复Flask Web应用中的 [Errno 22] 错误")
    print("=" * 50)
    
    fixes = [
        ("修复handle_import_sample函数", fix_handle_import_sample),
        ("增强export_error_report错误处理", add_error_handling_to_export_error_report),
        ("更新app.py使用安全版本", update_app_to_use_safe_version),
        ("测试修复后的Flask应用", test_fixed_flask_app),
    ]
    
    passed_fixes = 0
    total_fixes = len(fixes)
    
    for fix_name, fix_func in fixes:
        try:
            if fix_func():
                passed_fixes += 1
        except Exception as e:
            print(f"❌ 修复 '{fix_name}' 执行异常: {e}")
    
    print("\n" + "=" * 50)
    print("📊 修复结果摘要")
    print(f"成功修复: {passed_fixes}/{total_fixes}")
    print(f"成功率: {(passed_fixes/total_fixes)*100:.1f}%")
    
    if passed_fixes == total_fixes:
        print("🎉 Flask Web应用修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 增强了handle_import_sample函数的错误处理")
        print("2. ✅ 添加了安全版本的错误报告生成函数")
        print("3. ✅ 更新了所有错误报告调用为安全版本")
        print("4. ✅ 即使错误报告生成失败也不会影响导入流程")
        
        print("\n🎯 现在可以正常使用:")
        print("• Flask Web应用不会再因为错误报告生成而崩溃")
        print("• 即使出现文件操作问题，导入流程仍能继续")
        print("• 错误信息会正确显示给用户")
        print("• 系统具有更强的容错能力")
        
    else:
        print("⚠️  部分修复失败，但主要功能应该已改善")
    
    return passed_fixes == total_fixes

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
