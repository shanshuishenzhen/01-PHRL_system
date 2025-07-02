#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建分批上传包

将项目分成多个小于100MB的压缩包，便于GitHub上传
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime


def get_dir_size(path):
    """获取目录大小"""
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total += os.path.getsize(file_path)
    return total


def create_split_packages():
    """创建分批上传包"""
    print("📦 创建分批上传包...")
    
    # 定义模块分组
    module_groups = [
        {
            "name": "core_system",
            "description": "核心系统文件",
            "paths": [
                "README.md",
                "README_GitHub.md", 
                "requirements.txt",
                "config.json",
                "start_system.py",
                "main_console.py",
                "launcher.py",
                "manage.py",
                ".gitignore",
                ".env.example",
                "docker-compose.yml",
                "Dockerfile",
                "pytest.ini",
                "SYSTEM_ENHANCEMENT_REPORT.md",
                "UPLOAD_INSTRUCTIONS.md",
                "GITHUB_UPLOAD_LOG.md"
            ]
        },
        {
            "name": "common_modules",
            "description": "公共模块",
            "paths": ["common/"]
        },
        {
            "name": "question_bank",
            "description": "题库管理模块",
            "paths": ["question_bank_web/"]
        },
        {
            "name": "user_management",
            "description": "用户管理模块", 
            "paths": ["user_management/"]
        },
        {
            "name": "exam_management",
            "description": "考试管理模块",
            "paths": ["exam_management/"]
        },
        {
            "name": "grading_center",
            "description": "阅卷中心模块",
            "paths": ["grading_center/"]
        },
        {
            "name": "client_and_stats",
            "description": "客户端和统计模块",
            "paths": [
                "client/",
                "score_statistics/",
                "api_gateway/"
            ]
        },
        {
            "name": "tests_and_docs",
            "description": "测试框架和文档",
            "paths": [
                "tests/",
                "docs/",
                "developer_tools/",
                "translations/"
            ]
        },
        {
            "name": "legacy_and_others",
            "description": "遗留系统和其他文件",
            "paths": [
                "legacy_system/",
                "main_console/",
                "data/",
                "*.py",
                "*.md",
                "*.txt",
                "*.json",
                "*.bat",
                "*.sh",
                "*.spec"
            ]
        }
    ]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    created_packages = []
    
    for i, group in enumerate(module_groups, 1):
        package_name = f"PHRL_System_Part{i:02d}_{group['name']}_{timestamp}.zip"
        
        print(f"\n📁 创建包 {i}/{len(module_groups)}: {group['name']}")
        print(f"   描述: {group['description']}")
        
        with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            
            for path_pattern in group['paths']:
                if path_pattern.endswith('/'):
                    # 目录
                    dir_path = Path(path_pattern.rstrip('/'))
                    if dir_path.exists():
                        for root, dirs, files in os.walk(dir_path):
                            # 排除不需要的目录
                            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
                            
                            for file in files:
                                file_path = Path(root) / file
                                if should_include_file(file_path):
                                    arcname = str(file_path).replace('\\', '/')
                                    try:
                                        zipf.write(file_path, arcname)
                                        file_count += 1
                                    except Exception as e:
                                        print(f"     警告: 无法添加 {file_path}: {e}")
                else:
                    # 单个文件或通配符
                    if '*' in path_pattern:
                        # 通配符匹配
                        import glob
                        for file_path in glob.glob(path_pattern):
                            if os.path.isfile(file_path) and should_include_file(Path(file_path)):
                                try:
                                    zipf.write(file_path, file_path)
                                    file_count += 1
                                except Exception as e:
                                    print(f"     警告: 无法添加 {file_path}: {e}")
                    else:
                        # 单个文件
                        file_path = Path(path_pattern)
                        if file_path.exists() and should_include_file(file_path):
                            try:
                                zipf.write(file_path, str(file_path))
                                file_count += 1
                            except Exception as e:
                                print(f"     警告: 无法添加 {file_path}: {e}")
        
        # 检查包大小
        package_size = os.path.getsize(package_name) / (1024 * 1024)  # MB
        print(f"   ✅ 包含文件: {file_count} 个")
        print(f"   💾 文件大小: {package_size:.2f} MB")
        
        if package_size > 95:  # 留5MB余量
            print(f"   ⚠️  警告: 文件大小接近GitHub限制")
        
        created_packages.append({
            "filename": package_name,
            "description": group['description'],
            "file_count": file_count,
            "size_mb": package_size
        })
    
    return created_packages


