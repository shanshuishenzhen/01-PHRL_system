#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控台修复测试脚本

测试修复后的主控台功能，包括：
1. 滚动功能
2. 代码问题修复
3. 模块启动功能
4. 界面响应性
"""

import sys
import os
import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入主控台模块
try:
    from main_console import MainConsole
    MAIN_CONSOLE_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入主控台模块: {e}")
    MAIN_CONSOLE_AVAILABLE = False

class TestMainConsoleFix(unittest.TestCase):
    """主控台修复测试类"""
    
    def setUp(self):
        """测试前准备"""
        if not MAIN_CONSOLE_AVAILABLE:
            self.skipTest("主控台模块不可用")
        
        # 创建测试用的根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口
        
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_main_console_initialization(self):
        """测试主控台初始化"""
        try:
            # 创建主控台实例
            console = MainConsole()
            
            # 检查基本属性
            self.assertIsNotNone(console.root)
            self.assertIsNotNone(console.module_status)
            self.assertIsNotNone(console.config)
            
            # 检查滚动相关属性
            self.assertTrue(hasattr(console, 'canvas'))
            self.assertTrue(hasattr(console, 'scrollbar'))
            self.assertTrue(hasattr(console, 'scrollable_frame'))
            
            print("✅ 主控台初始化测试通过")
            
        except Exception as e:
            self.fail(f"主控台初始化失败: {e}")
    
    def test_scroll_functionality(self):
        """测试滚动功能"""
        try:
            console = MainConsole()
            
            # 检查滚动方法是否存在
            self.assertTrue(hasattr(console, '_on_mousewheel'))
            self.assertTrue(hasattr(console, '_on_canvas_configure'))
            self.assertTrue(hasattr(console, '_update_scroll_region'))
            
            # 测试滚动方法是否可调用
            self.assertTrue(callable(console._on_mousewheel))
            self.assertTrue(callable(console._on_canvas_configure))
            self.assertTrue(callable(console._update_scroll_region))
            
            print("✅ 滚动功能测试通过")
            
        except Exception as e:
            self.fail(f"滚动功能测试失败: {e}")
    
    def test_module_status_structure(self):
        """测试模块状态结构"""
        try:
            console = MainConsole()
            
            # 检查模块状态字典
            expected_modules = [
                "question_bank", "user_management", "score_statistics",
                "grading_center", "client", "exam_management",
                "conversation", "developer_tools"
            ]
            
            for module in expected_modules:
                self.assertIn(module, console.module_status)
                module_info = console.module_status[module]
                
                # 检查必要的键
                self.assertIn("status", module_info)
                self.assertIn("process", module_info)
                self.assertIn("pid", module_info)
                self.assertIn("start_time", module_info)
            
            print("✅ 模块状态结构测试通过")
            
        except Exception as e:
            self.fail(f"模块状态结构测试失败: {e}")
    
    @patch('subprocess.Popen')
    def test_developer_tools_start(self, mock_popen):
        """测试开发工具启动功能"""
        try:
            console = MainConsole()
            
            # 模拟进程对象
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process
            
            # 模拟文件存在
            with patch('os.path.exists', return_value=True):
                # 调用开发工具启动方法
                console.start_developer_tools()
                
                # 检查状态是否更新
                self.assertEqual(console.module_status["developer_tools"]["status"], "运行中")
                self.assertEqual(console.module_status["developer_tools"]["process"], mock_process)
                self.assertEqual(console.module_status["developer_tools"]["pid"], 12345)
            
            print("✅ 开发工具启动测试通过")
            
        except Exception as e:
            self.fail(f"开发工具启动测试失败: {e}")
    
    def test_config_loading(self):
        """测试配置加载"""
        try:
            console = MainConsole()
            
            # 检查配置是否加载
            self.assertIsNotNone(console.config)
            self.assertIsInstance(console.config, dict)
            
            # 检查默认配置项
            expected_keys = ["version", "update_interval", "module_ports"]
            for key in expected_keys:
                self.assertIn(key, console.config)
            
            print("✅ 配置加载测试通过")
            
        except Exception as e:
            self.fail(f"配置加载测试失败: {e}")
    
    def test_system_resources_monitoring(self):
        """测试系统资源监控"""
        try:
            console = MainConsole()
            
            # 检查系统资源字典
            self.assertIsNotNone(console.system_resources)
            self.assertIsInstance(console.system_resources, dict)
            
            expected_keys = ['cpu_usage', 'memory_usage', 'disk_usage']
            for key in expected_keys:
                self.assertIn(key, console.system_resources)
            
            # 测试资源更新方法
            console.update_system_resources()
            
            print("✅ 系统资源监控测试通过")
            
        except Exception as e:
            self.fail(f"系统资源监控测试失败: {e}")
    
    def test_ui_components(self):
        """测试UI组件"""
        try:
            console = MainConsole()
            
            # 检查主要UI组件是否存在
            self.assertIsNotNone(console.canvas)
            self.assertIsNotNone(console.scrollbar)
            self.assertIsNotNone(console.scrollable_frame)
            
            # 检查时间标签
            self.assertTrue(hasattr(console, 'time_label'))
            
            print("✅ UI组件测试通过")
            
        except Exception as e:
            self.fail(f"UI组件测试失败: {e}")

def run_visual_test():
    """运行可视化测试"""
    print("\n🎨 开始可视化测试...")
    
    try:
        # 创建主控台实例
        app = MainConsole()
        
        # 设置测试窗口标题
        app.root.title("PH&RL 主控台 - 修复测试版")
        
        # 添加测试信息
        test_info = tk.Label(
            app.scrollable_frame,
            text="🧪 这是修复测试版本 - 请测试滚动功能和模块启动",
            font=("Microsoft YaHei", 10),
            fg="red",
            bg="yellow"
        )
        test_info.pack(pady=10)
        
        print("✅ 主控台已启动，请手动测试以下功能：")
        print("   1. 鼠标滚轮滚动")
        print("   2. 窗口大小调整")
        print("   3. 模块按钮点击")
        print("   4. 界面响应性")
        print("   5. 关闭窗口退出测试")
        
        # 启动主循环
        app.root.mainloop()
        
        print("✅ 可视化测试完成")
        
    except Exception as e:
        print(f"❌ 可视化测试失败: {e}")

def main():
    """主函数"""
    print("🔧 PH&RL 主控台修复测试")
    print("=" * 50)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if not MAIN_CONSOLE_AVAILABLE:
        print("❌ 主控台模块不可用，无法进行测试")
        return
    
    # 运行单元测试
    print("\n🧪 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 询问是否运行可视化测试
    print("\n" + "=" * 50)
    response = input("是否运行可视化测试？(y/n): ").lower().strip()
    
    if response in ['y', 'yes', '是']:
        run_visual_test()
    else:
        print("跳过可视化测试")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
