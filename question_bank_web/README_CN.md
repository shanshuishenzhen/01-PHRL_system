# 📚 题库管理系统

一个专业的题库导入和管理平台，支持从Excel文件导入题目到数据库。

## ✨ 功能特性

- 📥 **Excel导入**: 支持.xlsx格式的Excel文件导入
- 📋 **模板下载**: 提供标准题库模板下载，包含示例数据和使用说明
- 🔒 **安全验证**: 文件类型、大小、MIME类型多重验证
- 📊 **数据统计**: 实时显示题目数量和统计信息
- 🎨 **现代化UI**: 响应式设计，支持移动端访问
- 🗄️ **数据库支持**: 支持SQLite和MySQL数据库
- 🧹 **自动清理**: 自动清理超过24小时的上传文件
- 📋 **错误报告**: 详细的导入错误报告和日志

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- 推荐使用虚拟环境

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 创建数据库表

如果首次运行，需要先创建数据库表：

```bash
python create_tables.py
```

### 4. 启动应用

```bash
# 方式1: 使用启动脚本 (推荐)
python run.py

# 方式2: 直接运行
python app.py
```

### 5. 访问系统

打开浏览器访问: http://127.0.0.1:5000

### 6. 使用系统

1. **(可选) 填充演示数据**: 为了快速体验功能，可以先运行演示脚本来填充一些数据。
    ```bash
    python demo.py
    ```
2. **下载模板**: 点击"📋 下载题库模板"按钮获取标准Excel模板
3. **填写数据**: 按照模板格式填写题目数据
4. **导入题库**: 点击"📥 导入Excel题库"按钮上传并导入数据
5. **查看结果**: 在首页查看导入的题目和统计信息，并使用分页功能浏览。

## 📋 Excel文件格式要求

### 必需列名

| 列名 | 说明 | 是否必需 |
|------|------|----------|
| ID | 题目ID (格式: A-B-C-001-001) | ✅ |
| 题型代码 | 题目类型代码 | ✅ |
| 试题（题干） | 题目内容 | ✅ |
| 正确答案 | 正确答案 | ✅ |
| 难度代码 | 难度等级 (1-5) | ✅ |
| 序号 | 序号 | ❌ |
| 认定点代码 | 认定点代码 | ❌ |
| 题号 | 题号 | ❌ |
| 试题（选项A-E） | 选项内容 | ❌ |
| 【图】及位置 | 图片信息 | ❌ |
| 一致性代码 | 一致性代码 (1-5) | ❌ |
| 解析 | 题目解析 | ❌ |

### 支持的题型代码

| 代码 | 题型 |
|------|------|
| B（单选题） | 单选题 |
| G（多选题） | 多选题 |
| C（判断题） | 判断题 |
| T（填空题） | 填空题 |
| D（简答题） | 简答题 |
| U（计算题） | 计算题 |
| W（论述题） | 论述题 |
| E（案例分析题） | 案例分析 |
| F（综合题） | 综合题 |

### 难度代码

| 代码 | 难度 |
|------|------|
| 1（很简单） | 很简单 |
| 2（简单） | 简单 |
| 3（中等） | 中等 |
| 4（困难） | 困难 |
| 5（很难） | 很难 |

### 一致性代码

| 代码 | 一致性 |
|------|--------|
| 1（很低） | 很低 |
| 2（低） | 低 |
| 3（中等） | 中等 |
| 4（高） | 高 |
| 5（很高） | 很高 |

### 题库ID字段与命名规则

- 每个题库可自定义命名，如：保卫管理员（三级）题库、健康管理师（二级）题库等。
- 题库中每道题的ID为主键，在本题库中唯一。
- ID格式：题型代码字母-一级代码-二级代码-三级代码-知识点代码-顺序号
- 具体规则：
    - 题型代码：如B（单选题）、G（多选题）等
    - 一级代码：如A
    - 二级代码：如B
    - 三级代码：如C
    - 知识点代码：如001
    - 顺序号：如001、002（同一认定点下多题时递增）
- 示例：B-A-B-C-001-002
    - B：单选题
    - A：一级代码
    - B：二级代码
    - C：三级代码
    - 001：知识点代码
    - 002：顺序号（如该认定点有6道题，则001~006）

## 🗄️ 数据库配置

### 默认配置 (SQLite)

系统默认使用SQLite数据库，文件为 `local_dev.db`

### MySQL配置

设置环境变量 `DATABASE_URL`:

