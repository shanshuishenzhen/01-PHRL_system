@echo off
REM PH&RL 测试运行批处理脚本 (Windows)

setlocal enabledelayedexpansion

echo ========================================
echo PH^&RL 在线考试系统 - 测试运行器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

REM 检查是否在项目根目录
if not exist "launcher.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 显示菜单
:menu
echo 请选择要运行的测试类型:
echo.
echo 1. 单元测试 (Unit Tests)
echo 2. 集成测试 (Integration Tests)  
echo 3. 端到端测试 (E2E Tests)
echo 4. 所有测试 (All Tests)
echo 5. 冒烟测试 (Smoke Tests)
echo 6. 性能测试 (Performance Tests)
echo 7. 安全测试 (Security Tests)
echo 8. 代码质量检查 (Code Quality)
echo 9. 生成测试数据 (Generate Test Data)
echo 0. 退出
echo.

set /p choice="请输入选择 (0-9): "

if "%choice%"=="1" goto unit_tests
if "%choice%"=="2" goto integration_tests
if "%choice%"=="3" goto e2e_tests
if "%choice%"=="4" goto all_tests
if "%choice%"=="5" goto smoke_tests
if "%choice%"=="6" goto performance_tests
if "%choice%"=="7" goto security_tests
if "%choice%"=="8" goto quality_checks
if "%choice%"=="9" goto generate_data
if "%choice%"=="0" goto exit
goto invalid_choice

:unit_tests
echo.
echo 🧪 运行单元测试...
python scripts/run_tests.py unit -v
goto test_complete

:integration_tests
echo.
echo 🔗 运行集成测试...
python scripts/run_tests.py integration -v
goto test_complete

:e2e_tests
echo.
echo 🎯 运行端到端测试...
python scripts/run_tests.py e2e -v
goto test_complete

:all_tests
echo.
echo 🚀 运行所有测试...
python scripts/run_tests.py all -v --report
goto test_complete

:smoke_tests
echo.
echo 💨 运行冒烟测试...
python scripts/run_tests.py smoke -v
goto test_complete

:performance_tests
echo.
echo ⚡ 运行性能测试...
python scripts/run_tests.py performance -v
goto test_complete

:security_tests
echo.
echo 🔒 运行安全测试...
python scripts/run_tests.py security
goto test_complete

:quality_checks
echo.
echo 📊 运行代码质量检查...
python scripts/run_tests.py quality
goto test_complete

:generate_data
echo.
echo 📁 生成测试数据...
python tests/generate_test_data.py
echo.
echo ✅ 测试数据生成完成！
goto menu_return

:test_complete
echo.
if errorlevel 1 (
    echo ❌ 测试执行失败！
) else (
    echo ✅ 测试执行完成！
)

REM 检查是否生成了报告
if exist "test_reports" (
    echo.
    echo 📊 测试报告已生成在 test_reports 目录中
    echo    - 覆盖率报告: test_reports\full_coverage\index.html
    echo    - 测试报告: test_reports\full_report.html
    echo    - 报告摘要: test_reports\test_summary.md
)

:menu_return
echo.
set /p continue="是否继续运行其他测试? (y/n): "
if /i "%continue%"=="y" goto menu
if /i "%continue%"=="yes" goto menu
goto exit

:invalid_choice
echo.
echo ❌ 无效选择，请输入 0-9 之间的数字
echo.
goto menu

:exit
echo.
echo 👋 感谢使用 PH^&RL 测试运行器！
pause
exit /b 0
