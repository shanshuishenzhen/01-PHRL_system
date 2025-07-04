# Trae 在线考试系统

## 项目概述

Trae 在线考试系统是一个基于 Python 的模块化考试管理平台，采用分模块开发方式，支持题库管理、考试管理、用户管理等功能。

## 项目结构

```
Trae_OLE_03/
├── main_console/          # 主控台模块
│   ├── main.py           # 主控台入口
│   └── README.md         # 主控台说明
├── question_bank/         # 题库管理模块
│   ├── question_bank_manager.py  # 题库管理主入口
│   └── README.md         # 题库管理说明
├── exam_management/       # 考试管理模块
├── user_management/       # 用户管理模块
├── grading_center/        # 阅卷中心模块
├── score_statistics/      # 成绩统计模块
├── client/               # 客户端模块
├── shared/               # 共享组件库
├── docs/                 # 项目文档
└── README.md             # 项目总说明
```

## 当前状态

### ✅ 已完成功能

1. **主控台模块** - 正常运行
   - 基于 Tkinter 的图形界面
   - 模块跳转功能
   - 支持题库管理模块跳转

2. **题库管理模块** - 功能完整
   - 基于 Tkinter 的桌面应用
   - 完整的题库管理功能
   - 支持题目的增删改查
   - 支持题库导入导出

### ⚠️ 待开发模块

1. **考试管理模块** - 开发中
2. **用户管理模块** - 开发中
3. **阅卷中心模块** - 开发中
4. **成绩统计模块** - 开发中
5. **客户端模块** - 开发中

## 使用说明

### 环境要求

- Python 3.6+
- tkinter (通常随Python安装)

### 启动主控台

```bash
python main_console/main.py
```

### 启动题库管理模块

```bash
# 方式1：通过主控台跳转
python main_console/main.py
# 然后点击"题库管理"按钮

# 方式2：直接启动
python question_bank/question_bank_manager.py
```

### 题库管理功能

- **新增题目**：添加新的考试题目
- **编辑题目**：修改现有题目内容
- **删除题目**：删除不需要的题目
- **搜索题目**：根据关键词搜索题目
- **导入题库**：从JSON文件导入题库
- **导出题库**：将题库导出为JSON文件

## 开发说明

### 模块化架构

- **主控台模块**：统一入口，负责模块跳转
- **功能模块**：独立开发，各自维护
- **共享组件**：公共功能和配置

### 技术栈

- **主控台**：Tkinter (GUI)
- **题库管理**：Tkinter (GUI)
- **其他模块**：待开发

### 开发规范

1. **模块独立性**：每个模块可以独立运行
2. **统一接口**：通过主控台统一调用
3. **数据共享**：通过共享组件实现数据交换

## 下一步计划

1. 完善其他功能模块
2. 实现模块间数据共享
3. 优化用户界面和用户体验
4. 添加数据库支持
5. 实现网络通信功能

## 问题排查

### 常见问题

1. **Python环境问题**
   - 确保Python版本为3.6+
   - 检查tkinter是否可用

2. **模块启动失败**
   - 检查文件路径是否正确
   - 确认依赖是否安装

3. **界面显示异常**
   - 检查系统分辨率设置
   - 确认字体支持

## 联系方式

如有问题，请联系开发团队。 