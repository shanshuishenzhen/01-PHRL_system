# -*- coding: utf-8 -*-
"""
SQL安全防护工具

提供SQL注入防护、参数化查询、输入验证等安全功能。

更新日志：
- 2025-01-07：创建SQL安全防护工具
"""

import re
import sqlite3
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager


class SQLSecurityError(Exception):
    """SQL安全异常"""
    pass


class SQLInjectionDetector:
    """SQL注入检测器"""
    
    # SQL注入关键词模式
    INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(or|and)\s+\d+\s*=\s*\d+)",
        r"(\b(or|and)\s+['\"].*['\"])",
        r"(;|\|\||&&)",
        r"(\bxp_cmdshell\b)",
        r"(\bsp_executesql\b)",
        r"(\binto\s+outfile\b)",
        r"(\bload_file\b)",
        r"(\bchar\s*\(\s*\d+\s*\))",
    ]
    
    def __init__(self):
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.INJECTION_PATTERNS]
    
    def detect(self, input_string: str) -> bool:
        """
        检测输入是否包含SQL注入
        
        Args:
            input_string: 待检测的字符串
            
        Returns:
            bool: 是否检测到SQL注入
        """
        if not isinstance(input_string, str):
            return False
        
        for pattern in self.patterns:
            if pattern.search(input_string):
                return True
        
        return False
    
    def get_detected_patterns(self, input_string: str) -> List[str]:
        """
        获取检测到的SQL注入模式
        
        Args:
            input_string: 待检测的字符串
            
        Returns:
            List[str]: 检测到的模式列表
        """
        detected = []
        if not isinstance(input_string, str):
            return detected
        
        for i, pattern in enumerate(self.patterns):
            if pattern.search(input_string):
                detected.append(self.INJECTION_PATTERNS[i])
        
        return detected


class ParameterizedQuery:
    """参数化查询工具"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.detector = SQLInjectionDetector()
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        验证查询参数
        
        Args:
            params: 查询参数字典
            
        Returns:
            bool: 参数是否安全
        """
        for key, value in params.items():
            if isinstance(value, str):
                if self.detector.detect(value):
                    detected_patterns = self.detector.get_detected_patterns(value)
                    self.logger.warning(f"检测到SQL注入尝试 - 参数: {key}, 值: {value}, 模式: {detected_patterns}")
                    return False
        
        return True
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[sqlite3.Row]:
        """
        执行安全的参数化查询
        
        Args:
            query: SQL查询语句（使用命名参数）
            params: 查询参数
            
        Returns:
            List[sqlite3.Row]: 查询结果
        """
        if params is None:
            params = {}
        
        # 验证参数
        if not self.validate_parameters(params):
            raise SQLSecurityError("检测到潜在的SQL注入攻击")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        执行安全的参数化更新操作
        
        Args:
            query: SQL更新语句（使用命名参数）
            params: 查询参数
            
        Returns:
            int: 受影响的行数
        """
        if params is None:
            params = {}
        
        # 验证参数
        if not self.validate_parameters(params):
            raise SQLSecurityError("检测到潜在的SQL注入攻击")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_batch(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        """
        执行批量参数化操作
        
        Args:
            query: SQL语句
            params_list: 参数列表
            
        Returns:
            int: 总共受影响的行数
        """
        total_affected = 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for params in params_list:
                # 验证每组参数
                if not self.validate_parameters(params):
                    raise SQLSecurityError(f"检测到潜在的SQL注入攻击: {params}")
                
                cursor.execute(query, params)
                total_affected += cursor.rowcount
            
            conn.commit()
        
        return total_affected


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_user_id(user_id: Union[str, int]) -> bool:
        """验证用户ID"""
        if isinstance(user_id, int):
            return user_id > 0
        if isinstance(user_id, str):
            return user_id.isdigit() and int(user_id) > 0
        return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        if not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """验证用户名格式"""
        if not isinstance(username, str):
            return False
        # 用户名只能包含字母、数字、下划线，长度3-20
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 255) -> str:
        """清理字符串输入"""
        if not isinstance(input_string, str):
            return ""
        
        # 移除潜在危险字符
        sanitized = re.sub(r'[<>"\';\\]', '', input_string)
        
        # 限制长度
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()


def create_safe_query_examples():
    """创建安全查询示例"""
    examples = """
# 安全查询示例

from common.sql_security import ParameterizedQuery, InputValidator

# 1. 创建参数化查询实例
db = ParameterizedQuery("users.db")

# 2. 安全的用户查询
def get_user_by_id(user_id):
    # 验证输入
    if not InputValidator.validate_user_id(user_id):
        raise ValueError("无效的用户ID")
    
    # 参数化查询
    query = "SELECT * FROM users WHERE id = :user_id"
    results = db.execute_query(query, {"user_id": user_id})
    return results

# 3. 安全的用户创建
def create_user(username, email, password):
    # 验证输入
    if not InputValidator.validate_username(username):
        raise ValueError("无效的用户名")
    if not InputValidator.validate_email(email):
        raise ValueError("无效的邮箱")
    
    # 清理输入
    username = InputValidator.sanitize_string(username)
    email = InputValidator.sanitize_string(email)
    
    # 参数化插入
    query = '''
    INSERT INTO users (username, email, password_hash) 
    VALUES (:username, :email, :password)
    '''
    params = {
        "username": username,
        "email": email,
        "password": password  # 应该是已经哈希的密码
    }
    
    affected_rows = db.execute_update(query, params)
    return affected_rows > 0

# 4. 安全的搜索查询
def search_users(search_term):
    # 清理搜索词
    search_term = InputValidator.sanitize_string(search_term, 50)
    
    # 使用LIKE查询，但仍然参数化
    query = '''
    SELECT id, username, email FROM users 
    WHERE username LIKE :search_pattern OR email LIKE :search_pattern
    '''
    params = {"search_pattern": f"%{search_term}%"}
    
    results = db.execute_query(query, params)
    return results
"""
    
    example_file = Path(__file__).parent / "sql_security_examples.py"
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(examples)
    
    print(f"✅ 创建安全查询示例: {example_file}")


if __name__ == "__main__":
    # 测试SQL注入检测
    detector = SQLInjectionDetector()
    
    test_inputs = [
        "normal_input",
        "'; DROP TABLE users; --",
        "1 OR 1=1",
        "admin' OR '1'='1",
        "user@example.com",
        "SELECT * FROM users",
    ]
    
    print("🔍 SQL注入检测测试:")
    for input_str in test_inputs:
        is_injection = detector.detect(input_str)
        status = "❌ 检测到注入" if is_injection else "✅ 安全"
        print(f"  {input_str:<30} {status}")
    
    # 创建示例文件
    create_safe_query_examples()
    
    print("\n📋 使用说明:")
    print("1. 导入安全工具: from common.sql_security import ParameterizedQuery, InputValidator")
    print("2. 创建查询实例: db = ParameterizedQuery('database.db')")
    print("3. 使用参数化查询: db.execute_query('SELECT * FROM users WHERE id = :id', {'id': user_id})")
    print("4. 验证输入: InputValidator.validate_user_id(user_id)")
    print("5. 清理输入: InputValidator.sanitize_string(input_string)")
