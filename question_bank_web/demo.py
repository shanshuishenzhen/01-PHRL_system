#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理系统功能演示脚本
"""

import os
import sys
import pandas as pd
from datetime import datetime

def demo_template_generation():
    """演示模板生成功能"""
    print("🎬 演示1: 模板生成功能")
    print("-" * 40)
    
    try:
        from create_template import create_question_bank_template
        
        print("📋 正在生成题库模板...")
        template_path = create_question_bank_template()
        
        if os.path.exists(template_path):
            file_size = os.path.getsize(template_path)
            print(f"✅ 模板生成成功!")
            print(f"📁 文件路径: {template_path}")
            print(f"📊 文件大小: {file_size} bytes")
            print(f"🕒 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ 模板生成失败")
            
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_excel_import():
    """演示Excel导入功能"""
    print("\n🎬 演示2: Excel导入功能")
    print("-" * 40)
    
    try:
        from excel_importer import import_questions_from_excel
        
        # 创建测试数据
        test_data = {
            'ID': ['DEMO-001-001', 'DEMO-001-002', 'DEMO-001-003'],
            '序号': ['1', '2', '3'],
            '认定点代码': ['001', '001', '001'],
            '题型代码': ['B（单选题）', 'G（多选题）', 'C（判断题）'],
            '题号': ['D001', 'D002', 'D003'],
            '试题（题干）': [
                '演示单选题：1+1等于多少？',
                '演示多选题：以下哪些是编程语言？',
                '演示判断题：Python是一种编程语言。'
            ],
            '试题（选项A）': ['1', 'Python', ''],
            '试题（选项B）': ['2', 'Java', ''],
            '试题（选项C）': ['3', 'C++', ''],
            '试题（选项D）': ['4', 'HTML', ''],
            '试题（选项E）': ['', 'CSS', ''],
            '【图】及位置': ['', '', ''],
            '正确答案': ['2', 'A,B,C,D', '正确'],
            '难度代码': ['1（很简单）', '3（中等）', '2（简单）'],
            '一致性代码': ['5（很高）', '4（高）', '5（很高）'],
            '解析': [
                '1+1=2，这是基础数学知识。',
                'Python、Java、C++、HTML都是编程语言。',
                'Python确实是一种编程语言。'
            ]
        }
        
        # 创建测试文件
        test_df = pd.DataFrame(test_data)
        test_file = 'demo_questions.xlsx'
        test_df.to_excel(test_file, index=False)
        
        print(f"📄 创建测试文件: {test_file}")
        
        # 测试导入
        questions, errors = import_questions_from_excel(test_file)
        
        print(f"📊 导入结果:")
        print(f"   ✅ 成功导入: {len(questions)} 道题目")
        print(f"   ❌ 错误数量: {len(errors)}")
        
        if questions:
            print(f"   📝 示例题目:")
            for i, q in enumerate(questions[:2], 1):
                print(f"      {i}. {q['stem'][:30]}...")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 已清理测试文件")
            
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_database_operations():
    """演示数据库操作"""
    print("\n🎬 演示3: 数据库操作")
    print("-" * 40)
    
    try:
        from app import get_db, close_db
        from models import Question
        
        db = get_db()
        
        # 查询数据库
        total_questions = db.query(Question).count()
        print(f"📊 数据库统计:")
        print(f"   总题目数: {total_questions}")
        
        if total_questions > 0:
            # 显示最新题目
            latest_question = db.query(Question).order_by(Question.created_at.desc()).first()
            print(f"   最新题目: {latest_question.stem[:30]}...")
            print(f"   创建时间: {latest_question.created_at}")
        
        # 按题型统计
        question_types = db.query(Question.question_type_code).distinct().all()
        print(f"   题型种类: {len(question_types)} 种")
        
        close_db(db)
        print("✅ 数据库操作演示完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_system_status():
    """演示系统状态"""
    print("\n🎬 演示4: 系统状态")
    print("-" * 40)
    
    try:
        # 检查文件结构
        required_files = ['app.py', 'models.py', 'excel_importer.py', 'create_template.py']
        required_dirs = ['uploads', 'templates', 'error_reports']
        
        print("📁 文件结构检查:")
        for file in required_files:
            status = "✅" if os.path.exists(file) else "❌"
            print(f"   {status} {file}")
        
        for dir_name in required_dirs:
            status = "✅" if os.path.exists(dir_name) and os.path.isdir(dir_name) else "❌"
            print(f"   {status} {dir_name}/")
        
        # 检查模板文件
        template_path = os.path.join('templates', '题库模板.xlsx')
        if os.path.exists(template_path):
            file_size = os.path.getsize(template_path)
            print(f"   ✅ 题库模板.xlsx ({file_size} bytes)")
        else:
            print(f"   ❌ 题库模板.xlsx (缺失)")
        
        # 检查数据库文件
        if os.path.exists('local_dev.db'):
            db_size = os.path.getsize('local_dev.db')
            print(f"   ✅ local_dev.db ({db_size} bytes)")
        else:
            print(f"   ❌ local_dev.db (缺失)")
        
        print("✅ 系统状态检查完成")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def main():
    """主演示函数"""
    print("🎭 题库管理系统功能演示")
    print("=" * 60)
    print(f"🕒 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 工作目录: {os.getcwd()}")
    print("=" * 60)
    
    # 运行演示
    demo_template_generation()
    demo_excel_import()
    demo_database_operations()
    demo_system_status()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("💡 提示: 运行 'python run.py' 启动Web应用")
    print("🌐 访问地址: http://localhost:5000")

if __name__ == '__main__':
    main() 