#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建GitHub上传包

由于网络问题无法直接推送，创建一个可以手动上传的压缩包
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime


def should_exclude(file_path, exclude_patterns):
    """检查文件是否应该被排除"""
    file_str = str(file_path).replace('\\', '/')
    
    for pattern in exclude_patterns:
        if pattern in file_str:
            return True
    
    return False


def create_upload_package():
    """创建上传包"""
    print("📦 创建GitHub上传包...")
    
    # 排除的文件和目录
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
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
        'temp/',
        'tmp/',
        'logs/',
        'cache/',
        '.env',
        'config.ini',
        'secrets.json'
    ]
    
    # 创建压缩包
    zip_filename = f"PHRL_System_Upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = 0
        excluded_files = 0
        
        for root, dirs, files in os.walk('.'):
            # 排除目录
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d, exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                
                # 跳过压缩包本身
                if file == zip_filename:
                    continue
                
                if should_exclude(file_path, exclude_patterns):
                    excluded_files += 1
                    continue
                
                # 添加到压缩包
                arcname = str(file_path).replace('\\', '/')
                if arcname.startswith('./'):
                    arcname = arcname[2:]
                
                try:
                    zipf.write(file_path, arcname)
                    total_files += 1
                    
                    if total_files % 50 == 0:
                        print(f"  已处理 {total_files} 个文件...")
                        
                except Exception as e:
                    print(f"  警告: 无法添加文件 {file_path}: {e}")
    
    # 获取压缩包大小
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    
    print(f"\n✅ 上传包创建完成!")
    print(f"📁 文件名: {zip_filename}")
    print(f"📊 包含文件: {total_files} 个")
    print(f"🚫 排除文件: {excluded_files} 个")
    print(f"💾 文件大小: {zip_size:.2f} MB")
    
    return zip_filename


def create_upload_instructions(zip_filename):
    """创建上传说明"""
    instructions = f"""# PH&RL 在线考试系统 - 手动上传指南

## 📦 上传包信息
- **文件名**: `{zip_filename}`
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **包含内容**: 完整的PH&RL在线考试系统代码

## 🚀 推荐上传方法

### 方法1: GitHub Web界面上传 (推荐)

1. **访问GitHub仓库**
   ```
   https://github.com/shanshuishenzhen/01-PHRL_system
   ```

2. **上传压缩包**
   - 点击 "Add file" → "Upload files"
   - 拖拽 `{zip_filename}` 到上传区域
   - 等待上传完成

3. **提交更改**
   - 填写提交信息: "Initial upload - PH&RL 在线考试系统"
   - 点击 "Commit changes"

4. **解压文件** (如果需要)
   - GitHub会自动识别zip文件
   - 或者本地解压后重新上传文件夹

### 方法2: GitHub Desktop

1. **下载GitHub Desktop**
   ```
   https://desktop.github.com/
   ```

2. **克隆仓库**
   - File → Clone repository
   - URL: `https://github.com/shanshuishenzhen/01-PHRL_system`

3. **复制文件**
   - 解压 `{zip_filename}`
   - 将所有文件复制到克隆的仓库目录

4. **提交推送**
   - 在GitHub Desktop中查看更改
   - 填写提交信息并提交
   - 点击 "Push origin"

### 方法3: Git命令行 (网络条件好时)

```bash
# 解压文件
unzip {zip_filename}

# 添加文件
git add .

# 提交
git commit -m "Initial upload - PH&RL 在线考试系统"

# 推送
git push -u origin main
```

## 📋 验证清单

上传完成后，请验证以下内容：

- [ ] README_GitHub.md 文件正确显示
- [ ] 主要目录结构完整:
  - [ ] `question_bank_web/` - 题库管理
  - [ ] `user_management/` - 用户管理  
  - [ ] `exam_management/` - 考试管理
  - [ ] `grading_center/` - 阅卷中心
  - [ ] `score_statistics/` - 成绩统计
  - [ ] `client/` - 客户端
  - [ ] `common/` - 公共模块
  - [ ] `tests/` - 测试框架
  - [ ] `api_gateway/` - API网关
- [ ] 配置文件存在:
  - [ ] `.gitignore`
  - [ ] `requirements.txt`
  - [ ] `docker-compose.yml`
  - [ ] `manage.py`
- [ ] 文档文件完整:
  - [ ] `README.md`
  - [ ] `SYSTEM_ENHANCEMENT_REPORT.md`
  - [ ] 各模块的README文件

## 🔧 故障排除

### 上传失败
- 检查文件大小限制 (GitHub单文件限制100MB)
- 尝试分批上传
- 使用Git LFS处理大文件

### 网络问题
- 使用VPN或代理
- 检查防火墙设置
- 尝试不同的网络环境

### 权限问题
- 确认GitHub账户有仓库写入权限
- 检查Personal Access Token权限

## 📞 技术支持

如有问题，请：
1. 检查GitHub仓库: https://github.com/shanshuishenzhen/01-PHRL_system
2. 查看项目文档: README_GitHub.md
3. 参考系统增强报告: SYSTEM_ENHANCEMENT_REPORT.md

---

**PH&RL 在线考试系统** - 让考试管理更简单、更高效！ 🎓✨
"""
    
    with open("UPLOAD_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print(f"📝 已创建上传说明: UPLOAD_INSTRUCTIONS.md")


def main():
    """主函数"""
    print("🔄 创建GitHub上传包")
    print("=" * 50)
    
    try:
        # 创建上传包
        zip_filename = create_upload_package()
        
        # 创建说明文档
        create_upload_instructions(zip_filename)
        
        print(f"\n🎉 准备完成!")
        print(f"📦 上传包: {zip_filename}")
        print(f"📖 说明文档: UPLOAD_INSTRUCTIONS.md")
        print(f"\n请按照说明文档进行手动上传。")
        
    except Exception as e:
        print(f"❌ 创建上传包失败: {e}")


if __name__ == "__main__":
    main()
