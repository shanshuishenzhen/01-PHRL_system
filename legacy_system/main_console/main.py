#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局总控模块 - 主入口文件
负责系统的统一调度、权限分发、模块间通信和全局配置管理
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加各模块路径到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'user_management'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'exam_management'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'question_bank'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'grading_center'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'score_statistics'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

class MainConsole:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("局域网在线考试系统 - 主控台")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置窗口图标和样式
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 标题
        title_label = ttk.Label(main_frame, text="局域网在线考试系统", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        subtitle_label = ttk.Label(main_frame, text="主控台", 
                                  font=("Arial", 14))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 功能模块按钮
        self.create_module_buttons(main_frame)
        
        # 状态栏
        self.status_label = ttk.Label(main_frame, text="就绪", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def create_module_buttons(self, parent):
        """创建功能模块按钮"""
        modules = [
            ("用户管理", self.open_user_management, 2, 0),
            ("考试管理", self.open_exam_management, 2, 1),
            ("题库管理", self.open_question_bank, 3, 0),
            ("阅卷中心", self.open_grading_center, 3, 1),
            ("成绩统计", self.open_score_statistics, 4, 0),
            ("客户机", self.open_client, 4, 1),
        ]
        
        for text, command, row, col in modules:
            btn = ttk.Button(parent, text=text, command=command)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
    def open_user_management(self):
        """打开用户管理模块"""
        try:
            self.status_label.config(text="正在打开用户管理模块...")
            from user_manager import UserManager
            user_manager = UserManager()
            user_manager.run()
        except ImportError:
            messagebox.showerror("错误", "用户管理模块未找到，请检查模块文件")
        except Exception as e:
            messagebox.showerror("错误", f"打开用户管理模块失败: {str(e)}")
        finally:
            self.status_label.config(text="就绪")
            
    def open_exam_management(self):
        """打开考试管理模块"""
        try:
            self.status_label.config(text="正在打开考试管理模块...")
            from exam_manager import ExamManager
            exam_manager = ExamManager()
            exam_manager.run()
        except ImportError:
            messagebox.showerror("错误", "考试管理模块未找到，请检查模块文件")
        except Exception as e:
            messagebox.showerror("错误", f"打开考试管理模块失败: {str(e)}")
        finally:
            self.status_label.config(text="就绪")
            
    def open_question_bank(self):
        """打开题库管理模块（仅跳转，不更改原有界面和功能）"""
        try:
            self.status_label.config(text="正在打开题库管理模块...")
            import subprocess
            import sys
            import os
            # 用子进程方式启动原有题库管理模块的主入口文件question_bank_manager.py
            question_bank_path = os.path.join(os.path.dirname(__file__), '..', 'question_bank', 'question_bank_manager.py')
            if os.path.exists(question_bank_path):
                subprocess.Popen([
                    sys.executable,
                    question_bank_path
                ])
            else:
                messagebox.showerror("错误", f"找不到题库管理模块文件: {question_bank_path}")
        except Exception as e:
            messagebox.showerror("错误", f"打开题库管理模块失败: {str(e)}")
        finally:
            self.status_label.config(text="就绪")
            
    def open_grading_center(self):
        """打开阅卷中心模块"""
        try:
            self.status_label.config(text="正在打开阅卷中心模块...")
            # 这里将调用阅卷中心模块
            messagebox.showinfo("提示", "阅卷中心模块功能开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"打开阅卷中心模块失败: {str(e)}")
        finally:
            self.status_label.config(text="就绪")
            
    def open_score_statistics(self):
        """打开成绩统计模块"""
        try:
            self.status_label.config(text="正在打开成绩统计模块...")
            # 这里将调用成绩统计模块
            messagebox.showinfo("提示", "成绩统计模块功能开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"打开成绩统计模块失败: {str(e)}")
        finally:
            self.status_label.config(text="就绪")
            
    def open_client(self):
        """打开客户机模块"""
        try:
            self.status_label.config(text="正在打开客户机模块...")
            # 这里将调用客户机模块
            messagebox.showinfo("提示", "客户机模块功能开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"打开客户机模块失败: {str(e)}")
        finally:
            self.status_label.config(text="就绪")
    
    def run(self):
        """运行主控台"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainConsole()
    app.run() 