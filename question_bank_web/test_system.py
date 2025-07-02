#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理系统测试脚本
"""

import os
import sys
import pandas as pd
from datetime import datetime

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        from app import get_db, close_db
        from models import Question
        
        db = get_db()
        count = db.query(Question).count()
        print(f"✅ 数据库连接成功，当前题目数量: {count}")
        close_db(db)
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_excel_import():
    """测试Excel导入功能"""
    print("\n🔍 测试Excel导入功能...")
    try:
        from excel_importer import import_questions_from_excel
        
        # 创建测试数据
        test_data = {
            'ID': ['TEST-001-001', 'TEST-001-002'],
            '序号': ['1', '2'],
            '认定点代码': ['001', '001'],
            '题型代码': ['B（单选题）', 'C（判断题）'],
            '题号': ['T001', 'T002'],
            '试题（题干）': ['这是一个测试单选题', '这是一个测试判断题'],
            '试题（选项A）': ['选项A1', ''],
            '试题（选项B）': ['选项B1', ''],
            '试题（选项C）': ['选项C1', ''],
            '试题（选项D）': ['选项D1', ''],
            '试题（选项E）': ['', ''],
            '【图】及位置': ['', ''],
            '正确答案': ['A', '正确'],
            '难度代码': ['3（中等）', '2（简单）'],
            '一致性代码': ['4（高）', '3（中等）'],
            '解析': ['解析1', '解析2']
        }
        
        test_df = pd.DataFrame(test_data)
        test_file = 'test_questions.xlsx'
        test_df.to_excel(test_file, index=False)
        
        # 测试导入
        questions, errors = import_questions_from_excel(test_file)
        
        print(f"✅ Excel导入测试成功")
        print(f"   导入题目数: {len(questions)}")
        print(f"   错误数量: {len(errors)}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"❌ Excel导入测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n🔍 测试文件结构...")
    
    required_files = [
        'app.py',
        'models.py', 
        'excel_importer.py',
        'requirements.txt',
        'run.py'
    ]
    
    required_dirs = [
        'uploads',
        'templates',
        'error_reports'
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 缺失")
            all_good = False
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - 缺失或不是目录")
            all_good = False
    
    return all_good

def test_dependencies():
    """测试依赖包"""
    print("\n🔍 测试依赖包...")
    
    required_packages = [
        'flask',
        'sqlalchemy',
        'pandas',
        'openpyxl',
        'werkzeug'
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            all_good = False
    
    return all_good

def test_template_download():
    """测试模板下载功能"""
    print("\n🔍 测试模板下载功能...")
    try:
        from create_template import create_question_bank_template
        
        # 测试模板生成
        template_path = create_question_bank_template()
        
        if os.path.exists(template_path):
            print(f"✅ 模板下载功能测试成功")
            print(f"   模板文件: {template_path}")
            print(f"   文件大小: {os.path.getsize(template_path)} bytes")
            return True
        else:
            print(f"❌ 模板文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 模板下载功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 题库管理系统测试")
    print("=" * 50)
    
    tests = [
        ("文件结构", test_file_structure),
        ("依赖包", test_dependencies),
        ("数据库连接", test_database_connection),
        ("Excel导入", test_excel_import),
        ("模板下载", test_template_download)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 