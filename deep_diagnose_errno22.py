#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度诊断 [Errno 22] Invalid argument 错误
"""

import os
import sys
import traceback
import tempfile
from pathlib import Path

def test_file_operations():
    """测试各种文件操作"""
    print("🔍 测试各种文件操作")
    print("-" * 40)
    
    try:
        # 测试1: 基本文件路径
        test_paths = [
            "question_bank_web/questions_sample.xlsx",
            os.path.join("question_bank_web", "questions_sample.xlsx"),
            os.path.abspath(os.path.join("question_bank_web", "questions_sample.xlsx")),
        ]
        
        for i, path in enumerate(test_paths):
            print(f"测试路径 {i+1}: {path}")
            try:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        data = f.read(100)
                    print(f"  ✅ 可以读取，前100字节长度: {len(data)}")
                else:
                    print(f"  ❌ 文件不存在")
            except Exception as e:
                print(f"  ❌ 读取失败: {e}")
        
        # 测试2: 错误报告目录创建
        print("\n测试错误报告目录:")
        report_dirs = [
            "question_bank_web/error_reports",
            os.path.join("question_bank_web", "error_reports"),
            os.path.abspath(os.path.join("question_bank_web", "error_reports")),
        ]
        
        for i, dir_path in enumerate(report_dirs):
            print(f"测试目录 {i+1}: {dir_path}")
            try:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                print(f"  ✅ 目录创建/存在成功")
                
                # 测试在该目录中创建文件
                test_file = os.path.join(dir_path, f"test_{i+1}.txt")
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write("测试内容")
                print(f"  ✅ 文件创建成功: {os.path.basename(test_file)}")
                
                # 清理测试文件
                os.remove(test_file)
                print(f"  ✅ 文件清理成功")
                
            except Exception as e:
                print(f"  ❌ 操作失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False

def test_import_function_step_by_step():
    """逐步测试导入函数"""
    print("\n🔍 逐步测试导入函数")
    print("-" * 40)
    
    try:
        # 添加路径
        sys.path.append('question_bank_web')
        
        # 步骤1: 测试模块导入
        print("步骤1: 测试模块导入")
        try:
            from excel_importer import import_questions_from_excel, export_error_report
            from models import Base, Question, QuestionBank
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            print("  ✅ 模块导入成功")
        except Exception as e:
            print(f"  ❌ 模块导入失败: {e}")
            return False
        
        # 步骤2: 测试文件路径
        print("步骤2: 测试文件路径")
        excel_file = 'question_bank_web/questions_sample.xlsx'
        if os.path.exists(excel_file):
            print(f"  ✅ 样例文件存在: {excel_file}")
            print(f"  文件大小: {os.path.getsize(excel_file)} 字节")
        else:
            print(f"  ❌ 样例文件不存在: {excel_file}")
            return False
        
        # 步骤3: 测试数据库创建
        print("步骤3: 测试数据库创建")
        try:
            engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            session = Session()
            print("  ✅ 内存数据库创建成功")
        except Exception as e:
            print(f"  ❌ 数据库创建失败: {e}")
            return False
        
        # 步骤4: 测试pandas读取
        print("步骤4: 测试pandas读取")
        try:
            import pandas as pd
            df = pd.read_excel(excel_file, dtype=str)
            print(f"  ✅ pandas读取成功，行数: {len(df)}")
        except Exception as e:
            print(f"  ❌ pandas读取失败: {e}")
            return False
        
        # 步骤5: 测试导入函数（但捕获所有异常）
        print("步骤5: 测试导入函数")
        try:
            questions_added, errors = import_questions_from_excel(excel_file, session)
            print(f"  ✅ 导入函数执行完成")
            print(f"  添加题目: {len(questions_added) if questions_added else 0}")
            print(f"  错误数量: {len(errors) if errors else 0}")
            
            # 步骤6: 测试错误报告生成（如果有错误）
            if errors:
                print("步骤6: 测试错误报告生成")
                try:
                    report_path = export_error_report(errors, "deep_test_errors.txt")
                    if report_path:
                        print(f"  ✅ 错误报告生成成功: {report_path}")
                        # 清理测试文件
                        if os.path.exists(report_path):
                            os.remove(report_path)
                            print(f"  ✅ 测试报告已清理")
                    else:
                        print(f"  ❌ 错误报告生成失败")
                        return False
                except Exception as e:
                    print(f"  ❌ 错误报告生成异常: {e}")
                    print(f"  错误详情: {traceback.format_exc()}")
                    return False
            
        except Exception as e:
            print(f"  ❌ 导入函数执行失败: {e}")
            print(f"  错误详情: {traceback.format_exc()}")
            return False
        
        finally:
            session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 逐步测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_flask_app_simulation():
    """模拟Flask应用的导入流程"""
    print("\n🔍 模拟Flask应用导入流程")
    print("-" * 40)
    
    try:
        # 模拟Flask应用的导入流程
        sys.path.append('question_bank_web')
        
        # 模拟get_db函数
        from models import Base, Question, QuestionBank
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        print("✅ 模拟数据库会话创建成功")
        
        # 模拟handle_import_sample函数的逻辑
        excel_file_path = os.path.join(os.path.dirname('question_bank_web/app.py'), 'questions_sample.xlsx')
        print(f"文件路径: {excel_file_path}")
        
        if not os.path.exists(excel_file_path):
            print(f"❌ 样例题库文件不存在: {excel_file_path}")
            return False
        
        print("✅ 样例题库文件存在")
        
        # 执行导入
        from excel_importer import import_questions_from_excel, export_error_report
        
        print("正在执行导入...")
        questions_added, errors = import_questions_from_excel(excel_file_path, db)
        
        print(f"导入结果: 添加 {len(questions_added) if questions_added else 0} 个题目")
        print(f"错误数量: {len(errors) if errors else 0}")
        
        # 如果有错误，测试错误报告生成
        if errors:
            print("测试错误报告生成...")
            try:
                error_report_path = export_error_report(errors, "sample_import_errors.txt")
                if error_report_path:
                    print(f"✅ 错误报告生成成功: {error_report_path}")
                    
                    # 测试文件是否真的存在和可读
                    if os.path.exists(error_report_path):
                        with open(error_report_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        print(f"✅ 错误报告文件可读，内容长度: {len(content)}")
                        
                        # 清理测试文件
                        os.remove(error_report_path)
                        print("✅ 测试错误报告已清理")
                    else:
                        print(f"❌ 错误报告文件不存在: {error_report_path}")
                        return False
                else:
                    print("❌ 错误报告生成返回None")
                    return False
                    
            except Exception as e:
                print(f"❌ 错误报告生成失败: {e}")
                print(f"错误详情: {traceback.format_exc()}")
                return False
        
        db.close()
        print("✅ Flask应用模拟测试完成")
        return True
        
    except Exception as e:
        print(f"❌ Flask应用模拟测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_windows_specific_issues():
    """测试Windows特定问题"""
    print("\n🔍 测试Windows特定问题")
    print("-" * 40)
    
    try:
        # 测试路径分隔符
        print("测试路径分隔符:")
        paths = [
            "question_bank_web/questions_sample.xlsx",
            "question_bank_web\\questions_sample.xlsx",
            os.path.join("question_bank_web", "questions_sample.xlsx"),
        ]
        
        for path in paths:
            print(f"  路径: {path}")
            print(f"  标准化: {os.path.normpath(path)}")
            print(f"  存在: {os.path.exists(path)}")
        
        # 测试文件名中的特殊字符
        print("\n测试文件名特殊字符:")
        test_names = [
            "sample_import_errors.txt",
            "sample_import_errors_测试.txt",
            "sample_import_errors_2024.txt",
        ]
        
        report_dir = "question_bank_web/error_reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)
        
        for name in test_names:
            try:
                test_path = os.path.join(report_dir, name)
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write("测试内容")
                print(f"  ✅ 文件名可用: {name}")
                os.remove(test_path)
            except Exception as e:
                print(f"  ❌ 文件名有问题: {name} - {e}")
        
        # 测试长路径
        print("\n测试长路径:")
        long_name = "a" * 100 + ".txt"
        try:
            long_path = os.path.join(report_dir, long_name)
            with open(long_path, 'w', encoding='utf-8') as f:
                f.write("测试")
            print(f"  ✅ 长路径可用，长度: {len(long_path)}")
            os.remove(long_path)
        except Exception as e:
            print(f"  ❌ 长路径有问题: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Windows特定问题测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 深度诊断 [Errno 22] Invalid argument 错误")
    print("=" * 50)
    
    tests = [
        ("文件操作测试", test_file_operations),
        ("逐步导入函数测试", test_import_function_step_by_step),
        ("Flask应用模拟测试", test_flask_app_simulation),
        ("Windows特定问题测试", test_windows_specific_issues),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行异常: {e}")
            print(f"异常详情: {traceback.format_exc()}")
    
    print("\n" + "=" * 50)
    print("📊 深度诊断结果")
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！问题可能在其他地方")
    else:
        print("⚠️  发现问题，请根据上述测试结果进行分析")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
