# 阅卷中心模块

## 📝 模块概述

阅卷中心模块是 PH&RL 在线考试系统的核心评分组件，提供专业的在线阅卷和评分功能。该模块采用前后端分离架构，基于 Node.js + Vue.js 开发，支持多人协作阅卷、自动评分、评分标准管理等功能，为考评员提供高效、准确的阅卷工具。

## 🎯 主要功能

### 阅卷管理
- **试卷列表**：查看待阅卷的试卷列表
- **试卷详情**：查看试卷完整内容和考生答案
- **评分操作**：对主观题进行人工评分
- **评分标准**：查看和应用评分标准
- **评分历史**：查看评分操作历史记录

### 协作功能
- **多人协作**：支持多名考评员同时阅卷
- **任务分配**：自动分配阅卷任务
- **进度监控**：实时监控阅卷进度
- **冲突处理**：处理评分冲突和差异
- **质量检查**：评分质量检查和复核

### 自动评分
- **客观题评分**：自动评分选择题、判断题等
- **关键词匹配**：基于关键词的填空题评分
- **相似度分析**：答案相似度分析和评分
- **评分规则**：灵活的评分规则配置
- **评分校准**：评分结果校准和调整

### 数据管理
- **评分数据**：管理所有评分数据
- **评分统计**：评分统计和分析
- **数据导出**：导出评分数据和报告
- **数据备份**：评分数据备份和恢复

## 🏗️ 技术架构

### 前端技术
- **框架**：Vue.js 3.x
- **UI组件**：Element Plus
- **状态管理**：Vuex 4.x
- **路由管理**：Vue Router 4.x
- **HTTP客户端**：Axios

### 后端技术
- **运行环境**：Node.js 14+
- **Web框架**：Express.js
- **数据库**：MySQL 8.0+
- **ORM框架**：Sequelize
- **认证授权**：JWT

### 文件结构
```
grading_center/
├── backend/                     # Node.js后端
│   ├── app.js                   # 应用入口
│   ├── routes/                  # 路由定义
│   ├── models/                  # 数据模型
│   ├── controllers/             # 控制器
│   ├── middleware/              # 中间件
│   ├── config/                  # 配置文件
│   └── package.json
├── frontend/                    # Vue.js前端
│   ├── src/                     # 源代码
│   │   ├── components/          # 组件
│   │   ├── views/               # 页面
│   │   ├── router/              # 路由
│   │   ├── store/               # 状态管理
│   │   └── utils/               # 工具函数
│   ├── public/                  # 静态资源
│   └── package.json
├── database/                    # 数据库文件
│   ├── init.sql                 # 初始化脚本
│   └── migrations/              # 数据库迁移
└── README.md                    # 模块说明文档
```

### 数据库设计
```sql
-- 试卷表
CREATE TABLE exams (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    total_score INT NOT NULL,
    duration INT NOT NULL,
    status ENUM('pending', 'grading', 'completed') DEFAULT 'pending',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 考生答题表
CREATE TABLE student_answers (
    id VARCHAR(50) PRIMARY KEY,
    exam_id VARCHAR(50) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    answers JSON NOT NULL,
    score DECIMAL(5,2) DEFAULT 0,
    status ENUM('submitted', 'grading', 'completed') DEFAULT 'submitted',
    submitted_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    graded_time DATETIME,
    grader_id VARCHAR(50),
    FOREIGN KEY (exam_id) REFERENCES exams(id),
    FOREIGN KEY (grader_id) REFERENCES users(id)
);

-- 评分记录表
CREATE TABLE grading_records (
    id VARCHAR(50) PRIMARY KEY,
    answer_id VARCHAR(50) NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    comments TEXT,
    grader_id VARCHAR(50) NOT NULL,
    graded_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (answer_id) REFERENCES student_answers(id),
    FOREIGN KEY (grader_id) REFERENCES users(id)
);
```

## 🚀 使用指南

### 环境要求
- **Node.js**：14.0.0 或更高版本
- **SQLite/MySQL**：用于数据存储
- **Python**：3.6+（用于启动脚本）

### 启动方式
```bash
# 方式1：通过主控台启动（推荐）
python main_console.py
# 然后点击"阅卷中心"按钮

# 方式2：手动启动
cd grading_center
# 启动后端
cd server && npm install && node app.js
# 启动前端
cd client && npm install && npm run dev
```

### 当前开发状态
- ✅ 基础框架搭建完成（前后端分离架构）
- ✅ 考试管理基本功能实现
- ✅ 单人阅卷功能实现
- ✅ 多人协作阅卷功能实现
- ✅ 评分仲裁功能实现
- ⏳ 客观题自动评分功能开发中
- ⏳ 数据统计与导出功能开发中

### 基本操作

#### 1. 登录系统
1. 使用考评员账户登录
2. 验证身份和权限
3. 进入阅卷中心主界面

#### 2. 查看试卷列表
1. 在试卷列表中查看待阅卷的试卷
2. 使用筛选条件查找特定试卷
3. 查看试卷的基本信息和状态

#### 3. 开始阅卷
1. 选择要阅卷的试卷
2. 点击"开始阅卷"按钮
3. 查看试卷内容和考生答案
4. 根据评分标准进行评分

#### 4. 评分操作
1. 查看题目内容和标准答案
2. 阅读考生答案
3. 根据评分标准给出分数
4. 添加评分评语（可选）
5. 保存评分结果

