# 题库管理模块 (Question Bank Management)

## 📝 模块概述

题库管理模块是 PH&RL 在线考试系统的核心组件之一，负责试题和试卷的全生命周期管理。本模块采用Web界面实现，基于Python Flask框架开发，提供直观的用户界面和强大的后台管理功能，支持多种题型管理、智能组卷和试卷导出等核心功能。

## 🎯 主要功能

### 题库管理
- **试题管理**：增删改查试题，支持多种题型（单选、多选、判断、填空、简答、编程等）
- **批量操作**：支持Excel批量导入导出试题
- **分类管理**：按学科、章节、难度等多维度分类管理
- **高级搜索**：支持关键词、题型、难度等条件组合搜索
- **试题预览**：支持预览试题的实际显示效果
- **版本控制**：记录试题修改历史，支持版本回溯

### 组卷功能
- **手动组卷**：手动选择试题组成试卷
- **智能组卷**：根据试卷结构、难度分布、知识点覆盖等条件自动组卷
- **试卷模板**：支持创建和使用试卷模板
- **试卷预览**：支持预览试卷的实际显示效果
- **试卷导出**：支持导出试卷为Word、PDF等格式
- **试卷分析**：分析试卷的难度、知识点覆盖等指标
- **分数设置**：设置试卷总分和及格分数/及格百分比

### 数据分析
- **使用统计**：统计试题使用频率、正确率等数据
- **难度分析**：分析试题实际难度与设定难度的偏差
- **知识点覆盖**：分析知识点覆盖情况
- **试卷质量**：评估试卷的区分度、信度、效度等指标

## 📊 数据规范

### 试题结构
```json
{
  "id": 1,
  "type": "single_choice",
  "stem": "以下哪个选项是Python的基本数据类型？",
  "options": [
    {"key": "A", "content": "Integer"},
    {"key": "B", "content": "Float"},
    {"key": "C", "content": "Dictionary"},
    {"key": "D", "content": "以上都是"}
  ],
  "answer": "D",
  "analysis": "Python的基本数据类型包括整数(Integer)、浮点数(Float)、字典(Dictionary)等。",
  "difficulty": 2,
  "score": 5,
  "category": "Python基础",
  "tags": ["数据类型", "基础概念"],
  "created_at": "2024-01-01 10:00:00",
  "updated_at": "2024-01-02 11:00:00",
  "created_by": "admin"
}
```

### 题型支持
- **单选题**：一个问题，多个选项，只有一个正确答案
- **多选题**：一个问题，多个选项，有多个正确答案
- **判断题**：一个陈述，判断对错
- **填空题**：句子中留空，填入正确答案
- **简答题**：开放性问题，需要文字回答
- **编程题**：编写代码解决问题，支持多种编程语言

### 媒体支持
- **文本**：支持富文本编辑，包括字体、颜色、大小等样式
- **图片**：支持JPG、PNG等格式图片
- **公式**：支持LaTeX数学公式
- **代码**：支持代码高亮显示
- **音频**：支持MP3等音频文件（用于听力题）

### 元数据
- **基本信息**：创建时间、修改时间、创建者等
- **使用统计**：使用次数、正确率、区分度等
- **关联信息**：关联的知识点、章节、课程等

## 🔧 技术架构

### 前端技术
- **基础框架**：HTML5 + CSS3 + JavaScript
- **UI框架**：Bootstrap 5
- **交互增强**：jQuery + AJAX
- **富文本编辑**：CKEditor
- **数学公式**：MathJax
- **图表展示**：ECharts

### 后端技术
- **Web框架**：Python Flask
- **ORM框架**：SQLAlchemy
- **模板引擎**：Jinja2
- **文件处理**：Werkzeug
- **Excel处理**：openpyxl
- **PDF生成**：ReportLab

### 数据存储
- **关系型数据库**：MySQL 8.0
- **文件存储**：本地文件系统（图片、附件等）
- **缓存系统**：Redis（可选）

### 系统架构
- **MVC模式**：模型-视图-控制器分离
- **RESTful API**：提供标准化的API接口
- **模块化设计**：功能模块化，便于扩展
- **权限控制**：基于角色的访问控制

## 🏗️ 文件结构

```
question_bank_web/
├── app.py                 # 应用入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── models/                # 数据模型
│   ├── __init__.py
│   ├── question.py        # 试题模型
│   ├── paper.py           # 试卷模型
│   └── category.py        # 分类模型
├── controllers/           # 控制器
│   ├── __init__.py
│   ├── question_controller.py
│   ├── paper_controller.py
│   └── category_controller.py
├── services/              # 业务逻辑
│   ├── __init__.py
│   ├── question_service.py
│   ├── paper_service.py
│   └── auto_paper_service.py
├── static/                # 静态资源
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/           # 上传文件
├── templates/             # 模板文件
│   ├── base.html
│   ├── questions/
│   ├── papers/
│   └── categories/
├── utils/                 # 工具类
│   ├── __init__.py
│   ├── excel_handler.py   # Excel处理
│   ├── validators.py      # 数据验证
│   ├── file_handler.py    # 文件处理
│   └── pdf_generator.py   # PDF生成
└── tests/                 # 单元测试
    ├── __init__.py
    ├── test_models.py
    └── test_services.py
```

