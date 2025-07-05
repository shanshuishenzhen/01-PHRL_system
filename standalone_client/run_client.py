#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端启动脚本

用于启动PH&RL独立考试客户端。
"""

import sys
import os
from pathlib import Path

# 添加当前目录到系统路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

def main():
    """主函数"""
    try:
        print("🚀 启动 PH&RL 考试客户端...")
        
        # 导入主模块
        from main import main as client_main
        
        # 启动客户端
        client_main()
        
    except KeyboardInterrupt:
        print("\n👋 用户取消，客户端已退出")
    except Exception as e:
        print(f"❌ 客户端启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
