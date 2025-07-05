#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量部署客户端配置工具

用于批量配置多个客户端的服务器连接信息。
"""

import json
import shutil
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

class BatchDeployTool:
    """批量部署工具"""
    
    def __init__(self):
        self.config_template = {
            "server": {
                "host": "",
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
                "auto_save_interval": 30,
                "theme": "default"
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
                "enable_encryption": True,
                "check_interval": 1
            },
            "network": {
                "connection_check_interval": 60,
                "offline_mode": False,
                "cache_questions": True,
                "max_cache_size": 100
            },
            "exam": {
                "auto_save_interval": 30,
                "confirm_submit": True,
                "show_question_numbers": True,
                "allow_review": True,
                "time_warning_minutes": 5
            }
        }
    
    def create_config_file(self, server_ip: str, target_path: Path, custom_settings: Dict = None) -> bool:
        """创建配置文件"""
        try:
            # 复制模板
            config = self.config_template.copy()
            
            # 设置服务器IP
            config["server"]["host"] = server_ip
            
            # 应用自定义设置
            if custom_settings:
                self._deep_update(config, custom_settings)
            
            # 确保目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入配置文件
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ 创建配置文件失败 {target_path}: {e}")
            return False
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def deploy_to_directories(self, server_ip: str, target_dirs: List[str], custom_settings: Dict = None) -> int:
        """部署到指定目录列表"""
        success_count = 0
        
        print(f"🚀 开始批量部署配置...")
        print(f"服务器IP: {server_ip}")
        print(f"目标目录数: {len(target_dirs)}")
        print("=" * 50)
        
        for i, target_dir in enumerate(target_dirs, 1):
            target_path = Path(target_dir) / "config" / "client_config.json"
            
            print(f"[{i}/{len(target_dirs)}] 部署到: {target_dir}")
            
            if self.create_config_file(server_ip, target_path, custom_settings):
                print(f"   ✅ 成功")
                success_count += 1
            else:
                print(f"   ❌ 失败")
        
        print("=" * 50)
        print(f"📊 部署结果: {success_count}/{len(target_dirs)} 成功")
        
        return success_count
    
    def deploy_to_network_drives(self, server_ip: str, network_paths: List[str]) -> int:
        """部署到网络驱动器"""
        success_count = 0
        
        print(f"🌐 开始网络部署配置...")
        print(f"服务器IP: {server_ip}")
        print(f"网络路径数: {len(network_paths)}")
        print("=" * 50)
        
        for i, network_path in enumerate(network_paths, 1):
            target_path = Path(network_path) / "config" / "client_config.json"
            
            print(f"[{i}/{len(network_paths)}] 部署到: {network_path}")
            
            # 检查网络路径是否可访问
            if not Path(network_path).exists():
                print(f"   ❌ 网络路径不可访问")
                continue
            
            if self.create_config_file(server_ip, target_path):
                print(f"   ✅ 成功")
                success_count += 1
            else:
                print(f"   ❌ 失败")
        
        print("=" * 50)
        print(f"📊 网络部署结果: {success_count}/{len(network_paths)} 成功")
        
        return success_count
    
    def generate_batch_script(self, server_ip: str, output_file: str = "deploy_config.bat") -> bool:
        """生成批处理部署脚本"""
        try:
            script_content = f'''@echo off
echo 🚀 PH&RL 客户端配置批量部署
echo ================================

set SERVER_IP={server_ip}
set CONFIG_DIR=config
set CONFIG_FILE=client_config.json

echo 服务器IP: %SERVER_IP%
echo.

REM 创建配置目录
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM 生成配置文件
echo {{> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   "server": {{>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "host": "%SERVER_IP%",>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "port": 5000,>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "protocol": "http",>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "timeout": 30,>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "retry_count": 3,>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "retry_delay": 5>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   }},>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   "app": {{>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "name": "PH&RL 考试客户端",>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "version": "1.0.0",>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "debug": false>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   }},>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   "ui": {{>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "window_size": "1024x768",>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "fullscreen_exam": true,>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "theme_color": "#2196F3">> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   }},>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   "security": {{>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "enable_anti_cheat": true,>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo     "enable_encryption": true>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo   }}>> "%CONFIG_DIR%\\%CONFIG_FILE%"
echo }}>> "%CONFIG_DIR%\\%CONFIG_FILE%"

echo ✅ 配置文件已生成: %CONFIG_DIR%\\%CONFIG_FILE%
echo.
echo 📋 配置信息:
type "%CONFIG_DIR%\\%CONFIG_FILE%"
echo.
echo 🎯 部署完成！
pause
'''
            
            with open(output_file, 'w', encoding='gbk') as f:
                f.write(script_content)
            
            print(f"✅ 批处理脚本已生成: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成批处理脚本失败: {e}")
            return False
    
    def validate_deployment(self, target_dirs: List[str]) -> Dict[str, Any]:
        """验证部署结果"""
        print("🔍 验证部署结果...")
        print("=" * 50)
        
        results = {
            "total": len(target_dirs),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for i, target_dir in enumerate(target_dirs, 1):
            config_path = Path(target_dir) / "config" / "client_config.json"
            
            print(f"[{i}/{len(target_dirs)}] 验证: {target_dir}")
            
            detail = {
                "path": target_dir,
                "config_exists": False,
                "config_valid": False,
                "server_ip": None
            }
            
            # 检查配置文件是否存在
            if config_path.exists():
                detail["config_exists"] = True
                print(f"   ✅ 配置文件存在")
                
                # 检查配置文件是否有效
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    if "server" in config and "host" in config["server"]:
                        detail["config_valid"] = True
                        detail["server_ip"] = config["server"]["host"]
                        print(f"   ✅ 配置有效，服务器: {detail['server_ip']}")
                        results["success"] += 1
                    else:
                        print(f"   ❌ 配置格式错误")
                        results["failed"] += 1
                        
                except Exception as e:
                    print(f"   ❌ 配置文件损坏: {e}")
                    results["failed"] += 1
            else:
                print(f"   ❌ 配置文件不存在")
                results["failed"] += 1
            
            results["details"].append(detail)
        
        print("=" * 50)
        print(f"📊 验证结果: {results['success']}/{results['total']} 成功")
        
        return results

def main():
    """主函数"""
    tool = BatchDeployTool()
    
    print("🚀 PH&RL 客户端配置批量部署工具")
    print("=" * 60)
    
    while True:
        print("\n📋 请选择操作:")
        print("1. 批量部署到本地目录")
        print("2. 批量部署到网络驱动器")
        print("3. 生成批处理部署脚本")
        print("4. 验证部署结果")
        print("5. 生成配置模板")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选项 (0-5): ").strip()
            
            if choice == '0':
                print("👋 再见！")
                break
            elif choice == '1':
                server_ip = input("服务器IP地址: ").strip()
                if not server_ip:
                    print("❌ 服务器IP地址不能为空")
                    continue
                
                print("请输入目标目录列表（每行一个，空行结束）:")
                target_dirs = []
                while True:
                    dir_path = input().strip()
                    if not dir_path:
                        break
                    target_dirs.append(dir_path)
                
                if target_dirs:
                    tool.deploy_to_directories(server_ip, target_dirs)
                else:
                    print("❌ 未输入目标目录")
            
            elif choice == '2':
                server_ip = input("服务器IP地址: ").strip()
                if not server_ip:
                    print("❌ 服务器IP地址不能为空")
                    continue
                
                print("请输入网络路径列表（每行一个，空行结束）:")
                print("示例: \\\\192.168.1.101\\ExamClient")
                network_paths = []
                while True:
                    path = input().strip()
                    if not path:
                        break
                    network_paths.append(path)
                
                if network_paths:
                    tool.deploy_to_network_drives(server_ip, network_paths)
                else:
                    print("❌ 未输入网络路径")
            
            elif choice == '3':
                server_ip = input("服务器IP地址: ").strip()
                if not server_ip:
                    print("❌ 服务器IP地址不能为空")
                    continue
                
                output_file = input("输出文件名 (默认deploy_config.bat): ").strip()
                if not output_file:
                    output_file = "deploy_config.bat"
                
                tool.generate_batch_script(server_ip, output_file)
            
            elif choice == '4':
                print("请输入要验证的目录列表（每行一个，空行结束）:")
                target_dirs = []
                while True:
                    dir_path = input().strip()
                    if not dir_path:
                        break
                    target_dirs.append(dir_path)
                
                if target_dirs:
                    tool.validate_deployment(target_dirs)
                else:
                    print("❌ 未输入目录")
            
            elif choice == '5':
                server_ip = input("服务器IP地址: ").strip()
                if not server_ip:
                    print("❌ 服务器IP地址不能为空")
                    continue
                
                output_file = input("输出文件名 (默认client_config_template.json): ").strip()
                if not output_file:
                    output_file = "client_config_template.json"
                
                config_path = Path(output_file)
                if tool.create_config_file(server_ip, config_path):
                    print(f"✅ 配置模板已生成: {output_file}")
                else:
                    print(f"❌ 生成配置模板失败")
            
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作，退出程序")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()
