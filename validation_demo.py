#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库复核与组卷复核功能演示脚本
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def demo_question_bank_validation():
    """演示题库复核功能"""
    print("🔍 题库复核功能演示")
    print("=" * 50)
    
    print("📍 程序入口: developer_tools/question_bank_validator.py")
    print("📁 蓝图文件: developer_tools/question_bank_blueprint.json")
    
    # 检查文件
    blueprint_path = project_root / "developer_tools" / "question_bank_blueprint.json"
    validator_path = project_root / "developer_tools" / "question_bank_validator.py"
    
    print(f"\n📋 文件检查:")
    print(f"   蓝图文件: {'✅' if blueprint_path.exists() else '❌'}")
    print(f"   验证器: {'✅' if validator_path.exists() else '❌'}")
    
    # 查找验证报告
    validation_reports = list((project_root / "developer_tools" / "validation_reports").glob("*.xlsx"))
    if validation_reports:
        latest_report = max(validation_reports, key=lambda x: x.stat().st_mtime)
        print(f"\n📊 最新验证报告: {latest_report.name}")
        print(f"   路径: {latest_report}")
        
        # 尝试打开报告
        try:
            os.startfile(str(latest_report))
            print("   📖 已在Excel中打开验证报告")
        except:
            print("   ⚠️ 无法自动打开Excel文件")
    else:
        print("\n⚠️ 未找到验证报告，请先运行题库生成器")
    
    print(f"\n🚀 运行命令:")
    print(f"   自动验证: cd developer_tools && python question_bank_generator.py")
    print(f"   手动验证: cd developer_tools && python question_bank_validator.py blueprint.json generated.json")

def demo_paper_validation():
    """演示组卷复核功能"""
    print("\n🔍 组卷复核功能演示")
    print("=" * 50)
    
    print("📍 程序入口: question_bank_web/paper_validator.py")
    print("🌐 Web界面: http://localhost:5000/validate-papers")
    
    # 查找验证报告
    validation_reports = list((project_root / "question_bank_web" / "paper_validation_test_reports").glob("*.xlsx"))
    if validation_reports:
        latest_report = max(validation_reports, key=lambda x: x.stat().st_mtime)
        print(f"\n📊 最新验证报告: {latest_report.name}")
        print(f"   路径: {latest_report}")
        
        # 尝试打开报告
        try:
            os.startfile(str(latest_report))
            print("   📖 已在Excel中打开验证报告")
        except:
            print("   ⚠️ 无法自动打开Excel文件")
    else:
        print("\n⚠️ 未找到验证报告")
    
    print(f"\n🚀 使用方法:")
    print(f"   Web界面: 访问 http://localhost:5000/validate-papers")
    print(f"   命令行: cd question_bank_web && python test_paper_validation.py")

def demo_web_interface():
    """演示Web界面"""
    print("\n🌐 Web界面演示")
    print("=" * 50)
    
    urls = [
        ("主页", "http://localhost:5000/"),
        ("试卷管理", "http://localhost:5000/papers"),
        ("批量验证", "http://localhost:5000/validate-papers"),
    ]
    
    print("🔗 可用的Web界面:")
    for name, url in urls:
        print(f"   {name}: {url}")
    
    # 尝试打开批量验证页面
    try:
        print(f"\n🚀 正在打开批量验证页面...")
        webbrowser.open("http://localhost:5000/validate-papers")
        print("   ✅ 已在浏览器中打开")
    except:
        print("   ⚠️ 无法自动打开浏览器")

def show_validation_features():
    """显示验证功能特点"""
    print("\n📋 验证功能特点")
    print("=" * 50)
    
    print("🔍 题库复核功能:")
    print("   ✅ 验证题目总数是否符合蓝图要求")
    print("   ✅ 验证题型分布是否正确")
    print("   ✅ 验证知识点分布是否符合规则")
    print("   ✅ 验证题目ID格式是否标准")
    print("   ✅ 生成详细的Excel验证报告")
    
    print("\n📝 组卷复核功能:")
    print("   ✅ 分析试卷三级代码分布")
    print("   ✅ 统计题型分布情况")
    print("   ✅ 生成交叉分析矩阵")
    print("   ✅ 与组题模板对比分析")
    print("   ✅ 支持批量验证多套试卷")

def show_report_examples():
    """显示报告示例"""
    print("\n📊 验证报告示例")
    print("=" * 50)
    
    print("🔍 题库验证报告包含:")
    print("   📈 验证摘要（总体准确率）")
    print("   📊 题型分布对比表")
    print("   📋 知识点分布统计")
    print("   ⚠️ 错误和警告列表")
    print("   📄 详细题目清单")
    
    print("\n📝 试卷验证报告包含:")
    print("   📄 试卷基本信息")
    print("   📊 三级代码分布统计")
    print("   📈 题型分布分析")
    print("   🔄 三级代码×题型交叉矩阵")
    print("   📋 详细题目列表")
    print("   📊 模板对比分析（如提供）")

def main():
    """主演示函数"""
    print("🎯 题库复核与组卷复核功能演示")
    print("=" * 60)
    
    # 显示功能特点
    show_validation_features()
    
    # 演示题库复核
    demo_question_bank_validation()
    
    # 演示组卷复核
    demo_paper_validation()
    
    # 演示Web界面
    demo_web_interface()
    
    # 显示报告示例
    show_report_examples()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("=" * 60)
    
    print("💡 快速开始:")
    print("   1. 题库复核: cd developer_tools && python question_bank_generator.py")
    print("   2. 组卷复核: 访问 http://localhost:5000/validate-papers")
    print("   3. 查看报告: 自动在Excel中打开验证报告")
    
    print("\n📁 报告位置:")
    print("   题库验证: developer_tools/validation_reports/")
    print("   试卷验证: question_bank_web/paper_validation_reports/")
    
    print("\n🔧 调试工具:")
    print("   python validation_debug_tool.py - 运行完整功能测试")
    print("   python validation_demo.py - 查看功能演示")

if __name__ == "__main__":
    main()
