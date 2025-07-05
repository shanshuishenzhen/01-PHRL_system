#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包配置

PyInstaller打包配置和构建脚本。
"""

import os
import sys
from pathlib import Path

# 项目信息
PROJECT_NAME = "PH&RL考试客户端"
PROJECT_VERSION = "1.0.0"
PROJECT_AUTHOR = "PH&RL Team"
PROJECT_DESCRIPTION = "PH&RL独立考试客户端"

# 路径配置
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
MAIN_SCRIPT = CURRENT_DIR / "main.py"
BUILD_DIR = CURRENT_DIR / "build"
DIST_DIR = CURRENT_DIR / "dist"

# PyInstaller配置
PYINSTALLER_CONFIG = {
    # 基本配置
    'name': 'PH&RL_ExamClient',
    'onefile': True,  # 打包成单个exe文件
    'windowed': True,  # Windows下隐藏控制台
    'icon': None,  # 图标文件路径
    
    # 路径配置
    'workpath': str(BUILD_DIR),
    'distpath': str(DIST_DIR),
    'specpath': str(CURRENT_DIR),
    
    # 包含的数据文件
    'datas': [
        # (源路径, 目标路径)
        (str(CURRENT_DIR / "config"), "config"),
        (str(PROJECT_ROOT / "system_conventions.json"), "."),
    ],
    
    # 包含的二进制文件
    'binaries': [],
    
    # 隐藏导入
    'hiddenimports': [
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'requests',
        'sqlite3',
        'json',
        'threading',
        'time',
        'pathlib',
        'psutil',
    ],
    
    # 排除的模块
    'excludes': [
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
    ],
    
    # 运行时钩子
    'runtime_hooks': [],
    
    # 其他选项
    'console': False,  # 不显示控制台
    'debug': False,    # 调试模式
    'strip': False,    # 不剥离符号
    'upx': True,       # 使用UPX压缩
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'bootloader_ignore_signals': False,
}

# 版本信息（Windows）
VERSION_INFO = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({PROJECT_VERSION.replace('.', ', ')}, 0),
    prodvers=({PROJECT_VERSION.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{PROJECT_AUTHOR}'),
            StringStruct(u'FileDescription', u'{PROJECT_DESCRIPTION}'),
            StringStruct(u'FileVersion', u'{PROJECT_VERSION}'),
            StringStruct(u'InternalName', u'{PROJECT_NAME}'),
            StringStruct(u'LegalCopyright', u'Copyright © 2025 {PROJECT_AUTHOR}'),
            StringStruct(u'OriginalFilename', u'PH&RL_ExamClient.exe'),
            StringStruct(u'ProductName', u'{PROJECT_NAME}'),
            StringStruct(u'ProductVersion', u'{PROJECT_VERSION}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

def generate_spec_file():
    """生成PyInstaller spec文件"""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=['{CURRENT_DIR}'],
    binaries={PYINSTALLER_CONFIG['binaries']},
    datas={PYINSTALLER_CONFIG['datas']},
    hiddenimports={PYINSTALLER_CONFIG['hiddenimports']},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks={PYINSTALLER_CONFIG['runtime_hooks']},
    excludes={PYINSTALLER_CONFIG['excludes']},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{PYINSTALLER_CONFIG['name']}',
    debug={str(PYINSTALLER_CONFIG['debug']).lower()},
    bootloader_ignore_signals={str(PYINSTALLER_CONFIG['bootloader_ignore_signals']).lower()},
    strip={str(PYINSTALLER_CONFIG['strip']).lower()},
    upx={str(PYINSTALLER_CONFIG['upx']).lower()},
    upx_exclude={PYINSTALLER_CONFIG['upx_exclude']},
    runtime_tmpdir={PYINSTALLER_CONFIG['runtime_tmpdir']},
    console={str(PYINSTALLER_CONFIG['console']).lower()},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{PYINSTALLER_CONFIG['icon'] or ''}',
)
"""
    
    spec_file = CURRENT_DIR / f"{PYINSTALLER_CONFIG['name']}.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ 已生成spec文件: {spec_file}")
    return spec_file

def build_executable():
    """构建可执行文件"""
    try:
        import PyInstaller.__main__
        
        # 创建构建目录
        BUILD_DIR.mkdir(exist_ok=True)
        DIST_DIR.mkdir(exist_ok=True)
        
        # 生成spec文件
        spec_file = generate_spec_file()
        
        # 构建参数
        build_args = [
            str(spec_file),
            '--clean',  # 清理临时文件
            '--noconfirm',  # 不确认覆盖
        ]
        
        print("🔨 开始构建可执行文件...")
        print(f"📁 构建目录: {BUILD_DIR}")
        print(f"📦 输出目录: {DIST_DIR}")
        
        # 执行构建
        PyInstaller.__main__.run(build_args)
        
        # 检查构建结果
        exe_file = DIST_DIR / f"{PYINSTALLER_CONFIG['name']}.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 构建成功!")
            print(f"📄 可执行文件: {exe_file}")
            print(f"📏 文件大小: {file_size:.2f} MB")
            return True
        else:
            print("❌ 构建失败: 未找到可执行文件")
            return False
            
    except ImportError:
        print("❌ PyInstaller未安装，请运行: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        return False

def clean_build():
    """清理构建文件"""
    import shutil
    
    try:
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
            print(f"🧹 已清理构建目录: {BUILD_DIR}")
        
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
            print(f"🧹 已清理输出目录: {DIST_DIR}")
        
        # 清理spec文件
        spec_file = CURRENT_DIR / f"{PYINSTALLER_CONFIG['name']}.spec"
        if spec_file.exists():
            spec_file.unlink()
            print(f"🧹 已清理spec文件: {spec_file}")
        
        print("✅ 清理完成")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    required_packages = [
        'requests',
        'psutil',
        'pyinstaller'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 请安装缺失的包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖已满足")
    return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PH&RL客户端构建工具")
    parser.add_argument('action', choices=['build', 'clean', 'check'], 
                       help='执行的操作')
    
    args = parser.parse_args()
    
    if args.action == 'check':
        check_dependencies()
    elif args.action == 'clean':
        clean_build()
    elif args.action == 'build':
        if check_dependencies():
            build_executable()
        else:
            print("❌ 依赖检查失败，无法构建")

if __name__ == "__main__":
    main()
