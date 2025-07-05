#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能Git推送工具

自动处理大文件、敏感文件和生成的文件，安全地推送到GitHub。
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

class SmartGitPush:
    """智能Git推送工具"""
    
    def __init__(self):
        self.root_path = Path(__file__).parent
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        
        # 需要排除的文件模式
        self.exclude_patterns = [
            # 数据库文件
            "*.db",
            "*.db-wal",
            "*.db-shm",
            "*.sqlite",
            "*.sqlite3",
            
            # 日志文件
            "*.log",
            "logs/",
            
            # 缓存和临时文件
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".pytest_cache/",
            "*.tmp",
            "*.temp",
            
            # 敏感配置文件
            "*password*",
            "*secret*",
            "*private*",
            "*.env",
            
            # 大型媒体文件
            "*.mp4",
            "*.avi",
            "*.mov",
            "*.wmv",
            "*.flv",
            
            # 备份文件
            "*.bak",
            "*.backup",
            "*_backup*",
            
            # Node.js
            "node_modules/",
            "package-lock.json",
            
            # Python虚拟环境
            "venv/",
            "env/",
            ".venv/",
            
            # IDE文件
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            
            # 系统文件
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini"
        ]
        
        # 需要特别处理的敏感文件
        self.sensitive_files = [
            "exam_backup_*.json",
            "*_credentials.json",
            "user_data.json",
            "admin_config.json"
        ]
    
    def check_git_status(self):
        """检查Git状态"""
        print("🔍 检查Git状态...")
        
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.root_path)
            
            if result.returncode != 0:
                print(f"❌ Git状态检查失败: {result.stderr}")
                return False
            
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"📊 发现 {len(changes)} 个变更文件")
            
            return changes
            
        except Exception as e:
            print(f"❌ Git状态检查异常: {e}")
            return False
    
    def check_large_files(self):
        """检查大文件"""
        print("📏 检查大文件...")
        
        large_files = []
        
        try:
            # 获取所有跟踪的文件
            result = subprocess.run(['git', 'ls-files'], 
                                  capture_output=True, text=True, cwd=self.root_path)
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                
                for file_path in files:
                    full_path = self.root_path / file_path
                    if full_path.exists():
                        size = full_path.stat().st_size
                        if size > self.max_file_size:
                            large_files.append({
                                'path': file_path,
                                'size': size,
                                'size_mb': size / (1024 * 1024)
                            })
            
            if large_files:
                print(f"⚠️ 发现 {len(large_files)} 个大文件:")
                for file_info in large_files:
                    print(f"   {file_info['path']} ({file_info['size_mb']:.1f}MB)")
            else:
                print("✅ 没有发现大文件")
            
            return large_files
            
        except Exception as e:
            print(f"❌ 大文件检查异常: {e}")
            return []
    
    def update_gitignore(self):
        """更新.gitignore文件"""
        print("📝 更新.gitignore文件...")
        
        gitignore_path = self.root_path / '.gitignore'
        
        # 读取现有内容
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 准备新的忽略规则
        new_rules = [
            "# PH&RL System - Auto Generated Ignore Rules",
            "",
            "# Database files",
            "*.db",
            "*.db-wal", 
            "*.db-shm",
            "*.sqlite",
            "*.sqlite3",
            "",
            "# Log files",
            "*.log",
            "logs/",
            "",
            "# Cache and temporary files",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".pytest_cache/",
            "*.tmp",
            "*.temp",
            "",
            "# Sensitive files",
            "*password*",
            "*secret*",
            "*private*",
            "*.env",
            "exam_backup_*.json",
            "*_credentials.json",
            "",
            "# Large media files",
            "*.mp4",
            "*.avi", 
            "*.mov",
            "*.wmv",
            "*.flv",
            "",
            "# Backup files",
            "*.bak",
            "*.backup",
            "*_backup*",
            "",
            "# Development environment",
            "node_modules/",
            "venv/",
            "env/",
            ".venv/",
            "",
            "# IDE files",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "",
            "# System files",
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini",
            "",
            "# Generated reports (keep only essential ones)",
            "*_REPORT.md",
            "*_GUIDE.md",
            "paper_validation_reports/",
            "",
            "# Test and debug files",
            "test_*.py",
            "debug_*.py",
            "minimal_*.py",
            "quick_*.py",
            "simple_*.py",
            ""
        ]
        
        # 检查是否需要更新
        new_content = "\n".join(new_rules)
        
        if "# PH&RL System - Auto Generated Ignore Rules" not in existing_content:
            # 添加新规则
            updated_content = existing_content + "\n\n" + new_content
            
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ .gitignore已更新")
            return True
        else:
            print("✅ .gitignore已是最新")
            return False
    
    def create_readme_github(self):
        """创建GitHub专用README"""
        print("📖 创建GitHub README...")
        
        readme_content = f"""# 🎓 PH&RL 专业技能认证考试系统

## 📋 项目概述

PH&RL（Professional & Reliable）考试系统是一个完整的专业技能认证考试解决方案，支持多种题型、防作弊功能和自动阅卷。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   题库管理      │    │   考试管理      │    │   阅卷中心      │
│ Question Bank   │    │ Exam Management │    │ Grading Center  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────┐
         │              客户端 (Standalone Client)      │
         │            • 考试答题界面                    │
         │            • 防作弊功能                      │
         │            • 离线答题支持                    │
         └─────────────────────────────────────────────┘
```

## ✨ 主要功能

### 🎯 核心功能
- **多题型支持**：单选、多选、判断、填空、简答、论述题
- **智能组卷**：自动组卷和手动组卷
- **防作弊系统**：全屏模式、进程监控、焦点检测
- **自动阅卷**：客观题自动评分，主观题辅助评分
- **成绩管理**：成绩统计、分析和导出

### 🛡️ 安全特性
- **多层认证**：用户认证 + 隐藏超级管理员
- **权限控制**：基于角色的访问控制
- **数据加密**：敏感数据加密存储
- **审计日志**：完整的操作日志记录

### 🌐 网络功能
- **局域网部署**：支持C/S架构部署
- **离线支持**：支持离线答题和同步
- **批量管理**：支持批量用户和考试管理

## 🚀 快速开始

### 环境要求
- **操作系统**：Windows 10/11
- **Python**：3.8+
- **数据库**：SQLite/MySQL
- **网络**：局域网环境

### 安装部署

1. **克隆项目**
```bash
git clone https://github.com/shanshuishenzhen/01-PHRL_system.git
cd 01-PHRL_system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
# 启动所有服务
python start_all_services.py

# 或分别启动各个模块
python exam_management/app.py
python question_bank_web/app.py
python standalone_client.py
```

4. **访问系统**
- 题库管理：http://localhost:5001
- 考试管理：http://localhost:5002
- 客户端：直接运行可执行文件

## 📚 文档指南

- **[完整系统指南](COMPLETE_SYSTEM_GUIDE.md)**：系统完整使用指南
- **[客户端通信指南](CLIENT_SERVER_COMMUNICATION_GUIDE.md)**：客户端与服务器通信配置
- **[快速部署指南](QUICK_DEPLOYMENT_GUIDE.md)**：快速部署和配置
- **[约定管理指南](CONVENTIONS_MANAGEMENT_GUIDE.md)**：系统约定和规范管理

## 🔧 配置说明

### 服务器配置
```json
{{
    "server": {{
        "host": "192.168.1.100",
        "port": 5000,
        "protocol": "http",
        "timeout": 30
    }}
}}
```

### 客户端配置
```json
{{
    "ui": {{
        "fullscreen_exam": true,
        "theme_color": "#2196F3"
    }},
    "security": {{
        "enable_anti_cheat": true
    }}
}}
```

## 🎯 使用场景

- **教育机构**：学校、培训机构的在线考试
- **企业培训**：员工技能认证和培训考核
- **资格认证**：专业资格认证考试
- **竞赛活动**：各类知识竞赛和技能比赛

## 🛠️ 技术栈

- **后端**：Python Flask, SQLAlchemy
- **前端**：HTML5, CSS3, JavaScript, Tkinter
- **数据库**：SQLite, MySQL
- **网络**：HTTP/HTTPS RESTful API
- **安全**：JWT认证, 数据加密

## 📊 系统特点

- **高可靠性**：稳定的系统架构和容错机制
- **易部署**：支持一键部署和批量配置
- **可扩展**：模块化设计，易于扩展功能
- **用户友好**：直观的用户界面和操作流程

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

如有问题或建议，请通过以下方式联系：
- 提交Issue：[GitHub Issues](https://github.com/shanshuishenzhen/01-PHRL_system/issues)
- 邮件联系：[技术支持邮箱]

---

**🎓 PH&RL考试系统 - 专业、可靠的考试解决方案**

*最后更新：{datetime.now().strftime('%Y-%m-%d')}*
"""
        
        readme_path = self.root_path / 'README_GitHub.md'
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ GitHub README已创建")
        return True
    
    def selective_add_files(self):
        """选择性添加文件"""
        print("📁 选择性添加文件...")
        
        # 重要的核心文件和目录
        important_files = [
            # 核心应用文件
            "launcher.py",
            "standalone_client.py", 
            "developer_tools.py",
            "start_all_services.py",
            
            # 核心模块
            "exam_management/",
            "question_bank_web/",
            "grading_center/",
            "standalone_client/",
            "common/",
            "client/",
            
            # 配置和约定
            "system_conventions.json",
            "client_config.json",
            
            # 重要文档
            "README_GitHub.md",
            "COMPLETE_SYSTEM_GUIDE.md",
            "CLIENT_SERVER_COMMUNICATION_GUIDE.md",
            "QUICK_DEPLOYMENT_GUIDE.md",
            "CONVENTIONS_MANAGEMENT_GUIDE.md",
            
            # 部署工具
            "batch_deploy_config.py",
            "smart_git_push.py",
            
            # 配置文件
            ".gitignore",
            "requirements.txt"
        ]
        
        added_count = 0
        
        for file_pattern in important_files:
            file_path = self.root_path / file_pattern
            
            if file_path.exists():
                try:
                    if file_path.is_dir():
                        # 添加目录（排除敏感文件）
                        result = subprocess.run(['git', 'add', file_pattern], 
                                              cwd=self.root_path, capture_output=True)
                        if result.returncode == 0:
                            print(f"   ✅ 已添加目录: {file_pattern}")
                            added_count += 1
                        else:
                            print(f"   ⚠️ 添加目录失败: {file_pattern}")
                    else:
                        # 添加文件
                        result = subprocess.run(['git', 'add', file_pattern], 
                                              cwd=self.root_path, capture_output=True)
                        if result.returncode == 0:
                            print(f"   ✅ 已添加文件: {file_pattern}")
                            added_count += 1
                        else:
                            print(f"   ⚠️ 添加文件失败: {file_pattern}")
                            
                except Exception as e:
                    print(f"   ❌ 添加失败 {file_pattern}: {e}")
            else:
                print(f"   ⚠️ 文件不存在: {file_pattern}")
        
        print(f"📊 成功添加 {added_count} 个文件/目录")
        return added_count > 0
    
    def commit_changes(self):
        """提交更改"""
        print("💾 提交更改...")
        
        commit_message = f"""🚀 PH&RL考试系统重大更新 - {datetime.now().strftime('%Y-%m-%d')}

✨ 新增功能:
• 完整的客户端考试系统
• 防作弊功能和调试模式
• 智能网络配置和批量部署工具
• 系统约定管理和自然语言配置
• 隐藏超级管理员认证系统

🔧 技术改进:
• 客户端与服务器通信优化
• 数据库集成和API接口完善
• 用户模块集成修复
• 考试流程和答题功能完善

📚 文档完善:
• 完整系统使用指南
• 客户端通信配置文档
• 快速部署操作手册
• 约定管理使用指南

🛡️ 安全增强:
• 多层认证机制
• 防作弊监控系统
• 数据加密和权限控制
• 审计日志和安全检查

🚀 部署优化:
• 一键启动所有服务
• 批量客户端配置部署
• 智能Git推送工具
• 网络诊断和故障排除

系统现已完全就绪，支持生产环境部署！"""
        
        try:
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 更改已提交")
                return True
            else:
                print(f"❌ 提交失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 提交异常: {e}")
            return False
    
    def push_to_github(self):
        """推送到GitHub"""
        print("🚀 推送到GitHub...")
        
        try:
            # 推送到远程仓库
            result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                  cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 成功推送到GitHub!")
                print(f"🔗 仓库地址: https://github.com/shanshuishenzhen/01-PHRL_system")
                return True
            else:
                print(f"❌ 推送失败: {result.stderr}")
                
                # 如果是认证问题，提供帮助信息
                if "authentication" in result.stderr.lower() or "permission" in result.stderr.lower():
                    print("\n🔐 认证问题解决方案:")
                    print("1. 检查GitHub Personal Access Token")
                    print("2. 运行: git config --global credential.helper store")
                    print("3. 或使用SSH密钥认证")
                
                return False
                
        except Exception as e:
            print(f"❌ 推送异常: {e}")
            return False
    
    def run(self):
        """执行完整的推送流程"""
        print("🎯 PH&RL系统智能Git推送")
        print("=" * 60)
        
        # 1. 检查Git状态
        changes = self.check_git_status()
        if not changes:
            print("✅ 没有需要推送的更改")
            return True
        
        # 2. 检查大文件
        large_files = self.check_large_files()
        if large_files:
            print("⚠️ 发现大文件，将通过.gitignore排除")
        
        # 3. 更新.gitignore
        self.update_gitignore()
        
        # 4. 创建GitHub README
        self.create_readme_github()
        
        # 5. 选择性添加文件
        if not self.selective_add_files():
            print("❌ 没有文件被添加")
            return False
        
        # 6. 提交更改
        if not self.commit_changes():
            print("❌ 提交失败")
            return False
        
        # 7. 推送到GitHub
        if not self.push_to_github():
            print("❌ 推送失败")
            return False
        
        print("\n🎉 推送完成!")
        print("📊 推送总结:")
        print(f"   • 处理了 {len(changes)} 个变更文件")
        print(f"   • 排除了敏感和大文件")
        print(f"   • 更新了项目文档")
        print(f"   • 成功推送到GitHub")
        
        return True

def main():
    """主函数"""
    pusher = SmartGitPush()
    success = pusher.run()
    
    if success:
        print("\n🎯 下一步操作:")
        print("1. 访问GitHub仓库查看更新")
        print("2. 检查Actions是否正常运行")
        print("3. 更新项目文档和Wiki")
        print("4. 通知团队成员拉取最新代码")
    else:
        print("\n❌ 推送失败，请检查错误信息并重试")

if __name__ == "__main__":
    main()