def should_include_file(file_path):
    """检查文件是否应该包含"""
    file_str = str(file_path).lower()
    
    # 排除的文件类型和路径
    exclude_patterns = [
        '.git/',
        '__pycache__/',
        '.venv/',
        'venv/',
        'env/',
        'node_modules/',
        '.pytest_cache/',
        'htmlcov/',
        '.coverage',
        'temp/',
        'tmp/',
        'logs/',
        'cache/',
        '.pyc',
        '.pyo',
        '.pyd',
        '.ds_store',
        'thumbs.db'
    ]
    
    for pattern in exclude_patterns:
        if pattern in file_str:
            return False
    
    return True


def create_upload_guide(packages):
    """创建上传指南"""
    guide = f"""# PH&RL 在线考试系统 - 分批上传指南

## 📦 上传包列表

由于项目较大，已分成 {len(packages)} 个包，每个包都小于100MB：

"""
    
    total_size = 0
    total_files = 0
    
    for i, package in enumerate(packages, 1):
        guide += f"""### 包 {i}: {package['filename']}
- **描述**: {package['description']}
- **文件数**: {package['file_count']} 个
- **大小**: {package['size_mb']:.2f} MB

"""
        total_size += package['size_mb']
        total_files += package['file_count']
    
    guide += f"""
## 📊 总计
- **总包数**: {len(packages)} 个
- **总文件数**: {total_files} 个  
- **总大小**: {total_size:.2f} MB

## 🚀 上传步骤

### 方法1: GitHub Web界面 (推荐)

1. **访问仓库**: https://github.com/shanshuishenzhen/01-PHRL_system

2. **按顺序上传每个包**:
   ```
   建议上传顺序:
   1. 先上传 core_system (核心系统文件)
   2. 再上传 common_modules (公共模块)
   3. 然后上传各功能模块
   4. 最后上传测试和文档
   ```

3. **每个包的上传步骤**:
   - 点击 "Add file" → "Upload files"
   - 拖拽包文件到上传区域
   - 填写提交信息: "Upload [包名] - [描述]"
   - 点击 "Commit changes"
   - 等待上传完成后再上传下一个包

4. **解压和整理** (可选):
   - 所有包上传完成后
   - 可以在GitHub中解压zip文件
   - 或者本地解压后重新整理文件结构

### 方法2: Git命令行分批推送

```bash
# 解压第一个包
unzip {packages[0]['filename']}

# 添加并提交
git add .
git commit -m "Upload core system files"
git push origin main

# 重复上述步骤处理其他包
```

### 方法3: GitHub Desktop

1. 克隆仓库到本地
2. 逐个解压包到仓库目录
3. 在GitHub Desktop中分批提交推送

## ⚠️ 注意事项

1. **上传顺序**: 建议按编号顺序上传，确保依赖关系正确
2. **网络稳定**: 确保网络连接稳定，避免上传中断
3. **文件检查**: 每个包上传后检查文件是否完整
4. **避免重复**: 不要重复上传相同的文件

## 🔍 验证清单

所有包上传完成后，验证以下内容：

- [ ] README_GitHub.md 正确显示
- [ ] 所有主要目录存在
- [ ] 配置文件完整
- [ ] 没有重复文件
- [ ] 项目可以正常运行

## 📞 技术支持

如遇问题：
1. 检查包文件完整性
2. 确认网络连接稳定  
3. 参考GitHub帮助文档
4. 联系技术支持

---

**PH&RL 在线考试系统** - 分批上传，确保完整！ 🎓✨
"""
    
    with open("SPLIT_UPLOAD_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print(f"📖 已创建分批上传指南: SPLIT_UPLOAD_GUIDE.md")


def main():
    """主函数"""
    print("🔄 创建分批上传包")
    print("=" * 50)
    
    try:
        # 创建分批包
        packages = create_split_packages()
        
        # 创建上传指南
        create_upload_guide(packages)
        
        print(f"\n🎉 分批包创建完成!")
        print(f"📦 共创建 {len(packages)} 个包")
        print(f"📖 上传指南: SPLIT_UPLOAD_GUIDE.md")
        print(f"\n请按照指南进行分批上传。")
        
    except Exception as e:
        print(f"❌ 创建分批包失败: {e}")


if __name__ == "__main__":
    main()
