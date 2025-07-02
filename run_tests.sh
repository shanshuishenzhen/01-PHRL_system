#!/bin/bash
# PH&RL 测试运行脚本 (Linux/macOS)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo "========================================"
    print_message $CYAN "PH&RL 在线考试系统 - 测试运行器"
    echo "========================================"
    echo
}

# 检查Python是否安装
check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_message $RED "❌ 错误: 未找到Python，请先安装Python 3.6+"
        exit 1
    fi
    
    # 优先使用python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
}

# 检查是否在项目根目录
check_project_root() {
    if [ ! -f "launcher.py" ]; then
        print_message $RED "❌ 错误: 请在项目根目录运行此脚本"
        exit 1
    fi
}

# 显示菜单
show_menu() {
    echo "请选择要运行的测试类型:"
    echo
    echo "1. 单元测试 (Unit Tests)"
    echo "2. 集成测试 (Integration Tests)"
    echo "3. 端到端测试 (E2E Tests)"
    echo "4. 所有测试 (All Tests)"
    echo "5. 冒烟测试 (Smoke Tests)"
    echo "6. 性能测试 (Performance Tests)"
    echo "7. 安全测试 (Security Tests)"
    echo "8. 代码质量检查 (Code Quality)"
    echo "9. 生成测试数据 (Generate Test Data)"
    echo "0. 退出"
    echo
}

# 运行测试并处理结果
run_test() {
    local test_type=$1
    local description=$2
    local icon=$3
    
    echo
    print_message $BLUE "${icon} ${description}..."
    
    if $PYTHON_CMD scripts/run_tests.py $test_type -v; then
        print_message $GREEN "✅ 测试执行完成！"
        return 0
    else
        print_message $RED "❌ 测试执行失败！"
        return 1
    fi
}

# 检查并显示报告
check_reports() {
    if [ -d "test_reports" ]; then
        echo
        print_message $YELLOW "📊 测试报告已生成在 test_reports 目录中"
        echo "   - 覆盖率报告: test_reports/full_coverage/index.html"
        echo "   - 测试报告: test_reports/full_report.html"
        echo "   - 报告摘要: test_reports/test_summary.md"
    fi
}

# 主循环
main_loop() {
    while true; do
        show_menu
        read -p "请输入选择 (0-9): " choice
        
        case $choice in
            1)
                run_test "unit" "运行单元测试" "🧪"
                check_reports
                ;;
            2)
                run_test "integration" "运行集成测试" "🔗"
                check_reports
                ;;
            3)
                run_test "e2e" "运行端到端测试" "🎯"
                check_reports
                ;;
            4)
                echo
                print_message $BLUE "🚀 运行所有测试..."
                if $PYTHON_CMD scripts/run_tests.py all -v --report; then
                    print_message $GREEN "✅ 测试执行完成！"
                else
                    print_message $RED "❌ 测试执行失败！"
                fi
                check_reports
                ;;
            5)
                run_test "smoke" "运行冒烟测试" "💨"
                ;;
            6)
                run_test "performance" "运行性能测试" "⚡"
                check_reports
                ;;
            7)
                run_test "security" "运行安全测试" "🔒"
                check_reports
                ;;
            8)
                run_test "quality" "运行代码质量检查" "📊"
                check_reports
                ;;
            9)
                echo
                print_message $BLUE "📁 生成测试数据..."
                if $PYTHON_CMD tests/generate_test_data.py; then
                    print_message $GREEN "✅ 测试数据生成完成！"
                else
                    print_message $RED "❌ 测试数据生成失败！"
                fi
                ;;
            0)
                echo
                print_message $CYAN "👋 感谢使用 PH&RL 测试运行器！"
                exit 0
                ;;
            *)
                echo
                print_message $RED "❌ 无效选择，请输入 0-9 之间的数字"
                echo
                continue
                ;;
        esac
        
        echo
        read -p "是否继续运行其他测试? (y/n): " continue_choice
        if [[ ! $continue_choice =~ ^[Yy]$ ]]; then
            break
        fi
        echo
    done
}

# 主函数
main() {
    print_header
    check_python
    check_project_root
    
    # 如果有命令行参数，直接运行对应测试
    if [ $# -gt 0 ]; then
        case $1 in
            "unit"|"integration"|"e2e"|"all"|"smoke"|"performance"|"security"|"quality")
                run_test $1 "运行 $1 测试" "🧪"
                check_reports
                ;;
            "generate")
                print_message $BLUE "📁 生成测试数据..."
                $PYTHON_CMD tests/generate_test_data.py
                ;;
            *)
                print_message $RED "❌ 未知的测试类型: $1"
                echo "支持的类型: unit, integration, e2e, all, smoke, performance, security, quality, generate"
                exit 1
                ;;
        esac
    else
        main_loop
    fi
    
    echo
    print_message $CYAN "👋 感谢使用 PH&RL 测试运行器！"
}

# 运行主函数
main "$@"
