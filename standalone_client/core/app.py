#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用程序

客户端的主应用程序类，负责管理整个应用的生命周期。
"""

import tkinter as tk
from tkinter import messagebox, ttk
import sys
from pathlib import Path
from typing import Optional

from .config import client_config
from .auth import auth_manager
from .api import api_client
from utils.logger import get_logger
from utils.storage import local_storage
from utils.network import network_monitor

logger = get_logger(__name__)

class ExamClientApp:
    """考试客户端主应用程序"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_view = None
        
        # 初始化应用
        self._init_app()
        self._setup_window()
        self._setup_network_monitoring()
        
        # 显示登录界面
        self.show_login()
        
        logger.info("考试客户端应用已初始化")
    
    def _init_app(self):
        """初始化应用程序"""
        try:
            # 清理过期缓存
            local_storage.clear_expired_cache()
            
            # 配置API客户端
            api_client.base_url = client_config.get_server_url()
            api_client.timeout = client_config.get('server.timeout', 30)
            
            logger.debug("应用程序初始化完成")
            
        except Exception as e:
            logger.error(f"应用程序初始化失败: {e}")
            messagebox.showerror("初始化错误", f"应用程序初始化失败：\n{e}")
            sys.exit(1)
    
    def _setup_window(self):
        """设置主窗口"""
        try:
            # 窗口标题和图标
            app_name = client_config.get('app.name', 'PH&RL 考试客户端')
            self.root.title(app_name)
            
            # 窗口大小
            window_size = client_config.get('ui.window_size', '1024x768')
            self.root.geometry(window_size)
            
            # 窗口居中
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            
            # 设置最小窗口大小
            self.root.minsize(800, 600)
            
            # 设置字体
            font_family = client_config.get('ui.font_family', 'Microsoft YaHei')
            font_size = client_config.get('ui.font_size', 12)
            
            # 配置默认字体
            self.root.option_add('*Font', f'{font_family} {font_size}')
            
            # 设置主题色
            theme_color = client_config.get('ui.theme_color', '#2196F3')
            self.root.configure(bg='white')
            
            # 窗口关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            logger.debug("主窗口设置完成")
            
        except Exception as e:
            logger.error(f"主窗口设置失败: {e}")
    
    def _setup_network_monitoring(self):
        """设置网络监控"""
        try:
            # 设置服务器URL
            network_monitor.set_server_url(client_config.get_server_url())
            
            # 设置回调函数
            network_monitor.on_connection_lost = self._on_connection_lost
            network_monitor.on_connection_restored = self._on_connection_restored
            network_monitor.on_server_unreachable = self._on_server_unreachable
            network_monitor.on_server_restored = self._on_server_restored
            
            # 启动监控
            if client_config.get('network.connection_check_interval', 60) > 0:
                network_monitor.check_interval = client_config.get('network.connection_check_interval', 60)
                network_monitor.start_monitoring()
            
            logger.debug("网络监控设置完成")
            
        except Exception as e:
            logger.error(f"网络监控设置失败: {e}")
    
    def _on_connection_lost(self):
        """网络连接丢失回调"""
        logger.warning("网络连接已断开")
        self.root.after(0, lambda: messagebox.showwarning(
            "网络提示", 
            "网络连接已断开，请检查网络设置。\n考试数据将在本地保存，网络恢复后自动同步。"
        ))
    
    def _on_connection_restored(self):
        """网络连接恢复回调"""
        logger.info("网络连接已恢复")
        self.root.after(0, lambda: messagebox.showinfo(
            "网络提示", 
            "网络连接已恢复，正在同步数据..."
        ))
    
    def _on_server_unreachable(self):
        """服务器不可达回调"""
        logger.warning("服务器连接不可达")
        self.root.after(0, lambda: messagebox.showwarning(
            "服务器提示", 
            "无法连接到考试服务器，请联系管理员。\n考试数据将在本地保存。"
        ))
    
    def _on_server_restored(self):
        """服务器连接恢复回调"""
        logger.info("服务器连接已恢复")
        self.root.after(0, lambda: messagebox.showinfo(
            "服务器提示", 
            "服务器连接已恢复，正在同步数据..."
        ))
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 如果正在考试中，询问是否确认退出
            if hasattr(self, 'current_view') and hasattr(self.current_view, 'is_exam_active'):
                if getattr(self.current_view, 'is_exam_active', False):
                    result = messagebox.askyesno(
                        "确认退出", 
                        "您正在考试中，退出将自动提交当前答案。\n确定要退出吗？"
                    )
                    if not result:
                        return
                    
                    # 自动提交考试
                    if hasattr(self.current_view, 'auto_submit_exam'):
                        self.current_view.auto_submit_exam()
            
            # 停止网络监控
            network_monitor.stop_monitoring()
            
            # 登出用户
            auth_manager.logout()
            
            # 清理临时数据
            local_storage.cleanup_storage()
            
            logger.info("应用程序正常退出")
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"退出处理异常: {e}")
            self.root.destroy()
    
    def show_login(self):
        """显示登录界面"""
        try:
            # 清除当前视图
            self._clear_current_view()
            
            # 导入并创建登录视图
            from ui.login import LoginView
            self.current_view = LoginView(self.root, self)
            
            logger.debug("显示登录界面")
            
        except Exception as e:
            logger.error(f"显示登录界面失败: {e}")
            messagebox.showerror("界面错误", f"无法显示登录界面：\n{e}")
    
    def show_exam_list(self):
        """显示考试列表界面"""
        try:
            # 检查是否已登录
            if not auth_manager.is_authenticated():
                self.show_login()
                return
            
            # 清除当前视图
            self._clear_current_view()
            
            # 导入并创建考试列表视图
            from ui import get_exam_list_view
            ExamListView = get_exam_list_view()
            self.current_view = ExamListView(self.root, self)
            
            logger.debug("显示考试列表界面")
            
        except Exception as e:
            logger.error(f"显示考试列表界面失败: {e}")
            messagebox.showerror("界面错误", f"无法显示考试列表界面：\n{e}")
    
    def show_exam_window(self, exam_id: str):
        """显示考试答题界面"""
        try:
            # 检查是否已登录
            if not auth_manager.is_authenticated():
                self.show_login()
                return
            
            # 清除当前视图
            self._clear_current_view()
            
            # 导入并创建考试答题视图
            from ui import get_exam_window_view
            ExamWindowView = get_exam_window_view()
            self.current_view = ExamWindowView(self.root, self, exam_id)
            
            logger.debug(f"显示考试答题界面: {exam_id}")
            
        except Exception as e:
            logger.error(f"显示考试答题界面失败: {e}")
            messagebox.showerror("界面错误", f"无法显示考试答题界面：\n{e}")
    
    def _clear_current_view(self):
        """清除当前视图"""
        try:
            if self.current_view:
                # 如果视图有清理方法，调用它
                if hasattr(self.current_view, 'cleanup'):
                    self.current_view.cleanup()
                
                # 销毁视图
                if hasattr(self.current_view, 'destroy'):
                    self.current_view.destroy()
                elif hasattr(self.current_view, 'frame'):
                    self.current_view.frame.destroy()
                
                self.current_view = None
            
            # 清除所有子组件
            for widget in self.root.winfo_children():
                widget.destroy()
                
        except Exception as e:
            logger.error(f"清除当前视图失败: {e}")
    
    def run(self):
        """运行应用程序"""
        try:
            logger.info("考试客户端应用开始运行")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"应用程序运行异常: {e}")
            messagebox.showerror("运行错误", f"应用程序运行异常：\n{e}")
        finally:
            # 确保清理资源
            try:
                network_monitor.stop_monitoring()
                auth_manager.logout()
            except:
                pass
