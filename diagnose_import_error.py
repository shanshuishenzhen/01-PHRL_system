#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断题库导入错误的脚本
"""

import os
import sys
import pandas as pd
import traceback
from pathlib import Path

def test_file_access():
    """测试文件访问"""
    print("🔍 测试1: 文件访问检查")
    print("-" * 40)
    
    try:
        # 检查文件路径
        excel_file_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        print(f"文件路径: {excel_file_path}")
        
        # 检查文件是否存在
        if os.path.exists(excel_file_path):
            print("✅ 文件存在")
        else:
            print("❌ 文件不存在")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(excel_file_path)
        print(f"✅ 文件大小: {file_size} 字节")
        
        # 检查文件权限
        if os.access(excel_file_path, os.R_OK):
            print("✅ 文件可读")
        else:
            print("❌ 文件不可读")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 文件访问测试失败: {e}")
        return False

def test_pandas_read():
    """测试pandas读取"""
    print("\n🔍 测试2: Pandas读取检查")
    print("-" * 40)
    
    try:
        excel_file_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        
        # 尝试读取Excel文件
        print("正在尝试读取Excel文件...")
        df = pd.read_excel(excel_file_path, dtype=str)
        print(f"✅ 成功读取Excel文件，共 {len(df)} 行")
        
        # 检查列名
        print(f"✅ 列名: {list(df.columns)}")
        
        # 检查是否有必要的列
        required_cols = ['ID', '题库名称', '题型代码', '试题（题干）', '正确答案', '难度代码']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ 缺少必要列: {missing_cols}")
            return False
        else:
            print("✅ 所有必要列都存在")
        
        # 检查前几行数据
        print("\n前3行数据预览:")
        for i, row in df.head(3).iterrows():
            print(f"行 {i}: ID={row.get('ID', 'N/A')}, 题库名称={row.get('题库名称', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pandas读取失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_path_encoding():
    """测试路径编码"""
    print("\n🔍 测试3: 路径编码检查")
    print("-" * 40)
    
    try:
        excel_file_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        
        # 检查路径编码
        print(f"原始路径: {excel_file_path}")
        print(f"路径类型: {type(excel_file_path)}")
        
        # 尝试不同的路径表示方法
        abs_path = os.path.abspath(excel_file_path)
        print(f"绝对路径: {abs_path}")
        
        # 使用pathlib
        path_obj = Path(excel_file_path)
        print(f"Pathlib路径: {path_obj}")
        print(f"Pathlib绝对路径: {path_obj.absolute()}")
        
        # 检查路径中的特殊字符
        if any(ord(c) > 127 for c in excel_file_path):
            print("⚠️  路径包含非ASCII字符")
        else:
            print("✅ 路径只包含ASCII字符")
        
        return True
        
    except Exception as e:
        print(f"❌ 路径编码测试失败: {e}")
        return False

def test_alternative_read_methods():
    """测试替代读取方法"""
    print("\n🔍 测试4: 替代读取方法")
    print("-" * 40)
    
    try:
        excel_file_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        
        # 方法1: 使用openpyxl引擎
        try:
            print("尝试使用openpyxl引擎...")
            df1 = pd.read_excel(excel_file_path, engine='openpyxl', dtype=str)
            print(f"✅ openpyxl引擎成功，读取 {len(df1)} 行")
        except Exception as e:
            print(f"❌ openpyxl引擎失败: {e}")
        
        # 方法2: 使用二进制模式
        try:
            print("尝试使用二进制模式...")
            with open(excel_file_path, 'rb') as f:
                df2 = pd.read_excel(f, dtype=str)
            print(f"✅ 二进制模式成功，读取 {len(df2)} 行")
        except Exception as e:
            print(f"❌ 二进制模式失败: {e}")
        
        # 方法3: 使用绝对路径
        try:
            print("尝试使用绝对路径...")
            abs_path = os.path.abspath(excel_file_path)
            df3 = pd.read_excel(abs_path, dtype=str)
            print(f"✅ 绝对路径成功，读取 {len(df3)} 行")
        except Exception as e:
            print(f"❌ 绝对路径失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 替代读取方法测试失败: {e}")
        return False

def test_import_function():
    """测试导入函数"""
    print("\n🔍 测试5: 导入函数测试")
    print("-" * 40)
    
    try:
        # 导入必要模块
        sys.path.append('question_bank_web')
        from excel_importer import import_questions_from_excel
        from models import Base, Question, QuestionBank
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        print("✅ 模块导入成功")
        
        # 创建测试数据库会话
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ 测试数据库创建成功")
        
        # 测试导入函数
        excel_file_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        questions_added, errors = import_questions_from_excel(excel_file_path, session)
        
        print(f"✅ 导入函数执行完成")
        print(f"添加的题目数量: {len(questions_added) if questions_added else 0}")
        print(f"错误数量: {len(errors) if errors else 0}")
        
        if errors:
            print("错误详情:")
            for i, error in enumerate(errors[:3]):  # 只显示前3个错误
                print(f"  错误 {i+1}: {error}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 导入函数测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🔧 题库导入错误诊断")
    print("=" * 50)
    
    tests = [
        ("文件访问检查", test_file_access),
        ("Pandas读取检查", test_pandas_read),
        ("路径编码检查", test_path_encoding),
        ("替代读取方法", test_alternative_read_methods),
        ("导入函数测试", test_import_function),
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
    print("📊 诊断结果摘要")
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！问题可能在其他地方")
    else:
        print("⚠️  发现问题，请根据上述测试结果进行修复")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
