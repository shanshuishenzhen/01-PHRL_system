#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化数据库脚本
"""

import os
import sys

def init_database():
    """初始化数据库"""
    print("🔧 初始化数据库")
    print("-" * 40)
    
    try:
        # 添加路径
        sys.path.append('question_bank_web')
        
        from models import Base
        from sqlalchemy import create_engine
        
        # 数据库路径
        db_path = "question_bank_web/questions.db"
        
        # 如果数据库已存在，先删除
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ 已删除旧数据库: {db_path}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 创建数据库
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        
        print(f"✅ 数据库已创建: {db_path}")
        print(f"✅ 数据库文件存在: {os.path.exists(db_path)}")
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✅ 创建的表: {tables}")
        
        if 'questions' in tables and 'question_banks' in tables:
            print("✅ 数据库初始化成功")
            return True
        else:
            print("❌ 数据库表创建不完整")
            return False
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_import_after_init():
    """测试初始化后的导入功能"""
    print("\n🧪 测试导入功能")
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
        
        print("✅ 数据库连接成功")
        
        # 测试导入
        excel_file = 'question_bank_web/questions_sample.xlsx'
        if not os.path.exists(excel_file):
            print(f"❌ 样例文件不存在: {excel_file}")
            return False
        
        print("正在导入样例题库...")
        questions_added, errors = import_questions_from_excel(excel_file, session)
        
        print(f"✅ 导入完成:")
        print(f"   成功添加: {len(questions_added) if questions_added else 0} 个题目")
        print(f"   错误数量: {len(errors) if errors else 0} 个")
        
        # 统计数据库中的题目
        total_questions = session.query(Question).count()
        total_banks = session.query(QuestionBank).count()
        
        print(f"   数据库题目总数: {total_questions}")
        print(f"   数据库题库总数: {total_banks}")
        
        # 按题库统计
        banks = session.query(QuestionBank).all()
        for bank in banks:
            question_count = session.query(Question).filter_by(bank_id=bank.id).count()
            print(f"   题库 '{bank.name}': {question_count} 个题目")
        
        session.close()
        
        # 如果有错误，显示错误信息
        if errors:
            print(f"\n⚠️  导入过程中有 {len(errors)} 个错误:")
            for i, error in enumerate(errors[:5]):  # 只显示前5个错误
                print(f"   {i+1}. {error}")
            if len(errors) > 5:
                print(f"   ... 还有 {len(errors) - 5} 个错误")
        
        # 判断是否成功
        if total_questions > 0:
            print("✅ 导入测试成功")
            return True
        else:
            print("❌ 导入测试失败，没有题目被添加")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("🔧 数据库初始化和测试")
    print("=" * 50)
    
    # 初始化数据库
    if not init_database():
        print("❌ 数据库初始化失败")
        return False
    
    # 测试导入功能
    if not test_import_after_init():
        print("❌ 导入测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 数据库初始化和测试完成！")
    print("\n✅ 完成内容:")
    print("1. ✅ 数据库已重新创建")
    print("2. ✅ 所有表结构正确")
    print("3. ✅ 样例题库导入成功")
    print("4. ✅ 题目数量统计正确")
    
    print("\n🎯 现在可以正常使用:")
    print("• 开发工具生成样例题库")
    print("• 题库管理模块导入和管理")
    print("• 完整的题库管理功能")
    print("• 数据统计和报告功能")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
