#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试样例题库导入错误脚本
"""

import os
import sys
import traceback
import sqlite3
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'question_bank_web'))

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接")
    print("-" * 40)
    
    db_path = os.path.join('question_bank_web', 'questions.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ 数据库连接成功，包含表: {[t[0] for t in tables]}")
        
        # 检查题库表
        cursor.execute("SELECT COUNT(*) FROM question_banks;")
        bank_count = cursor.fetchone()[0]
        print(f"✅ 题库表包含 {bank_count} 个题库")
        
        # 检查题目表
        cursor.execute("SELECT COUNT(*) FROM questions;")
        question_count = cursor.fetchone()[0]
        print(f"✅ 题目表包含 {question_count} 个题目")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        traceback.print_exc()
        return False

def test_excel_file():
    """测试Excel文件"""
    print("\n🔍 测试Excel文件")
    print("-" * 40)
    
    excel_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel文件不存在: {excel_path}")
        return False
    
    try:
        df = pd.read_excel(excel_path, dtype=str)
        df = df.fillna('')
        
        print(f"✅ Excel文件读取成功")
        print(f"  行数: {len(df)}")
        print(f"  列数: {len(df.columns)}")
        print(f"  列名: {list(df.columns)}")
        
        # 检查必需列
        required_cols = ['ID', '题库名称', '题型代码', '试题（题干）', '正确答案', '难度代码']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ 缺少必需列: {missing_cols}")
            return False
        else:
            print(f"✅ 所有必需列都存在")
        
        # 检查数据样本
        if len(df) > 0:
            print(f"✅ 数据样本:")
            sample_row = df.iloc[0]
            for col in required_cols:
                print(f"  {col}: {sample_row[col]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel文件读取失败: {e}")
        traceback.print_exc()
        return False

def test_import_function():
    """测试导入函数"""
    print("\n🔍 测试导入函数")
    print("-" * 40)
    
    try:
        from excel_importer import import_questions_from_excel
        from models import get_db, close_db
        
        print("✅ 导入函数模块加载成功")
        
        # 获取数据库连接
        db = get_db()
        excel_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        
        print("🔄 开始测试导入...")
        questions_added, errors = import_questions_from_excel(excel_path, db)
        
        print(f"✅ 导入测试完成")
        print(f"  添加题目数: {len(questions_added) if questions_added else 0}")
        print(f"  错误数: {len(errors) if errors else 0}")
        
        if errors:
            print("❌ 导入错误详情:")
            for i, error in enumerate(errors[:5]):  # 只显示前5个错误
                print(f"  {i+1}. {error}")
        
        close_db(db)
        return True
        
    except Exception as e:
        print(f"❌ 导入函数测试失败: {e}")
        traceback.print_exc()
        return False

def test_flask_app():
    """测试Flask应用"""
    print("\n🔍 测试Flask应用")
    print("-" * 40)
    
    try:
        # 设置Flask测试环境
        os.environ['FLASK_ENV'] = 'testing'
        
        from app import app
        
        with app.test_client() as client:
            print("✅ Flask应用创建成功")
            
            # 测试主页
            response = client.get('/')
            print(f"✅ 主页访问: {response.status_code}")
            
            # 测试导入样例路由
            response = client.get('/import-sample')
            print(f"✅ 导入样例路由: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ 导入样例路由返回500错误")
                # 尝试获取错误信息
                if hasattr(response, 'data'):
                    print(f"错误响应: {response.data.decode('utf-8')[:500]}")
                return False
            
        return True
        
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        traceback.print_exc()
        return False

def test_app_route_directly():
    """直接测试应用路由"""
    print("\n🔍 直接测试应用路由")
    print("-" * 40)
    
    try:
        # 模拟Flask路由逻辑
        from models import get_db, close_db
        from excel_importer import import_questions_from_excel
        
        print("✅ 模块导入成功")
        
        # 模拟路由逻辑
        db = get_db()
        excel_file_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        
        if not os.path.exists(excel_file_path):
            print(f"❌ 样例题库文件不存在: {excel_file_path}")
            return False
        
        print("🔄 开始模拟导入过程...")
        
        # 执行导入
        questions_added, errors = import_questions_from_excel(excel_file_path, db)
        
        print(f"✅ 模拟导入完成")
        print(f"  添加题目: {len(questions_added) if questions_added else 0}")
        print(f"  错误数量: {len(errors) if errors else 0}")
        
        if errors:
            print("⚠️ 导入错误:")
            for i, error in enumerate(errors[:3]):
                print(f"  {i+1}. {error}")
        
        close_db(db)
        return True
        
    except Exception as e:
        print(f"❌ 直接路由测试失败: {e}")
        traceback.print_exc()
        return False

def check_app_py_issues():
    """检查app.py中的问题"""
    print("\n🔍 检查app.py中的问题")
    print("-" * 40)
    
    app_path = os.path.join('question_bank_web', 'app.py')
    
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查重复的代码块
        import_sample_count = content.count('@app.route(\'/import-sample\'')
        print(f"✅ /import-sample 路由定义次数: {import_sample_count}")
        
        if import_sample_count > 1:
            print("❌ 发现重复的路由定义！")
            
            # 找到重复的位置
            lines = content.split('\n')
            route_lines = []
            for i, line in enumerate(lines):
                if '@app.route(\'/import-sample\'' in line:
                    route_lines.append(i + 1)
            
            print(f"重复路由位置: 行 {route_lines}")
            return False
        
        # 检查语法错误
        try:
            compile(content, app_path, 'exec')
            print("✅ app.py 语法检查通过")
        except SyntaxError as e:
            print(f"❌ app.py 语法错误: {e}")
            print(f"  行 {e.lineno}: {e.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 检查app.py失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 样例题库导入错误调试")
    print("=" * 50)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("Excel文件", test_excel_file),
        ("app.py问题检查", check_app_py_issues),
        ("导入函数", test_import_function),
        ("直接路由测试", test_app_route_directly),
        ("Flask应用", test_flask_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 发生异常: {e}")
            results.append((test_name, False))
    
    print("\n📊 测试结果汇总")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count < len(results):
        print("\n🔧 建议的修复步骤:")
        print("1. 检查并修复app.py中的重复路由定义")
        print("2. 确保数据库文件存在且可访问")
        print("3. 验证Excel文件格式和内容")
        print("4. 检查导入函数的异常处理")
        print("5. 重启Flask应用服务")
    else:
        print("\n🎉 所有测试通过！问题可能是临时的。")

if __name__ == '__main__':
    main()
