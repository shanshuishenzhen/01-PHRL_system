#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试开发工具生成第2个题库的错误
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'developer_tools'))

def test_database_models():
    """测试数据库模型导入"""
    print("🔍 测试数据库模型导入")
    print("-" * 40)
    
    try:
        from models import QuestionBank, Question, get_db, close_db
        print("✅ 数据库模型导入成功")
        
        # 测试数据库连接
        db = get_db()
        print("✅ 数据库连接成功")
        
        # 检查现有题库
        banks = db.query(QuestionBank).all()
        print(f"✅ 当前题库数量: {len(banks)}")
        for bank in banks:
            question_count = db.query(Question).filter(Question.question_bank_id == bank.id).count()
            print(f"  - {bank.name}: {question_count} 个题目")
        
        close_db(db)
        return True
        
    except Exception as e:
        print(f"❌ 数据库模型导入失败: {e}")
        traceback.print_exc()
        return False

def test_question_generator_import():
    """测试题库生成器导入"""
    print("\n🔍 测试题库生成器导入")
    print("-" * 40)
    
    try:
        from question_bank_generator import generate_from_excel, save_to_question_bank_db
        print("✅ 题库生成器导入成功")
        
        # 测试数据库集成状态
        from question_bank_generator import DB_INTEGRATION_AVAILABLE
        print(f"✅ 数据库集成状态: {DB_INTEGRATION_AVAILABLE}")
        
        return True
        
    except Exception as e:
        print(f"❌ 题库生成器导入失败: {e}")
        traceback.print_exc()
        return False

def test_save_to_database_function():
    """测试保存到数据库函数"""
    print("\n🔍 测试保存到数据库函数")
    print("-" * 40)
    
    try:
        from question_bank_generator import save_to_question_bank_db
        
        # 创建测试题目数据
        test_questions = [
            {
                "id": "TEST-001-001-001",
                "stem": "这是一个测试题目",
                "type": "B",
                "type_name": "单选题",
                "options": [
                    {"key": "A", "text": "选项A"},
                    {"key": "B", "text": "选项B"},
                    {"key": "C", "text": "选项C"},
                    {"key": "D", "text": "选项D"}
                ],
                "answer": "A",
                "difficulty": 0.5,
                "explanation": "这是测试解析"
            }
        ]
        
        # 测试保存
        print("🔄 测试保存到数据库...")
        success, message = save_to_question_bank_db("测试题库_DEBUG", test_questions)
        
        if success:
            print(f"✅ 保存成功: {message}")
        else:
            print(f"❌ 保存失败: {message}")
        
        return success
        
    except Exception as e:
        print(f"❌ 保存到数据库函数测试失败: {e}")
        traceback.print_exc()
        return False

def test_second_bank_generation():
    """测试生成第2个题库"""
    print("\n🔍 测试生成第2个题库")
    print("-" * 40)
    
    try:
        from question_bank_generator import generate_from_excel
        
        # 检查模板文件
        template_path = os.path.join('developer_tools', '样例题组题规则模板.xlsx')
        if not os.path.exists(template_path):
            print(f"❌ 模板文件不存在: {template_path}")
            return False
        
        print(f"✅ 模板文件存在: {template_path}")
        
        # 设置输出路径
        output_path = os.path.join('question_bank_web', 'questions_sample.xlsx')
        
        # 检查是否已存在题库文件
        if os.path.exists(output_path):
            print(f"✅ 现有题库文件存在: {output_path}")
            
            # 读取现有文件查看内容
            try:
                df = pd.read_excel(output_path)
                existing_banks = df['题库名称'].unique() if '题库名称' in df.columns else []
                print(f"✅ 现有题库: {list(existing_banks)}")
                print(f"✅ 现有题目数量: {len(df)}")
            except Exception as e:
                print(f"⚠️ 读取现有文件失败: {e}")
        
        # 测试增量生成（第2个题库）
        print("\n🔄 开始测试增量生成...")
        
        try:
            result = generate_from_excel(template_path, output_path, append_mode=True)
            
            if len(result) == 3:
                total_generated, bank_name, db_success = result
                print(f"✅ 生成完成")
                print(f"  题库名称: {bank_name}")
                print(f"  生成题目数: {total_generated}")
                print(f"  数据库保存: {'成功' if db_success else '失败'}")
            else:
                total_generated, bank_name = result
                print(f"✅ 生成完成")
                print(f"  题库名称: {bank_name}")
                print(f"  生成题目数: {total_generated}")
            
            return True
            
        except Exception as e:
            print(f"❌ 增量生成失败: {e}")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 第2个题库生成测试失败: {e}")
        traceback.print_exc()
        return False

