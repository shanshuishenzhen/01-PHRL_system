#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub上传助手

当Git推送失败时，提供替代的上传方案和诊断信息
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path


def run_command(cmd, timeout=30):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "命令超时"
    except Exception as e:
        return -1, "", str(e)


def check_network():
    """检查网络连接"""
    print("🌐 检查网络连接...")
    
    # 检查基本网络
    code, out, err = run_command("ping github.com -n 2")
    if code == 0:
        print("✅ 基本网络连接正常")
    else:
        print("❌ 基本网络连接失败")
        return False
    
    # 检查HTTPS连接
    code, out, err = run_command("curl -I https://github.com --connect-timeout 10")
    if code == 0:
        print("✅ HTTPS连接正常")
        return True
    else:
        print(f"❌ HTTPS连接失败: {err}")
        return False


def check_git_config():
    """检查Git配置"""
    print("\n🔧 检查Git配置...")
    
    configs = [
        "user.name",
        "user.email", 
        "http.sslVerify",
        "http.postBuffer",
        "remote.origin.url"
    ]
    
    for config in configs:
        code, out, err = run_command(f"git config --get {config}")
        if code == 0:
            print(f"✅ {config}: {out.strip()}")
        else:
            print(f"❌ {config}: 未设置")


def try_different_push_methods():
    """尝试不同的推送方法"""
    print("\n🚀 尝试不同的推送方法...")
    
    methods = [
        {
            "name": "标准推送",
            "commands": ["git push -u origin main"]
        },
        {
            "name": "强制推送",
            "commands": ["git push -f origin main"]
        },
        {
            "name": "设置代理后推送",
            "commands": [
                "git config --global http.proxy ''",
                "git config --global https.proxy ''",
                "git push -u origin main"
            ]
        },
        {
            "name": "增加缓冲区后推送",
            "commands": [
                "git config --global http.postBuffer 1048576000",
                "git config --global http.lowSpeedLimit 0",
                "git config --global http.lowSpeedTime 999999",
                "git push -u origin main"
            ]
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n方法 {i}: {method['name']}")
        
        success = True
        for cmd in method['commands']:
            print(f"  执行: {cmd}")
            code, out, err = run_command(cmd, timeout=120)
            
            if code != 0:
                print(f"  ❌ 失败: {err}")
                success = False
                break
            else:
                if out.strip():
                    print(f"  ✅ 成功: {out.strip()}")
        
        if success:
            print(f"🎉 方法 {i} 成功!")
            return True
        
        time.sleep(2)  # 等待2秒后尝试下一个方法
    
    return False


def generate_manual_instructions():
    """生成手动操作说明"""
    instructions = """
📋 手动上传说明

如果自动推送失败，请尝试以下手动方法：

方法1: 使用GitHub Desktop
1. 下载并安装 GitHub Desktop
2. 克隆仓库: https://github.com/shanshuishenzhen/01-PHRL_system
3. 将本地文件复制到克隆的仓库目录
4. 在GitHub Desktop中提交并推送

方法2: 使用Web界面上传
1. 访问: https://github.com/shanshuishenzhen/01-PHRL_system
2. 点击 "uploading an existing file"
3. 将项目文件打包为zip上传
4. 解压并整理文件结构

方法3: 使用SSH
1. 生成SSH密钥: ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
2. 添加SSH密钥到GitHub账户
3. 更改远程URL: git remote set-url origin git@github.com:shanshuishenzhen/01-PHRL_system.git
4. 推送: git push -u origin main

方法4: 分批推送
1. 创建.gitignore忽略大文件
2. 分批添加文件: git add 目录名/
3. 分批提交和推送

网络问题排查:
- 检查防火墙设置
- 尝试使用VPN
- 检查代理设置
- 联系网络管理员
"""
    
    with open("MANUAL_UPLOAD_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("📝 已生成手动上传说明: MANUAL_UPLOAD_INSTRUCTIONS.md")


def main():
    """主函数"""
    print("🔄 GitHub上传助手")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if not Path(".git").exists():
        print("❌ 当前目录不是Git仓库")
        return
    
    # 检查网络连接
    if not check_network():
        print("\n❌ 网络连接有问题，请检查网络设置")
        generate_manual_instructions()
        return
    
    # 检查Git配置
    check_git_config()
    
    # 尝试推送
    if try_different_push_methods():
        print("\n🎉 成功推送到GitHub!")
        print("📍 仓库地址: https://github.com/shanshuishenzhen/01-PHRL_system")
    else:
        print("\n❌ 所有自动推送方法都失败了")
        generate_manual_instructions()
        print("\n请查看 MANUAL_UPLOAD_INSTRUCTIONS.md 获取手动上传说明")


if __name__ == "__main__":
    main()
