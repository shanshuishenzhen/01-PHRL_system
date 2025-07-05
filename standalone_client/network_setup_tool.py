#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置和测试工具

提供客户端网络配置、连接测试、故障诊断等功能。
"""

import sys
import json
import subprocess
import socket
import time
from pathlib import Path

# 添加当前目录到系统路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils.network import NetworkUtils
from core.config import client_config

class NetworkSetupTool:
    """网络配置工具"""
    
    def __init__(self):
        self.config = client_config
    
    def show_current_config(self):
        """显示当前网络配置"""
        print("📋 当前网络配置")
        print("=" * 50)
        
        server_url = self.config.get_server_url()
        host = self.config.get('server.host')
        port = self.config.get('server.port')
        protocol = self.config.get('server.protocol')
        timeout = self.config.get('server.timeout')
        
        print(f"服务器URL: {server_url}")
        print(f"服务器地址: {host}")
        print(f"端口: {port}")
        print(f"协议: {protocol}")
        print(f"超时时间: {timeout}秒")
        print(f"重试次数: {self.config.get('server.retry_count')}")
        print(f"重试延迟: {self.config.get('server.retry_delay')}秒")
    
    def configure_server(self, host, port=5000, protocol='http', timeout=30):
        """配置服务器连接"""
        print(f"🔧 配置服务器连接: {protocol}://{host}:{port}")
        
        try:
            # 验证输入
            if not host:
                raise ValueError("服务器地址不能为空")
            
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise ValueError("端口必须是1-65535之间的整数")
            
            if protocol not in ['http', 'https']:
                raise ValueError("协议必须是http或https")
            
            if timeout <= 0:
                raise ValueError("超时时间必须大于0")
            
            # 保存配置
            self.config.set('server.host', host)
            self.config.set('server.port', port)
            self.config.set('server.protocol', protocol)
            self.config.set('server.timeout', timeout)
            
            print("✅ 服务器配置已保存")
            return True
            
        except Exception as e:
            print(f"❌ 配置失败: {e}")
            return False
    
    def test_connection(self):
        """测试网络连接"""
        print("\n🔍 网络连接测试")
        print("=" * 50)
        
        host = self.config.get('server.host')
        port = self.config.get('server.port')
        server_url = self.config.get_server_url()
        
        results = {}
        
        # 1. 测试本地网络
        print("1. 检查本地网络...")
        local_ip = NetworkUtils.get_local_ip()
        print(f"   本地IP地址: {local_ip}")
        results['local_ip'] = local_ip
        
        # 2. 测试互联网连接
        print("2. 测试互联网连接...")
        internet_ok = NetworkUtils.check_internet_connection(timeout=5)
        status = "✅ 正常" if internet_ok else "❌ 异常"
        print(f"   结果: {status}")
        results['internet'] = internet_ok
        
        # 3. 测试服务器端口
        print(f"3. 测试服务器端口 {host}:{port}...")
        port_ok = NetworkUtils.test_port_open(host, port, timeout=5)
        status = "✅ 开放" if port_ok else "❌ 关闭"
        print(f"   结果: {status}")
        results['port'] = port_ok
        
        # 4. 测试服务器响应
        print(f"4. 测试服务器响应 {server_url}...")
        ping_time = NetworkUtils.ping_server(f"{server_url}/api/ping", timeout=10)
        if ping_time:
            print(f"   结果: ✅ 响应时间 {ping_time:.2f}ms")
            results['ping'] = ping_time
        else:
            print(f"   结果: ❌ 无响应")
            results['ping'] = None
        
        # 5. 测试DNS解析
        print(f"5. 测试DNS解析 {host}...")
        try:
            resolved_ip = socket.gethostbyname(host)
            print(f"   结果: ✅ 解析到 {resolved_ip}")
            results['dns'] = resolved_ip
        except Exception as e:
            print(f"   结果: ❌ 解析失败 ({e})")
            results['dns'] = None
        
        # 总结
        print(f"\n📊 连接测试总结:")
        success_count = sum([
            results['internet'],
            results['port'],
            results['ping'] is not None,
            results['dns'] is not None
        ])
        
        print(f"   成功项目: {success_count}/4")
        
        if success_count == 4:
            print("   ✅ 网络连接完全正常")
            return True
        elif success_count >= 2:
            print("   ⚠️ 网络连接部分正常，可能影响使用")
            return False
        else:
            print("   ❌ 网络连接异常，无法正常使用")
            return False
    
    def diagnose_network(self):
        """网络诊断"""
        print("\n🔍 网络诊断")
        print("=" * 50)
        
        host = self.config.get('server.host')
        
        # 1. Ping测试
        print(f"1. Ping测试 {host}...")
        try:
            result = subprocess.run(['ping', '-n', '4', host], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("   ✅ Ping成功")
                # 提取延迟信息
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'ms' in line and '=' in line:
                        print(f"   {line.strip()}")
            else:
                print("   ❌ Ping失败")
                print(f"   错误: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Ping测试异常: {e}")
        
        # 2. 路由跟踪
        print(f"\n2. 路由跟踪 {host}...")
        try:
            result = subprocess.run(['tracert', '-h', '10', host], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("   ✅ 路由跟踪成功")
                lines = result.stdout.split('\n')[:10]  # 只显示前10跳
                for line in lines:
                    if line.strip() and not line.startswith('Tracing'):
                        print(f"   {line.strip()}")
            else:
                print("   ❌ 路由跟踪失败")
        except Exception as e:
            print(f"   ❌ 路由跟踪异常: {e}")
        
        # 3. 端口扫描
        print(f"\n3. 端口扫描 {host}...")
        common_ports = [80, 443, 5000, 8080, 3000]
        for port in common_ports:
            is_open = NetworkUtils.test_port_open(host, port, timeout=3)
            status = "✅ 开放" if is_open else "❌ 关闭"
            print(f"   端口 {port}: {status}")
    
    def generate_config_template(self, server_ip, output_file="client_config_template.json"):
        """生成配置模板"""
        print(f"📝 生成配置模板: {output_file}")
        
        template = {
            "server": {
                "host": server_ip,
                "port": 5000,
                "protocol": "http",
                "timeout": 30,
                "retry_count": 3,
                "retry_delay": 5
            },
            "app": {
                "name": "PH&RL 考试客户端",
                "version": "1.0.0",
                "debug": False,
                "auto_save_interval": 30
            },
            "ui": {
                "window_size": "1024x768",
                "fullscreen_exam": True,
                "font_family": "Microsoft YaHei",
                "font_size": 12,
                "theme_color": "#2196F3",
                "show_progress": True,
                "show_timer": True
            },
            "security": {
                "enable_anti_cheat": True,
                "enable_encryption": True
            },
            "network": {
                "connection_check_interval": 60,
                "offline_mode": False,
                "cache_questions": True,
                "max_cache_size": 100
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置模板已生成: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成配置模板失败: {e}")
            return False

def main():
    """主函数"""
    tool = NetworkSetupTool()
    
    print("🌐 PH&RL 网络配置和测试工具")
    print("=" * 60)
    
    while True:
        print("\n📋 请选择操作:")
        print("1. 显示当前配置")
        print("2. 配置服务器连接")
        print("3. 测试网络连接")
        print("4. 网络诊断")
        print("5. 生成配置模板")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选项 (0-5): ").strip()
            
            if choice == '0':
                print("👋 再见！")
                break
            elif choice == '1':
                tool.show_current_config()
            elif choice == '2':
                print("\n🔧 配置服务器连接")
                host = input("服务器地址: ").strip()
                if not host:
                    print("❌ 服务器地址不能为空")
                    continue
                
                try:
                    port = int(input("端口 (默认5000): ").strip() or "5000")
                    protocol = input("协议 (http/https, 默认http): ").strip() or "http"
                    timeout = int(input("超时时间 (默认30秒): ").strip() or "30")
                    
                    tool.configure_server(host, port, protocol, timeout)
                except ValueError as e:
                    print(f"❌ 输入错误: {e}")
            elif choice == '3':
                tool.test_connection()
            elif choice == '4':
                tool.diagnose_network()
            elif choice == '5':
                server_ip = input("服务器IP地址: ").strip()
                if server_ip:
                    output_file = input("输出文件名 (默认client_config_template.json): ").strip()
                    if not output_file:
                        output_file = "client_config_template.json"
                    tool.generate_config_template(server_ip, output_file)
                else:
                    print("❌ 服务器IP地址不能为空")
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作，退出程序")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()
