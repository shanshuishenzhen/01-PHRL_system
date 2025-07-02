import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import pandas as pd
import uuid
import sqlite3

class SimpleUserManager:
    """简化版用户管理主类"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("用户管理系统")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.db_path = 'user_management/users.db'
        
        # 设置主题颜色
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff'
        }
        
        # 用户数据存储 - 不再从JSON加载
        self.current_page = 1
        self.page_size = 20
        self.checked_items = set()
        
        # 用户角色定义
        self.roles = {
            'super_admin': '超级用户',
            'admin': '管理员', 
            'examiner': '考评员',
            'student': '考生'
        }
        
        # 用户状态定义
        self.statuses = {
            'active': '正常',
            'inactive': '禁用',
            'pending': '待审批'
        }
        
        self.setup_ui()
        self.init_database()
        self.refresh_user_list()

    def init_database(self):
        """初始化数据库和表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 创建用户表，使用 TEXT 类型的 id 作为主键
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    id_card TEXT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    real_name TEXT,
                    email TEXT,
                    phone TEXT,
                    department TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            conn.commit()
            
            # 检查是否需要从JSON导入数据
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            if count == 0:
                self.import_users_from_json()
        except sqlite3.Error as e:
            print(f"数据库初始化错误: {e}")
        finally:
            conn.close()
            
    def import_users_from_json(self):
        """从users.json导入用户数据到数据库"""
        json_path = os.path.join(os.path.dirname(self.db_path), 'users.json')
        if not os.path.exists(json_path):
            print(f"用户数据文件不存在: {json_path}")
            return
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            users = data.get('users', [])
            if not users:
                print("JSON文件中没有用户数据")
                return
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for user in users:
                try:
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
                    
                except sqlite3.IntegrityError:
                    print(f"跳过重复用户: {username}")
                except Exception as e:
                    print(f"导入用户 {username} 时出错: {e}")
            
            conn.commit()
            print(f"成功从JSON导入用户数据")
            
        except Exception as e:
            print(f"导入JSON数据时出错: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_filtered_users(self):
        """从数据库获取筛选后的用户列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE 1=1"
        params = []

        search_text = self.search_var.get()
        if search_text:
            query += " AND (username LIKE ? OR real_name LIKE ? OR email LIKE ? OR phone LIKE ? OR department LIKE ? OR id_card LIKE ?)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param, search_param, search_param, search_param, search_param])

        role_filter = self.role_filter_var.get()
        if role_filter != "all":
            query += " AND role = ?"
            params.append(role_filter)

        status_filter = self.status_filter_var.get()
        if status_filter != "all":
            query += " AND status = ?"
            params.append(status_filter)

        try:
            cursor.execute(query, params)
            users = [dict(row) for row in cursor.fetchall()]
            return users
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"查询用户失败: {e}")
            return []
        finally:
            conn.close()

    def search_users(self):
        """搜索用户"""
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        self.create_toolbar(main_frame)
        
        # 搜索和筛选区域
        self.create_search_frame(main_frame)
        
        # 用户列表区域
        self.create_user_list_frame(main_frame)
        
        # 分页控件
        self.create_pagination_frame(main_frame)
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 15))
        
        # 左侧标题区域
        title_frame = ttk.Frame(toolbar)
        title_frame.pack(side=tk.LEFT)
        
        # 标题图标和文字
        title_label = ttk.Label(
            title_frame, 
            text="👥 用户管理", 
            font=("Microsoft YaHei", 20, "bold"),
            foreground=self.colors['primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # 用户统计信息
        self.stats_label = ttk.Label(
            title_frame,
            text="",
            font=("Microsoft YaHei", 10),
            foreground=self.colors['dark']
        )
        self.stats_label.pack(side=tk.LEFT, padx=(15, 0), pady=(5, 0))
        
        # 右侧按钮区域
        button_frame = ttk.Frame(toolbar)
        button_frame.pack(side=tk.RIGHT)
        
        # 按钮样式配置
        button_style = {
            "font": ("Microsoft YaHei", 10),
            "relief": "flat",
            "borderwidth": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # 批量导入按钮
        import_btn = tk.Button(
            button_frame, 
            text="📥 批量导入", 
            command=self.batch_import_users,
            bg=self.colors['info'],
            fg="white",
            activebackground=self.colors['info'],
            activeforeground="white",
            **button_style
        )
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # 批量删除按钮
        batch_delete_btn = tk.Button(
            button_frame, 
            text="🗑️ 批量删除", 
            command=self.batch_delete_users,
            bg=self.colors['danger'],
            fg="white",
            activebackground=self.colors['danger'],
            activeforeground="white",
            **button_style
        )
        batch_delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 新增用户按钮
        add_btn = tk.Button(
            button_frame, 
            text="➕ 新增用户", 
            command=self.add_user,
            bg=self.colors['success'],
            fg="white",
            activebackground=self.colors['success'],
            activeforeground="white",
            **button_style
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 编辑用户按钮
        edit_btn = tk.Button(
            button_frame, 
            text="✏️ 编辑用户", 
            command=self.edit_user,
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            **button_style
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            button_frame, 
            text="🔄 刷新", 
            command=self.refresh_user_list,
            bg=self.colors['info'],
            fg="white",
            activebackground=self.colors['info'],
            activeforeground="white",
            **button_style
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_search_frame(self, parent):
        """创建搜索和筛选区域"""
        search_frame = ttk.LabelFrame(
            parent, 
            text="🔍 搜索和筛选", 
            padding="10",
            style="Search.TLabelframe"
        )
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 搜索框
        search_label = ttk.Label(
            search_frame, 
            text="搜索:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            width=25,
            font=("Microsoft YaHei", 10)
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # 角色筛选
        role_label = ttk.Label(
            search_frame, 
            text="角色:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        role_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.role_filter_var = tk.StringVar(value="all")
        role_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.role_filter_var, 
            values=["全部"] + list(self.roles.values()), 
            width=12,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        role_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 状态筛选
        status_label = ttk.Label(
            search_frame, 
            text="状态:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.status_filter_var,
            values=["全部"] + list(self.statuses.values()), 
            width=10,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 搜索按钮
        search_btn = tk.Button(
            search_frame, 
            text="🔍 搜索", 
            command=self.search_users,
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            font=("Microsoft YaHei", 10),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        reset_btn = tk.Button(
            search_frame, 
            text="🔄 重置", 
            command=self.reset_search,
            bg=self.colors['warning'],
            fg="white",
            activebackground=self.colors['warning'],
            activeforeground="white",
            font=("Microsoft YaHei", 10),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def create_user_list_frame(self, parent):
        """创建用户列表区域"""
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # 用户列表标题和全选框区域
        header_frame = ttk.Frame(list_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        list_label = ttk.Label(header_frame, text="📋 用户列表", font=("Microsoft YaHei", 12, "bold"))
        list_label.pack(side=tk.LEFT)
        
        # 全选复选框
        self.select_all_var = tk.BooleanVar(value=False)
        select_all_cb = ttk.Checkbutton(header_frame, text="全选", variable=self.select_all_var, 
                                       command=self.toggle_select_all)
        select_all_cb.pack(side=tk.RIGHT, padx=10)
        
        # 表格和滚动条
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("checkbox", "seq", "username", "real_name", "id_card", "role", "status", "email", "phone", "department", "created_at")
        self.user_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="none")

        # 定义列
        self.user_tree.heading("checkbox", text="选择")
        self.user_tree.column("checkbox", width=50, stretch=tk.NO, anchor=tk.CENTER)
        
        self.user_tree.heading("seq", text="序号")
        self.user_tree.column("seq", width=50, stretch=tk.NO, anchor=tk.CENTER)

        self.user_tree.heading("username", text="用户名")
        self.user_tree.column("username", width=120)

        self.user_tree.heading("real_name", text="真实姓名")
        self.user_tree.column("real_name", width=100)

        self.user_tree.heading("id_card", text="身份证号")
        self.user_tree.column("id_card", width=180)

        self.user_tree.heading("role", text="角色")
        self.user_tree.column("role", width=100)

        self.user_tree.heading("status", text="状态")
        self.user_tree.column("status", width=80, anchor=tk.CENTER)

        self.user_tree.heading("email", text="邮箱")
        self.user_tree.column("email", width=180)

        self.user_tree.heading("phone", text="手机号")
        self.user_tree.column("phone", width=120)
        
        self.user_tree.heading("department", text="部门")
        self.user_tree.column("department", width=120)

        self.user_tree.heading("created_at", text="创建时间")
        self.user_tree.column("created_at", width=150)
        
        # 绑定点击事件
        self.user_tree.bind('<Button-1>', self.on_tree_click)

        # 滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.user_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.user_tree.xview)
        self.user_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_pagination_frame(self, parent):
        """创建分页控件"""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 分页信息
        self.page_info_label = ttk.Label(
            pagination_frame, 
            text="",
            font=("Microsoft YaHei", 10),
            foreground=self.colors['dark']
        )
        self.page_info_label.pack(side=tk.LEFT)
        
        # 分页按钮
        button_frame = ttk.Frame(pagination_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # 按钮样式
        page_button_style = {
            "font": ("Microsoft YaHei", 10),
            "relief": "flat",
            "borderwidth": 1,
            "padx": 12,
            "pady": 5,
            "cursor": "hand2"
        }
        
        prev_btn = tk.Button(
            button_frame, 
            text="◀ 上一页", 
            command=self.prev_page,
            bg=self.colors['light'],
            fg=self.colors['dark'],
            activebackground=self.colors['primary'],
            activeforeground="white",
            **page_button_style
        )
        prev_btn.pack(side=tk.LEFT, padx=2)
        
        next_btn = tk.Button(
            button_frame, 
            text="下一页 ▶", 
            command=self.next_page,
            bg=self.colors['light'],
            fg=self.colors['dark'],
            activebackground=self.colors['primary'],
            activeforeground="white",
            **page_button_style
        )
        next_btn.pack(side=tk.LEFT, padx=2)
    
    def on_tree_click(self, event):
        """处理 Treeview 点击事件以切换复选框状态"""
        region = self.user_tree.identify_region(event.x, event.y)
        if region != 'cell':
            return

        column_id = self.user_tree.identify_column(event.x)
        if column_id == '#1': # 只响应第一列（复选框列）的点击
            item_id = self.user_tree.identify_row(event.y)
            if not item_id:
                return

            # 从tags中获取用户ID
            tags = self.user_tree.item(item_id, 'tags')
            if not tags:
                return
                
            try:
                user_id = tags[0]  # 用户ID可能是字符串
                values = self.user_tree.item(item_id, 'values')
                
                if user_id in self.checked_items:
                    self.checked_items.remove(user_id)
                    self.user_tree.item(item_id, values=('☐', *values[1:]))
                else:
                    self.checked_items.add(user_id)
                    self.user_tree.item(item_id, values=('☑', *values[1:]))
                
                # 更新全选复选框状态
                self.update_select_all_checkbox()
            except (ValueError, IndexError):
                # 如果tags中没有有效的用户ID，使用序号方法作为备选
                values = self.user_tree.item(item_id, 'values')
                if not values or len(values) < 2:
                    return
                    
                seq_num = int(values[1])  # 序号
                start_idx = (self.current_page - 1) * self.page_size
                user_index = seq_num - start_idx - 1
                
                filtered_users = self.get_filtered_users()
                if 0 <= user_index < len(filtered_users):
                    user = filtered_users[user_index]
                    user_id = user.get("id")
                    
                    if user_id in self.checked_items:
                        self.checked_items.remove(user_id)
                        self.user_tree.item(item_id, values=('☐', *values[1:]))
                    else:
                        self.checked_items.add(user_id)
                        self.user_tree.item(item_id, values=('☑', *values[1:]))
                    
                    # 更新全选复选框状态
                    self.update_select_all_checkbox()
    
    def update_select_all_checkbox(self):
        """更新全选复选框状态"""
        filtered_users = self.get_filtered_users()
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_users = filtered_users[start_idx:end_idx]
        
        # 检查是否所有当前页用户都被选中
        all_selected = True
        for user in page_users:
            user_id = user.get("id")
            if user_id not in self.checked_items:
                all_selected = False
                break
        
        # 更新全选复选框状态
        self.select_all_var.set(all_selected and len(page_users) > 0)

    def toggle_select_all(self):
        """全选/取消全选所有用户"""
        is_select_all = self.select_all_var.get()
        
        # 获取当前页的用户
        filtered_users = self.get_filtered_users()
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_users = filtered_users[start_idx:end_idx]
        
        # 清除之前的选择
        if not is_select_all:
            self.checked_items.clear()
        else:
            # 添加当前页所有用户到选中集合
            for user in page_users:
                user_id = user.get("id")
                if user_id:
                    self.checked_items.add(user_id)
        
        # 刷新用户列表以更新复选框状态
        self.refresh_user_list()
    
    def refresh_user_list(self):
        """刷新用户列表"""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        filtered_users = self.get_filtered_users()
        total_users = len(filtered_users)

        # 更新统计标签
        self.stats_label.config(text=f"共 {total_users} 个用户")

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_users = filtered_users[start_idx:end_idx]
        
        for i, user in enumerate(page_users):
            user_id = user.get("id")
            checkbox_char = '☑' if user_id in self.checked_items else '☐'
            self.user_tree.insert(
                "", 
                tk.END, 
                values=(
                    checkbox_char,
                    start_idx + i + 1,
                    user.get("username", ""),
                    user.get("real_name", ""),
                    user.get("id_card", ""),
                    self.roles.get(user.get("role"), user.get("role")),
                    self.statuses.get(user.get("status"), user.get("status")),
                    user.get("email", ""),
                    user.get("phone", ""),
                    user.get("department", ""),
                    user.get("created_at", "")
                ),
                tags=(user_id,)
            )
        
        # 更新全选复选框状态
        self.update_select_all_checkbox()
        
        # 更新分页信息
        total_pages = (total_users + self.page_size - 1) // self.page_size
        self.page_info_label.config(text=f"第 {self.current_page} 页，共 {total_pages} 页，总计 {total_users} 条记录")
        self.user_tree.update()
        self.root.update_idletasks()
    
   
    
    def search_users(self):
        """搜索用户"""
        self.current_page = 1
        self.checked_items.clear()  # 清除选中项
        self.refresh_user_list()
    
    def reset_search(self):
        """重置搜索条件"""
        self.search_var.set("")
        self.role_filter_var.set("all")
        self.status_filter_var.set("all")
        self.current_page = 1
        self.checked_items.clear()  # 清除选中项
        self.refresh_user_list()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_user_list()
    
    def next_page(self):
        """下一页"""
        filtered_users = self.get_filtered_users()
        total_pages = (len(filtered_users) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_user_list()
    
    def add_user(self):
        """新增用户"""
        UserDialog(self.root, self, None)
    
    def edit_user(self, event=None):
        """编辑用户"""
        if len(self.checked_items) != 1:
            messagebox.showwarning("警告", "请勾选一个且仅一个用户进行编辑")
            return
        
        user_id = list(self.checked_items)[0]
        user = self.get_user_by_id(user_id)
        
        if user:
            dialog = UserDialog(self.root, self, user)
            self.root.wait_window(dialog.dialog)
        else:
            messagebox.showerror("错误", "找不到该用户信息，请刷新列表")
    
    def delete_user(self):
        """删除单个用户（此方法保留以防未来需要，但按钮已移除）"""
        if len(self.checked_items) != 1:
            messagebox.showwarning("警告", "请勾选一个用户进行删除")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的用户吗？"):
            user_id = list(self.checked_items)[0]
            self.delete_user_from_database(user_id)
    
    def get_user_by_id(self, user_id):
        """根据ID从数据库获取用户"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            return dict(user_row) if user_row else None
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取用户信息失败: {e}")
            return None
        finally:
            conn.close()
    
    def run(self):
        """运行用户管理界面"""
        self.root.mainloop()

    def batch_import_users(self):
        """批量导入用户"""
        try:
            # 选择Excel或CSV文件
            file_path = filedialog.askopenfilename(
                title="选择导入文件",
                filetypes=[
                    ("表格文件", "*.xlsx *.xls *.csv"),
                    ("Excel文件", "*.xlsx *.xls"),
                    ("CSV文件", "*.csv"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # 读取文件
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # 验证必要的列
            required_columns = ['username', 'real_name', 'id_card', 'role', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messagebox.showerror("错误", f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
                return
            
            # 显示导入预览
            preview_dialog = BatchImportPreviewDialog(self.root, self, df)
            self.root.wait_window(preview_dialog.dialog)
            
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")
    
    def batch_delete_users(self):
        """批量删除数据库中的用户"""
        if not self.checked_items:
            messagebox.showwarning("警告", "请先勾选要删除的用户")
            return

        count = len(self.checked_items)
        if not messagebox.askyesno("确认删除", f"确定要删除选中的 {count} 个用户吗？\n此操作不可恢复！"):
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查是否有超级用户被选中
            placeholders = ','.join('?' for _ in self.checked_items)
            cursor.execute(f"SELECT username FROM users WHERE id IN ({placeholders}) AND role = 'super_admin'", tuple(self.checked_items))
            super_admins = cursor.fetchall()

            if super_admins:
                messagebox.showerror("错误", f"无法删除超级用户: {[name[0] for name in super_admins]}")
                conn.close()
                return

            # 执行删除
            cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", tuple(self.checked_items))
            conn.commit()
            
            deleted_count = cursor.rowcount
            self.checked_items.clear()
            
            messagebox.showinfo("操作完成", f"成功删除 {deleted_count} 个用户。")
            self.refresh_user_list()
            # 删除后全选复选框应该是未选中状态
            self.select_all_var.set(False)

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"删除失败: {e}")
        finally:
            conn.close()  

    def import_users_from_dataframe(self, df, skip_duplicates=True):
        """从DataFrame导入用户数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        imported_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        try:
            # 如果需要跳过重复项，先获取所有现有用户名
            existing_usernames = set()
            if skip_duplicates:
                cursor.execute("SELECT username FROM users")
                existing_usernames = {row[0] for row in cursor.fetchall()}

            for index, row in df.iterrows():
                try:
                    username = str(row.get('username', '')).strip()
                    if not username:
                        errors.append(f"第 {index + 2} 行: 用户名不能为空。")
                        error_count += 1
                        continue

                    if skip_duplicates and username in existing_usernames:
                        skipped_count += 1
                        continue
                    
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    params = (
                        str(row.get('id_card', row.get('ID', ''))).strip(),  # 兼容旧的ID字段
                        username,
                        str(row.get('password', '123456')).strip(),
                        str(row.get('real_name', '')).strip(),
                        str(row.get('email', '')).strip(),
                        str(row.get('phone', '')).strip(),
                        str(row.get('department', '')).strip(),
                        str(row.get('role', 'student')).strip(),
                        str(row.get('status', 'active')).strip(),
                        now,
                        now
                    )

                    # 验证角色
                    if params[7] not in self.roles:
                        errors.append(f"第 {index + 2} 行: 无效的角色 '{params[7]}'")
                        error_count += 1
                        continue

                    cursor.execute("""
                        INSERT INTO users (id_card, username, password, real_name, email, phone, department, role, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, params)
                    
                    imported_count += 1
                    if skip_duplicates:
                        existing_usernames.add(username)

                except sqlite3.IntegrityError:
                    skipped_count += 1
                    errors.append(f"第 {index + 2} 行: 用户名 '{username}' 已存在。")
                except Exception as e:
                    error_count += 1
                    errors.append(f"第 {index + 2} 行: {str(e)}")
            
            conn.commit()

        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("数据库错误", f"导入过程中发生严重错误: {e}")
            return
        finally:
            conn.close()

        # 显示结果
        result_message = f"导入完成！\n\n成功导入: {imported_count} 个用户"
        if skipped_count > 0:
            result_message += f"\n跳过（重复）: {skipped_count} 个用户"
        if error_count > 0:
            result_message += f"\n格式错误: {error_count} 个用户"
        
        if errors:
            result_message += "\n\n错误详情:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                result_message += f"\n... 还有 {len(errors) - 10} 个错误"
        
        messagebox.showinfo("导入结果", result_message)
        self.refresh_user_list()

    def get_next_user_id(self):
        """获取下一个用户ID"""
        users = self.users.get("users", [])
        if not users:
            return 1
        return max(user["id"] for user in users) + 1

    def delete_user_from_database(self, user_id):
        """从数据库删除用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        # 从数据库删除成功后，立即刷新UI
        self.load_users()
        messagebox.showinfo("成功", f"用户 '{user_id}' 已被删除。")


class UserDialog:
    """用户编辑/新增对话框"""
    def __init__(self, parent, user_manager, user_data=None):
        self.parent = parent
        self.user_manager = user_manager
        self.user_data = user_data
        self.is_edit = user_data is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑用户" if self.is_edit else "新增用户")
        self.dialog.geometry("450x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        if self.is_edit:
            self.load_user_data()
    
    def setup_ui(self):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        fields = [
            ("身份证号:", "id_card"),
            ("用户名:", "username"),
            ("密码:", "password"),
            ("真实姓名:", "real_name"),
            ("邮箱:", "email"),
            ("电话:", "phone"),
            ("部门:", "department")
        ]
        
        self.field_vars = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            self.field_vars[field] = var
            entry = ttk.Entry(main_frame, textvariable=var, width=35)
            entry.grid(row=i, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 角色选择
        ttk.Label(main_frame, text="角色:").grid(row=len(fields), column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(value="student")
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var, 
                                 values=list(self.user_manager.roles.keys()), width=32, state="readonly")
        role_combo.grid(row=len(fields), column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 状态选择
        ttk.Label(main_frame, text="状态:").grid(row=len(fields)+1, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar(value="active")
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var,
                                   values=list(self.user_manager.statuses.keys()), width=32, state="readonly")
        status_combo.grid(row=len(fields)+1, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 如果是编辑模式，密码字段设为提示且不可编辑
        if self.is_edit:
            self.field_vars["password"].set("****** (如需修改请联系管理员)")
            # 找到密码输入框并设为只读
            for child in main_frame.winfo_children():
                if isinstance(child, ttk.Entry) and child.grid_info()["row"] == 2:
                    child.config(state="readonly")

    def load_user_data(self):
        """加载用户数据到表单"""
        if not self.user_data:
            return
        
        self.field_vars["id_card"].set(self.user_data.get("id_card", ""))
        self.field_vars["username"].set(self.user_data.get("username", ""))
        self.field_vars["real_name"].set(self.user_data.get("real_name", ""))
        self.field_vars["email"].set(self.user_data.get("email", ""))
        self.field_vars["phone"].set(self.user_data.get("phone", ""))
        self.field_vars["department"].set(self.user_data.get("department", ""))
        self.role_var.set(self.user_data.get("role", "student"))
        self.status_var.set(self.user_data.get("status", "active"))
    
    def save_user(self):
        """保存用户数据到数据库"""
        # 收集表单数据
        username = self.field_vars["username"].get().strip()
        id_card = self.field_vars["id_card"].get().strip()
        
        if not username or not id_card:
            messagebox.showerror("错误", "身份证号和用户名不能为空", parent=self.dialog)
            return

        conn = sqlite3.connect(self.user_manager.db_path)
        cursor = conn.cursor()

        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.is_edit:
                # 编辑模式: UPDATE
                query = """
                    UPDATE users SET 
                    id_card = ?, username = ?, real_name = ?, email = ?, phone = ?, 
                    department = ?, role = ?, status = ?, updated_at = ?
                    WHERE id = ?
                """
                params = (
                    id_card, username, self.field_vars["real_name"].get().strip(),
                    self.field_vars["email"].get().strip(), self.field_vars["phone"].get().strip(),
                    self.field_vars["department"].get().strip(), self.role_var.get(),
                    self.status_var.get(), now, self.user_data["id"]
                )
                cursor.execute(query, params)
            else:
                # 新增模式: INSERT
                password = self.field_vars["password"].get().strip()
                if not password:
                    messagebox.showerror("错误", "新用户密码不能为空", parent=self.dialog)
                    return
                
                query = """
                    INSERT INTO users (id_card, username, password, real_name, email, phone, department, role, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    id_card, username, password,
                    self.field_vars["real_name"].get().strip(), self.field_vars["email"].get().strip(),
                    self.field_vars["phone"].get().strip(), self.field_vars["department"].get().strip(),
                    self.role_var.get(), self.status_var.get(), now, now
                )
                cursor.execute(query, params)
            
            conn.commit()
            messagebox.showinfo("成功", "用户保存成功", parent=self.dialog)
            self.user_manager.refresh_user_list()
            self.dialog.destroy()

        except sqlite3.IntegrityError:
            messagebox.showerror("错误", f"用户名 '{username}' 已存在，请使用其他用户名。", parent=self.dialog)
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"保存用户失败: {e}", parent=self.dialog)
        finally:
            conn.close()

class BatchImportPreviewDialog:
    """批量导入预览对话框"""
    def __init__(self, parent, user_manager, df):
        self.parent = parent
        self.user_manager = user_manager
        self.df = df
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("批量导入预览")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置主题颜色
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff'
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="📥 批量导入预览",
            font=("Microsoft YaHei", 16, "bold"),
            foreground=self.colors['primary']
        )
        title_label.pack(pady=(0, 15))
        
        # 文件信息
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_text = f"文件包含 {len(self.df)} 行数据，{len(self.df.columns)} 列"
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("Microsoft YaHei", 10),
            foreground=self.colors['dark']
        )
        info_label.pack()
        
        # 预览表格
        preview_frame = ttk.Frame(main_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 创建表格
        columns = list(self.df.columns)
        self.tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加数据到表格
        for index, row in self.df.head(50).iterrows():  # 只显示前50行
            values = [str(row.get(col, '')) for col in columns]
            self.tree.insert('', tk.END, values=values)
        
        # 选项框架
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 跳过重复选项
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        skip_check = ttk.Checkbutton(
            options_frame,
            text="跳过重复的用户名",
            variable=self.skip_duplicates_var
        )
        skip_check.pack(side=tk.LEFT)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 导入按钮
        import_btn = tk.Button(
            button_frame,
            text="✅ 确认导入",
            command=self.confirm_import,
            bg=self.colors['success'],
            fg="white",
            font=("Microsoft YaHei", 10, "bold"),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        import_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="❌ 取消",
            command=self.dialog.destroy,
            bg=self.colors['danger'],
            fg="white",
            font=("Microsoft YaHei", 10),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT)
    
    def confirm_import(self):
        """确认导入"""
        try:
            skip_duplicates = self.skip_duplicates_var.get()
            self.user_manager.import_users_from_dataframe(self.df, skip_duplicates)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")


if __name__ == "__main__":
    app = SimpleUserManager()
    app.run()