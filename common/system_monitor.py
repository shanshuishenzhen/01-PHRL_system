#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控器

监控系统运行状态，包括：
- 系统资源监控（CPU、内存、磁盘）
- 进程监控
- 网络监控
- 服务健康检查
- 性能指标收集
- 告警和通知
"""

import os
import sys
import json
import time
import psutil
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]
    uptime: float


@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    create_time: str
    cmdline: List[str]


@dataclass
class Alert:
    """告警信息"""
    id: str
    level: str  # info, warning, error, critical
    title: str
    message: str
    timestamp: str
    source: str
    resolved: bool = False
    resolved_at: str = None


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, config_path: str = "config/monitor.json"):
        self.config_path = Path(config_path)
        self.setup_logging()
        self.load_config()
        
        # 监控状态
        self.running = False
        self.monitor_thread = None
        
        # 数据存储
        self.db_path = Path("data/monitor.db")
        self.init_database()
        
        # 告警管理
        self.alerts: List[Alert] = []
        self.alert_handlers = []
        
        # 性能历史
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "monitor.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"加载配置失败: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "monitoring": {
                "interval": 30,  # 监控间隔（秒）
                "enabled": True,
                "collect_process_info": True,
                "collect_network_info": True
            },
            "thresholds": {
                "cpu_warning": 80,
                "cpu_critical": 95,
                "memory_warning": 85,
                "memory_critical": 95,
                "disk_warning": 85,
                "disk_critical": 95,
                "process_cpu_warning": 50,
                "process_memory_warning": 500  # MB
            },
            "alerts": {
                "enabled": True,
                "email_enabled": False,
                "email_smtp": "smtp.gmail.com",
                "email_port": 587,
                "email_user": "",
                "email_password": "",
                "email_recipients": []
            },
            "retention": {
                "metrics_days": 30,
                "alerts_days": 90
            },
            "services": [
                {
                    "name": "question_bank",
                    "host": "localhost",
                    "port": 5000,
                    "path": "/health"
                },
                {
                    "name": "exam_management",
                    "host": "localhost",
                    "port": 5001,
                    "path": "/health"
                },
                {
                    "name": "grading_center",
                    "host": "localhost",
                    "port": 3000,
                    "path": "/health"
                }
            ]
        }
    
    def save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def init_database(self):
        """初始化数据库"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # 系统指标表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_io TEXT,
                    process_count INTEGER,
                    load_average TEXT,
                    uptime REAL
                )
            """)
            
            # 进程信息表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS process_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    pid INTEGER,
                    name TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_mb REAL,
                    status TEXT
                )
            """)
            
            # 告警表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    level TEXT,
                    title TEXT,
                    message TEXT,
                    timestamp TEXT,
                    source TEXT,
                    resolved INTEGER,
                    resolved_at TEXT
                )
            """)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 网络IO
            network_io = {}
            if self.config["monitoring"]["collect_network_info"]:
                net_io = psutil.net_io_counters()
                network_io = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 负载平均值
            load_average = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # 系统运行时间
            uptime = time.time() - psutil.boot_time()
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                process_count=process_count,
                load_average=load_average,
                uptime=uptime
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
            return None
    
    def collect_process_info(self) -> List[ProcessInfo]:
        """收集进程信息"""
        if not self.config["monitoring"]["collect_process_info"]:
            return []
        
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time', 'cmdline']):
                try:
                    info = proc.info
                    
                    # 过滤高资源使用的进程
                    cpu_threshold = self.config["thresholds"]["process_cpu_warning"]
                    memory_threshold = self.config["thresholds"]["process_memory_warning"]
                    
                    memory_mb = info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0
                    
                    if info['cpu_percent'] > cpu_threshold or memory_mb > memory_threshold:
                        process_info = ProcessInfo(
                            pid=info['pid'],
                            name=info['name'],
                            cpu_percent=info['cpu_percent'] or 0,
                            memory_percent=info['memory_percent'] or 0,
                            memory_mb=memory_mb,
                            status=info['status'],
                            create_time=datetime.fromtimestamp(info['create_time']).isoformat() if info['create_time'] else "",
                            cmdline=info['cmdline'] or []
                        )
                        processes.append(process_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"收集进程信息失败: {e}")
        
        return processes
    
    def check_thresholds(self, metrics: SystemMetrics):
        """检查阈值并生成告警"""
        thresholds = self.config["thresholds"]
        
        # CPU告警
        if metrics.cpu_percent >= thresholds["cpu_critical"]:
            self.create_alert("critical", "CPU使用率过高", 
                            f"CPU使用率达到 {metrics.cpu_percent:.1f}%", "system")
        elif metrics.cpu_percent >= thresholds["cpu_warning"]:
            self.create_alert("warning", "CPU使用率警告", 
                            f"CPU使用率达到 {metrics.cpu_percent:.1f}%", "system")
        
        # 内存告警
        if metrics.memory_percent >= thresholds["memory_critical"]:
            self.create_alert("critical", "内存使用率过高", 
                            f"内存使用率达到 {metrics.memory_percent:.1f}%", "system")
        elif metrics.memory_percent >= thresholds["memory_warning"]:
            self.create_alert("warning", "内存使用率警告", 
                            f"内存使用率达到 {metrics.memory_percent:.1f}%", "system")
        
        # 磁盘告警
        if metrics.disk_percent >= thresholds["disk_critical"]:
            self.create_alert("critical", "磁盘使用率过高", 
                            f"磁盘使用率达到 {metrics.disk_percent:.1f}%", "system")
        elif metrics.disk_percent >= thresholds["disk_warning"]:
            self.create_alert("warning", "磁盘使用率警告", 
                            f"磁盘使用率达到 {metrics.disk_percent:.1f}%", "system")
    
    def create_alert(self, level: str, title: str, message: str, source: str):
        """创建告警"""
        alert_id = f"{source}_{level}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now().isoformat(),
            source=source
        )
        
        self.alerts.append(alert)
        self.save_alert_to_db(alert)
        
        # 触发告警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"告警处理器失败: {e}")
        
        # 发送邮件通知
        if self.config["alerts"]["email_enabled"]:
            self.send_email_alert(alert)
        
        self.logger.warning(f"[{level.upper()}] {title}: {message}")
    
    def save_metrics_to_db(self, metrics: SystemMetrics):
        """保存指标到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_percent, 
                     network_io, process_count, load_average, uptime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp, metrics.cpu_percent, metrics.memory_percent,
                    metrics.disk_percent, json.dumps(metrics.network_io),
                    metrics.process_count, json.dumps(metrics.load_average),
                    metrics.uptime
                ))
        except Exception as e:
            self.logger.error(f"保存指标到数据库失败: {e}")
    
    def save_alert_to_db(self, alert: Alert):
        """保存告警到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO alerts 
                    (id, level, title, message, timestamp, source, resolved, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.id, alert.level, alert.title, alert.message,
                    alert.timestamp, alert.source, int(alert.resolved),
                    alert.resolved_at
                ))
        except Exception as e:
            self.logger.error(f"保存告警到数据库失败: {e}")
    
    def send_email_alert(self, alert: Alert):
        """发送邮件告警"""
        try:
            config = self.config["alerts"]
            
            msg = MimeMultipart()
            msg['From'] = config["email_user"]
            msg['To'] = ", ".join(config["email_recipients"])
            msg['Subject'] = f"[{alert.level.upper()}] {alert.title}"
            
            body = f"""
            告警级别: {alert.level}
            告警标题: {alert.title}
            告警消息: {alert.message}
            告警来源: {alert.source}
            告警时间: {alert.timestamp}
            """
            
            msg.attach(MimeText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(config["email_smtp"], config["email_port"])
            server.starttls()
            server.login(config["email_user"], config["email_password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"邮件告警发送成功: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"发送邮件告警失败: {e}")
    
    def monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 收集系统指标
                metrics = self.collect_system_metrics()
                if metrics:
                    self.metrics_history.append(metrics)
                    self.save_metrics_to_db(metrics)
                    
                    # 检查阈值
                    self.check_thresholds(metrics)
                    
                    # 限制历史记录大小
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history.pop(0)
                
                # 收集进程信息
                processes = self.collect_process_info()
                
                # 等待下次监控
                time.sleep(self.config["monitoring"]["interval"])
                
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
                time.sleep(10)  # 异常时等待10秒
    
    def start_monitoring(self):
        """开始监控"""
        if self.running:
            self.logger.warning("监控已在运行中")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("系统监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("系统监控已停止")
    
    def get_current_status(self) -> Dict:
        """获取当前状态"""
        if not self.metrics_history:
            return {"error": "没有监控数据"}
        
        latest_metrics = self.metrics_history[-1]
        
        return {
            "timestamp": latest_metrics.timestamp,
            "system": {
                "cpu_percent": latest_metrics.cpu_percent,
                "memory_percent": latest_metrics.memory_percent,
                "disk_percent": latest_metrics.disk_percent,
                "process_count": latest_metrics.process_count,
                "uptime": latest_metrics.uptime
            },
            "alerts": {
                "total": len(self.alerts),
                "unresolved": len([a for a in self.alerts if not a.resolved]),
                "critical": len([a for a in self.alerts if a.level == "critical" and not a.resolved])
            },
            "monitoring": {
                "running": self.running,
                "interval": self.config["monitoring"]["interval"],
                "history_size": len(self.metrics_history)
            }
        }


def main():
    """主函数 - 测试系统监控器"""
    monitor = SystemMonitor()
    
    print("📊 系统监控器测试")
    
    # 启动监控
    monitor.start_monitoring()
    
    try:
        # 运行一段时间
        for i in range(5):
            time.sleep(10)
            status = monitor.get_current_status()
            print(f"\n状态更新 {i+1}:")
            print(f"CPU: {status['system']['cpu_percent']:.1f}%")
            print(f"内存: {status['system']['memory_percent']:.1f}%")
            print(f"磁盘: {status['system']['disk_percent']:.1f}%")
            print(f"进程数: {status['system']['process_count']}")
            print(f"未解决告警: {status['alerts']['unresolved']}")
    
    except KeyboardInterrupt:
        print("\n停止监控...")
    
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()
