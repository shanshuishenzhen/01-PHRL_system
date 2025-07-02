# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import uuid
import random
import argparse
from datetime import datetime, timedelta
import io
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
import subprocess  # 添加这一行
import time  # 添加这一行
import webbrowser  # 添加这一行
import threading  # 添加这一行
import sqlite3  # 添加数据库支持

# -- 解决模块导入路径问题 --
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -- 路径问题解决 --

from developer_tools.question_bank_generator import generate_from_excel

# 全局常量
USER_DATA_FILE = os.path.join(project_root, 'user_management', 'users.json')
# 修改这一行
SAMPLE_QUESTIONS_FILE = os.path.join(project_root, 'question_bank_web', 'questions_sample.xlsx')
TEMPLATE_FILE_NAME = '样例题组题规则模板.xlsx'

class DeveloperTools:
    """
    一个用于开发和测试的辅助工具模块。
    提供快速生成用户、题库、试卷等模拟数据的功能。
    """
    def __init__(self, root):
        self.root = root
        self.root.title("开发工具 - 数据生成助手")
        self.root.geometry("800x650")

        # 样式配置
        style = ttk.Style()
        style.theme_use('clam')
        self.colors = {'danger': '#e74c3c', 'primary': '#3498db', 'success': '#27ae60'}
        style.configure("TNotebook.Tab", padding=[10, 5], font=("Microsoft YaHei", 10))
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        style.configure("TButton", font=("Microsoft YaHei", 10))

        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="🛠️ 数据生成助手", font=("Microsoft YaHei", 20, "bold"))
        title_label.pack(pady=(0, 20))

        # 标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        user_tab = ttk.Frame(notebook)
        question_tab = ttk.Frame(notebook)
        danger_zone_tab = ttk.Frame(notebook)
        notebook.add(user_tab, text="👤 用户生成")
        notebook.add(question_tab, text="📝 样例题库生成")
        notebook.add(danger_zone_tab, text="🔥 危险区域")

        # 初始化变量
        self.uploaded_template_path = tk.StringVar()

        # 初始化各标签页
        self.create_user_generation_tab(user_tab)
        self.create_question_generation_tab(question_tab)
        self.create_danger_zone_tab(danger_zone_tab)
        
    def create_question_generation_tab(self, parent):
        """创建题库生成标签页的UI(新版)"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 创建模板 ---
        template_frame = ttk.LabelFrame(frame, text="步骤 1: 获取模板", padding=15)
        template_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(template_frame, text="您可以下载一个空白的Excel模板文件作为开始。").pack(anchor="w")
        create_btn = tk.Button(template_frame, text="下载空白模板", command=self.create_excel_template, bg=self.colors['primary'], fg='white', relief="flat", padx=10)
        create_btn.pack(side="left", pady=10)

        # --- 2. 上传模板 ---
        upload_frame = ttk.LabelFrame(frame, text="步骤 2: 上传您的模板", padding=15)
        upload_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(upload_frame, text="选择一个根据模板填写好的Excel文件 (.xlsx)").pack(anchor="w")
        
        upload_btn_frame = ttk.Frame(upload_frame)
        upload_btn_frame.pack(fill="x", pady=10)
        upload_btn = tk.Button(upload_btn_frame, text="选择文件...", command=self.upload_template, bg=self.colors['primary'], fg='white', relief="flat", padx=10)
        upload_btn.pack(side="left")
        self.uploaded_path_label = ttk.Label(upload_btn_frame, textvariable=self.uploaded_template_path, foreground="gray")
        self.uploaded_path_label.pack(side="left", padx=10)
        self.uploaded_template_path.set("尚未上传文件")

        # --- 3. 生成题库 ---
        generate_frame = ttk.LabelFrame(frame, text="步骤 3: 生成样例题库", padding=15)
        generate_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(generate_frame, text="此操作将根据您上传的Excel文件，生成一个独立的样例题库。").pack(anchor="w")
        generate_btn = tk.Button(generate_frame, text="🚀 生成样例题库", command=self.run_sample_generation, bg=self.colors['success'], fg='white', font=("Microsoft YaHei", 10, "bold"), relief="flat", padx=10, pady=5)
        generate_btn.pack(pady=10)
        

    def create_excel_template(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
            initialfile=TEMPLATE_FILE_NAME,
            title="保存模板文件"
        )
        if not save_path:
            return

        data = {
            '题库名称': ['保卫管理员（三级）理论'] + [''] * 22,
            '1级代码': ['A'] + [''] * 7 + ['B'] + [''] * 5 + ['C'] + [''] * 4 + ['D'] + [''] * 3, '1级比重(%)': [20] + [''] * 7 + [10] + [''] * 5 + [45] + [''] * 4 + [25] + [''] * 3,
            '2级代码': ['A-A'] + [''] * 1 + ['A-B'] + [''] * 5 + ['B-A'] + [''] * 1 + ['B-B'] + [''] * 1 + ['B-C'] + [''] * 1 + ['C-A'] + [''] * 2 + ['C-B'] + [''] * 1 + ['D-A'] + [''] * 1 + ['D-B'] + [''] * 1, '2级比重(%)': [5] + [''] * 1 + [15] + [''] * 5 + [4] + [''] * 1 + [3] + [''] * 1 + [3] + [''] * 1 + [25] + [''] * 2 + [20] + [''] * 1 + [12] + [''] * 1 + [13] + [''] * 1,
            '3级代码': ['A-A-A', 'A-A-B', 'A-B-A', 'A-B-B', 'A-B-C', 'A-B-D', 'A-B-E', 'A-B-F', 'B-A-A', 'B-A-B', 'B-B-A', 'B-B-B', 'B-C-A', 'B-C-B', 'C-A-A', 'C-A-B', 'C-A-C', 'C-B-A', 'C-B-B', 'D-A-A', 'D-A-B', 'D-B-A', 'D-B-B'],
            '3级比重(%)': [2.5, 2.5, 2, 3, 2, 3, 1, 4, 2, 2, 2, 1, 1, 2, 7, 8, 10, 10, 10, 6, 6, 6, 7], '知识点数量': [4, 5, 8, 7, 6, 5, 7, 5, 2, 4, 5, 8, 9, 7, 5, 2, 4, 5, 8, 9, 5, 8, 9],
            'B(单选题)': [10, 20, 15, 20, 10, 20, 15, 20, 20, 15, 20, 10, 20, 15, 20, 15, 15, 20, 10, 20, 15, 20, 20], 'G(多选题)': [10, 20, 15, 20, 10, 20, 15, 20, 20, 15, 20, 10, 20, 15, 20, 15, 15, 20, 10, 20, 15, 20, 20],
            'C(判断题)': [8, 18, 13, 18, 8, 18, 13, 18, 18, 13, 18, 8, 18, 13, 18, 13, 13, 18, 8, 18, 13, 18, 18], 'T(填空题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
            'D(简答题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15], 'U(计算题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
            'W(论述题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15], 'E(案例分析题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15],
            'F(组合题)': [5, 15, 10, 15, 5, 15, 10, 15, 15, 10, 15, 5, 15, 10, 15, 10, 10, 15, 5, 15, 10, 15, 15]
        }
        df = pd.DataFrame(data)
        try:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("成功", f"模板文件已保存到:\n{save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存模板失败: {e}")

    def upload_template(self):
        filepath = filedialog.askopenfilename(
            title="选择组题规则模板",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if filepath:
            self.uploaded_template_path.set(filepath)

    def run_sample_generation(self):
        template_path = self.uploaded_template_path.get()
        if not template_path or not os.path.exists(template_path):
            messagebox.showwarning("警告", "请先上传一个有效的Excel模板文件。")
            return

        if not messagebox.askyesno("确认操作", "此操作将覆盖现有的样例题库。\n请谨慎操作！\n是否确定要继续？"):
            return
            
        try:
            total_generated = generate_from_excel(template_path, SAMPLE_QUESTIONS_FILE)
            result = messagebox.askquestion("成功", 
                f"样例题库生成完毕！\n\n共生成 {total_generated} 道题目。\n文件已保存至: {SAMPLE_QUESTIONS_FILE}\n\n是否要自动启动题库管理系统并导入样例题库？")
            
            if result == 'yes':
                # 检查题库管理应用是否存在
                flask_app_path = os.path.join(os.path.dirname(__file__), 'question_bank_web', 'app.py')
                if not os.path.exists(flask_app_path):
                    messagebox.showerror("错误", "题库管理应用 'question_bank_web/app.py' 未找到！")
                    return
                    
                # 启动Flask应用并导入样例题库
                def start_flask_and_import():
                    try:
                        command = f'start cmd /k "cd /d {os.path.dirname(flask_app_path)} && flask run"'
                        process = subprocess.Popen(command, shell=True)
                        
                        # 等待服务启动
                        time.sleep(3)
                        # 直接打开导入样例题库的URL
                        webbrowser.open_new("http://127.0.0.1:5000/import-sample")
                        
                    except Exception as e:
                        messagebox.showerror("错误", f"启动题库管理失败: {e}")
                
                threading.Thread(target=start_flask_and_import, daemon=True).start()
                
        except Exception as e:
            messagebox.showerror("生成失败", f"生成过程中发生错误: {e}")
            
    def delete_sample_questions(self):
        if not os.path.exists(SAMPLE_QUESTIONS_FILE):
            messagebox.showinfo("提示", "样例题库文件不存在，无需删除。")
            return
            
        if not messagebox.askyesno("严重警告", f"此操作将永久删除以下文件，且无法恢复！\n\n{SAMPLE_QUESTIONS_FILE}\n\n是否确定要继续？"):
            return
            
        try:
            os.remove(SAMPLE_QUESTIONS_FILE)
            messagebox.showinfo("成功", "样例题库已成功删除。")
        except Exception as e:
            messagebox.showerror("删除失败", f"删除文件时发生错误: {e}")

    def create_user_generation_tab(self, parent):
        ttk.Label(parent, text="设置要生成的用户数量：", font=("Microsoft YaHei", 12)).pack(anchor="w")
        entry_frame = ttk.Frame(parent)
        entry_frame.pack(fill="x", pady=10)
        self.entries = {}
        user_types = {"考生": "student", "考评员": "evaluator", "管理员": "admin"}
        defaults = {"考生": 88, "考评员": 10, "管理员": 2}
        for i, (label_text, key) in enumerate(user_types.items()):
            ttk.Label(entry_frame, text=f"{label_text}:", width=10).grid(row=i, column=0, padx=5, pady=5)
            self.entries[key] = ttk.Entry(entry_frame)
            self.entries[key].grid(row=i, column=1, padx=5, pady=5)
            self.entries[key].insert(0, str(defaults.get(label_text, 0)))
        generate_btn = tk.Button(parent, text="🚀 生成并追加用户", command=self.generate_users_gui, relief="flat", bg=self.colors['primary'], fg='white', font=("Microsoft YaHei", 10, "bold"))
        generate_btn.pack(pady=20)
        info_label = ttk.Label(parent, text="说明：此操作会保留现有用户，并在其基础上追加新用户。\n用户名将以'student_xxx', 'evaluator_xxx' 等形式生成。", justify="left")
        info_label.pack(anchor="w", pady=10)

    def create_danger_zone_tab(self, parent):
        ttk.Label(parent, text="警告：以下操作会永久删除数据，请谨慎使用！", font=("Microsoft YaHei", 12, "bold"), foreground=self.colors['danger']).pack(anchor="w", pady=10)
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=20)
        clear_users_btn = tk.Button(btn_frame, text="🔥 清空测试用户", command=self.clear_all_users, bg=self.colors['danger'], fg="white", font=("Microsoft YaHei", 10, "bold"), relief="flat", padx=10, pady=5)
        clear_users_btn.pack(side="left", padx=10)

        delete_questions_btn = tk.Button(btn_frame, text="🔥 删除样例题库", command=self.delete_sample_questions, bg=self.colors['danger'], fg="white", font=("Microsoft YaHei", 10, "bold"), relief="flat", padx=10, pady=5)
        delete_questions_btn.pack(side="left", padx=10)

    def generate_users_gui(self):
        try:
            user_counts = {key: int(entry.get()) for key, entry in self.entries.items()}
            total_count = sum(user_counts.values())
            if total_count == 0:
                messagebox.showwarning("提示", "请输入要生成的用户数量。")
                return
            if not messagebox.askyesno("确认操作", f"您确定要生成并追加 {total_count} 个新用户吗？"):
                return
            
            generated_count, _ = _generate_users_logic(**user_counts)
            messagebox.showinfo("成功", f"成功生成并追加了 {generated_count} 个新用户！")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("生成失败", str(e))
    
    def clear_all_users(self):
        if not messagebox.askyesno("严重警告", "此操作将删除所有'考生'、'考评员'和'管理员'角色的用户，且无法恢复！\n\n系统将保留'super_admin'角色的用户。\n是否确定要继续？"):
            return
        try:
            # 1. 更新JSON文件
            if not os.path.exists(USER_DATA_FILE):
                messagebox.showinfo("提示", "用户文件不存在，无需操作。")
                return
            
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            initial_count = len(data.get("users", []))
            # 保留 super_admin
            data["users"] = [u for u in data["users"] if u.get("role") == "super_admin"]
            final_count = len(data["users"])
            
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # 2. 同步更新数据库
            db_path = os.path.join(project_root, 'user_management', 'users.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                try:
                    # 删除非超级管理员用户
                    cursor.execute("DELETE FROM users WHERE role != 'super_admin'")
                    conn.commit()
                except Exception as db_error:
                    messagebox.showerror("数据库操作失败", str(db_error))
                finally:
                    conn.close()
                
            messagebox.showinfo("成功", f"操作完成！共删除了 {initial_count - final_count} 个用户。\n数据库已同步更新。")
        except Exception as e:
            messagebox.showerror("操作失败", str(e))

def _generate_users_logic(student=0, evaluator=0, admin=0):
    if not os.path.exists(USER_DATA_FILE):
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"users": []}, f, ensure_ascii=False, indent=4)
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = {"users": []}

    users = data.get("users", [])
    initial_user_count = len(users)
    generated_students = []
    new_users = []

    role_map = {
        "admin": (admin, "admin", "管理员"),
        "evaluator": (evaluator, "evaluator", "考评员"),
        "student": (student, "student", "考生"),
    }

    for role_key, (count, role_val, role_name) in role_map.items():
        for i in range(count):
            username = f"{role_key}_{random.randint(1000, 99999)}"
            user_entry = _create_user_entry(username, role_val, role_name)
            users.append(user_entry)
            new_users.append(user_entry)
            if role_key == "student":
                generated_students.append(username)
    
    # 1. 更新JSON文件
    data["users"] = users
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    # 2. 同步更新数据库
    db_path = os.path.join(project_root, 'user_management', 'users.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            for user in new_users:
                # 准备用户数据
                user_id = user.get('id')
                id_card = user.get('ID', '')  # 从JSON中的ID字段获取身份证号
                username = user.get('username', '')
                password = user.get('password', user.get('password_hash', '123456'))
                role = user.get('role', 'student')
                status = user.get('status', 'active')
                real_name = user.get('real_name', '')
                email = user.get('email', '')
                phone = user.get('phone', '')
                department = user.get('department', '')
                created_at = user.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # 插入用户数据
                cursor.execute("""
                    INSERT INTO users (id, id_card, username, password, role, status, real_name, email, phone, department, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, id_card, username, password, role, status, real_name, email, phone, department, created_at))
            conn.commit()
            print("数据库已同步更新。")
        except Exception as db_error:
            print(f"数据库操作失败: {db_error}")
        finally:
            conn.close()
    
    generated_count = len(users) - initial_user_count
    print(f"成功生成 {admin} 个管理员, {evaluator} 个考评员, {student} 个考生。总计: {generated_count}")
    return generated_count, generated_students

