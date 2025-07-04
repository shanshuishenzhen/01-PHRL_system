#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Requirements文件验证脚本
验证requirements.txt中的依赖包是否正确安装
"""

import subprocess
import sys
import pkg_resources
from pathlib import Path

def read_requirements():
    """读取requirements.txt文件"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return []
    
    requirements = []
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if line and not line.startswith('#'):
                requirements.append(line)
    
    return requirements

def check_installed_packages():
    """检查已安装的包"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            installed_packages = {}
            lines = result.stdout.strip().split('\n')[2:]  # 跳过标题行
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        package_name = parts[0].lower()
                        version = parts[1]
                        installed_packages[package_name] = version
            return installed_packages
        else:
            print(f"❌ 获取已安装包列表失败: {result.stderr}")
            return {}
    except Exception as e:
        print(f"❌ 检查已安装包时出错: {e}")
        return {}

def parse_requirement(req_line):
    """解析requirements行"""
    try:
        # 处理不同的版本指定符
        if '==' in req_line:
            package, version = req_line.split('==', 1)
        elif '>=' in req_line:
            package, version = req_line.split('>=', 1)
        elif '<=' in req_line:
            package, version = req_line.split('<=', 1)
        elif '>' in req_line:
            package, version = req_line.split('>', 1)
        elif '<' in req_line:
            package, version = req_line.split('<', 1)
        else:
            package = req_line
            version = None
        
        return package.strip().lower(), version.strip() if version else None
    except Exception:
        return None, None

def verify_requirements():
    """验证requirements.txt"""
    print("🔍 验证requirements.txt依赖包")
    print("=" * 50)
    
    # 读取requirements
    requirements = read_requirements()
    if not requirements:
        print("❌ 无法读取requirements.txt或文件为空")
        return False
    
    print(f"📋 找到 {len(requirements)} 个依赖包")
    
    # 获取已安装的包
    installed_packages = check_installed_packages()
    if not installed_packages:
        print("❌ 无法获取已安装包列表")
        return False
    
    print(f"📦 系统中已安装 {len(installed_packages)} 个包")
    print()
    
    # 验证每个依赖
    missing_packages = []
    version_mismatches = []
    correct_packages = []
    
    for req in requirements:
        package_name, required_version = parse_requirement(req)
        
        if not package_name:
            print(f"⚠️  无法解析依赖: {req}")
            continue
        
        if package_name in installed_packages:
            installed_version = installed_packages[package_name]
            
            if required_version and required_version != installed_version:
                version_mismatches.append({
                    'package': package_name,
                    'required': required_version,
                    'installed': installed_version
                })
                print(f"⚠️  {package_name}: 版本不匹配 (需要: {required_version}, 已安装: {installed_version})")
            else:
                correct_packages.append(package_name)
                print(f"✅ {package_name}: {installed_version}")
        else:
            missing_packages.append(package_name)
            print(f"❌ {package_name}: 未安装")
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📊 验证结果总结")
    print(f"✅ 正确安装: {len(correct_packages)} 个")
    print(f"⚠️  版本不匹配: {len(version_mismatches)} 个")
    print(f"❌ 缺失包: {len(missing_packages)} 个")
    
    # 重点检查psutil
    print("\n🔍 重点检查psutil:")
    if 'psutil' in installed_packages:
        psutil_version = installed_packages['psutil']
        print(f"✅ psutil已安装: {psutil_version}")
        
        # 检查requirements.txt中的psutil版本
        psutil_req = None
        for req in requirements:
            if req.lower().startswith('psutil'):
                psutil_req = req
                break
        
        if psutil_req:
            _, required_version = parse_requirement(psutil_req)
            if required_version == psutil_version:
                print(f"✅ psutil版本匹配requirements.txt: {required_version}")
            else:
                print(f"⚠️  psutil版本不匹配 (requirements.txt: {required_version}, 已安装: {psutil_version})")
        else:
            print("⚠️  requirements.txt中未找到psutil")
    else:
        print("❌ psutil未安装")
    
    # 提供修复建议
    if missing_packages or version_mismatches:
        print("\n💡 修复建议:")
        if missing_packages:
            print("安装缺失的包:")
            print(f"pip install {' '.join(missing_packages)}")
        
        if version_mismatches:
            print("更新版本不匹配的包:")
            for mismatch in version_mismatches:
                print(f"pip install {mismatch['package']}=={mismatch['required']}")
        
        print("\n或者一次性安装所有依赖:")
        print("pip install -r requirements.txt")
        
        return False
    else:
        print("\n🎉 所有依赖包都已正确安装！")
        return True

def test_psutil_functionality():
    """测试psutil功能"""
    print("\n🧪 测试psutil功能")
    print("-" * 30)
    
    try:
        import psutil
        
        # 测试基本功能
        print(f"✅ psutil版本: {psutil.__version__}")
        print(f"✅ CPU核心数: {psutil.cpu_count()}")
        print(f"✅ CPU使用率: {psutil.cpu_percent(interval=1):.1f}%")
        
        # 测试内存信息
        memory = psutil.virtual_memory()
        print(f"✅ 内存总量: {memory.total / (1024**3):.1f} GB")
        print(f"✅ 内存使用率: {memory.percent:.1f}%")
        
        # 测试磁盘信息
        disk = psutil.disk_usage('/')
        print(f"✅ 磁盘使用率: {disk.percent:.1f}%")
        
        print("✅ psutil功能测试通过")
        return True
        
    except ImportError:
        print("❌ 无法导入psutil")
        return False
    except Exception as e:
        print(f"❌ psutil功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 PH&RL系统依赖包验证工具")
    print("=" * 50)
    
    # 验证requirements.txt
    requirements_ok = verify_requirements()
    
    # 测试psutil功能
    psutil_ok = test_psutil_functionality()
    
    print("\n" + "=" * 50)
    print("🎯 最终结果")
    
    if requirements_ok and psutil_ok:
        print("🎉 所有检查通过！系统依赖完整。")
        print("\n现在可以正常启动主控台:")
        print("python main_console.py")
        return True
    else:
        print("⚠️  发现问题，请按照上述建议修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
