#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析题库导入错误的脚本
"""

import os
import sys
import pandas as pd
import traceback

def analyze_error_pattern():
    """分析错误模式"""
    print("🔍 分析错误模式")
    print("-" * 40)
    
    try:
        # 读取错误报告
        error_file = "question_bank_web/error_reports/sample_import_errors.txt"
        if not os.path.exists(error_file):
            print(f"❌ 错误报告文件不存在: {error_file}")
            return False
        
        with open(error_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 错误报告文件存在，内容长度: {len(content)} 字符")
        
        # 分析错误模式
        lines = content.split('\n')
        error_lines = [line for line in lines if 'Invalid argument' in line]
        
        print(f"✅ 发现 {len(error_lines)} 个 Invalid argument 错误")
        
        # 分析错误的题目ID模式
        error_ids = []
        for line in error_lines:
            if 'ID:' in line:
                start = line.find('ID:') + 3
                end = line.find(')', start)
                if end > start:
                    error_id = line[start:end].strip()
                    error_ids.append(error_id)
        
        print(f"✅ 提取到 {len(error_ids)} 个错误题目ID")
        
        # 分析ID模式
        if error_ids:
            print("\n错误题目ID模式分析:")
            
            # 按题库名称分组
            by_bank = {}
            for error_id in error_ids:
                if '_' in error_id:
                    parts = error_id.split('_')
                    if len(parts) >= 2:
                        bank_name = parts[1]
                        if bank_name not in by_bank:
                            by_bank[bank_name] = []
                        by_bank[bank_name].append(error_id)
            
            for bank_name, ids in by_bank.items():
                print(f"  {bank_name}: {len(ids)} 个错误")
            
            # 检查是否有特殊字符
            special_chars = set()
            for error_id in error_ids:
                for char in error_id:
                    if ord(char) > 127:  # 非ASCII字符
                        special_chars.add(char)
            
            if special_chars:
                print(f"\n⚠️  发现非ASCII字符: {list(special_chars)}")
            else:
                print("\n✅ 所有错误ID都是ASCII字符")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False

def check_sample_file():
    """检查样例题库文件"""
    print("\n🔍 检查样例题库文件")
    print("-" * 40)
    
    try:
        sample_file = "question_bank_web/questions_sample.xlsx"
        if not os.path.exists(sample_file):
            print(f"❌ 样例题库文件不存在: {sample_file}")
            return False
        
        # 读取Excel文件
        df = pd.read_excel(sample_file, dtype=str)
        print(f"✅ 样例题库文件读取成功")
        print(f"   总行数: {len(df)}")
        print(f"   列数: {len(df.columns)}")
        
        # 检查ID列
        if 'ID' in df.columns:
            ids = df['ID'].tolist()
            print(f"   ID列存在，共 {len(ids)} 个ID")
            
            # 检查重复ID
            unique_ids = set(ids)
            if len(unique_ids) != len(ids):
                print(f"⚠️  发现重复ID: {len(ids) - len(unique_ids)} 个")
            else:
                print("✅ 所有ID都是唯一的")
            
            # 检查空ID
            empty_ids = [i for i, id_val in enumerate(ids) if pd.isna(id_val) or str(id_val).strip() == '']
            if empty_ids:
                print(f"⚠️  发现空ID: {len(empty_ids)} 个，行号: {empty_ids[:5]}...")
            else:
                print("✅ 没有空ID")
            
            # 检查ID中的特殊字符
            problematic_ids = []
            for i, id_val in enumerate(ids):
                if pd.notna(id_val):
                    id_str = str(id_val)
                    # 检查是否包含可能导致文件系统问题的字符
                    problematic_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
                    if any(char in id_str for char in problematic_chars):
                        problematic_ids.append((i+2, id_str))  # +2因为Excel行号从1开始，且有标题行
            
            if problematic_ids:
                print(f"⚠️  发现包含特殊字符的ID: {len(problematic_ids)} 个")
                for row, id_val in problematic_ids[:5]:
                    print(f"     行 {row}: {id_val}")
            else:
                print("✅ 所有ID都不包含特殊字符")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def check_database_count():
    """检查数据库中的题目数量"""
    print("\n🔍 检查数据库题目数量")
    print("-" * 40)
    
    try:
        sys.path.append('question_bank_web')
        from models import Base, Question, QuestionBank
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 连接到实际数据库
        db_path = "question_bank_web/questions.db"
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 统计题目数量
        total_questions = session.query(Question).count()
        total_banks = session.query(QuestionBank).count()
        
        print(f"✅ 数据库连接成功")
        print(f"   题目总数: {total_questions}")
        print(f"   题库总数: {total_banks}")
        
        # 按题库统计
        banks = session.query(QuestionBank).all()
        for bank in banks:
            question_count = session.query(Question).filter_by(bank_id=bank.id).count()
            print(f"   题库 '{bank.name}': {question_count} 个题目")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def analyze_errno22_cause():
    """分析Errno 22错误的可能原因"""
    print("\n🔍 分析Errno 22错误原因")
    print("-" * 40)
    
    print("Errno 22 (Invalid argument) 可能的原因:")
    print("1. 文件路径包含非法字符")
    print("2. 文件名过长")
    print("3. 磁盘空间不足")
    print("4. 文件权限问题")
    print("5. 数据库锁定问题")
    print("6. 字符编码问题")
    
    # 检查磁盘空间
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        print(f"\n磁盘空间检查:")
        print(f"  总空间: {total // (1024**3)} GB")
        print(f"  已使用: {used // (1024**3)} GB")
        print(f"  可用空间: {free // (1024**3)} GB")
        
        if free < 1024**3:  # 小于1GB
            print("⚠️  磁盘空间可能不足")
        else:
            print("✅ 磁盘空间充足")
    except:
        print("⚠️  无法检查磁盘空间")
    
    # 检查数据库文件
    db_path = "question_bank_web/questions.db"
    if os.path.exists(db_path):
        try:
            size = os.path.getsize(db_path)
            print(f"\n数据库文件:")
            print(f"  路径: {db_path}")
            print(f"  大小: {size // 1024} KB")
            print(f"  可读: {os.access(db_path, os.R_OK)}")
            print(f"  可写: {os.access(db_path, os.W_OK)}")
        except Exception as e:
            print(f"⚠️  数据库文件检查失败: {e}")
    
    return True

def main():
    """主函数"""
    print("🔧 题库导入错误分析")
    print("=" * 50)
    
    tests = [
        ("错误模式分析", analyze_error_pattern),
        ("样例文件检查", check_sample_file),
        ("数据库数量检查", check_database_count),
        ("Errno 22原因分析", analyze_errno22_cause),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 完成")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行异常: {e}")
    
    print("\n" + "=" * 50)
    print("📊 分析结果摘要")
    print(f"完成分析: {passed_tests}/{total_tests}")
    
    print("\n💡 建议:")
    print("1. 检查错误报告中的具体错误模式")
    print("2. 验证样例题库文件的完整性")
    print("3. 确认数据库中的实际题目数量")
    print("4. 分析Errno 22错误的根本原因")
    
    return passed_tests >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