def _create_user_entry(username, role, role_name):
    return {
        "id": str(uuid.uuid4()),
        "username": username,
        "password_hash": "123456", # 设置默认密码为123456方便调试
        "real_name": f"{role_name}_{username}",
        "role": role,
        "department": random.choice(["技术部", "市场部", "人力资源部", "后勤部"]),
        "ID": ''.join([str(random.randint(0, 9)) for _ in range(18)]) # 自动生成18位数字作为身份证号
    }

def prepare_enrollment_files_cli(student_usernames, theory1_count):
    if len(student_usernames) < theory1_count:
        print(f"错误：考生总数 ({len(student_usernames)}) 小于理论一所需人数 ({theory1_count})。")
        return
    random.shuffle(student_usernames)
    theory1_candidates = student_usernames[:theory1_count]
    theory2_candidates = student_usernames[theory1_count:]
    with open("theory1_candidates.txt", 'w', encoding='utf-8') as f:
        for username in theory1_candidates:
            f.write(username + '\n')
    print(f"已生成 'theory1_candidates.txt'，包含 {len(theory1_candidates)} 名考生。")
    with open("theory2_candidates.txt", 'w', encoding='utf-8') as f:
        for username in theory2_candidates:
            f.write(username + '\n')
    print(f"已生成 'theory2_candidates.txt'，包含 {len(theory2_candidates)} 名考生。")

