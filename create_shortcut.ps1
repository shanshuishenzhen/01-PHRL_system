# 创建Windows快捷方式脚本

# 获取当前目录
$currentDir = Get-Location

# 创建快捷方式对象
$WshShell = New-Object -comObject WScript.Shell

# 桌面快捷方式
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\PH&RL 考试客户端.lnk"
$shortcut = $WshShell.CreateShortcut($shortcutPath)

# 设置快捷方式属性
$shortcut.TargetPath = "python.exe"
$shortcut.Arguments = "standalone_client.py"
$shortcut.WorkingDirectory = $currentDir
$shortcut.Description = "PH&RL 考试系统 - 独立客户端"
$shortcut.IconLocation = "python.exe,0"  # 使用Python图标

# 保存快捷方式
$shortcut.Save()

Write-Host "✅ 桌面快捷方式已创建: $shortcutPath" -ForegroundColor Green

# 开始菜单快捷方式
$startMenuPath = [Environment]::GetFolderPath("StartMenu")
$programsPath = "$startMenuPath\Programs"
$shortcutPath2 = "$programsPath\PH&RL 考试客户端.lnk"
$shortcut2 = $WshShell.CreateShortcut($shortcutPath2)

$shortcut2.TargetPath = "python.exe"
$shortcut2.Arguments = "standalone_client.py"
$shortcut2.WorkingDirectory = $currentDir
$shortcut2.Description = "PH&RL 考试系统 - 独立客户端"
$shortcut2.IconLocation = "python.exe,0"

$shortcut2.Save()

Write-Host "✅ 开始菜单快捷方式已创建: $shortcutPath2" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 快捷方式创建完成！" -ForegroundColor Cyan
Write-Host "现在可以通过以下方式启动客户端:" -ForegroundColor Yellow
Write-Host "1. 双击桌面上的 'PH&RL 考试客户端' 图标" -ForegroundColor White
Write-Host "2. 从开始菜单搜索 'PH&RL 考试客户端'" -ForegroundColor White
