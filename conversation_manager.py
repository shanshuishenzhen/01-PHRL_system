# -*- coding: utf-8 -*-
"""
对话上下文管理模块启动脚本

提供直接启动对话上下文管理模块的功能，无需通过主控制台。

更新日志：
- 2024-07-10：初始版本，提供基本对话上下文管理功能
"""

import os
import sys
import tkinter as tk
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent))

# 导入对话上下文管理UI模块
from common.conversation_ui import show_conversation_ui
from common.logger import get_logger

# 创建日志记录器
logger = get_logger("conversation_manager", os.path.join(os.path.dirname(__file__), "logs", "conversation_manager.log"))

def main():
    """
    主函数，启动对话上下文管理模块
    """
    try:
        logger.info("启动对话上下文管理模块")
        show_conversation_ui()
    except Exception as e:
        logger.error(f"启动对话上下文管理模块失败: {e}")
        print(f"启动对话上下文管理模块失败: {e}")

if __name__ == "__main__":
    main()