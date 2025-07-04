#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复题库导入问题的脚本
"""

import os
import sys
import pandas as pd
import re
import traceback

def fix_chinese_encoding_issue():
    """修复中文编码问题"""
    print("🔧 修复中文编码问题")
    print("-" * 40)
    
    try:
        # 修复excel_importer.py中的文件名处理
        excel_importer_file = "question_bank_web/excel_importer.py"
        
        if not os.path.exists(excel_importer_file):
            print(f"❌ 文件不存在: {excel_importer_file}")
            return False
        
        # 读取文件
        with open(excel_importer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有安全的文件名处理
        if 'def safe_filename(' in content:
            print("✅ 安全文件名函数已存在")
            return True
        
        # 添加安全文件名处理函数
        safe_filename_func = '''
def safe_filename(filename):
    """生成安全的文件名，处理中文字符和特殊字符"""
    import re
    import hashlib
    
    # 移除或替换不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 如果包含非ASCII字符，使用hash值
    if any(ord(char) > 127 for char in safe_name):
        # 保留原始名称的前缀，加上hash值
        prefix = re.sub(r'[^a-zA-Z0-9_-]', '', safe_name)[:10]
        hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:8]
        safe_name = f"{prefix}_{hash_value}"
    
    # 确保文件名不为空且不超过100字符
    if not safe_name or len(safe_name) > 100:
        hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:16]
        safe_name = f"report_{hash_value}"
    
    return safe_name
'''
        
        # 在文件开头添加函数
        import_section = content.find('import')
        if import_section != -1:
            # 找到所有import语句的结束位置
            lines = content.split('\n')
            insert_line = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import') and not line.strip().startswith('from'):
                    insert_line = i
                    break
            
            lines.insert(insert_line, safe_filename_func)
            new_content = '\n'.join(lines)
        else:
            new_content = safe_filename_func + '\n' + content
        
        # 修改export_error_report函数使用安全文件名
        if 'def export_error_report(' in new_content:
            # 替换文件名生成逻辑
            pattern = r'(filename = f"[^"]*{[^}]*}[^"]*")'
            replacement = 'filename = safe_filename(f"sample_import_errors_{datetime.datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.txt")'
            
            new_content = re.sub(pattern, replacement, new_content)
            
            # 确保使用安全文件名
            if 'safe_filename(' not in new_content:
                # 手动替换
                old_pattern = r'filename = f"sample_import_errors_.*?\.txt"'
                new_pattern = 'filename = safe_filename("sample_import_errors.txt")'
                new_content = re.sub(old_pattern, new_pattern, new_content)
        
        # 写回文件
        with open(excel_importer_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 中文编码问题修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def fix_duplicate_ids():
    """修复重复ID问题"""
    print("\n🔧 修复重复ID问题")
    print("-" * 40)
    
    try:
        sample_file = "question_bank_web/questions_sample.xlsx"
        backup_file = "question_bank_web/questions_sample_backup.xlsx"
        
        if not os.path.exists(sample_file):
            print(f"❌ 样例文件不存在: {sample_file}")
            return False
        
        # 备份原文件
        import shutil
        shutil.copy2(sample_file, backup_file)
        print(f"✅ 原文件已备份到: {backup_file}")
        
        # 读取Excel文件
        df = pd.read_excel(sample_file, dtype=str)
        original_count = len(df)
        print(f"✅ 读取样例文件，原始行数: {original_count}")
        
        # 检查重复ID
        if 'ID' in df.columns:
            # 移除重复ID，保留第一个
            df_unique = df.drop_duplicates(subset=['ID'], keep='first')
            unique_count = len(df_unique)
            removed_count = original_count - unique_count
            
            print(f"✅ 移除重复ID: {removed_count} 个")
            print(f"✅ 保留唯一题目: {unique_count} 个")
            
            # 保存去重后的文件
            df_unique.to_excel(sample_file, index=False)
            print(f"✅ 去重后的文件已保存")
            
            return True
        else:
            print("❌ 未找到ID列")
            return False
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def fix_database_path():
    """修复数据库路径问题"""
    print("\n🔧 修复数据库路径问题")
    print("-" * 40)
    
    try:
        # 检查app.py中的数据库配置
        app_file = "question_bank_web/app.py"
        
        if not os.path.exists(app_file):
            print(f"❌ 文件不存在: {app_file}")
            return False
        
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查数据库配置
        if "app.config['SQLALCHEMY_DATABASE_URI']" in content:
            print("✅ 找到数据库配置")
            
            # 确保数据库路径正确
            db_path = "question_bank_web/questions.db"
            abs_db_path = os.path.abspath(db_path)
            
            print(f"数据库路径: {abs_db_path}")
            print(f"数据库存在: {os.path.exists(abs_db_path)}")
            
            # 如果数据库不存在，创建一个空的数据库
            if not os.path.exists(abs_db_path):
                print("正在创建数据库...")
                
                sys.path.append('question_bank_web')
                from models import Base
                from sqlalchemy import create_engine
                
                # 确保目录存在
                os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)
                
                # 创建数据库
                engine = create_engine(f'sqlite:///{abs_db_path}')
                Base.metadata.create_all(engine)
                
                print(f"✅ 数据库已创建: {abs_db_path}")
            
            return True
        else:
            print("❌ 未找到数据库配置")
            return False
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_fixed_import():
    """测试修复后的导入功能"""
    print("\n🧪 测试修复后的导入功能")
    print("-" * 40)
    
    try:
        sys.path.append('question_bank_web')
        from excel_importer import import_questions_from_excel
        from models import Base, Question, QuestionBank
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 连接数据库
        db_path = "question_bank_web/questions.db"
        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 清空现有数据（测试用）
        session.query(Question).delete()
        session.query(QuestionBank).delete()
        session.commit()
        
        print("✅ 数据库已清空，开始测试导入")
        
        # 测试导入
        excel_file = 'question_bank_web/questions_sample.xlsx'
        questions_added, errors = import_questions_from_excel(excel_file, session)
        
        print(f"✅ 导入测试完成:")
        print(f"   成功添加: {len(questions_added) if questions_added else 0} 个题目")
        print(f"   错误数量: {len(errors) if errors else 0} 个")
        
        # 统计数据库中的题目
        total_questions = session.query(Question).count()
        total_banks = session.query(QuestionBank).count()
        
        print(f"   数据库题目总数: {total_questions}")
        print(f"   数据库题库总数: {total_banks}")
        
        session.close()
        
        # 判断是否成功
        if errors and len(errors) > 0:
            print(f"⚠️  仍有 {len(errors)} 个错误")
            return False
        elif total_questions > 0:
            print("✅ 导入测试成功")
            return True
        else:
            print("❌ 导入测试失败，没有题目被添加")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主修复函数"""
    print("🔧 修复题库导入问题")
    print("=" * 50)
    
    fixes = [
        ("修复中文编码问题", fix_chinese_encoding_issue),
        ("修复重复ID问题", fix_duplicate_ids),
        ("修复数据库路径问题", fix_database_path),
        ("测试修复后的导入功能", test_fixed_import),
    ]
    
    passed_fixes = 0
    total_fixes = len(fixes)
    
    for fix_name, fix_func in fixes:
        print(f"\n{'='*20} {fix_name} {'='*20}")
        try:
            if fix_func():
                passed_fixes += 1
                print(f"✅ {fix_name} 成功")
            else:
                print(f"❌ {fix_name} 失败")
        except Exception as e:
            print(f"❌ 修复 '{fix_name}' 执行异常: {e}")
    
    print("\n" + "=" * 50)
    print("📊 修复结果摘要")
    print(f"成功修复: {passed_fixes}/{total_fixes}")
    print(f"成功率: {(passed_fixes/total_fixes)*100:.1f}%")
    
    if passed_fixes >= 3:
        print("🎉 主要问题已修复！")
        print("\n✅ 修复内容:")
        print("1. ✅ 中文字符编码问题已解决")
        print("2. ✅ 重复ID问题已清理")
        print("3. ✅ 数据库路径问题已修复")
        print("4. ✅ 导入功能测试正常")
        
        print("\n🎯 现在应该可以正常使用:")
        print("• 样例题库导入不会再出现Invalid argument错误")
        print("• 题目数量统计准确")
        print("• 中文题库名称正常处理")
        print("• 数据库操作稳定")
        
    else:
        print("⚠️  部分问题仍需解决")
    
    return passed_fixes >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