def clear_all_users_cli():
    """命令行方式清空用户"""
    try:
        # 1. 更新JSON文件
        if not os.path.exists(USER_DATA_FILE):
            print("用户文件不存在，无需操作。")
            return
        
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        initial_count = len(data.get("users", []))
        # 保留 super_admin
        data["users"] = [u for u in data["users"] if u.get("role") == "super_admin"]
        final_count = len(data["users"])
        
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 2. 同步更新数据库
        db_path = os.path.join(project_root, 'user_management', 'users.db')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                # 删除非超级管理员用户
                cursor.execute("DELETE FROM users WHERE role != 'super_admin'")
                conn.commit()
                print("数据库已同步更新。")
            except Exception as db_error:
                print(f"数据库操作失败: {db_error}")
            finally:
                conn.close()
            
        print(f"操作完成！共删除了 {initial_count - final_count} 个用户。")
    except Exception as e:
        print(f"操作失败: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PH&RL 开发辅助工具")
    parser.add_argument('task', nargs='?', default='gui', help="要执行的任务: 'gui', 'generate_users', 'clear_all_users'")
    parser.add_argument('--admins', type=int, default=0)
    parser.add_argument('--evaluators', type=int, default=0)
    parser.add_argument('--students', type=int, default=0)
    parser.add_argument('--theory1-count', type=int, default=0)
    args = parser.parse_args()

    if args.task == 'generate_users':
        _, student_list = _generate_users_logic(student=args.students, evaluator=args.evaluators, admin=args.admins)
        if args.theory1_count > 0 and student_list:
            prepare_enrollment_files_cli(student_list, args.theory1_count)
    elif args.task == 'clear_all_users':
        clear_all_users_cli()
    else: # 'gui' or no task
        root = tk.Tk()
        app = DeveloperTools(root)
        root.mainloop()
