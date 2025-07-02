# -*- coding: utf-8 -*-
"""
自动化测试框架

提供统一的测试工具和测试用例管理。

更新日志：
- 2025-01-07：创建自动化测试框架
"""

import os
import sys
import unittest
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 导入项目模块
from common.logger import get_logger
from common.config_manager import ConfigManager
from common.error_handler import handle_error, safe_call
from common.sql_security import ParameterizedQuery, SQLInjectionDetector
from common.health_checker import SystemHealthChecker


class TestResult:
    """测试结果类"""
    
    def __init__(self, test_name: str, success: bool, message: str = "", duration: float = 0.0):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.duration = duration
        self.timestamp = time.time()


class BaseTestCase(unittest.TestCase):
    """基础测试用例类"""
    
    def setUp(self):
        """测试前置设置"""
        self.logger = get_logger("test_framework")
        self.config_manager = ConfigManager()
        self.start_time = time.time()
    
    def tearDown(self):
        """测试后置清理"""
        self.duration = time.time() - self.start_time
    
    def assert_no_sql_injection(self, input_string: str):
        """断言输入不包含SQL注入"""
        detector = SQLInjectionDetector()
        self.assertFalse(
            detector.detect(input_string),
            f"检测到SQL注入: {input_string}"
        )
    
    def assert_safe_file_path(self, file_path: str):
        """断言文件路径安全"""
        # 检查路径遍历攻击
        self.assertNotIn("..", file_path, "检测到路径遍历攻击")
        self.assertNotIn("//", file_path, "检测到双斜杠")
        
        # 检查绝对路径（在某些情况下可能不安全）
        if os.path.isabs(file_path):
            self.logger.warning(f"使用了绝对路径: {file_path}")


class ConfigManagerTest(BaseTestCase):
    """配置管理器测试"""
    
    def test_config_loading(self):
        """测试配置加载"""
        # 测试获取默认配置
        version = self.config_manager.get("version")
        self.assertIsNotNone(version, "版本配置不能为空")
        
        # 测试获取不存在的配置
        non_existent = self.config_manager.get("non_existent_key", "default_value")
        self.assertEqual(non_existent, "default_value", "默认值返回错误")
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试端口配置
        module_ports = self.config_manager.get("module_ports", {})
        self.assertIsInstance(module_ports, dict, "模块端口配置应该是字典")
        
        for module, port in module_ports.items():
            self.assertIsInstance(port, int, f"端口 {module}:{port} 应该是整数")
            self.assertGreater(port, 0, f"端口 {module}:{port} 应该大于0")
            self.assertLess(port, 65536, f"端口 {module}:{port} 应该小于65536")


class SQLSecurityTest(BaseTestCase):
    """SQL安全测试"""
    
    def test_sql_injection_detection(self):
        """测试SQL注入检测"""
        detector = SQLInjectionDetector()
        
        # 正常输入
        safe_inputs = [
            "normal_user",
            "user@example.com",
            "123456",
            "测试用户"
        ]
        
        for input_str in safe_inputs:
            self.assertFalse(
                detector.detect(input_str),
                f"正常输入被误判为SQL注入: {input_str}"
            )
        
        # 恶意输入
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; exec xp_cmdshell('dir'); --"
        ]
        
        for input_str in malicious_inputs:
            self.assertTrue(
                detector.detect(input_str),
                f"SQL注入未被检测到: {input_str}"
            )
    
    def test_parameterized_query(self):
        """测试参数化查询"""
        # 创建临时数据库
        test_db = "test_security.db"
        
        try:
            # 初始化测试数据库
            import sqlite3
            conn = sqlite3.connect(test_db)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    email TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            # 测试参数化查询
            db = ParameterizedQuery(test_db)
            
            # 测试安全插入
            result = db.execute_update(
                "INSERT INTO test_users (username, email) VALUES (:username, :email)",
                {"username": "test_user", "email": "test@example.com"}
            )
            self.assertGreater(result, 0, "插入操作应该成功")
            
            # 测试安全查询
            results = db.execute_query(
                "SELECT * FROM test_users WHERE username = :username",
                {"username": "test_user"}
            )
            self.assertGreater(len(results), 0, "查询应该返回结果")
            
        finally:
            # 清理测试数据库
            if os.path.exists(test_db):
                os.remove(test_db)


