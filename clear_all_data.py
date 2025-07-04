#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空所有题库数据的脚本
"""

import os
import sys
import shutil
import glob

def clear_all_databases():
    """清空所有项目数据库"""
    print("🧹 清空所有题库数据")
    print("-" * 40)
    
    try:
        # 清空question_banks目录下的所有.db文件
        db_dir = "question_bank_web/question_banks"
        if os.path.exists(db_dir):
            db_files = glob.glob(os.path.join(db_dir, "*.db"))
            
            if db_files:
                print(f"找到 {len(db_files)} 个数据库文件:")
                for db_file in db_files:
                    print(f"  - {os.path.basename(db_file)}")
                
                # 删除所有数据库文件
                for db_file in db_files:
                    os.remove(db_file)
                    print(f"✅ 已删除: {os.path.basename(db_file)}")
                
                print(f"✅ 成功清空 {len(db_files)} 个数据库文件")
            else:
                print("✅ question_banks目录中没有数据库文件")
        else:
            print("✅ question_banks目录不存在，无需清空")
        
        # 清空主数据库文件（如果存在）
        main_db = "question_bank_web/questions.db"
        if os.path.exists(main_db):
            os.remove(main_db)
            print(f"✅ 已删除主数据库: {os.path.basename(main_db)}")
        
        # 清空备份文件
        backup_files = glob.glob("question_bank_web/*.backup")
        if backup_files:
            for backup_file in backup_files:
                os.remove(backup_file)
                print(f"✅ 已删除备份文件: {os.path.basename(backup_file)}")
        
        # 清空错误报告
        error_reports_dir = "question_bank_web/error_reports"
        if os.path.exists(error_reports_dir):
            error_files = glob.glob(os.path.join(error_reports_dir, "*"))
            for error_file in error_files:
                if os.path.isfile(error_file):
                    os.remove(error_file)
                    print(f"✅ 已删除错误报告: {os.path.basename(error_file)}")
        
        print("\n🎉 所有题库数据已清空！")
        print("现在可以开始生成新的题库进行测试。")
        
        return True
        
    except Exception as e:
        print(f"❌ 清空失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False

def verify_clean_state():
    """验证清空状态"""
    print("\n🔍 验证清空状态")
    print("-" * 40)
    
    try:
        # 检查question_banks目录
        db_dir = "question_bank_web/question_banks"
        if os.path.exists(db_dir):
            db_files = glob.glob(os.path.join(db_dir, "*.db"))
            if db_files:
                print(f"⚠️  仍有 {len(db_files)} 个数据库文件:")
                for db_file in db_files:
                    print(f"  - {os.path.basename(db_file)}")
                return False
            else:
                print("✅ question_banks目录已清空")
        else:
            print("✅ question_banks目录不存在")
        
        # 检查主数据库
        main_db = "question_bank_web/questions.db"
        if os.path.exists(main_db):
            print(f"⚠️  主数据库仍存在: {os.path.basename(main_db)}")
            return False
        else:
            print("✅ 主数据库已清空")
        
        # 检查样例题库文件是否存在（这个应该保留）
        sample_file = "question_bank_web/questions_sample.xlsx"
        if os.path.exists(sample_file):
            print(f"✅ 样例题库文件存在: {os.path.basename(sample_file)}")
        else:
            print(f"⚠️  样例题库文件不存在: {os.path.basename(sample_file)}")
        
        print("\n✅ 清空状态验证完成，可以开始测试！")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def show_test_instructions():
    """显示测试说明"""
    print("\n📋 测试说明")
    print("=" * 50)
    
    print("现在您可以按照以下步骤进行验证:")
    print()
    print("🔸 第1步: 启动Flask应用")
    print("   cd question_bank_web")
    print("   python app.py")
    print()
    print("🔸 第2步: 访问项目管理页面")
    print("   打开浏览器访问: http://localhost:5000/projects")
    print()
    print("🔸 第3步: 创建第一个项目")
    print("   - 输入项目名称，例如: '视频创推1'")
    print("   - 点击'创建项目'")
    print("   - 系统会自动切换到该项目")
    print()
    print("🔸 第4步: 生成第一个题库")
    print("   - 访问主页，使用开发工具生成样例题库")
    print("   - 或直接访问: http://localhost:5000/import-sample")
    print("   - 记录导入的题目数量和ID范围")
    print()
    print("🔸 第5步: 创建第二个项目")
    print("   - 返回项目管理页面: http://localhost:5000/projects")
    print("   - 输入项目名称，例如: '保卫管理1'")
    print("   - 点击'创建项目'")
    print()
    print("🔸 第6步: 生成第二个题库")
    print("   - 在新项目中再次导入样例题库")
    print("   - 观察是否可以导入相同的题目ID")
    print()
    print("🔸 第7步: 验证结果")
    print("   - 在项目管理页面查看两个项目的题目数量")
    print("   - 切换项目查看题目列表")
    print("   - 验证两个项目可以有相同的题目ID")
    print()
    print("🎯 预期结果:")
    print("   ✅ 两个项目都能成功导入相同数量的题目")
    print("   ✅ 两个项目中存在相同的题目ID")
    print("   ✅ 项目间数据完全独立")
    print("   ✅ 切换项目时看到不同的数据")

def main():
    """主函数"""
    print("🧹 清空题库数据准备测试")
    print("=" * 50)
    
    # 确认操作
    print("⚠️  警告: 此操作将删除所有现有的题库数据！")
    print("包括:")
    print("- 所有项目数据库文件")
    print("- 主数据库文件")
    print("- 备份文件")
    print("- 错误报告文件")
    print()
    
    confirm = input("确定要继续吗？(输入 'yes' 确认): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ 操作已取消")
        return False
    
    print("\n开始清空数据...")
    
    # 执行清空
    if not clear_all_databases():
        print("❌ 清空失败")
        return False
    
    # 验证清空状态
    if not verify_clean_state():
        print("❌ 验证失败")
        return False
    
    # 显示测试说明
    show_test_instructions()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
