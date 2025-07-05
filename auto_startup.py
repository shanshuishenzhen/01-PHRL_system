#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动启动配置工具
"""

import os
import sys
import winreg
import shutil
from pathlib import Path

def add_to_startup():
    """添加到Windows启动项"""
    try:
        # 获取当前脚本路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        client_path = os.path.join(current_dir, "standalone_client.py")
        
        if not os.path.exists(client_path):
            print("❌ 错误：找不到 standalone_client.py")
            return False
        
        # 创建启动批处理文件
        startup_bat = os.path.join(current_dir, "startup_client.bat")
        with open(startup_bat, 'w', encoding='utf-8') as f:
            f.write(f'''@echo off
cd /d "{current_dir}"
python standalone_client.py
''')
        
        # 添加到注册表启动项
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "PH&RL_ExamClient", 0, winreg.REG_SZ, startup_bat)
        winreg.CloseKey(key)
        
        print("✅ 已添加到Windows启动项")
        print(f"   启动文件: {startup_bat}")
        return True
        
    except Exception as e:
        print(f"❌ 添加启动项失败: {e}")
        return False

def remove_from_startup():
    """从Windows启动项移除"""
    try:
        # 从注册表移除
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "PH&RL_ExamClient")
            print("✅ 已从Windows启动项移除")
        except FileNotFoundError:
            print("⚠️ 启动项不存在")
        winreg.CloseKey(key)
        
        # 删除启动批处理文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        startup_bat = os.path.join(current_dir, "startup_client.bat")
        if os.path.exists(startup_bat):
            os.remove(startup_bat)
            print("✅ 已删除启动文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 移除启动项失败: {e}")
        return False

def create_desktop_shortcut():
    """创建桌面快捷方式"""
    try:
        import win32com.client
        
        # 获取桌面路径
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "PH&RL 考试客户端.lnk"
        
        # 获取当前目录和Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        python_exe = sys.executable
        
        # 创建快捷方式
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = python_exe
        shortcut.Arguments = "standalone_client.py"
        shortcut.WorkingDirectory = current_dir
        shortcut.Description = "PH&RL 考试系统 - 独立客户端"
        shortcut.save()
        
        print(f"✅ 桌面快捷方式已创建: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠️ 需要安装 pywin32: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ 创建快捷方式失败: {e}")
        return False

def setup_auto_startup():
    """设置自动启动"""
    print("🔧 PH&RL 考试客户端 - 自动启动配置")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 添加到Windows启动项（开机自动启动）")
        print("2. 从Windows启动项移除")
        print("3. 创建桌面快捷方式")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            print("\n正在添加到启动项...")
            if add_to_startup():
                print("✅ 配置完成！客户端将在下次开机时自动启动")
            
        elif choice == "2":
            print("\n正在从启动项移除...")
            if remove_from_startup():
                print("✅ 移除完成！客户端不再自动启动")
            
        elif choice == "3":
            print("\n正在创建桌面快捷方式...")
            if create_desktop_shortcut():
                print("✅ 快捷方式创建完成！")
            
        elif choice == "4":
            print("退出配置工具")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add":
            add_to_startup()
        elif sys.argv[1] == "--remove":
            remove_from_startup()
        elif sys.argv[1] == "--shortcut":
            create_desktop_shortcut()
        else:
            print("用法:")
            print("  python auto_startup.py --add      # 添加到启动项")
            print("  python auto_startup.py --remove   # 从启动项移除")
            print("  python auto_startup.py --shortcut # 创建快捷方式")
    else:
        setup_auto_startup()

if __name__ == "__main__":
    main()