class ErrorHandlerTest(BaseTestCase):
    """错误处理测试"""
    
    def test_safe_call(self):
        """测试安全调用"""
        # 测试正常函数
        success, result = safe_call(lambda x: x * 2, 5)
        self.assertTrue(success, "正常函数调用应该成功")
        self.assertEqual(result, 10, "函数结果错误")
        
        # 测试异常函数
        success, result = safe_call(lambda x: 1 / x, 0)
        self.assertFalse(success, "异常函数调用应该失败")
        self.assertIsInstance(result, Exception, "应该返回异常对象")
    
    def test_error_decorator(self):
        """测试错误装饰器"""
        @handle_error
        def test_function(x):
            if x == 0:
                raise ValueError("测试异常")
            return x * 2
        
        # 正常情况
        result = test_function(5)
        self.assertEqual(result, 10, "正常情况应该返回正确结果")
        
        # 异常情况
        result = test_function(0)
        self.assertIsNone(result, "异常情况应该返回None")


class HealthCheckerTest(BaseTestCase):
    """健康检查测试"""
    
    def test_system_health_check(self):
        """测试系统健康检查"""
        checker = SystemHealthChecker()
        
        # 测试系统资源检查
        result = checker.check_system_resources()
        self.assertIsNotNone(result, "系统资源检查应该返回结果")
        self.assertIn(result.status.value, ["healthy", "warning", "critical"], "状态值应该有效")
        
        # 测试依赖检查
        result = checker.check_dependencies()
        self.assertIsNotNone(result, "依赖检查应该返回结果")
        
        # 测试完整检查
        results = checker.run_full_check()
        self.assertGreater(len(results), 0, "完整检查应该返回多个结果")


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.logger = get_logger("test_runner")
        self.results: List[TestResult] = []
    
    def run_all_tests(self) -> List[TestResult]:
        """运行所有测试"""
        test_classes = [
            ConfigManagerTest,
            SQLSecurityTest,
            ErrorHandlerTest,
            HealthCheckerTest
        ]
        
        for test_class in test_classes:
            self.run_test_class(test_class)
        
        return self.results
    
    def run_test_class(self, test_class):
        """运行测试类"""
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        for test in suite:
            start_time = time.time()
            
            try:
                test.debug()  # 运行测试
                duration = time.time() - start_time
                
                result = TestResult(
                    test_name=f"{test_class.__name__}.{test._testMethodName}",
                    success=True,
                    message="测试通过",
                    duration=duration
                )
                
            except Exception as e:
                duration = time.time() - start_time
                
                result = TestResult(
                    test_name=f"{test_class.__name__}.{test._testMethodName}",
                    success=False,
                    message=str(e),
                    duration=duration
                )
            
            self.results.append(result)
            self.logger.info(f"测试 {result.test_name}: {'通过' if result.success else '失败'}")
    
    def generate_report(self) -> str:
        """生成测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.results)
        
        report = f"""
# 自动化测试报告
生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 测试概要
- 总测试数: {total_tests}
- 通过: {passed_tests}
- 失败: {failed_tests}
- 成功率: {(passed_tests/total_tests*100):.1f}%
- 总耗时: {total_duration:.2f}秒

## 测试详情
"""
        
        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            report += f"\n### {status_icon} {result.test_name}\n"
            report += f"状态: {'通过' if result.success else '失败'}\n"
            report += f"耗时: {result.duration:.3f}秒\n"
            if not result.success:
                report += f"错误信息: {result.message}\n"
        
        return report


if __name__ == "__main__":
    # 运行所有测试
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # 生成报告
    report = runner.generate_report()
    print(report)
    
    # 保存报告
    report_file = f"test_report_{int(time.time())}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📋 测试报告已保存: {report_file}")
    
    # 返回退出码
    failed_count = sum(1 for r in results if not r.success)
    sys.exit(failed_count)
