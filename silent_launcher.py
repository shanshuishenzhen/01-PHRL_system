#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静默启动器 - 无中间窗口版本
"""

import subprocess
import sys
import os
import time

def start_module_silent(module_name, script_path, wait_time=2):
    """静默启动模块"""
    try:
        if os.name == 'nt':  # Windows
            # 使用 CREATE_NO_WINDOW 标志隐藏窗口
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                [sys.executable, script_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print(f"✅ {module_name} 已静默启动 (PID: {process.pid})")
        time.sleep(wait_time)
        return process
        
    except Exception as e:
        print(f"❌ 启动 {module_name} 失败: {e}")
        return None

def main():
    """主函数"""
    print("🔇 静默启动器 - 无中间窗口版本")
    print("=" * 50)
    
    # 启动各个模块
    modules = [
        ("题库管理", os.path.join("question_bank_web", "app.py")),
        ("用户管理", os.path.join("user_management", "simple_user_manager.py")),
        ("考试管理", os.path.join("exam_management", "simple_exam_manager.py")),
        ("客户端", os.path.join("client", "client_app.py")),
    ]
    
    processes = []
    for name, path in modules:
        if os.path.exists(path):
            process = start_module_silent(name, path)
            if process:
                processes.append((name, process))
        else:
            print(f"⚠️ 模块文件不存在: {path}")
    
    print(f"\n🎉 已启动 {len(processes)} 个模块")
    
    # 保持进程运行
    try:
        while True:
            time.sleep(10)
            # 检查进程状态
            for name, process in processes[:]:
                if process.poll() is not None:
                    print(f"⚠️ {name} 进程已退出")
                    processes.remove((name, process))
            
            if not processes:
                print("所有进程已退出，启动器结束")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 收到中断信号，正在关闭所有进程...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"✅ {name} 已关闭")
            except:
                pass

if __name__ == "__main__":
    main()
