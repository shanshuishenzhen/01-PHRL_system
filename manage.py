#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL 在线考试系统管理脚本

提供系统管理功能，包括：
- 数据库初始化和迁移
- 用户管理
- 系统配置
- 数据备份和恢复
- 系统监控
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from common.config_manager import ConfigManager
from common.enhanced_logger import get_enhanced_log_manager


class SystemManager:
    """系统管理器"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = get_enhanced_log_manager().get_logger("system_manager")
        self.project_root = Path(__file__).parent
    
    def init_database(self):
        """初始化数据库"""
        print("🗄️ 初始化数据库...")
        
        try:
            # 创建数据库表
            from common.data_manager import ensure_dir
            
            # 创建数据目录
            data_dir = self.project_root / "data"
            ensure_dir(str(data_dir))
            
            # 初始化各模块数据库
            modules = [
                "user_management",
                "question_bank_web", 
                "exam_management",
                "grading_center",
                "score_statistics"
            ]
            
            for module in modules:
                module_data_dir = data_dir / module
                ensure_dir(str(module_data_dir))
                
                # 创建默认数据文件
                if module == "user_management":
                    self._create_default_users(module_data_dir)
                elif module == "question_bank_web":
                    self._create_default_questions(module_data_dir)
            
            print("✅ 数据库初始化完成")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            sys.exit(1)
    
    def _create_default_users(self, data_dir: Path):
        """创建默认用户"""
        users_file = data_dir / "users.json"
        if not users_file.exists():
            default_users = {
                "users": [
                    {
                        "id": 1,
                        "username": "admin",
                        "password": "admin123",
                        "role": "super_admin",
                        "name": "系统管理员",
                        "email": "admin@phrl.com",
                        "status": "active",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "username": "teacher",
                        "password": "teacher123",
                        "role": "teacher",
                        "name": "示例教师",
                        "email": "teacher@phrl.com",
                        "status": "active",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 3,
                        "username": "student",
                        "password": "student123",
                        "role": "student",
                        "name": "示例学生",
                        "email": "student@phrl.com",
                        "status": "active",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
    
    def _create_default_questions(self, data_dir: Path):
        """创建默认题目"""
        questions_file = data_dir / "questions.json"
        if not questions_file.exists():
            default_questions = {
                "questions": [
                    {
                        "id": 1,
                        "type": "single_choice",
                        "content": "Python是什么类型的语言？",
                        "options": ["编译型", "解释型", "汇编型", "机器型"],
                        "correct_answer": "B",
                        "score": 5,
                        "difficulty": "easy",
                        "category": "Python基础",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "type": "multiple_choice",
                        "content": "以下哪些是Python的特点？",
                        "options": ["面向对象", "动态类型", "解释执行", "跨平台"],
                        "correct_answer": "ABCD",
                        "score": 10,
                        "difficulty": "medium",
                        "category": "Python基础",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(default_questions, f, indent=2, ensure_ascii=False)
    
    def create_user(self, username: str, password: str, role: str, name: str, email: str):
        """创建用户"""
        print(f"👤 创建用户: {username}")
        
        try:
            users_file = self.project_root / "data" / "user_management" / "users.json"
            
            # 读取现有用户
            if users_file.exists():
                with open(users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"users": []}
            
            # 检查用户是否已存在
            for user in data["users"]:
                if user["username"] == username:
                    print(f"❌ 用户 {username} 已存在")
                    return
            
            # 创建新用户
            new_user = {
                "id": max([u["id"] for u in data["users"]], default=0) + 1,
                "username": username,
                "password": password,
                "role": role,
                "name": name,
                "email": email,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            data["users"].append(new_user)
            
            # 保存用户数据
            users_file.parent.mkdir(parents=True, exist_ok=True)
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 用户 {username} 创建成功")
            
        except Exception as e:
            print(f"❌ 创建用户失败: {e}")
    
    def backup_data(self, backup_path: str = None):
        """备份数据"""
        if not backup_path:
            backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        print(f"💾 备份数据到: {backup_path}")
        
        try:
            import tarfile
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                # 备份数据目录
                data_dir = self.project_root / "data"
                if data_dir.exists():
                    tar.add(data_dir, arcname="data")
                
                # 备份配置文件
                config_dir = self.project_root / "config"
                if config_dir.exists():
                    tar.add(config_dir, arcname="config")
                
                # 备份日志文件（最近7天）
                logs_dir = self.project_root / "logs"
                if logs_dir.exists():
                    tar.add(logs_dir, arcname="logs")
            
            print(f"✅ 数据备份完成: {backup_path}")
            
        except Exception as e:
            print(f"❌ 数据备份失败: {e}")
    
    def restore_data(self, backup_path: str):
        """恢复数据"""
        print(f"🔄 从备份恢复数据: {backup_path}")
        
        try:
            import tarfile
            
            if not Path(backup_path).exists():
                print(f"❌ 备份文件不存在: {backup_path}")
                return
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(self.project_root)
            
            print("✅ 数据恢复完成")
            
        except Exception as e:
            print(f"❌ 数据恢复失败: {e}")
    
    def check_system(self):
        """系统检查"""
        print("🔍 系统检查...")
        
        # 检查Python版本
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查依赖包
        try:
            import flask
            print(f"Flask版本: {flask.__version__}")
        except ImportError:
            print("❌ Flask未安装")
        
        try:
            import pandas
            print(f"Pandas版本: {pandas.__version__}")
        except ImportError:
            print("❌ Pandas未安装")
        
        # 检查目录结构
        required_dirs = ["data", "logs", "config", "common"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name} 目录存在")
            else:
                print(f"❌ {dir_name} 目录不存在")
        
        # 检查配置文件
        config_file = self.project_root / "config.json"
        if config_file.exists():
            print("✅ 配置文件存在")
        else:
            print("❌ 配置文件不存在")
    
    def start_services(self):
        """启动所有服务"""
        print("🚀 启动所有服务...")
        
        try:
            # 启动主系统
            subprocess.run([sys.executable, "start_system.py"], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 启动服务失败: {e}")
        except KeyboardInterrupt:
            print("\n🛑 服务已停止")
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        try:
            subprocess.run([sys.executable, "run_tests.py", "--all"], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 测试失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PH&RL 在线考试系统管理工具")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 初始化数据库
    subparsers.add_parser("init_db", help="初始化数据库")
    
    # 创建用户
    user_parser = subparsers.add_parser("create_user", help="创建用户")
    user_parser.add_argument("username", help="用户名")
    user_parser.add_argument("password", help="密码")
    user_parser.add_argument("role", choices=["super_admin", "admin", "teacher", "student"], help="角色")
    user_parser.add_argument("name", help="姓名")
    user_parser.add_argument("email", help="邮箱")
    
    # 备份数据
    backup_parser = subparsers.add_parser("backup", help="备份数据")
    backup_parser.add_argument("--path", help="备份文件路径")
    
    # 恢复数据
    restore_parser = subparsers.add_parser("restore", help="恢复数据")
    restore_parser.add_argument("path", help="备份文件路径")
    
    # 系统检查
    subparsers.add_parser("check", help="系统检查")
    
    # 启动服务
    subparsers.add_parser("start", help="启动所有服务")
    
    # 运行测试
    subparsers.add_parser("test", help="运行测试")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = SystemManager()
    
    if args.command == "init_db":
        manager.init_database()
    elif args.command == "create_user":
        manager.create_user(args.username, args.password, args.role, args.name, args.email)
    elif args.command == "backup":
        manager.backup_data(args.path)
    elif args.command == "restore":
        manager.restore_data(args.path)
    elif args.command == "check":
        manager.check_system()
    elif args.command == "start":
        manager.start_services()
    elif args.command == "test":
        manager.run_tests()


if __name__ == "__main__":
    main()
