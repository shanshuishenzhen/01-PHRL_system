# 阅卷中心客户端

## 📝 项目概述
阅卷中心客户端是基于Vue 3 + TypeScript + Vite构建的前端应用，提供阅卷评分系统的用户界面和交互功能。

## 🛠️ 技术栈
- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

## 🚀 功能特性
### 认证功能 (v1.1.0新增)
- 用户登录/登出
- JWT认证
- 路由守卫保护
- 用户状态管理

### 文件结构
```
src/
├── api/                # API服务
│   ├── auth.ts         # 认证API
│   ├── config.ts       # API配置
│   └── ...
├── components/         # 公共组件
├── router/             # 路由配置
│   └── index.ts        # 路由定义和守卫
├── stores/             # Pinia状态管理
│   └── user.ts         # 用户状态
├── views/              # 页面组件
│   └── LoginView.vue   # 登录页面
└── ...
```

## 🔧 开发指南
### 环境要求
- Node.js 16+
- npm 8+

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 📌 更新记录
### v1.1.0 (2025-06-29)
- 新增用户登录认证功能
- 实现前端路由守卫
- 创建认证API服务(auth.ts)
- 开发登录页面(LoginView.vue)
- 集成Pinia状态管理

## 📞 技术支持
如有问题请联系: support@phrl-exam.com
