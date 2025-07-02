#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的客户端测试程序
用于诊断登录问题
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# 添加客户端路径
sys.path.append('client')

try:
    import api
    print("API模块导入成功")
except Exception as e:
    print(f"API模块导入失败: {e}")
    sys.exit(1)

class SimpleLoginTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("简化登录测试")
        self.root.geometry("400x300")
        
        # 创建登录界面
        tk.Label(self.root, text="用户名:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "student")  # 默认用户名
        
        tk.Label(self.root, text="密码:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "123456")  # 默认密码
        
        tk.Button(self.root, text="登录", command=self.test_login).pack(pady=10)
        
        # 结果显示区域
        self.result_text = tk.Text(self.root, height=10, width=50)
        self.result_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
    def test_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"尝试登录: {username}\n")
        
        try:
            # 测试登录
            user_info = api.login(username, password)
            
            if user_info:
                self.result_text.insert(tk.END, f"登录成功!\n")
                self.result_text.insert(tk.END, f"用户ID: {user_info.get('id')}\n")
                self.result_text.insert(tk.END, f"用户名: {user_info.get('username')}\n")
                self.result_text.insert(tk.END, f"真实姓名: {user_info.get('real_name')}\n")
                self.result_text.insert(tk.END, f"角色: {user_info.get('role')}\n")
                
                # 测试获取考试列表
                self.result_text.insert(tk.END, "\n正在获取考试列表...\n")
                exams = api.get_exams_for_student(user_info.get('id'), user_info)
                
                self.result_text.insert(tk.END, f"获取到 {len(exams)} 个考试:\n")
                for i, exam in enumerate(exams[:5]):  # 只显示前5个
                    self.result_text.insert(tk.END, f"  {i+1}. {exam.get('name')} ({exam.get('status')})\n")
                
                if len(exams) > 5:
                    self.result_text.insert(tk.END, f"  ... 还有 {len(exams)-5} 个考试\n")
                    
                messagebox.showinfo("成功", f"登录成功！获取到 {len(exams)} 个考试")
                
            else:
                self.result_text.insert(tk.END, "登录失败: 用户名或密码错误\n")
                messagebox.showerror("失败", "登录失败")
                
        except Exception as e:
            error_msg = f"登录过程中出现错误: {str(e)}"
            self.result_text.insert(tk.END, f"{error_msg}\n")
            
            # 显示详细错误信息
            import traceback
            error_detail = traceback.format_exc()
            self.result_text.insert(tk.END, f"\n详细错误信息:\n{error_detail}\n")
            
            messagebox.showerror("错误", error_msg)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("启动简化登录测试...")
    app = SimpleLoginTest()
    app.run()
