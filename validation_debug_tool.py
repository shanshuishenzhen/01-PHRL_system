#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库复核与组卷复核功能调试工具
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "question_bank_web"))
sys.path.append(str(project_root / "developer_tools"))

def test_question_bank_validation():
    """测试题库复核功能"""
    print("=" * 60)
    print("🔍 测试题库复核功能")
    print("=" * 60)
    
    try:
        # 检查必要文件是否存在
        blueprint_path = project_root / "developer_tools" / "question_bank_blueprint.json"
        validator_path = project_root / "developer_tools" / "question_bank_validator.py"
        
        print(f"📁 检查文件存在性:")
        print(f"   蓝图文件: {blueprint_path} - {'✅' if blueprint_path.exists() else '❌'}")
        print(f"   验证器: {validator_path} - {'✅' if validator_path.exists() else '❌'}")
        
        if not blueprint_path.exists():
            print("⚠️ 蓝图文件不存在，无法进行题库验证测试")
            return False
        
        if not validator_path.exists():
            print("⚠️ 验证器文件不存在，无法进行题库验证测试")
            return False
        
        # 导入验证器
        from developer_tools.question_bank_validator import QuestionBankValidator
        
        # 查找生成的题库文件
        generated_files = []
        for ext in ['.json', '.xlsx']:
            for pattern in ['generated_questions*', 'questions*', '*题库*']:
                files = list((project_root / "developer_tools").glob(f"{pattern}{ext}"))
                generated_files.extend(files)
        
        print(f"\n📋 找到的题库文件:")
        for i, file in enumerate(generated_files[:5]):  # 只显示前5个
            print(f"   {i+1}. {file.name}")
        
        if not generated_files:
            print("⚠️ 未找到生成的题库文件，请先运行题库生成器")
            return False
        
        # 使用第一个找到的文件进行测试
        generated_path = generated_files[0]
        print(f"\n🧪 使用文件进行测试: {generated_path.name}")
        
        # 创建验证器并运行验证
        validator = QuestionBankValidator()
        result = validator.validate_generated_bank(
            str(blueprint_path),
            str(generated_path),
            "validation_test_reports"
        )
        
        # 显示结果
        print(f"\n📊 验证结果:")
        print(f"   状态: {'✅ 通过' if result.get('is_valid') else '❌ 失败'}")
        print(f"   准确率: {result.get('accuracy_rate', 0):.2%}")
        print(f"   期望题目数: {result.get('total_questions_expected', 0)}")
        print(f"   实际题目数: {result.get('total_questions_generated', 0)}")
        print(f"   报告路径: {result.get('report_path', 'N/A')}")
        
        if result.get('errors'):
            print(f"\n⚠️ 发现 {len(result['errors'])} 个错误:")
            for error in result['errors'][:3]:  # 只显示前3个错误
                print(f"   - {error}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paper_validation():
    """测试组卷复核功能"""
    print("\n" + "=" * 60)
    print("📝 测试组卷复核功能")
    print("=" * 60)
    
    try:
        # 导入验证器
        from question_bank_web.paper_validator import PaperValidator
        from question_bank_web.models import Paper
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 连接数据库
        engine = create_engine('sqlite:///question_bank_web/questions.db')
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # 查找试卷
        papers = db.query(Paper).order_by(Paper.created_at.desc()).limit(5).all()
        
        print(f"📋 找到的试卷:")
        for i, paper in enumerate(papers):
            print(f"   {i+1}. {paper.name} (ID: {paper.id})")
        
        if not papers:
            print("⚠️ 未找到试卷，请先创建试卷")
            db.close()
            return False
        
        # 使用第一个试卷进行测试
        test_paper = papers[0]
        print(f"\n🧪 使用试卷进行测试: {test_paper.name}")
        
        # 创建验证器并运行验证
        validator = PaperValidator()
        result = validator.validate_paper_composition(
            test_paper.id,
            output_dir="paper_validation_test_reports"
        )
        
        # 显示结果
        print(f"\n📊 验证结果:")
        print(f"   状态: {'✅ 成功' if result.get('status') == 'success' else '❌ 失败'}")
        print(f"   试卷名称: {result.get('paper_name', 'N/A')}")
        print(f"   总题数: {result.get('total_questions', 0)}")
        print(f"   报告路径: {result.get('report_path', 'N/A')}")
        
        if result.get('l3_code_distribution'):
            print(f"\n📈 三级代码分布:")
            for l3_code, count in list(result['l3_code_distribution'].items())[:5]:
                print(f"   {l3_code}: {count}题")
        
        if result.get('type_distribution'):
            print(f"\n📊 题型分布:")
            for q_type, count in result['type_distribution'].items():
                print(f"   {q_type}型题: {count}题")
        
        db.close()
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface():
    """测试Web界面功能"""
    print("\n" + "=" * 60)
    print("🌐 测试Web界面功能")
    print("=" * 60)
    
    try:
        import requests
        
        # 测试主页
        print("🔗 测试Web界面连接:")
        
        urls = [
            ("主页", "http://localhost:5000/"),
            ("批量验证页面", "http://localhost:5000/validate-papers"),
            ("试卷管理", "http://localhost:5000/papers")
        ]
        
        for name, url in urls:
            try:
                response = requests.get(url, timeout=5)
                status = "✅ 正常" if response.status_code == 200 else f"❌ 错误({response.status_code})"
                print(f"   {name}: {status}")
            except requests.exceptions.RequestException as e:
                print(f"   {name}: ❌ 连接失败 - {e}")
        
        return True
        
    except ImportError:
        print("❌ requests库未安装，无法测试Web界面")
        return False
    except Exception as e:
        print(f"❌ Web界面测试失败: {e}")
        return False

def show_validation_entry_points():
    """显示验证功能的入口点"""
    print("\n" + "=" * 60)
    print("📍 验证功能入口点")
    print("=" * 60)
    
    print("🔍 题库复核（题库生成验证）:")
    print("   📁 程序位置: developer_tools/question_bank_validator.py")
    print("   🚀 自动验证: cd developer_tools && python question_bank_generator.py")
    print("   🔧 手动验证: cd developer_tools && python question_bank_validator.py blueprint.json generated.json")
    
    print("\n📝 组卷复核（试卷组题验证）:")
    print("   📁 程序位置: question_bank_web/paper_validator.py")
    print("   🌐 Web界面: http://localhost:5000/validate-papers")
    print("   🔧 命令行: cd question_bank_web && python -c \"from paper_validator import validate_paper_from_command_line; validate_paper_from_command_line(1)\"")
    
    print("\n📊 验证报告输出:")
    print("   📁 题库验证报告: validation_reports/")
    print("   📁 试卷验证报告: paper_validation_reports/")

def main():
    """主函数"""
    print("🔧 题库复核与组卷复核功能调试工具")
    print("=" * 60)
    
    # 显示入口点
    show_validation_entry_points()
    
    # 测试题库复核功能
    qb_success = test_question_bank_validation()
    
    # 测试组卷复核功能
    paper_success = test_paper_validation()
    
    # 测试Web界面
    web_success = test_web_interface()
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 调试结果总结")
    print("=" * 60)
    print(f"🔍 题库复核功能: {'✅ 正常' if qb_success else '❌ 异常'}")
    print(f"📝 组卷复核功能: {'✅ 正常' if paper_success else '❌ 异常'}")
    print(f"🌐 Web界面功能: {'✅ 正常' if web_success else '❌ 异常'}")
    
    if all([qb_success, paper_success, web_success]):
        print("\n🎉 所有验证功能正常！")
    else:
        print("\n⚠️ 部分功能存在问题，请检查上述错误信息")
    
    print("\n💡 使用建议:")
    print("   1. 访问 http://localhost:5000/validate-papers 进行批量试卷验证")
    print("   2. 在 developer_tools 目录运行题库生成器进行题库验证")
    print("   3. 查看生成的验证报告了解详细结果")

if __name__ == "__main__":
    main()
