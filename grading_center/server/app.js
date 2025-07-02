const express = require('express');
const cors = require('cors'); // 引入 cors
const db = require('./models/db'); // 如果暂时不用数据库，可以注释掉或确保连接成功
const models = require('./models'); // 引入数据库模型

const app = express();
const port = 3000; // 硬编码端口为 3000，避免冲突

// 使用 CORS 中间件
// 简单允许所有来源 (开发时方便，生产环境应配置具体的来源)
app.use(cors()); 

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 引入路由
const testRoutes = require('./routes/test.routes');
const examRoutes = require('./routes/exam.routes');
const scoreRoutes = require('./routes/score.routes');
const authRoutes = require('./routes/auth.routes');
const userRoutes = require('./routes/user.routes');

// 注册路由
app.use('/api/test', testRoutes); // 路由前缀 /api/test
app.use('/api/exams', examRoutes); // 考试管理路由
app.use('/api/scores', scoreRoutes); // 成绩管理路由
app.use('/api/auth', authRoutes); // 认证路由
app.use('/api/users', userRoutes); // 用户管理路由

app.get('/', (req, res) => {
  res.send('Server is running.');
});

// 数据库模型已在上方引入

// 初始化用户数据
async function initializeUsers() {
  try {
    // 检查是否有用户数据
    const userCount = await models.user.count();
    if (userCount === 0) {
      // 如果没有用户数据，则执行初始化脚本
      console.log('No users found, initializing default users...');
      const initUsers = require('./database_scripts/init_users');
      await initUsers.initUsers();
    } else {
      console.log(`✅ Found ${userCount} existing users, skipping initialization.`);
    }
  } catch (error) {
    console.error('❌ Error initializing users:', error);
  }
}

// 只在直接运行此文件时启动服务器
if (require.main === module) {
  // 同步数据库模型
  models.sequelize.sync({ alter: true })
    .then(async () => {
      console.log('✅ Database synchronized successfully.');
      
      // 初始化用户数据
      await initializeUsers();
      
      app.listen(port, () => {
        console.log(`Server is running on port ${port}.`);
      });
    })
    .catch(err => {
      console.error('❌ Failed to synchronize database:', err);
    });
}

module.exports = app;