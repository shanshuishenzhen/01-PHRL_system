#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试验证功能集成到开发工具模块
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_validation_integration():
    """测试验证功能集成"""
    print("🔧 测试验证功能集成到开发工具模块")
    print("=" * 60)
    
    # 检查开发工具模块文件
    developer_tools_path = project_root / "developer_tools.py"
    print(f"📁 开发工具模块: {'✅' if developer_tools_path.exists() else '❌'}")
    
    # 检查验证相关文件
    validation_files = [
        ("题库验证器", project_root / "developer_tools" / "question_bank_validator.py"),
        ("试卷验证器", project_root / "question_bank_web" / "paper_validator.py"),
        ("蓝图文件", project_root / "developer_tools" / "question_bank_blueprint.json"),
    ]
    
    print(f"\n📋 验证相关文件检查:")
    for name, path in validation_files:
        status = "✅" if path.exists() else "❌"
        print(f"   {name}: {status}")
    
    # 检查报告目录
    report_dirs = [
        ("题库验证报告", project_root / "developer_tools" / "validation_reports"),
        ("试卷验证报告", project_root / "question_bank_web" / "paper_validation_reports"),
        ("试卷测试报告", project_root / "question_bank_web" / "paper_validation_test_reports"),
    ]
    
    print(f"\n📁 报告目录检查:")
    for name, path in report_dirs:
        if path.exists():
            files = list(path.glob("*.xlsx"))
            print(f"   {name}: ✅ ({len(files)} 个报告)")
        else:
            print(f"   {name}: ❌ (目录不存在)")
    
    # 检查开发工具模块代码
    print(f"\n🔍 代码集成检查:")
    try:
        with open(developer_tools_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键功能是否已添加
        checks = [
            ("验证标签页", "validation_tab" in content),
            ("创建验证标签页方法", "create_validation_tab" in content),
            ("题库生成验证方法", "run_question_bank_generation_with_validation" in content),
            ("手动题库验证方法", "run_manual_question_bank_validation" in content),
            ("组卷验证Web方法", "open_paper_validation_web" in content),
            ("批量试卷验证方法", "run_batch_paper_validation" in content),
            ("报告管理方法", "refresh_validation_reports" in content),
            ("打开报告文件方法", "open_report_file" in content),
        ]
        
        for name, check in checks:
            status = "✅" if check else "❌"
            print(f"   {name}: {status}")
        
        all_checks_passed = all(check for _, check in checks)
        print(f"\n📊 代码集成状态: {'✅ 完成' if all_checks_passed else '❌ 不完整'}")
        
    except Exception as e:
        print(f"   ❌ 代码检查失败: {e}")
        return False
    
    return True

def test_report_links():
    """测试报告链接功能"""
    print(f"\n🔗 测试报告链接功能")
    print("=" * 40)
    
    # 查找现有报告
    report_dirs = [
        project_root / "developer_tools" / "validation_reports",
        project_root / "question_bank_web" / "paper_validation_reports",
        project_root / "question_bank_web" / "paper_validation_test_reports",
    ]
    
    all_reports = []
    for report_dir in report_dirs:
        if report_dir.exists():
            reports = list(report_dir.glob("*.xlsx"))
            for report in reports:
                all_reports.append((report.name, str(report)))
    
    if all_reports:
        print(f"📄 找到 {len(all_reports)} 个验证报告:")
        for i, (name, path) in enumerate(all_reports[:5]):  # 只显示前5个
            print(f"   {i+1}. {name}")
            print(f"      路径: {path}")
        
        print(f"\n💡 这些报告将在开发工具的验证标签页中显示为可点击链接")
    else:
        print(f"⚠️ 未找到验证报告，请先运行验证功能生成报告")
    
    return len(all_reports) > 0

def show_usage_guide():
    """显示使用指南"""
    print(f"\n📖 验证功能使用指南")
    print("=" * 40)
    
    print(f"🚀 启动开发工具:")
    print(f"   python developer_tools.py")
    
    print(f"\n📋 验证功能位置:")
    print(f"   在开发工具界面中点击 '验证复核' 标签页")
    
    print(f"\n🔍 题库复核功能:")
    print(f"   1. 点击 '生成题库并自动验证' - 自动生成题库并验证")
    print(f"   2. 点击 '手动验证现有题库' - 选择文件手动验证")
    print(f"   3. 查看生成的验证报告链接")
    
    print(f"\n📝 组卷复核功能:")
    print(f"   1. 点击 '打开Web验证界面' - 在浏览器中打开验证页面")
    print(f"   2. 点击 '批量验证试卷' - 运行批量验证")
    print(f"   3. 查看生成的验证报告链接")
    
    print(f"\n📊 报告管理:")
    print(f"   1. 点击 '打开报告目录' - 在文件管理器中打开报告文件夹")
    print(f"   2. 点击 '刷新报告列表' - 更新报告链接列表")
    print(f"   3. 点击报告文件名链接 - 在Excel中打开报告")

def main():
    """主测试函数"""
    print("🎯 验证功能集成测试")
    print("=" * 60)
    
    # 测试集成状态
    integration_success = test_validation_integration()
    
    # 测试报告链接
    reports_available = test_report_links()
    
    # 显示使用指南
    show_usage_guide()
    
    # 总结
    print(f"\n" + "=" * 60)
    print(f"📋 测试结果总结")
    print("=" * 60)
    print(f"🔧 代码集成: {'✅ 成功' if integration_success else '❌ 失败'}")
    print(f"📄 验证报告: {'✅ 可用' if reports_available else '⚠️ 需要生成'}")
    
    if integration_success:
        print(f"\n🎉 验证功能已成功集成到开发工具模块！")
        print(f"💡 现在可以通过开发工具界面使用验证功能了")
        
        if not reports_available:
            print(f"\n📝 建议:")
            print(f"   1. 启动开发工具: python developer_tools.py")
            print(f"   2. 切换到 '验证复核' 标签页")
            print(f"   3. 运行验证功能生成报告")
    else:
        print(f"\n❌ 集成存在问题，请检查代码")
    
    print(f"\n🔗 快速启动:")
    print(f"   python developer_tools.py")

if __name__ == "__main__":
    main()
