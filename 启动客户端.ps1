# PH&RL 考试系统 - 独立客户端启动脚本
# PowerShell版本

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PH&RL 考试系统 - 独立客户端" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python环境
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python未找到"
    }
} catch {
    Write-Host "❌ 错误：未找到Python环境" -ForegroundColor Red
    Write-Host "请确保已安装Python并添加到系统PATH" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}

# 检查客户端文件
$clientFile = "standalone_client.py"
if (Test-Path $clientFile) {
    Write-Host "✅ 客户端文件检查通过: $clientFile" -ForegroundColor Green
} else {
    Write-Host "❌ 错误：未找到客户端文件 $clientFile" -ForegroundColor Red
    Write-Host "请确保在正确的目录中运行此脚本" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}

# 检查依赖库
Write-Host ""
Write-Host "🔍 检查依赖库..." -ForegroundColor Yellow

$requiredModules = @("tkinter", "requests")
$missingModules = @()

foreach ($module in $requiredModules) {
    try {
        $result = python -c "import $module; print('OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $module" -ForegroundColor Green
        } else {
            $missingModules += $module
            Write-Host "  ❌ $module" -ForegroundColor Red
        }
    } catch {
        $missingModules += $module
        Write-Host "  ❌ $module" -ForegroundColor Red
    }
}

if ($missingModules.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ 缺少必要的依赖库: $($missingModules -join ', ')" -ForegroundColor Red
    Write-Host "请运行以下命令安装:" -ForegroundColor Yellow
    Write-Host "pip install $($missingModules -join ' ')" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}

Write-Host ""
Write-Host "🚀 正在启动独立客户端..." -ForegroundColor Green
Write-Host ""

# 启动客户端
try {
    python $clientFile
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "❌ 客户端异常退出，错误代码: $exitCode" -ForegroundColor Red
        Write-Host "请检查日志文件 standalone_client.log 获取详细信息" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "❌ 启动客户端时发生错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "客户端已关闭" -ForegroundColor Gray
Read-Host "按任意键退出"
