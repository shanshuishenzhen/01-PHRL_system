const express = require('express');
const cors = require('cors'); // 引入 cors
const db = require('./models/db'); // 如果暂时不用数据库，可以注释掉或确保连接成功

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

// 注册路由
app.use('/api/test', testRoutes); // 路由前缀 /api/test
app.use('/api/exams', examRoutes); // 考试管理路由
app.use('/api/scores', scoreRoutes); // 成绩数据路由

app.get('/', (req, res) => {
  res.send('Server is running.');
});

// 引入数据库模型
const models = require('./models');

// 只在直接运行此文件时启动服务器
if (require.main === module) {
  // 同步数据库模型
  models.sequelize.sync({ alter: true })
    .then(() => {
      console.log('✅ Database synchronized successfully.');
      // 启动时指定不同端口
      const port = process.env.PORT || 5000; // 主服务器
      const debugPort = process.env.DEBUG_PORT || 5001; // 调试服务器
      
      // 主服务器实例
      // 主服务器
      const mainServer = app.listen(5000, () => {
        console.log('主服务器运行在: http://localhost:5000');
      });
      
      // 调试服务器
      const debugApp = express();
      debugApp.use('/api', require('./routes/debug'));
      const debugServer = debugApp.listen(5001, () => {
        console.log('调试服务器运行在: http://localhost:5001');
      });
    })
    .catch(err => {
      console.error('❌ Failed to synchronize database:', err);
    });
}

module.exports = app;

// 新增考试检查路由
app.get('/api/student/exams', (req, res) => {
  const { studentId } = req.query;
  
  // 实际应查询数据库
  const hasExams = checkExams(studentId); 
  
  if(!hasExams) {
    return res.status(403).json({ 
      error: 'NO_AVAILABLE_EXAMS',
      message: '当前没有可参加的考试科目'
    });
  }
  
  res.json({ exams: getStudentExams(studentId) });
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  // 实际应查询数据库
  const user = await UserService.authenticate(username, password);
  
  if (!user) {
    return res.status(401).json({ error: 'INVALID_CREDENTIALS' });
  }
  
  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET);
  res.json({ token });
});

app.get('/student/exams', authMiddleware, async (req, res) => {
  try {
    const exams = await ExamService.getAvailableExams(req.user.userId);
    res.json({
      available_exams: exams.filter(e => e.status === 'available'),
      completed_exams: exams.filter(e => e.status === 'completed')
    });
  } catch (error) {
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});