def test_flask_import_route():
    """测试Flask导入路由"""
    print("\n🔍 测试Flask导入路由")
    print("-" * 40)
    
    try:
        # 设置Flask测试环境
        os.environ['FLASK_ENV'] = 'testing'
        
        from app import app
        
        with app.test_client() as client:
            print("✅ Flask应用创建成功")
            
            # 测试导入样例路由
            print("🔄 测试导入样例路由...")
            response = client.get('/import-sample')
            
            print(f"✅ 导入样例路由响应: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ 导入样例路由返回500错误")
                if hasattr(response, 'data'):
                    error_text = response.data.decode('utf-8')
                    print(f"错误详情: {error_text[:500]}")
                return False
            elif response.status_code == 302:
                print("✅ 导入样例路由正常重定向")
                return True
            else:
                print(f"⚠️ 导入样例路由返回状态码: {response.status_code}")
                return True
        
    except Exception as e:
        print(f"❌ Flask导入路由测试失败: {e}")
        traceback.print_exc()
        return False

def test_database_constraints():
    """测试数据库约束"""
    print("\n🔍 测试数据库约束")
    print("-" * 40)
    
    try:
        from models import get_db, close_db, Question, QuestionBank
        
        db = get_db()
        
        # 检查数据库表结构
        print("✅ 检查数据库表结构...")
        
        # 检查题库表
        banks = db.query(QuestionBank).all()
        print(f"✅ 题库表记录数: {len(banks)}")
        
        # 检查题目表
        questions = db.query(Question).all()
        print(f"✅ 题目表记录数: {len(questions)}")
        
        # 检查是否有重复ID
        question_ids = [q.id for q in questions]
        unique_ids = set(question_ids)
        
        if len(question_ids) == len(unique_ids):
            print("✅ 题目ID无重复")
        else:
            duplicate_count = len(question_ids) - len(unique_ids)
            print(f"⚠️ 发现 {duplicate_count} 个重复题目ID")
        
        # 检查外键约束
        orphaned_questions = db.query(Question).filter(~Question.question_bank_id.in_(
            db.query(QuestionBank.id)
        )).count()
        
        if orphaned_questions == 0:
            print("✅ 外键约束正常，无孤立题目")
        else:
            print(f"⚠️ 发现 {orphaned_questions} 个孤立题目")
        
        close_db(db)
        return True
        
    except Exception as e:
        print(f"❌ 数据库约束测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 开发工具生成第2个题库错误调试")
    print("=" * 60)
    
    tests = [
        ("数据库模型导入", test_database_models),
        ("题库生成器导入", test_question_generator_import),
        ("保存到数据库函数", test_save_to_database_function),
        ("数据库约束检查", test_database_constraints),
        ("Flask导入路由", test_flask_import_route),
        ("第2个题库生成", test_second_bank_generation),
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
    print("=" * 60)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count < len(results):
        print("\n🔧 建议的修复步骤:")
        print("1. 检查数据库模型和连接")
        print("2. 验证题库生成器的数据库集成")
        print("3. 检查Flask应用的导入路由")
        print("4. 验证数据库约束和外键关系")
        print("5. 测试增量生成模式")
    else:
        print("\n🎉 所有测试通过！问题可能是临时的。")

if __name__ == '__main__':
    main()
