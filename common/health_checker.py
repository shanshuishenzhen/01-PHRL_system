# -*- coding: utf-8 -*-
"""
系统健康检查工具

提供系统状态监控、健康检查、性能监控等功能。

更新日志：
- 2025-01-07：创建系统健康检查工具
"""

import os
import sys
import time
import psutil
import sqlite3
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.config_manager import ConfigManager


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: HealthStatus
    message: str
    details: Optional[Dict] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class SystemHealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.logger = get_logger("health_checker")
        self.config_manager = ConfigManager()
        self.results: List[HealthCheckResult] = []
    
    def check_system_resources(self) -> HealthCheckResult:
        """检查系统资源"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
            
            # 判断状态
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = HealthStatus.CRITICAL
                message = "系统资源使用率过高"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
                status = HealthStatus.WARNING
                message = "系统资源使用率较高"
            else:
                status = HealthStatus.HEALTHY
                message = "系统资源正常"
            
            return HealthCheckResult("system_resources", status, message, details)
            
        except Exception as e:
            return HealthCheckResult("system_resources", HealthStatus.CRITICAL, f"资源检查失败: {e}")
    
    def check_database_connection(self, db_path: str = "database.sqlite") -> HealthCheckResult:
        """检查数据库连接"""
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(db_path):
                return HealthCheckResult("database", HealthStatus.CRITICAL, f"数据库文件不存在: {db_path}")
            
            # 尝试连接数据库
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            
            # 执行简单查询
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            # 检查数据库大小
            db_size = os.path.getsize(db_path)
            db_size_mb = round(db_size / (1024**2), 2)
            
            conn.close()
            
            details = {
                "db_path": db_path,
                "db_size_mb": db_size_mb,
                "connection_test": "success"
            }
            
            return HealthCheckResult("database", HealthStatus.HEALTHY, "数据库连接正常", details)
            
        except sqlite3.Error as e:
            return HealthCheckResult("database", HealthStatus.CRITICAL, f"数据库连接失败: {e}")
        except Exception as e:
            return HealthCheckResult("database", HealthStatus.CRITICAL, f"数据库检查异常: {e}")
    
    def check_web_services(self) -> List[HealthCheckResult]:
        """检查Web服务"""
        results = []
        
        # 获取配置的端口
        try:
            module_ports = self.config_manager.get("module_ports", {})
        except:
            module_ports = {
                "question_bank": 5000,
                "grading_center": 3000,
                "exam_management": 5001
            }
        
        for service_name, port in module_ports.items():
            try:
                url = f"http://localhost:{port}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    status = HealthStatus.HEALTHY
                    message = f"服务正常运行"
                else:
                    status = HealthStatus.WARNING
                    message = f"服务响应异常: {response.status_code}"
                
                details = {
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
                
                results.append(HealthCheckResult(f"web_service_{service_name}", status, message, details))
                
            except requests.ConnectionError:
                results.append(HealthCheckResult(
                    f"web_service_{service_name}", 
                    HealthStatus.WARNING, 
                    "服务未启动或无法连接",
                    {"url": f"http://localhost:{port}"}
                ))
            except Exception as e:
                results.append(HealthCheckResult(
                    f"web_service_{service_name}", 
                    HealthStatus.CRITICAL, 
                    f"服务检查失败: {e}",
                    {"url": f"http://localhost:{port}"}
                ))
        
        return results
    
    def check_file_permissions(self) -> HealthCheckResult:
        """检查文件权限"""
        try:
            critical_paths = [
                "logs",
                "data",
                "uploads",
                "config.json"
            ]
            
            permission_issues = []
            
            for path in critical_paths:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        # 检查目录读写权限
                        if not os.access(path, os.R_OK | os.W_OK):
                            permission_issues.append(f"目录 {path} 权限不足")
                    else:
                        # 检查文件读写权限
                        if not os.access(path, os.R_OK | os.W_OK):
                            permission_issues.append(f"文件 {path} 权限不足")
                else:
                    permission_issues.append(f"路径 {path} 不存在")
            
            if permission_issues:
                return HealthCheckResult(
                    "file_permissions", 
                    HealthStatus.WARNING, 
                    "发现权限问题",
                    {"issues": permission_issues}
                )
            else:
                return HealthCheckResult("file_permissions", HealthStatus.HEALTHY, "文件权限正常")
                
        except Exception as e:
            return HealthCheckResult("file_permissions", HealthStatus.CRITICAL, f"权限检查失败: {e}")
    
    def check_dependencies(self) -> HealthCheckResult:
        """检查依赖包"""
        try:
            required_packages = [
                "flask", "pandas", "numpy", "openpyxl", 
                "psutil", "requests", "sqlalchemy"
            ]
            
            missing_packages = []
            installed_packages = {}
            
            for package in required_packages:
                try:
                    module = __import__(package)
                    version = getattr(module, "__version__", "unknown")
                    installed_packages[package] = version
                except ImportError:
                    missing_packages.append(package)
            
            details = {
                "installed": installed_packages,
                "missing": missing_packages
            }
            
            if missing_packages:
                return HealthCheckResult(
                    "dependencies", 
                    HealthStatus.CRITICAL, 
                    f"缺少依赖包: {', '.join(missing_packages)}",
                    details
                )
            else:
                return HealthCheckResult("dependencies", HealthStatus.HEALTHY, "依赖包完整", details)
                
        except Exception as e:
            return HealthCheckResult("dependencies", HealthStatus.CRITICAL, f"依赖检查失败: {e}")
    
    def run_full_check(self) -> List[HealthCheckResult]:
        """运行完整的健康检查"""
        self.results = []
        
        # 系统资源检查
        self.results.append(self.check_system_resources())
        
        # 数据库检查
        self.results.append(self.check_database_connection())
        
        # Web服务检查
        self.results.extend(self.check_web_services())
        
        # 文件权限检查
        self.results.append(self.check_file_permissions())
        
        # 依赖包检查
        self.results.append(self.check_dependencies())
        
        return self.results
    
    def get_overall_status(self) -> HealthStatus:
        """获取整体健康状态"""
        if not self.results:
            return HealthStatus.UNKNOWN
        
        has_critical = any(r.status == HealthStatus.CRITICAL for r in self.results)
        has_warning = any(r.status == HealthStatus.WARNING for r in self.results)
        
        if has_critical:
            return HealthStatus.CRITICAL
        elif has_warning:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def generate_report(self) -> str:
        """生成健康检查报告"""
        if not self.results:
            self.run_full_check()
        
        overall_status = self.get_overall_status()
        
        report = f"""
# 系统健康检查报告
生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
整体状态: {overall_status.value.upper()}

## 检查结果详情
"""
        
        for result in self.results:
            status_icon = {
                HealthStatus.HEALTHY: "✅",
                HealthStatus.WARNING: "⚠️",
                HealthStatus.CRITICAL: "❌",
                HealthStatus.UNKNOWN: "❓"
            }.get(result.status, "❓")
            
            report += f"\n### {status_icon} {result.component}\n"
            report += f"状态: {result.status.value}\n"
            report += f"消息: {result.message}\n"
            
            if result.details:
                report += "详情:\n"
                for key, value in result.details.items():
                    report += f"  - {key}: {value}\n"
        
        return report


if __name__ == "__main__":
    # 运行健康检查
    checker = SystemHealthChecker()
    results = checker.run_full_check()
    
    # 生成报告
    report = checker.generate_report()
    print(report)
    
    # 保存报告
    report_file = f"health_report_{int(time.time())}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📋 健康检查报告已保存: {report_file}")
