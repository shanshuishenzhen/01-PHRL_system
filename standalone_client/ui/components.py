#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用UI组件

提供可重用的UI组件和工具函数。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Any, Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)

class LoadingDialog:
    """加载对话框"""
    
    def __init__(self, parent: tk.Widget, title: str = "加载中", message: str = "请稍候..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建内容
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        # 消息标签
        ttk.Label(frame, text=message, font=('Microsoft YaHei', 12)).pack(pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=10)
        self.progress.start()
        
        # 居中对话框
        self._center_dialog()
    
    def _center_dialog(self):
        """居中对话框"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def close(self):
        """关闭对话框"""
        try:
            self.progress.stop()
            self.dialog.destroy()
        except:
            pass

class ServerConfigDialog:
    """服务器配置对话框"""
    
    def __init__(self, parent: tk.Widget, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("服务器配置")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # 模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self._create_widgets()
        self._load_current_config()
        
        # 居中显示
        self._center_dialog()
    
    def _create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 服务器地址
        ttk.Label(main_frame, text="服务器地址:").grid(row=0, column=0, sticky='w', pady=5)
        self.host_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.host_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # 端口
        ttk.Label(main_frame, text="端口:").grid(row=1, column=0, sticky='w', pady=5)
        self.port_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.port_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # 协议
        ttk.Label(main_frame, text="协议:").grid(row=2, column=0, sticky='w', pady=5)
        self.protocol_var = tk.StringVar()
        protocol_combo = ttk.Combobox(main_frame, textvariable=self.protocol_var, values=['http', 'https'], width=27)
        protocol_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        protocol_combo.state(['readonly'])
        
        # 超时时间
        ttk.Label(main_frame, text="超时时间(秒):").grid(row=3, column=0, sticky='w', pady=5)
        self.timeout_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.timeout_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 测试连接按钮
        ttk.Button(button_frame, text="测试连接", command=self._test_connection).pack(side='left', padx=5)
        
        # 保存按钮
        ttk.Button(button_frame, text="保存", command=self._save_config).pack(side='left', padx=5)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def _load_current_config(self):
        """加载当前配置"""
        self.host_var.set(self.config_manager.get('server.host', 'localhost'))
        self.port_var.set(str(self.config_manager.get('server.port', 5000)))
        self.protocol_var.set(self.config_manager.get('server.protocol', 'http'))
        self.timeout_var.set(str(self.config_manager.get('server.timeout', 30)))
    
    def _test_connection(self):
        """测试连接"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get().strip())
            protocol = self.protocol_var.get()
            
            if not host:
                messagebox.showerror("错误", "请输入服务器地址")
                return
            
            # 测试连接
            from utils.network import NetworkUtils
            url = f"{protocol}://{host}:{port}/api/ping"
            
            loading = LoadingDialog(self.dialog, "测试连接", "正在测试服务器连接...")
            
            def test_in_thread():
                import threading
                import time
                
                def test():
                    time.sleep(0.5)  # 给用户看到加载效果
                    result = NetworkUtils.ping_server(url, timeout=10)
                    
                    self.dialog.after(0, lambda: self._show_test_result(loading, result))
                
                threading.Thread(target=test, daemon=True).start()
            
            test_in_thread()
            
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"测试连接失败: {e}")
    
    def _show_test_result(self, loading: LoadingDialog, result: Optional[float]):
        """显示测试结果"""
        loading.close()
        
        if result is not None:
            messagebox.showinfo("连接成功", f"服务器连接正常\n响应时间: {result:.2f}ms")
        else:
            messagebox.showerror("连接失败", "无法连接到服务器，请检查配置")
    
    def _save_config(self):
        """保存配置"""
        try:
            host = self.host_var.get().strip()
            port_str = self.port_var.get().strip()
            protocol = self.protocol_var.get()
            timeout_str = self.timeout_var.get().strip()
            
            # 验证输入
            if not host:
                messagebox.showerror("错误", "请输入服务器地址")
                return
            
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("错误", "端口必须是1-65535之间的数字")
                return
            
            try:
                timeout = int(timeout_str)
                if timeout < 1:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("错误", "超时时间必须是大于0的数字")
                return
            
            # 保存配置
            self.config_manager.set('server.host', host)
            self.config_manager.set('server.port', port)
            self.config_manager.set('server.protocol', protocol)
            self.config_manager.set('server.timeout', timeout)
            
            messagebox.showinfo("成功", "服务器配置已保存")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def _center_dialog(self):
        """居中对话框"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

class ExamCard:
    """考试卡片组件"""
    
    def __init__(self, parent: tk.Widget, exam_data: Dict[str, Any], on_click: Callable):
        self.parent = parent
        self.exam_data = exam_data
        self.on_click = on_click
        
        # 创建卡片框架
        self.frame = ttk.Frame(parent, relief='raised', borderwidth=1)
        self.frame.pack(fill='x', padx=10, pady=5)
        
        # 创建内容
        self._create_content()
        
        # 绑定点击事件
        self._bind_click_events()
    
    def _create_content(self):
        """创建卡片内容"""
        # 主要信息框架
        info_frame = ttk.Frame(self.frame, padding="15")
        info_frame.pack(fill='both', expand=True)
        
        # 考试标题
        title = self.exam_data.get('title', '未知考试')
        title_label = ttk.Label(info_frame, text=title, font=('Microsoft YaHei', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        # 考试信息
        duration = self.exam_data.get('duration', 0)
        question_count = self.exam_data.get('question_count', 0)
        
        info_text = f"时长: {duration}分钟 | 题目数: {question_count}题"
        info_label = ttk.Label(info_frame, text=info_text, foreground='gray')
        info_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        # 考试描述
        description = self.exam_data.get('description', '')
        if description:
            desc_label = ttk.Label(info_frame, text=description, wraplength=400)
            desc_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # 状态和按钮
        status = self.exam_data.get('status', 'available')
        if status == 'available':
            status_text = "可参加"
            status_color = 'green'
        elif status == 'completed':
            status_text = "已完成"
            status_color = 'blue'
        elif status == 'in_progress':
            status_text = "进行中"
            status_color = 'orange'
        else:
            status_text = "不可用"
            status_color = 'red'
        
        status_label = ttk.Label(info_frame, text=status_text, foreground=status_color)
        status_label.grid(row=3, column=0, sticky='w')
        
        # 开始按钮
        if status in ['available', 'in_progress']:
            button_text = "继续考试" if status == 'in_progress' else "开始考试"
            start_button = ttk.Button(info_frame, text=button_text, command=self._on_start_click)
            start_button.grid(row=3, column=1, sticky='e')
    
    def _bind_click_events(self):
        """绑定点击事件"""
        def on_click(event):
            self.on_click(self.exam_data)
        
        # 为框架和所有子组件绑定点击事件
        self.frame.bind("<Button-1>", on_click)
        for child in self.frame.winfo_children():
            child.bind("<Button-1>", on_click)
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", on_click)
    
    def _on_start_click(self):
        """开始考试按钮点击"""
        self.on_click(self.exam_data)

class QuestionNavigator:
    """题目导航器"""
    
    def __init__(self, parent: tk.Widget, question_count: int, on_question_select: Callable):
        self.parent = parent
        self.question_count = question_count
        self.on_question_select = on_question_select
        self.current_question = 0
        self.answered_questions = set()
        
        # 创建导航框架
        self.frame = ttk.LabelFrame(parent, text="题目导航", padding="10")
        self.frame.pack(fill='x', padx=10, pady=5)
        
        # 创建导航按钮
        self._create_navigation_buttons()
    
    def _create_navigation_buttons(self):
        """创建导航按钮"""
        # 按钮框架
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x')
        
        self.nav_buttons = []
        
        # 创建题目按钮（每行显示10个）
        for i in range(self.question_count):
            row = i // 10
            col = i % 10
            
            button = ttk.Button(
                button_frame, 
                text=str(i + 1), 
                width=4,
                command=lambda idx=i: self._on_question_click(idx)
            )
            button.grid(row=row, column=col, padx=2, pady=2)
            self.nav_buttons.append(button)
        
        # 更新按钮状态
        self._update_button_states()
    
    def _on_question_click(self, question_index: int):
        """题目按钮点击"""
        self.current_question = question_index
        self._update_button_states()
        self.on_question_select(question_index)
    
    def set_current_question(self, question_index: int):
        """设置当前题目"""
        self.current_question = question_index
        self._update_button_states()
    
    def mark_answered(self, question_index: int):
        """标记题目已答"""
        self.answered_questions.add(question_index)
        self._update_button_states()
    
    def _update_button_states(self):
        """更新按钮状态"""
        for i, button in enumerate(self.nav_buttons):
            if i == self.current_question:
                # 当前题目 - 蓝色
                button.configure(style='Current.TButton')
            elif i in self.answered_questions:
                # 已答题目 - 绿色
                button.configure(style='Answered.TButton')
            else:
                # 未答题目 - 默认
                button.configure(style='TButton')

def show_error(parent: tk.Widget, title: str, message: str):
    """显示错误对话框"""
    messagebox.showerror(title, message, parent=parent)

def show_warning(parent: tk.Widget, title: str, message: str):
    """显示警告对话框"""
    messagebox.showwarning(title, message, parent=parent)

def show_info(parent: tk.Widget, title: str, message: str):
    """显示信息对话框"""
    messagebox.showinfo(title, message, parent=parent)

def ask_yes_no(parent: tk.Widget, title: str, message: str) -> bool:
    """显示是否确认对话框"""
    return messagebox.askyesno(title, message, parent=parent)
