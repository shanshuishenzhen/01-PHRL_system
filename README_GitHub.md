# PH&RL 在线考试系统

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

## 📋 项目简介

PH&RL 在线考试系统是一个基于 Python 的现代化、模块化考试管理平台，采用分布式微服务架构，提供完整的在线考试解决方案。系统界面简洁美观，功能操作简单，支持题库管理、用户管理、考试管理、成绩统计、阅卷中心、客户机端等核心功能。

### ✨ 核心特性

- 🏗️ **模块化架构**：各功能模块独立开发、独立部署，支持水平扩展
- 🔒 **安全可靠**：多层安全防护，支持用户认证、权限管理、数据加密
- 🚀 **高性能**：支持并发考试、实时阅卷、智能评分
- 📊 **智能分析**：提供丰富的数据分析和可视化功能
- 🔧 **易于维护**：完善的日志系统、监控告警、自动化测试
- 🌐 **跨平台**：支持Windows、Linux、macOS多平台部署
- 📱 **响应式设计**：支持PC、平板、手机等多种设备

## 🚀 快速开始

### 环境要求

- **Python**: 3.6 或更高版本
- **操作系统**: Windows 10/11, macOS, Linux
- **内存**: 建议 4GB 以上
- **磁盘空间**: 建议 2GB 以上

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/shanshuishenzhen/01-PHRH_system.git
   cd 01-PHRH_system
   ```

2. **创建虚拟环境**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **初始化系统**
   ```bash
   python manage.py init_db
   ```

5. **启动系统**
   ```bash
   # 方式一：使用启动器（推荐）
   python start_system.py
   
   # 方式二：使用管理工具
   python manage.py start
   ```

### 快速体验

启动系统后，您可以：

1. **访问主控台**: 运行 `python main_console.py`
2. **访问题库管理**: 浏览器打开 `http://localhost:5000`
3. **访问考试管理**: 浏览器打开 `http://localhost:5001`
4. **访问阅卷中心**: 浏览器打开 `http://localhost:3000`

### 默认账户

系统初始化后会创建以下默认账户：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 系统管理员账户 |
| teacher | teacher123 | 教师 | 示例教师账户 |
| student | student123 | 学生 | 示例学生账户 |

## 🏗️ 系统架构

### 核心模块

- **启动器 (Launcher)**: 系统入口点，负责启动和管理整个系统
- **主控台 (Main Console)**: 管理和监控系统的各个模块
- **题库管理**: 题目创建、编辑、分类管理
- **用户管理**: 用户注册、认证、权限管理
- **考试管理**: 考试创建、发布、监控
- **阅卷中心**: 自动阅卷、手动阅卷、评分管理
- **成绩统计**: 成绩分析、报表生成
- **客户端**: 学生考试界面

### 技术栈

- **后端**: Python, Flask
- **前端**: HTML, CSS, JavaScript
- **数据库**: SQLite (可扩展到 PostgreSQL/MySQL)
- **缓存**: Redis (可选)
- **测试**: pytest
- **部署**: Docker, Docker Compose

## 🧪 测试

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-html pytest-xdist

# 运行所有测试
python run_tests.py --all

# 运行单元测试
python run_tests.py --unit

# 运行集成测试
python run_tests.py --integration

# 生成覆盖率报告
python run_tests.py --coverage
```

### 测试结构

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── e2e/           # 端到端测试
└── utils/         # 测试工具
```

## 🔧 配置

### 环境配置

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

主要配置项：

- `DATABASE_URL`: 数据库连接地址
- `REDIS_URL`: Redis连接地址
- `SECRET_KEY`: 应用密钥
- `EMAIL_*`: 邮件服务配置

### 端口配置

默认端口分配：

- API网关: 8000
- 题库管理: 5000
- 考试管理: 5001
- 阅卷中心: 3000
- 用户管理: 5002
- 成绩统计: 5003

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

### 单独构建

```bash
# 构建镜像
docker build -t phrl-exam-system .

# 运行容器
docker run -d -p 8000:8000 --name phrl-exam phrl-exam-system
```

## 📚 文档

- [API 文档](docs/api.md)
- [部署指南](docs/deployment.md)
- [开发指南](docs/development.md)
- [故障排除](docs/troubleshooting.md)

## 🤝 贡献

欢迎提交 Pull Request 和 Issue！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- 📧 Email: support@phrl.com
- 🐛 Bug 报告: [GitHub Issues](https://github.com/shanshuishenzhen/01-PHRH_system/issues)
- 📖 文档: [在线文档](https://docs.phrl.com)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**PH&RL 在线考试系统** - 让考试管理更简单、更高效！ 🎓✨
