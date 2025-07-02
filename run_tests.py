#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL在线考试系统测试运行器

这个脚本提供了多种测试运行选项，包括：
- 单元测试
- 集成测试
- 端到端测试
- 性能测试
- 覆盖率报告
- 并行测试

使用方法：
    python run_tests.py --help
    python run_tests.py --unit
    python run_tests.py --integration
    python run_tests.py --e2e
    python run_tests.py --all
    python run_tests.py --coverage
    python run_tests.py --parallel
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(command, description=""):
    """运行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description or command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"\n✅ 成功: {description or command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 失败: {description or command}")
        print(f"错误代码: {e.returncode}")
        return False


def check_dependencies():
    """检查测试依赖"""
    print("检查测试依赖...")
    
    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-html",
        "pytest-xdist",
        "pytest-timeout",
        "pytest-mock"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少以下测试依赖: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有测试依赖已安装")
    return True


def run_unit_tests():
    """运行单元测试"""
    command = "pytest tests/unit/ -v --tb=short"
    return run_command(command, "单元测试")


def run_integration_tests():
    """运行集成测试"""
    command = "pytest tests/integration/ -v --tb=short"
    return run_command(command, "集成测试")


def run_e2e_tests():
    """运行端到端测试"""
    command = "pytest tests/e2e/ -v --tb=short"
    return run_command(command, "端到端测试")


def run_all_tests():
    """运行所有测试"""
    command = "pytest tests/ -v --tb=short"
    return run_command(command, "所有测试")


def run_fast_tests():
    """运行快速测试"""
    command = "pytest -m 'fast or unit' -v --tb=short"
    return run_command(command, "快速测试")


def run_slow_tests():
    """运行慢速测试"""
    command = "pytest -m 'slow' -v --tb=short"
    return run_command(command, "慢速测试")


def run_smoke_tests():
    """运行冒烟测试"""
    command = "pytest -m 'smoke' -v --tb=short"
    return run_command(command, "冒烟测试")


def run_coverage_tests():
    """运行覆盖率测试"""
    command = (
        "pytest tests/ --cov=. --cov-report=html:htmlcov "
        "--cov-report=term-missing --cov-report=xml "
        "--cov-fail-under=70 -v"
    )
    return run_command(command, "覆盖率测试")


def run_parallel_tests():
    """运行并行测试"""
    command = "pytest tests/ -n auto -v --tb=short"
    return run_command(command, "并行测试")


def run_specific_module_tests(module):
    """运行特定模块的测试"""
    command = f"pytest -m 'module_{module}' -v --tb=short"
    return run_command(command, f"{module}模块测试")


def run_performance_tests():
    """运行性能测试"""
    command = "pytest -m 'performance' -v --tb=short --durations=10"
    return run_command(command, "性能测试")


def run_security_tests():
    """运行安全测试"""
    command = "pytest -m 'security' -v --tb=short"
    return run_command(command, "安全测试")


def generate_test_report():
    """生成测试报告"""
    command = (
        "pytest tests/ --html=tests/reports/report.html "
        "--self-contained-html --junitxml=tests/reports/junit.xml -v"
    )
    return run_command(command, "生成测试报告")


def clean_test_artifacts():
    """清理测试产物"""
    print("清理测试产物...")
    
    artifacts = [
        ".pytest_cache",
        "htmlcov",
        "tests/logs",
        "tests/reports",
        "__pycache__",
        "*.pyc",
        ".coverage"
    ]
    
    for artifact in artifacts:
        if Path(artifact).exists():
            if Path(artifact).is_file():
                Path(artifact).unlink()
                print(f"删除文件: {artifact}")
            else:
                import shutil
                shutil.rmtree(artifact)
                print(f"删除目录: {artifact}")
    
    print("✅ 测试产物清理完成")


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")
    
    # 创建必要的目录
    test_dirs = [
        "tests/logs",
        "tests/reports",
        "tests/data",
        "tests/temp"
    ]
    
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {test_dir}")
    
    # 设置环境变量
    os.environ["PYTHONPATH"] = str(Path.cwd())
    os.environ["TESTING"] = "true"
    
    print("✅ 测试环境设置完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PH&RL在线考试系统测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_tests.py --unit              # 运行单元测试
  python run_tests.py --integration       # 运行集成测试
  python run_tests.py --e2e               # 运行端到端测试
  python run_tests.py --all               # 运行所有测试
  python run_tests.py --coverage          # 运行覆盖率测试
  python run_tests.py --parallel          # 运行并行测试
  python run_tests.py --fast              # 运行快速测试
  python run_tests.py --slow              # 运行慢速测试
  python run_tests.py --smoke             # 运行冒烟测试
  python run_tests.py --module question_bank  # 运行特定模块测试
  python run_tests.py --performance       # 运行性能测试
  python run_tests.py --security          # 运行安全测试
  python run_tests.py --report            # 生成测试报告
  python run_tests.py --clean             # 清理测试产物
        """
    )
    
    # 测试类型选项
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--e2e", action="store_true", help="运行端到端测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    
    # 测试模式选项
    parser.add_argument("--fast", action="store_true", help="运行快速测试")
    parser.add_argument("--slow", action="store_true", help="运行慢速测试")
    parser.add_argument("--smoke", action="store_true", help="运行冒烟测试")
    parser.add_argument("--coverage", action="store_true", help="运行覆盖率测试")
    parser.add_argument("--parallel", action="store_true", help="运行并行测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--security", action="store_true", help="运行安全测试")
    
    # 特定模块测试
    parser.add_argument("--module", type=str, help="运行特定模块的测试")
    
    # 工具选项
    parser.add_argument("--report", action="store_true", help="生成测试报告")
    parser.add_argument("--clean", action="store_true", help="清理测试产物")
    parser.add_argument("--setup", action="store_true", help="设置测试环境")
    parser.add_argument("--check-deps", action="store_true", help="检查测试依赖")
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # 设置测试环境
    setup_test_environment()
    
    # 检查依赖
    if args.check_deps or not check_dependencies():
        if not check_dependencies():
            sys.exit(1)
        return
    
    success = True
    
    # 执行相应的测试
    if args.clean:
        clean_test_artifacts()
    elif args.setup:
        setup_test_environment()
    elif args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.e2e:
        success = run_e2e_tests()
    elif args.all:
        success = run_all_tests()
    elif args.fast:
        success = run_fast_tests()
    elif args.slow:
        success = run_slow_tests()
    elif args.smoke:
        success = run_smoke_tests()
    elif args.coverage:
        success = run_coverage_tests()
    elif args.parallel:
        success = run_parallel_tests()
    elif args.performance:
        success = run_performance_tests()
    elif args.security:
        success = run_security_tests()
    elif args.module:
        success = run_specific_module_tests(args.module)
    elif args.report:
        success = generate_test_report()
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
