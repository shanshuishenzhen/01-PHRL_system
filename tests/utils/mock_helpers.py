"""
Mock辅助工具

提供测试中常用的Mock对象和函数。
"""

from unittest.mock import Mock, MagicMock, patch, PropertyMock
from typing import Dict, List, Any, Optional
import json


class MockConfigManager:
    """模拟配置管理器"""
    
    def __init__(self, config_data=None):
        self.config_data = config_data or {
            "version": "1.0.0",
            "module_ports": {
                "question_bank": 5000,
                "grading_center": 3000,
                "exam_management": 5001,
                "client": 8080
            }
        }
    
    def get(self, key=None, default=None):
        if key is None:
            return self.config_data
        return self.config_data.get(key, default)
    
    def set(self, key, value):
        self.config_data[key] = value
    
    def save(self):
        return True


class MockLogger:
    """模拟日志器"""
    
    def __init__(self):
        self.logs = []
    
    def info(self, message):
        self.logs.append(('INFO', message))
    
    def error(self, message):
        self.logs.append(('ERROR', message))
    
    def warning(self, message):
        self.logs.append(('WARNING', message))
    
    def debug(self, message):
        self.logs.append(('DEBUG', message))
    
    def get_logs(self, level=None):
        if level:
            return [msg for lvl, msg in self.logs if lvl == level]
        return self.logs
    
    def clear_logs(self):
        self.logs.clear()


class MockDatabase:
    """模拟数据库"""
    
    def __init__(self):
        self.data = {}
        self.connected = False
    
    def connect(self):
        self.connected = True
        return True
    
    def disconnect(self):
        self.connected = False
    
    def execute(self, query, params=None):
        # 简单的模拟执行
        return True
    
    def fetchall(self):
        return []
    
    def fetchone(self):
        return None
    
    def commit(self):
        return True
    
    def rollback(self):
        return True


class MockHTTPClient:
    """模拟HTTP客户端"""
    
    def __init__(self):
        self.responses = {}
        self.requests = []
    
    def set_response(self, method, url, response_data, status_code=200):
        """设置响应数据"""
        key = f"{method.upper()}:{url}"
        self.responses[key] = {
            'data': response_data,
            'status_code': status_code
        }
    
    def get(self, url, **kwargs):
        return self._make_request('GET', url, **kwargs)
    
    def post(self, url, data=None, json=None, **kwargs):
        return self._make_request('POST', url, data=data, json=json, **kwargs)
    
    def put(self, url, data=None, json=None, **kwargs):
        return self._make_request('PUT', url, data=data, json=json, **kwargs)
    
    def delete(self, url, **kwargs):
        return self._make_request('DELETE', url, **kwargs)
    
    def _make_request(self, method, url, **kwargs):
        # 记录请求
        self.requests.append({
            'method': method,
            'url': url,
            'kwargs': kwargs
        })
        
        # 返回模拟响应
        key = f"{method}:{url}"
        if key in self.responses:
            response = Mock()
            response.json.return_value = self.responses[key]['data']
            response.status_code = self.responses[key]['status_code']
            response.text = json.dumps(self.responses[key]['data'])
            return response
        
        # 默认响应
        response = Mock()
        response.json.return_value = {}
        response.status_code = 404
        response.text = "{}"
        return response


class MockFileSystem:
    """模拟文件系统"""
    
    def __init__(self):
        self.files = {}
        self.directories = set()
    
    def create_file(self, path, content=""):
        """创建文件"""
        self.files[path] = content
        # 创建父目录
        parent = '/'.join(path.split('/')[:-1])
        if parent:
            self.directories.add(parent)
    
    def read_file(self, path):
        """读取文件"""
        return self.files.get(path)
    
    def exists(self, path):
        """检查路径是否存在"""
        return path in self.files or path in self.directories
    
    def is_file(self, path):
        """检查是否为文件"""
        return path in self.files
    
    def is_dir(self, path):
        """检查是否为目录"""
        return path in self.directories
    
    def list_dir(self, path):
        """列出目录内容"""
        items = []
        for file_path in self.files:
            if file_path.startswith(path + '/'):
                relative = file_path[len(path)+1:]
                if '/' not in relative:
                    items.append(relative)
        for dir_path in self.directories:
            if dir_path.startswith(path + '/'):
                relative = dir_path[len(path)+1:]
                if '/' not in relative:
                    items.append(relative)
        return items


class MockProcess:
    """模拟进程"""
    
    def __init__(self, pid=1234, name="test_process"):
        self.pid = pid
        self.name = name
        self.status = "running"
        self.returncode = None
    
    def is_running(self):
        return self.status == "running"
    
    def terminate(self):
        self.status = "terminated"
        self.returncode = 0
    
    def kill(self):
        self.status = "killed"
        self.returncode = -9
    
    def wait(self, timeout=None):
        return self.returncode
    
    def poll(self):
        return self.returncode if self.status != "running" else None


def create_mock_user(user_id=1, username="testuser", role="student"):
    """创建模拟用户"""
    return {
        "id": user_id,
        "username": username,
        "role": role,
        "name": f"Test User {user_id}",
        "email": f"{username}@test.com",
        "status": "active"
    }


def create_mock_exam(exam_id=1, name="Test Exam", status="published"):
    """创建模拟考试"""
    return {
        "id": exam_id,
        "name": name,
        "status": status,
        "duration": 60,
        "total_score": 100,
        "pass_score": 60,
        "created_at": "2024-01-01T10:00:00Z"
    }


def create_mock_question(question_id=1, question_type="single_choice"):
    """创建模拟题目"""
    return {
        "id": question_id,
        "type": question_type,
        "content": f"Test Question {question_id}",
        "options": ["A", "B", "C", "D"] if "choice" in question_type else None,
        "correct_answer": "A" if "choice" in question_type else "Test Answer",
        "score": 5,
        "difficulty": "medium",
        "category": "Test Category"
    }


def mock_function_with_delay(delay=0.1):
    """创建带延迟的模拟函数"""
    import time
    
    def mock_func(*args, **kwargs):
        time.sleep(delay)
        return True
    
    return Mock(side_effect=mock_func)


def mock_function_with_exception(exception_class=Exception, message="Test exception"):
    """创建抛出异常的模拟函数"""
    def mock_func(*args, **kwargs):
        raise exception_class(message)
    
    return Mock(side_effect=mock_func)


def mock_function_with_sequence(return_values):
    """创建返回序列值的模拟函数"""
    return Mock(side_effect=return_values)


class MockContextManager:
    """模拟上下文管理器"""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.entered = False
        self.exited = False
    
    def __enter__(self):
        self.entered = True
        return self.return_value
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False


def patch_module_function(module_path, function_name, return_value=None, side_effect=None):
    """补丁模块函数的装饰器"""
    def decorator(func):
        with patch(f"{module_path}.{function_name}", 
                  return_value=return_value, side_effect=side_effect):
            return func
    return decorator


def patch_class_method(class_path, method_name, return_value=None, side_effect=None):
    """补丁类方法的装饰器"""
    def decorator(func):
        with patch.object(class_path, method_name, 
                         return_value=return_value, side_effect=side_effect):
            return func
    return decorator
