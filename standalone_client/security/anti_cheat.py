#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
防作弊管理

提供考试期间的防作弊功能，包括窗口监控、进程监控、快捷键禁用等。
"""

import tkinter as tk
import threading
import time
import psutil
import os
import sys
from typing import Callable, Optional, List, Set
from utils.logger import get_logger

logger = get_logger(__name__)

class AntiCheatManager:
    """防作弊管理器"""
    
    def __init__(self):
        self.is_active = False
        self.monitor_thread = None
        self.root_window = None
        
        # 回调函数
        self.on_violation_detected: Optional[Callable] = None
        
        # 监控配置
        self.check_interval = 1  # 秒
        self.forbidden_processes = {
            'notepad.exe', 'calc.exe', 'cmd.exe', 'powershell.exe',
            'chrome.exe', 'firefox.exe', 'edge.exe', 'iexplore.exe',
            'qq.exe', 'wechat.exe', 'dingtalk.exe', 'feishu.exe',
            'teamviewer.exe', 'anydesk.exe', 'vnc.exe'
        }
        
        # 违规记录
        self.violations = []
        
        logger.debug("防作弊管理器已初始化")
    
    def start_monitoring(self, root_window: tk.Tk):
        """开始监控"""
        if self.is_active:
            return
        
        self.root_window = root_window
        self.is_active = True
        
        # 启用全屏模式
        self._enable_fullscreen()
        
        # 禁用系统快捷键
        self._disable_system_shortcuts()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("防作弊监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        # 恢复窗口状态
        self._restore_window_state()
        
        # 恢复系统快捷键
        self._restore_system_shortcuts()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        logger.info("防作弊监控已停止")
    
    def _enable_fullscreen(self):
        """启用全屏模式"""
        try:
            if self.root_window:
                self.root_window.attributes('-fullscreen', True)
                self.root_window.attributes('-topmost', True)
                self.root_window.focus_force()
                logger.debug("全屏模式已启用")
        except Exception as e:
            logger.error(f"启用全屏模式失败: {e}")
    
    def _disable_system_shortcuts(self):
        """禁用系统快捷键"""
        try:
            if self.root_window:
                # 禁用Alt+Tab
                self.root_window.bind('<Alt-Tab>', lambda e: 'break')
                self.root_window.bind('<Alt-Shift-Tab>', lambda e: 'break')
                
                # 禁用Ctrl+Alt+Del (无法完全禁用，但可以记录)
                self.root_window.bind('<Control-Alt-Delete>', self._on_violation)
                
                # 禁用Windows键
                self.root_window.bind('<Super_L>', lambda e: 'break')
                self.root_window.bind('<Super_R>', lambda e: 'break')
                
                # 禁用F4 (Alt+F4)
                self.root_window.bind('<Alt-F4>', lambda e: 'break')
                
                # 禁用Escape
                self.root_window.bind('<Escape>', lambda e: 'break')
                
                logger.debug("系统快捷键已禁用")
        except Exception as e:
            logger.error(f"禁用系统快捷键失败: {e}")
    
    def _restore_window_state(self):
        """恢复窗口状态"""
        try:
            if self.root_window:
                self.root_window.attributes('-fullscreen', False)
                self.root_window.attributes('-topmost', False)
                logger.debug("窗口状态已恢复")
        except Exception as e:
            logger.error(f"恢复窗口状态失败: {e}")
    
    def _restore_system_shortcuts(self):
        """恢复系统快捷键"""
        try:
            if self.root_window:
                # 解绑所有快捷键
                shortcuts = [
                    '<Alt-Tab>', '<Alt-Shift-Tab>', '<Control-Alt-Delete>',
                    '<Super_L>', '<Super_R>', '<Alt-F4>', '<Escape>'
                ]
                
                for shortcut in shortcuts:
                    try:
                        self.root_window.unbind(shortcut)
                    except:
                        pass
                
                logger.debug("系统快捷键已恢复")
        except Exception as e:
            logger.error(f"恢复系统快捷键失败: {e}")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_active:
            try:
                # 检查窗口焦点
                self._check_window_focus()
                
                # 检查禁止的进程
                self._check_forbidden_processes()
                
                # 检查网络活动（可选）
                # self._check_network_activity()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(self.check_interval)
    
    def _check_window_focus(self):
        """检查窗口焦点"""
        try:
            if not self.root_window:
                return
            
            # 检查是否失去焦点
            if self.root_window.focus_get() is None:
                self._record_violation("窗口失去焦点", "检测到窗口失去焦点，可能切换到其他应用")
                
                # 强制获取焦点
                self.root_window.focus_force()
                self.root_window.lift()
                
        except Exception as e:
            logger.error(f"检查窗口焦点失败: {e}")
    
    def _check_forbidden_processes(self):
        """检查禁止的进程"""
        try:
            current_processes = set()
            
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    current_processes.add(proc_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 检查是否有禁止的进程
            forbidden_found = current_processes.intersection(self.forbidden_processes)
            
            if forbidden_found:
                for proc_name in forbidden_found:
                    self._record_violation(
                        "禁止的进程",
                        f"检测到禁止的进程: {proc_name}"
                    )
                    
        except Exception as e:
            logger.error(f"检查禁止进程失败: {e}")
    
    def _record_violation(self, violation_type: str, description: str):
        """记录违规行为"""
        try:
            violation = {
                'type': violation_type,
                'description': description,
                'timestamp': time.time(),
                'time_str': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.violations.append(violation)
            
            logger.warning(f"防作弊违规: {violation_type} - {description}")
            
            # 调用回调函数
            if self.on_violation_detected:
                self.on_violation_detected(violation)
                
        except Exception as e:
            logger.error(f"记录违规行为失败: {e}")
    
    def _on_violation(self, event=None):
        """违规事件处理"""
        self._record_violation("快捷键违规", f"检测到禁用快捷键使用: {event}")
        return 'break'
    
    def get_violations(self) -> List[dict]:
        """获取违规记录"""
        return self.violations.copy()
    
    def clear_violations(self):
        """清除违规记录"""
        self.violations.clear()
        logger.debug("违规记录已清除")
    
    def is_monitoring(self) -> bool:
        """检查是否正在监控"""
        return self.is_active
    
    def add_forbidden_process(self, process_name: str):
        """添加禁止的进程"""
        self.forbidden_processes.add(process_name.lower())
        logger.debug(f"添加禁止进程: {process_name}")
    
    def remove_forbidden_process(self, process_name: str):
        """移除禁止的进程"""
        self.forbidden_processes.discard(process_name.lower())
        logger.debug(f"移除禁止进程: {process_name}")
    
    def get_status(self) -> dict:
        """获取状态信息"""
        return {
            'is_active': self.is_active,
            'violation_count': len(self.violations),
            'forbidden_processes_count': len(self.forbidden_processes),
            'check_interval': self.check_interval
        }

# 全局防作弊管理器实例
anti_cheat_manager = AntiCheatManager()