```bash
# Windows
set DATABASE_URL=mysql+mysqlconnector://username:password@localhost/database_name

# Linux/Mac
export DATABASE_URL=mysql+mysqlconnector://username:password@localhost/database_name
```

## 📁 项目结构

```
Trae_ZUTI_01/
├── app.py                 # 主应用文件
├── models.py              # 数据模型
├── excel_importer.py      # Excel导入模块
├── create_template.py     # 模板生成脚本
├── create_tables.py       # 数据库表创建脚本
├── run.py                 # 启动脚本
├── demo.py                # 演示数据填充脚本
├── test_system.py         # 系统功能测试脚本
├── test_pagination.py     # 分页功能测试脚本
├── test_excel_importer.py # Excel导入模块测试脚本
├── README_CN.md           # 中文说明文档
├── requirements.txt       # 依赖包列表
├── uploads/               # 上传文件目录
├── templates/             # 网页模板目录
│   └── index.html         # 主页模板
├── error_reports/         # 错误报告目录
└── local_dev.db           # SQLite数据库文件
```

## 🔧 调试与测试

本项目包含一系列测试脚本，以确保各项功能正常工作。

### 运行单元测试和集成测试

你可以运行以下脚本来测试系统的不同部分：

-   **系统整体功能测试**:
    ```bash
    python test_system.py
    ```
    该脚本会测试文件上传、模板下载和基本页面渲染。

-   **分页功能测试**:
    ```bash
    python test_pagination.py
    ```
    此脚本需要 `beautifulsoup4` 依赖，专门测试主页的显示和分页逻辑是否正确。

-   **Excel 导入逻辑测试**:
    ```bash
    python test_excel_importer.py
    ```
    该脚本专注于测试 `excel_importer.py` 模块的数据提取和验证逻辑。

### 填充演示数据

`demo.py` 脚本可以快速向数据库中填充大量（默认100条）符合格式的随机测试数据，方便进行功能调试和预览。

```bash
python demo.py
```

## 🔧 故障排除

### 常见问题

1. **文件上传失败**
   - 检查文件格式是否为.xlsx
   - 检查文件大小是否超过10MB
   - 确保uploads目录存在且有写入权限

2. **数据库连接失败**
   - 检查数据库配置
   - 确保数据库服务正在运行
   - 检查网络连接

3. **导入错误**
   - 检查Excel文件格式是否符合要求
   - 查看错误报告文件
   - 确保所有必需列都存在

### 日志查看

错误日志会显示在控制台和 `error_reports/` 目录中。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持

如有问题，请提交Issue或联系开发团队。

## 主要功能

- 题库导入/导出（支持Excel模板）
- 题库管理（增删查）
- 题目管理（分页、题库名称自动显示）
- 组题规则上传与多套试卷自动生成
- 试卷管理（单套/批量导出Word、Excel，批量删除）
- 首页、题库、试卷页面均有显著导航入口
- 支持多题库、多题型、难度、一致性等国家标准字段

## 批量操作说明

- 试卷管理页面支持多选试卷，批量导出为Excel（多Sheet）或Word（合并），也可批量删除。
- 导出文件名、Sheet名自动处理，支持中文。

## 常见报错与修复

- **DetachedInstanceError**：如遇"Parent instance ... is not bound to a Session"，请在SQLAlchemy查询时用`joinedload`预加载外键关系。
- **TypeError: The view function ... did not return a valid response**：请检查路由函数是否始终有return。
- **KeyError: '1级代码'**：请严格使用系统下载的Excel模板，勿手动修改表头。

## Windows下打包为可执行文件（exe）

推荐使用 [PyInstaller](https://pyinstaller.org/)。

### 步骤
1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 进入项目根目录，执行：
   ```bash
   pyinstaller -F -w -i app.ico run.py
   ```
   - `-F` 生成单文件exe
   - `-w` 不弹出命令行窗口（如需调试可去掉）
   - `-i app.ico` 可选，指定图标
   - `run.py` 为你的启动脚本
3. 打包完成后，`dist`目录下会生成`run.exe`。

### 注意事项
- 打包前请确保所有依赖已安装（如pandas、flask、sqlalchemy、openpyxl、python-docx等）。
- 若用到Word导出，需确保`python-docx`已安装。
- 静态文件、模板、uploads等目录如需打包进exe，需用`--add-data`参数指定。
- 打包后首次运行会有解压延迟，属正常现象。

## 其它
如遇其它问题，请反馈报错信息或截图，开发者会持续优化。