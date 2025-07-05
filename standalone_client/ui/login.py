#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录界面

用户登录界面，支持用户名密码登录和记住登录状态。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import TYPE_CHECKING

from core.config import client_config
from core.auth import auth_manager
from utils.logger import get_logger
from .components import LoadingDialog, ServerConfigDialog

if TYPE_CHECKING:
    from core.app import ExamClientApp

logger = get_logger(__name__)

class LoginView:
    """登录视图"""
    
    def __init__(self, parent: tk.Widget, app: 'ExamClientApp'):
        self.parent = parent
        self.app = app
        
        # 创建主框架
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True)
        
        # 变量
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.remember_var = tk.BooleanVar()
        
        # 创建界面
        self._create_widgets()
        self._load_saved_credentials()
        
        # 绑定回车键
        self.parent.bind('<Return>', lambda e: self._login())
        
        logger.debug("登录界面已创建")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self.frame)
        main_container.pack(expand=True, fill='both')
        
        # 登录卡片
        login_card = ttk.Frame(main_container, relief='raised', borderwidth=1)
        login_card.place(relx=0.5, rely=0.5, anchor='center', width=400, height=500)
        
        # 标题区域
        title_frame = ttk.Frame(login_card, padding="30 30 30 20")
        title_frame.pack(fill='x')
        
        # 应用标题
        app_name = client_config.get('app.name', 'PH&RL 考试客户端')
        title_label = ttk.Label(
            title_frame,
            text=app_name,
            font=('Microsoft YaHei', 18, 'bold')
        )
        title_label.pack()
        
        # 副标题
        subtitle_label = ttk.Label(
            title_frame,
            text="请登录您的账户",
            font=('Microsoft YaHei', 12)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # 表单区域
        form_frame = ttk.Frame(login_card, padding="30 0 30 20")
        form_frame.pack(fill='x')
        
        # 用户名
        ttk.Label(form_frame, text="用户名:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        username_entry = ttk.Entry(
            form_frame, 
            textvariable=self.username_var,
            font=('Microsoft YaHei', 11),
            width=30
        )
        username_entry.pack(fill='x', pady=(0, 15))
        username_entry.focus()
        
        # 密码
        ttk.Label(form_frame, text="密码:", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(0, 5))
        password_entry = ttk.Entry(
            form_frame, 
            textvariable=self.password_var,
            font=('Microsoft YaHei', 11),
            show='*',
            width=30
        )
        password_entry.pack(fill='x', pady=(0, 15))
        
        # 记住登录
        remember_check = ttk.Checkbutton(
            form_frame,
            text="记住登录状态",
            variable=self.remember_var,
            style='TCheckbutton'
        )
        remember_check.pack(anchor='w', pady=(0, 20))
        
        # 登录按钮
        login_button = ttk.Button(
            form_frame,
            text="登录",
            command=self._login,
            style='Accent.TButton'
        )
        login_button.pack(fill='x', pady=(0, 15))
        
        # 底部区域
        bottom_frame = ttk.Frame(login_card, padding="30 0 30 30")
        bottom_frame.pack(fill='x', side='bottom')
        
        # 服务器配置按钮
        config_button = ttk.Button(
            bottom_frame,
            text="服务器配置",
            command=self._show_server_config
        )
        config_button.pack(side='left')
        
        # 版本信息
        version = client_config.get('app.version', '1.0.0')
        version_label = ttk.Label(
            bottom_frame,
            text=f"版本 {version}",
            font=('Microsoft YaHei', 9)
        )
        version_label.pack(side='right')
        
        # 状态标签
        self.status_label = ttk.Label(
            form_frame,
            text="",
            font=('Microsoft YaHei', 10)
        )
        self.status_label.pack(pady=(0, 10))
    
    def _load_saved_credentials(self):
        """加载保存的凭据"""
        try:
            # 如果用户已经登录，直接跳转到考试列表
            if auth_manager.is_authenticated():
                logger.info("用户已登录，跳转到考试列表")
                self.app.show_exam_list()
                return
            
            # 加载保存的用户名
            from utils.storage import local_storage
            saved_username = local_storage.get_cache('last_username')
            if saved_username:
                self.username_var.set(saved_username)
                self.remember_var.set(True)
                
        except Exception as e:
            logger.error(f"加载保存的凭据失败: {e}")
    
    def _login(self):
        """执行登录"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        # 验证输入
        if not username:
            self._show_status("请输入用户名", 'red')
            return
        
        if not password:
            self._show_status("请输入密码", 'red')
            return
        
        # 显示加载状态
        self._show_status("正在登录...", 'blue')
        self.parent.config(cursor="wait")
        
        # 在后台线程中执行登录
        def login_thread():
            try:
                success = auth_manager.login(username, password, self.remember_var.get())
                
                # 在主线程中更新UI
                self.parent.after(0, lambda: self._login_callback(success, username))
                
            except Exception as e:
                logger.error(f"登录异常: {e}")
                self.parent.after(0, lambda: self._login_callback(False, username, str(e)))
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def _login_callback(self, success: bool, username: str, error: str = None):
        """登录回调"""
        try:
            self.parent.config(cursor="")
            
            if success:
                # 保存用户名
                if self.remember_var.get():
                    from utils.storage import local_storage
                    local_storage.set_cache('last_username', username, expires_in=30*24*3600)  # 30天
                
                self._show_status("登录成功", 'green')
                logger.info(f"用户登录成功: {username}")
                
                # 延迟跳转到考试列表
                self.parent.after(1000, self.app.show_exam_list)
                
            else:
                error_msg = error or "用户名或密码错误"
                self._show_status(error_msg, 'red')
                logger.warning(f"用户登录失败: {username} - {error_msg}")
                
                # 清空密码
                self.password_var.set("")
                
        except Exception as e:
            logger.error(f"登录回调异常: {e}")
            self._show_status("登录过程中发生错误", 'red')
    
    def _show_status(self, message: str, color: str = 'black'):
        """显示状态消息"""
        self.status_label.config(text=message, foreground=color)
        
        # 如果是错误消息，5秒后清除
        if color == 'red':
            self.parent.after(5000, lambda: self.status_label.config(text=""))
    
    def _show_server_config(self):
        """显示服务器配置对话框"""
        try:
            ServerConfigDialog(self.parent, client_config)
        except Exception as e:
            logger.error(f"显示服务器配置对话框失败: {e}")
            messagebox.showerror("错误", f"无法打开服务器配置：\n{e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 解绑事件
            self.parent.unbind('<Return>')
            logger.debug("登录界面已清理")
        except Exception as e:
            logger.error(f"登录界面清理失败: {e}")
    
    def destroy(self):
        """销毁界面"""
        try:
            self.cleanup()
            self.frame.destroy()
        except Exception as e:
            logger.error(f"销毁登录界面失败: {e}")
