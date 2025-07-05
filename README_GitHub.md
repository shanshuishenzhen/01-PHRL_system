# 🎓 PH&RL 专业技能认证考试系统

## 📋 项目概述

PH&RL（Professional & Reliable）考试系统是一个完整的专业技能认证考试解决方案，支持多种题型、防作弊功能和自动阅卷。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   题库管理      │    │   考试管理      │    │   阅卷中心      │
│ Question Bank   │    │ Exam Management │    │ Grading Center  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────┐
         │              客户端 (Standalone Client)      │
         │            • 考试答题界面                    │
         │            • 防作弊功能                      │
         │            • 离线答题支持                    │
         └─────────────────────────────────────────────┘
```

## ✨ 主要功能

### 🎯 核心功能
- **多题型支持**：单选、多选、判断、填空、简答、论述题
- **智能组卷**：自动组卷和手动组卷
- **防作弊系统**：全屏模式、进程监控、焦点检测
- **自动阅卷**：客观题自动评分，主观题辅助评分
- **成绩管理**：成绩统计、分析和导出

### 🛡️ 安全特性
- **多层认证**：用户认证 + 隐藏超级管理员
- **权限控制**：基于角色的访问控制
- **数据加密**：敏感数据加密存储
- **审计日志**：完整的操作日志记录

### 🌐 网络功能
- **局域网部署**：支持C/S架构部署
- **离线支持**：支持离线答题和同步
- **批量管理**：支持批量用户和考试管理

## 🚀 快速开始

### 环境要求
- **操作系统**：Windows 10/11
- **Python**：3.8+
- **数据库**：SQLite/MySQL
- **网络**：局域网环境

### 安装部署

1. **克隆项目**
```bash
git clone https://github.com/shanshuishenzhen/01-PHRL_system.git
cd 01-PHRL_system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
# 启动所有服务
python start_all_services.py

# 或分别启动各个模块
python exam_management/app.py
python question_bank_web/app.py
python standalone_client.py
```

4. **访问系统**
- 题库管理：http://localhost:5001
- 考试管理：http://localhost:5002
- 客户端：直接运行可执行文件

## 📚 文档指南

- **[完整系统指南](COMPLETE_SYSTEM_GUIDE.md)**：系统完整使用指南
- **[客户端通信指南](CLIENT_SERVER_COMMUNICATION_GUIDE.md)**：客户端与服务器通信配置
- **[快速部署指南](QUICK_DEPLOYMENT_GUIDE.md)**：快速部署和配置
- **[约定管理指南](CONVENTIONS_MANAGEMENT_GUIDE.md)**：系统约定和规范管理

## 🔧 配置说明

### 服务器配置
```json
{
    "server": {
        "host": "192.168.1.100",
        "port": 5000,
        "protocol": "http",
        "timeout": 30
    }
}
```

### 客户端配置
```json
{
    "ui": {
        "fullscreen_exam": true,
        "theme_color": "#2196F3"
    },
    "security": {
        "enable_anti_cheat": true
    }
}
```

## 🎯 使用场景

- **教育机构**：学校、培训机构的在线考试
- **企业培训**：员工技能认证和培训考核
- **资格认证**：专业资格认证考试
- **竞赛活动**：各类知识竞赛和技能比赛

## 🛠️ 技术栈

- **后端**：Python Flask, SQLAlchemy
- **前端**：HTML5, CSS3, JavaScript, Tkinter
- **数据库**：SQLite, MySQL
- **网络**：HTTP/HTTPS RESTful API
- **安全**：JWT认证, 数据加密

## 📊 系统特点

- **高可靠性**：稳定的系统架构和容错机制
- **易部署**：支持一键部署和批量配置
- **可扩展**：模块化设计，易于扩展功能
- **用户友好**：直观的用户界面和操作流程

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

如有问题或建议，请通过以下方式联系：
- 提交Issue：[GitHub Issues](https://github.com/shanshuishenzhen/01-PHRL_system/issues)
- 邮件联系：[技术支持邮箱]

---

**🎓 PH&RL考试系统 - 专业、可靠的考试解决方案**

*最后更新：2025-07-06*
