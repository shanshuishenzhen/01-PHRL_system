#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多项目数据库管理器
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

class DatabaseManager:
    """多项目数据库管理器"""
    
    def __init__(self, base_dir="question_banks"):
        self.base_dir = base_dir
        # 确保目录存在
        os.makedirs(base_dir, exist_ok=True)
        self._engines = {}
        self._sessions = {}
    
    def get_engine(self, project_name):
        """获取指定项目的数据库引擎"""
        if project_name not in self._engines:
            # 安全的文件名处理
            safe_name = self._safe_filename(project_name)
            db_path = os.path.join(self.base_dir, f"{safe_name}.db")
            
            # 创建数据库引擎
            self._engines[project_name] = create_engine(f'sqlite:///{db_path}')
            
            # 创建表结构
            Base.metadata.create_all(self._engines[project_name])
            
        return self._engines[project_name]
    
    def get_session(self, project_name):
        """获取指定项目的数据库会话"""
        engine = self.get_engine(project_name)
        Session = sessionmaker(bind=engine)
        return Session()
    
    def list_projects(self):
        """列出所有项目"""
        if not os.path.exists(self.base_dir):
            return []
        
        projects = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.db'):
                # 恢复原始项目名称
                project_name = filename[:-3]  # 移除.db后缀
                projects.append(project_name)
        
        return sorted(projects)
    
    def create_project(self, project_name):
        """创建新项目"""
        try:
            # 获取引擎会自动创建数据库和表
            engine = self.get_engine(project_name)
            return True
        except Exception as e:
            print(f"创建项目失败: {e}")
            return False
    
    def delete_project(self, project_name):
        """删除项目（谨慎使用）"""
        try:
            safe_name = self._safe_filename(project_name)
            db_path = os.path.join(self.base_dir, f"{safe_name}.db")
            
            if os.path.exists(db_path):
                os.remove(db_path)
                
            # 清理缓存
            if project_name in self._engines:
                del self._engines[project_name]
            if project_name in self._sessions:
                del self._sessions[project_name]
                
            return True
        except Exception as e:
            print(f"删除项目失败: {e}")
            return False
    
    def get_project_stats(self, project_name):
        """获取项目统计信息"""
        try:
            from models import Question, QuestionBank
            session = self.get_session(project_name)
            
            question_count = session.query(Question).count()
            bank_count = session.query(QuestionBank).count()
            
            session.close()
            
            return {
                'questions': question_count,
                'banks': bank_count
            }
        except Exception as e:
            print(f"获取项目统计失败: {e}")
            return {'questions': 0, 'banks': 0}
    
    def _safe_filename(self, filename):
        """生成安全的文件名"""
        import re
        import hashlib
        
        # 移除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 如果包含非ASCII字符，使用hash值
        if any(ord(char) > 127 for char in safe_name):
            # 保留原始名称的前缀，加上hash值
            prefix = re.sub(r'[^a-zA-Z0-9_-]', '', safe_name)[:10]
            hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:8]
            safe_name = f"{prefix}_{hash_value}"
        
        # 确保文件名不为空且不超过100字符
        if not safe_name or len(safe_name) > 100:
            hash_value = hashlib.md5(filename.encode('utf-8')).hexdigest()[:16]
            safe_name = f"project_{hash_value}"
        
        return safe_name
    
    def close_all(self):
        """关闭所有连接"""
        for session in self._sessions.values():
            try:
                session.close()
            except:
                pass
        self._sessions.clear()

# 全局数据库管理器实例
db_manager = DatabaseManager()
