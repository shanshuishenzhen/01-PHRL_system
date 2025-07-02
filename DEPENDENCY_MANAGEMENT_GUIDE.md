# 📦 PH&RL在线考试系统 - 依赖管理指南

## 🎯 目标
- 统一管理所有模块的依赖环境
- 减少重复依赖和环境冲突
- 简化项目维护和团队协作
- 优化项目结构，减少臃肿

## 📝 具体方案

### 1. 统一依赖管理
- 在项目根目录下维护一个总的`requirements.txt`
- 所有模块共用一个虚拟环境（根目录的`.venv`）
- 删除各子模块独立的虚拟环境和依赖文件

### 2. 操作步骤

#### 2.1 创建统一虚拟环境
```bash
# 在项目根目录下执行
python -m venv .venv

# Windows激活虚拟环境
.venv\Scripts\activate

# Linux/Mac激活虚拟环境
source .venv/bin/activate
```

#### 2.2 合并所有模块依赖
1. 收集各模块的`requirements.txt`内容
2. 去重合并为根目录的`requirements.txt`
3. 统一安装所有依赖：
```bash
pip install -r requirements.txt
```

### 3. 目录结构优化
```
project_root/
│
├── .venv/                # 统一虚拟环境
├── requirements.txt      # 所有依赖合集
├── main_console.py      # 主控制台
├── common/              # 公共代码
│   ├── utils.py        # 工具函数
│   └── config.py       # 配置文件
├── user_management/    # 用户管理模块
├── question_bank/      # 题库管理模块
├── grading_center/     # 阅卷中心模块
└── ...
```

## 🔧 维护建议

### 1. 依赖管理
- 新增依赖时直接在根目录安装并更新`requirements.txt`：
```bash
pip install new_package
pip freeze > requirements.txt
```
- 定期检查并清理未使用的依赖

### 2. 代码优化
- 将多个模块共用的代码抽取到`common`目录
- 统一配置管理，避免重复配置
- 保持代码结构清晰，避免循环依赖

### 3. 文档维护
- 在README中清晰说明环境配置步骤
- 记录重要依赖的版本要求和用途
- 及时更新依赖变更说明

## ⚠️ 注意事项
1. 确保所有团队成员使用统一的虚拟环境
2. 依赖有重大更新时及时通知团队成员
3. 定期检查依赖的安全更新

## 🔍 特殊依赖问题及解决方案

### numpy导入问题

#### 问题描述
在模块化开发过程中，特别是在使用pandas等依赖numpy的库时，可能会遇到以下错误：

```
ImportError: Error importing numpy: you should not try to import numpy from its source directory; please exit the numpy source tree, and relaunch your python interpreter from there.
```

#### 问题原因
- 当前工作目录或Python路径中存在与`numpy`包同名的目录或文件
- Python解释器尝试从当前目录导入`numpy`而不是从已安装的包中导入
- 虚拟环境配置问题导致Python无法正确识别已安装的`numpy`包
- 模块化项目结构可能导致Python解释器错误地解析导入路径

#### 解决方案

**例外情况**：对于题库管理等特定模块，可能需要创建独立的虚拟环境以解决依赖冲突：

```bash
# 在模块目录下创建虚拟环境
cd question_bank_web
python -m venv venv_qb

# 激活虚拟环境
.\venv_qb\Scripts\activate  # Windows
source venv_qb/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

**运行时注意事项**：
- 确保在正确的目录中运行应用
- 验证当前激活的是正确的虚拟环境
- 避免在项目中创建与依赖包同名的目录或文件

**对Windows可执行文件打包的影响**：
- 使用PyInstaller打包时，需要在正确的虚拟环境中进行
- 打包脚本需要明确指定依赖路径，避免使用相对导入
- 可能需要在spec文件中添加特定的排除项，以避免打包过程中的路径冲突

## 🚀 后续优化建议
1. 考虑使用`poetry`或`pipenv`等现代依赖管理工具
2. 建立自动化测试确保依赖更新不破坏功能
3. 实现依赖自动更新检查机制
4. 建立依赖变更的评审机制

## 📞 遇到问题？
如遇依赖相关问题，请：
1. 检查虚拟环境是否正确激活
2. 确认`requirements.txt`是否最新
3. 尝试重新安装依赖
4. 联系技术支持团队

---
最后更新：2024-03-14