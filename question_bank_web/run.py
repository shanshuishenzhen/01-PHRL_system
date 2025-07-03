#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理系统启动脚本
"""

import os
import sys
from app import app

def main():
    """主函数"""
    # 检查是否在静默模式下运行
    silent_mode = '--silent' in sys.argv or os.environ.get('FLASK_SILENT') == '1'

    if not silent_mode:
        print("🚀 启动题库管理系统...")
        print("📁 工作目录:", os.getcwd())
        print("🌐 访问地址: http://localhost:5000")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)

    try:
        # 在静默模式下不启用调试模式
        debug_mode = not silent_mode
        app.run(debug=debug_mode, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        if not silent_mode:
            print("\n👋 服务已停止")
    except Exception as e:
        if not silent_mode:
            print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 