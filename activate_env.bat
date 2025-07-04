@echo off
echo ========================================
echo   PH&RL 在线考试系统 - 环境激活脚本
echo ========================================
echo.

REM 激活Python虚拟环境
echo [1/3] 激活Python虚拟环境...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 无法激活Python虚拟环境
    pause
    exit /b 1
)
echo ✓ Python虚拟环境已激活

REM 显示Python版本和已安装的包
echo.
echo [2/3] 检查Python环境...
python --version
echo ✓ Python环境检查完成

REM 显示Node.js版本
echo.
echo [3/3] 检查Node.js环境...
node --version
npm --version
echo ✓ Node.js环境检查完成

echo.
echo ========================================
echo   环境准备完成！
echo ========================================
echo.
echo 可用的启动命令:
echo   - python launcher.py          启动完整系统
echo   - python question_bank_web\app.py  启动题库管理
echo   - cd user_management ^&^& npm start   启动用户管理
echo   - cd grading_center ^&^& npm test     运行阅卷中心测试
echo.
echo 按任意键继续...
pause >nul
