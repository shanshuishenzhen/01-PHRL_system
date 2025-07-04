# 题库生成与试卷组题验证系统

## 概述

本系统提供了两套完整的验证程序，用于确保题库生成和试卷组题的质量：

1. **题库生成验证程序** - 验证开发工具生成的题库是否符合蓝图规则
2. **试卷组题验证程序** - 分析试卷的三级代码比例分布

## 1. 题库生成验证程序

### 功能特点

- ✅ **完全一致性验证**：确保生成的题库与给定规则表完全一致
- ✅ **多维度统计**：按题型、知识点、三级代码等维度进行统计对比
- ✅ **详细报告**：生成Excel格式的详细验证报告
- ✅ **自动集成**：在题库生成完成后自动运行验证

### 使用方法

#### 方法1：自动验证（推荐）
```bash
# 在开发工具目录运行题库生成器，会自动触发验证
cd developer_tools
python question_bank_generator.py
```

#### 方法2：手动验证
```bash
# 单独运行验证程序
cd developer_tools
python question_bank_validator.py blueprint.json generated_questions.json [output_dir]
```

#### 方法3：Python代码调用
```python
from question_bank_validator import QuestionBankValidator

validator = QuestionBankValidator()
result = validator.validate_generated_bank(
    blueprint_path="question_bank_blueprint.json",
    generated_questions_path="generated_questions.json",
    output_dir="validation_reports"
)

print(f"验证结果: {'通过' if result['is_valid'] else '失败'}")
print(f"准确率: {result['accuracy_rate']:.2%}")
```

### 验证报告内容

生成的Excel报告包含以下工作表：

1. **验证摘要** - 总体验证结果和准确率
2. **题型分布对比** - 各题型的期望数量vs实际数量
3. **知识点分布对比** - 各知识点的题目分布对比
4. **问题列表** - 详细的错误和警告信息

### 验证标准

- **总题目数量**：必须与蓝图计算的期望数量完全一致
- **题型分布**：每种题型的数量必须精确匹配
- **知识点分布**：每个三级知识点的题目数量必须符合规则
- **ID格式**：题目ID必须符合标准格式（B-A-B-C-001-002）

## 2. 试卷组题验证程序

### 功能特点

- 📊 **三级代码分析**：详细分析试卷中各三级代码的比例分布
- 📋 **模板对比**：支持与组题模板进行对比分析
- 📈 **批量验证**：支持同时验证多套试卷
- 📄 **Excel报告**：生成详细的对比分析报告

### 使用方法

#### 方法1：Web界面（推荐）
1. 访问题库管理系统：http://localhost:5000
2. 进入试卷详情页面，点击"验证试卷"按钮
3. 或访问"批量验证"页面，选择多套试卷进行验证

#### 方法2：命令行
```bash
cd question_bank_web
python -c "from paper_validator import validate_paper_from_command_line; validate_paper_from_command_line(paper_id=1, template_path='template.xlsx')"
```

#### 方法3：Python代码调用
```python
from paper_validator import PaperValidator

validator = PaperValidator()

# 单套试卷验证
result = validator.validate_paper_composition(
    paper_id=1,
    template_path="template.xlsx",  # 可选
    output_dir="paper_validation_reports"
)

# 批量验证
result = validator.validate_multiple_papers(
    paper_ids=[1, 2, 3],
    template_path="template.xlsx",  # 可选
    output_dir="paper_validation_reports"
)
```

### 验证报告内容

#### 单套试卷报告包含：

1. **试卷信息** - 基本信息（ID、名称、总题数、总分、时长）
2. **三级代码分布** - 各三级代码的题目数量和占比
3. **题型分布** - 各题型的题目数量和占比
4. **交叉分析** - 三级代码与题型的交叉统计
5. **详细题目列表** - 每道题的详细信息

#### 批量验证报告包含：

1. **批量对比摘要** - 所有试卷的基本统计
2. **三级代码分布对比** - 各试卷的三级代码分布对比
3. **题型分布对比** - 各试卷的题型分布对比

### 模板对比功能

如果提供了组题模板文件，系统会：

- 对比实际分布与模板要求的差异
- 计算偏差百分比
- 标识不符合要求的项目
- 生成改进建议

## 3. 文件结构

```
01-PHRH_system/
├── developer_tools/
│   ├── question_bank_generator.py      # 题库生成器（已集成验证）
│   ├── question_bank_validator.py      # 题库验证程序
│   ├── question_bank_blueprint.json    # 题库蓝图文件
│   └── validation_reports/             # 验证报告目录
├── question_bank_web/
│   ├── app.py                          # Web应用（已集成验证路由）
│   ├── paper_validator.py              # 试卷验证程序
│   └── paper_validation_reports/       # 试卷验证报告目录
└── VALIDATION_SYSTEM_README.md         # 本说明文件
```

## 4. 配置说明

### 题库验证配置

在 `question_bank_blueprint.json` 中配置：

```json
{
  "config": {
    "parallel_knowledge_points": 5,  // 每个三级知识点的并行点数量
    "question_types": ["B", "G", "C", "D", "E"],  // 支持的题型
    "total_questions_target": 20000  // 目标题目总数
  }
}
```

### 试卷验证配置

在组题模板Excel文件中配置：

- **题型分布** 工作表：定义各题型的数量要求
- **知识点分布** 工作表：定义各三级代码的比例要求

## 5. 常见问题

### Q1: 验证失败怎么办？
A: 查看生成的验证报告，根据错误信息调整题库生成规则或组题模板。

### Q2: 如何提高验证准确率？
A: 确保蓝图文件和模板文件的配置正确，检查题目ID格式是否标准。

### Q3: 验证报告保存在哪里？
A: 
- 题库验证报告：`developer_tools/validation_reports/`
- 试卷验证报告：`question_bank_web/paper_validation_reports/`

### Q4: 支持哪些文件格式？
A: 
- 题库文件：JSON、Excel (.xlsx)
- 模板文件：Excel (.xlsx)
- 报告文件：Excel (.xlsx)

## 6. 技术支持

如遇到问题，请检查：

1. 文件路径是否正确
2. 文件格式是否支持
3. 数据库连接是否正常
4. 依赖包是否安装完整

---

**更新时间**: 2025-07-05  
**版本**: v1.0.0  
**状态**: ✅ 已部署
