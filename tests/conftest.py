"""
pytest配置文件 - 全局fixtures和配置

这个文件包含了所有测试共享的fixtures和配置。
"""

import os
import sys
import json
import tempfile
import shutil
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入项目模块
try:
    from common.config_manager import ConfigManager
    from common.logger import setup_logger
    from common.data_manager import load_json_data, save_json_data
except ImportError as e:
    print(f"Warning: Could not import project modules: {e}")


@pytest.fixture(scope="session")
def project_root():
    """项目根目录路径"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return PROJECT_ROOT / "tests" / "data"


@pytest.fixture(scope="session")
def test_logs_dir():
    """测试日志目录"""
    logs_dir = PROJECT_ROOT / "tests" / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


@pytest.fixture(scope="function")
def temp_dir():
    """临时目录fixture"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_config():
    """模拟配置fixture"""
    return {
        "version": "1.0.0",
        "min_python_version": [3, 6],
        "module_ports": {
            "question_bank": 5000,
            "grading_center": 3000,
            "exam_management": 5001,
            "client": 8080
        },
        "logging": {
            "level": "INFO",
            "max_file_size_mb": 10,
            "backup_count": 5
        },
        "system": {
            "name": "PH&RL 在线考试系统",
            "organization": "PH&RL 教育科技"
        }
    }


@pytest.fixture(scope="function")
def mock_user_data():
    """模拟用户数据fixture"""
    return {
        "users": [
            {
                "id": 1,
                "username": "admin",
                "password": "admin123",
                "role": "super_admin",
                "name": "系统管理员",
                "email": "admin@phrl.com",
                "status": "active"
            },
            {
                "id": 2,
                "username": "teacher1",
                "password": "teacher123",
                "role": "teacher",
                "name": "张老师",
                "email": "teacher1@phrl.com",
                "status": "active"
            },
            {
                "id": 3,
                "username": "student1",
                "password": "student123",
                "role": "student",
                "name": "李同学",
                "email": "student1@phrl.com",
                "status": "active"
            }
        ]
    }


@pytest.fixture(scope="function")
def mock_exam_data():
    """模拟考试数据fixture"""
    return {
        "exams": [
            {
                "id": 1,
                "name": "Python基础测试",
                "description": "测试Python基础知识",
                "status": "published",
                "duration": 60,
                "total_score": 100,
                "pass_score": 60,
                "created_by": 2,
                "created_at": "2024-01-01T10:00:00Z"
            }
        ]
    }


@pytest.fixture(scope="function")
def mock_question_data():
    """模拟题目数据fixture"""
    return {
        "questions": [
            {
                "id": 1,
                "type": "single_choice",
                "content": "Python是什么类型的语言？",
                "options": ["编译型", "解释型", "汇编型", "机器型"],
                "correct_answer": "B",
                "score": 5,
                "difficulty": "easy",
                "category": "Python基础"
            },
            {
                "id": 2,
                "type": "multiple_choice",
                "content": "以下哪些是Python的特点？",
                "options": ["面向对象", "动态类型", "解释执行", "跨平台"],
                "correct_answer": "ABCD",
                "score": 10,
                "difficulty": "medium",
                "category": "Python基础"
            }
        ]
    }


@pytest.fixture(scope="function")
def mock_logger():
    """模拟日志器fixture"""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture(scope="function")
def isolated_filesystem(temp_dir):
    """隔离的文件系统环境"""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 创建测试日志目录
    test_logs_dir = PROJECT_ROOT / "tests" / "logs"
    test_logs_dir.mkdir(exist_ok=True)
    
    # 设置测试日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(test_logs_dir / "test_session.log"),
            logging.StreamHandler()
        ]
    )
    
    yield
    
    # 清理测试环境
    print("\n测试会话结束，清理测试环境...")


@pytest.fixture(scope="function")
def mock_database_connection():
    """模拟数据库连接"""
    connection = Mock()
    connection.execute = Mock()
    connection.fetchall = Mock(return_value=[])
    connection.fetchone = Mock(return_value=None)
    connection.commit = Mock()
    connection.rollback = Mock()
    connection.close = Mock()
    return connection


@pytest.fixture(scope="function")
def mock_http_client():
    """模拟HTTP客户端"""
    client = Mock()
    client.get = Mock()
    client.post = Mock()
    client.put = Mock()
    client.delete = Mock()
    return client


def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "requires_network: 需要网络连接的测试"
    )
    config.addinivalue_line(
        "markers", "requires_database: 需要数据库的测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集项"""
    # 为没有标记的测试添加默认标记
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


def pytest_runtest_setup(item):
    """测试运行前的设置"""
    # 检查网络标记
    if list(item.iter_markers(name="requires_network")):
        # 可以在这里添加网络连接检查
        pass
    
    # 检查数据库标记
    if list(item.iter_markers(name="requires_database")):
        # 可以在这里添加数据库连接检查
        pass


def pytest_runtest_teardown(item, nextitem):
    """测试运行后的清理"""
    # 清理临时文件、连接等
    pass