#### 5. 多人协作阅卷
1. 每道主观题由3名考评员同时评分
2. 系统自动计算平均分和评分方差
3. 当评分方差超过阈值时，系统标记为"有争议"状态
4. 有争议的答案需要由仲裁员进行最终评分
5. 完成最终评分确认

#### 6. 评分仲裁
1. 仲裁员查看有争议的答案列表
2. 查看所有考评员的评分记录和评语
3. 分析评分差异和争议原因
4. 给出最终仲裁分数和仲裁说明
5. 系统更新答案的最终得分

#### 7. 导出结果
1. 选择要导出的评分数据
2. 选择导出格式（Excel、PDF等）
3. 确认导出操作
4. 下载评分结果文件

## 📊 功能特性

### 用户界面
- **现代化设计**：基于Element Plus的现代化界面
- **响应式布局**：支持不同屏幕尺寸
- **主题定制**：支持多种主题和颜色方案
- **操作便捷**：直观的操作流程和快捷键支持

### 评分功能
- **智能评分**：自动评分和人工评分结合
- **多人评分**：主观题由3名考评员同时评分取平均值
- **评分标准**：灵活的评分标准配置
- **质量保证**：多重质量检查机制
- **仲裁机制**：评分争议自动检测和仲裁处理
- **效率提升**：批量操作和模板功能

### 协作特性
- **实时同步**：多人协作实时数据同步
- **任务分配**：自动分配评阅任务给多名考评员
- **评分统计**：自动计算多人评分的平均分和方差
- **冲突解决**：智能冲突检测和仲裁机制
- **权限控制**：细粒度的权限管理（考评员、仲裁员、管理员）
- **操作审计**：完整的操作记录和审计

### 数据处理
- **高性能**：优化的数据库查询和缓存
- **数据安全**：数据加密和备份机制
- **扩展性**：支持大规模数据处理
- **兼容性**：支持多种数据格式

## 🔧 配置说明

### 后端配置
```javascript
// config/database.js
module.exports = {
    host: 'localhost',
    port: 3306,
    database: 'phrl_exam',
    username: 'root',
    password: '',
    dialect: 'mysql',
    pool: {
        max: 10,
        min: 0,
        acquire: 30000,
        idle: 10000
    }
};

// config/app.js
module.exports = {
    port: 3000,
    jwt_secret: 'your-jwt-secret',
    cors_origin: 'http://localhost:8080',
    upload_path: './uploads/'
};
```

### 前端配置
```javascript
// vue.config.js
module.exports = {
    devServer: {
        port: 8080,
        proxy: {
            '/api': {
                target: 'http://localhost:3000',
                changeOrigin: true
            }
        }
    }
};

// .env
VUE_APP_API_BASE_URL=http://localhost:3000/api
VUE_APP_TITLE=PH&RL阅卷中心
```

### 数据库配置
```sql
-- 创建数据库
CREATE DATABASE phrl_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'phrl_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON phrl_exam.* TO 'phrl_user'@'localhost';
FLUSH PRIVILEGES;
```

## 🚨 故障排除

### 常见问题

#### 1. 后端启动失败
```bash
# 检查Node.js版本
node --version

# 检查依赖安装
cd backend && npm install

# 检查数据库连接
mysql -u root -p -e "SHOW DATABASES;"

# 检查端口占用
netstat -tulpn | grep :3000
```

#### 2. 前端启动失败
```bash
# 检查Node.js版本
node --version

# 检查依赖安装
cd frontend && npm install

# 检查端口占用
netstat -tulpn | grep :8080

# 检查代理配置
cat vue.config.js
```

#### 3. 数据库连接问题
```bash
# 检查MySQL服务
systemctl status mysql

# 检查数据库连接
mysql -u root -p -e "USE phrl_exam; SHOW TABLES;"

# 检查用户权限
mysql -u root -p -e "SHOW GRANTS FOR 'phrl_user'@'localhost';"
```

#### 4. 评分数据异常
- 检查数据库表结构是否正确
- 确认数据完整性约束
- 验证评分规则配置
- 查看错误日志文件

### 错误代码说明
- **E001**：数据库连接失败
- **E002**：用户认证失败
- **E003**：权限验证失败
- **E004**：数据操作失败
- **E005**：文件上传失败

## 📈 性能指标

### 系统性能
- **响应时间**：< 500ms
- **并发用户**：支持100+同时在线
- **数据处理**：支持10,000+试卷
- **内存占用**：< 500MB

### 评分效率
- **自动评分**：< 1秒/题
- **人工评分**：< 30秒/题
- **批量操作**：< 5秒/100题
- **数据导出**：< 10秒/1000条

## 🔄 版本历史

### v1.0.0 (2024-01-15)
- ✅ 完成基础阅卷功能
- ✅ 实现多人协作阅卷
- ✅ 添加自动评分功能
- ✅ 实现评分数据管理
- ✅ 优化用户界面设计

### 下一步计划
- 🔄 添加AI智能评分功能
- 🔄 实现评分质量分析
- 🔄 添加评分标准学习
- 🔄 支持更多题型评分
- 🔄 实现移动端阅卷

## 📞 技术支持

### 联系方式
- **模块负责人**：阅卷中心开发组
- **技术支持**：support@phrl-exam.com
- **问题反馈**：issues@phrl-exam.com

### 支持时间
- **工作日**：9:00-18:00
- **紧急支持**：7×24小时

---

**阅卷中心模块** - 让阅卷更高效、更准确！