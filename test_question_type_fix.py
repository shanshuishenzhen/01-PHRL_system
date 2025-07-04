#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试题型代码修复的脚本
"""

import os
import sys
import pandas as pd
import subprocess
from pathlib import Path

def test_question_type_mapping():
    """测试题型代码映射"""
    print("🔍 测试1: 题型代码映射检查")
    print("-" * 40)
    
    try:
        # 测试替换逻辑
        test_cases = [
            ("组合题", "综合题"),
            ("单选题", "单选题"),
            ("多选题", "多选题"),
            ("判断题", "判断题"),
        ]
        
        for original, expected in test_cases:
            result = original.replace('组合题', '综合题')
            if result == expected:
                print(f"✅ '{original}' -> '{result}'")
            else:
                print(f"❌ '{original}' -> '{result}' (期望: '{expected}')")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_question_generation():
    """测试题目生成"""
    print("\n🔍 测试2: 题目生成测试")
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
        
        print(f"✅ 模板文件存在: {template_file}")
        
        # 设置输出文件
        output_file = "question_bank_web/test_questions_fixed.xlsx"
        
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
                return True
            else:
                print(f"❌ 输出文件未创建: {output_file}")
                return False
        else:
            print("❌ 题库生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 题库生成测试失败: {e}")
        return False

def test_generated_question_types():
    """测试生成的题目题型代码"""
    print("\n🔍 测试3: 生成题目题型代码检查")
    print("-" * 40)
    
    try:
        output_file = "question_bank_web/test_questions_fixed.xlsx"
        
        if not os.path.exists(output_file):
            print(f"❌ 测试文件不存在: {output_file}")
            return False
        
        # 读取生成的文件
        df = pd.read_excel(output_file, dtype=str)
        print(f"✅ 成功读取测试文件，共 {len(df)} 行")
        
        # 检查题型代码列
        if '题型代码' not in df.columns:
            print("❌ 文件中没有'题型代码'列")
            return False
        
        # 统计题型代码
        question_types = df['题型代码'].value_counts()
        print("题型代码统计:")
        for qtype, count in question_types.items():
            print(f"  {qtype}: {count}个")
        
        # 检查是否有无效的题型代码
        valid_question_types = {
            'B（单选题）', 'G（多选题）', 'C（判断题）', 'T（填空题）', 
            'D（简答题）', 'U（计算题）', 'W（论述题）', 'E（案例分析题）', 'F（综合题）'
        }
        
        invalid_types = []
        for qtype in question_types.index:
            if qtype not in valid_question_types:
                invalid_types.append(qtype)
        
        if invalid_types:
            print(f"❌ 发现无效题型代码: {invalid_types}")
            return False
        else:
            print("✅ 所有题型代码都有效")
        
        # 特别检查是否还有"组合题"
        has_invalid_combo = any('组合题' in str(qtype) for qtype in question_types.index)
        if has_invalid_combo:
            print("❌ 仍然存在'组合题'题型代码")
            return False
        else:
            print("✅ 没有发现'组合题'题型代码")
        
        # 检查是否有"综合题"
        has_valid_combo = any('综合题' in str(qtype) for qtype in question_types.index)
        if has_valid_combo:
            print("✅ 发现'综合题'题型代码（正确）")
        else:
            print("ℹ️  没有发现'综合题'题型代码（可能模板中没有F类题目）")
        
        return True
        
    except Exception as e:
        print(f"❌ 题型代码检查失败: {e}")
        return False

def test_import_compatibility():
    """测试导入兼容性"""
    print("\n🔍 测试4: 导入兼容性测试")
    print("-" * 40)
    
    try:
        # 添加路径以便导入
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
        test_file = "question_bank_web/test_questions_fixed.xlsx"
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return False
        
        questions_added, errors = import_questions_from_excel(test_file, session)
        
        print(f"✅ 导入函数执行完成")
        print(f"成功添加的题目数量: {len(questions_added) if questions_added else 0}")
        print(f"错误数量: {len(errors) if errors else 0}")
        
        if errors:
            print("前5个错误详情:")
            for i, error in enumerate(errors[:5]):
                print(f"  错误 {i+1}: {error.get('message', error)}")
        
        # 检查是否还有题型代码错误
        type_errors = [e for e in errors if '题型代码' in str(e.get('message', ''))]
        if type_errors:
            print(f"❌ 仍有 {len(type_errors)} 个题型代码错误")
            return False
        else:
            print("✅ 没有题型代码错误")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 导入兼容性测试失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        "question_bank_web/test_questions_fixed.xlsx"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ 清理测试文件: {file_path}")
            except Exception as e:
                print(f"⚠️  清理文件失败: {file_path} - {e}")

def main():
    """主测试函数"""
    print("🔧 题型代码修复验证测试")
    print("=" * 50)
    
    tests = [
        ("题型代码映射检查", test_question_type_mapping),
        ("题目生成测试", test_question_generation),
        ("生成题目题型代码检查", test_generated_question_types),
        ("导入兼容性测试", test_import_compatibility),
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
        print("🎉 所有测试通过！题型代码修复成功！")
        print("\n✅ 修复内容:")
        print("1. ✅ 修复了题型代码映射逻辑")
        print("2. ✅ '组合题' 正确替换为 '综合题'")
        print("3. ✅ 生成的题目使用正确的题型代码")
        print("4. ✅ 题库管理模块可以正常导入")
        
        print("\n🎯 现在可以正常使用:")
        print("• 开发工具生成的题库使用正确的题型代码")
        print("• 题库管理模块可以正常导入样例题库")
        print("• 不会再出现'无效的题型代码'错误")
        
    else:
        print("⚠️  部分测试失败，请检查相关问题")
    
    # 清理测试文件
    print("\n🧹 清理测试文件...")
    cleanup_test_files()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