## 🚀 快速开始

### 环境要求
- **Python**：3.8+
- **数据库**：MySQL 8.0+
- **依赖库**：Flask, SQLAlchemy, openpyxl, ReportLab等

### 安装依赖

```bash
# 创建专用虚拟环境（推荐）
python -m venv venv_qb

# 激活虚拟环境
.\venv_qb\Scripts\activate  # Windows
source venv_qb/bin/activate   # Linux/Mac

# 安装依赖包
pip install -r requirements.txt
```

### 依赖冲突解决方案

#### numpy导入问题

在运行题库管理模块时，可能会遇到以下错误：

```
ImportError: Error importing numpy: you should not try to import numpy from its source directory; please exit the numpy source tree, and relaunch your python interpreter from there.
```

**问题原因**：
- 当前工作目录或Python路径中存在与`numpy`包同名的目录或文件
- 在模块化开发环境中，项目结构可能导致Python解释器错误地尝试从当前目录导入`numpy`
- 全局虚拟环境中的`numpy`包可能与模块的导入机制产生冲突

**解决方案**：
1. 使用专用虚拟环境：为题库管理模块创建独立的虚拟环境，避免与全局环境冲突
2. 在正确的目录中运行：确保在题库管理模块目录下运行应用
3. 确保激活正确的虚拟环境：运行前验证当前激活的是题库管理模块的专用虚拟环境

**对Windows可执行文件打包的影响**：
- 使用PyInstaller打包时，需要在专用虚拟环境中进行
- 打包配置中需要特别处理`numpy`相关的依赖路径
- 可能需要在`.spec`文件中添加特定的排除项，以避免路径冲突

### 配置数据库

1. 创建MySQL数据库
```sql
CREATE DATABASE question_bank CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改`config.py`中的数据库连接信息
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/question_bank'
```

### 启动方式

#### 方式一：通过主控台启动

在主控台界面中点击"题库管理"模块的"启动"按钮。

#### 方式二：直接启动

```bash
# 进入题库管理目录
cd question_bank_web

# 初始化数据库
python -c "from app import db; db.create_all()"

# 启动Flask应用
python app.py
```

### 访问系统

启动成功后，在浏览器中访问：http://localhost:5000

## 🔄 使用流程

### 1. 试题管理
1. 登录题库管理系统
2. 进入"试题管理"页面
3. 添加、编辑或删除试题
4. 使用批量导入功能批量添加试题

### 2. 组卷管理
1. 进入"组卷管理"页面
2. 选择手动组卷或智能组卷
3. 设置试卷结构和参数
4. 设置试卷总分和及格分数/及格百分比
5. 生成试卷并预览
6. 导出或保存试卷

## 🔄 与其他模块的集成

### 数据交互
- **考试管理模块**：提供试卷数据，接收考试结果数据
- **用户管理模块**：获取用户权限信息，控制访问权限
- **阅卷中心**：提供试题答案和评分标准
- **成绩统计**：接收试题和试卷的统计数据

### API接口
- **试题查询**：`GET /api/questions`
- **试题详情**：`GET /api/questions/{id}`
- **试卷查询**：`GET /api/papers`
- **试卷详情**：`GET /api/papers/{id}`
- **智能组卷**：`POST /api/papers/auto-generate`

## 🐛 问题排查

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 确认数据库连接信息是否正确
   - 验证数据库用户权限

2. **图片上传失败**
   - 检查上传目录权限
   - 确认文件大小是否超限
   - 验证文件格式是否支持

3. **Excel导入失败**
   - 检查Excel文件格式
   - 确认数据格式是否符合要求
   - 查看详细错误日志

### 调试方法

1. **查看日志**：检查应用日志文件
2. **开启调试模式**：设置`app.debug = True`
3. **数据库检查**：直接查询数据库验证数据
4. **API测试**：使用Postman等工具测试API接口

## 🔄 版本历史

### v1.0.0 (2024-01-10)
- ✅ 基础试题管理功能
- ✅ 手动组卷功能
- ✅ Excel导入导出
- ✅ 试卷预览和导出

### v1.1.0 (计划中)
- 🔄 智能组卷算法优化
- 🔄 数据分析功能增强
- 🔄 UI/UX改进
- 🔄 API完善

## 📞 技术支持

如有使用问题或建议，请联系：
- 邮箱：support@phrl-exam.com
- 电话：400-123-4567
- 工作时间：周一至周五 9:00-18:00

---

**题库管理模块** - 让试题管理和组卷更智能、更高效！
