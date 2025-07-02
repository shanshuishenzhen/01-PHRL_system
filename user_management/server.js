const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const multer = require('multer');
const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: function (req, file, cb) {
    cb(null, file.fieldname + '-' + Date.now() + '.csv')
  }
});
const upload = multer({ storage: storage });
const csv = require('csv-parse');
const fs = require('fs');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

// 模拟数据库
let users = [
  { id: 1, username: '测试用户1', email: 'test1@example.com', role: '1', status: '1' },  // 正常
  { id: 2, username: '测试用户2', email: 'test2@example.com', role: '2', status: '2' },  // 待审核
];

// 获取用户列表（带分页）
app.get('/api/users', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const startIndex = (page - 1) * limit;
  const endIndex = page * limit;

  const results = {};
  results.total = users.length;
  results.totalPages = Math.ceil(users.length / limit);
  results.currentPage = page;

  if (endIndex < users.length) {
    results.next = {
      page: page + 1,
      limit: limit
    };
  }

  if (startIndex > 0) {
    results.previous = {
      page: page - 1,
      limit: limit
    };
  }

  results.users = users.slice(startIndex, endIndex);
  res.json(results);
});

// 创建新用户
app.post('/api/users', (req, res) => {
  const { username, email, role, password } = req.body;
  
  // 简单的验证
  if (!username || !email || !role || !password) {
    return res.status(400).json({ message: '所有字段都是必填的' });
  }

  // 创建新用户
  const newUser = {
    id: users.length + 1,
    username,
    email,
    role,
    status: '2',  // 默认为待审核状态
  };

  users.push(newUser);
  res.status(201).json(newUser);
});

// 更新用户
app.put('/api/users/:id', (req, res) => {
  const userId = parseInt(req.params.id);
  const updateData = req.body;

  // 查找用户
  const userIndex = users.findIndex(user => user.id === userId);
  if (userIndex === -1) {
    return res.status(404).json({ message: '用户不存在' });
  }

  // 更新用户信息
  users[userIndex] = {
    ...users[userIndex],
    ...updateData
  };

  res.json(users[userIndex]);
});

// 删除用户
app.delete('/api/users/:id', (req, res) => {
  const userId = parseInt(req.params.id);
  
  // 查找并删除用户
  const userIndex = users.findIndex(user => user.id === userId);
  if (userIndex === -1) {
    return res.status(404).json({ message: '用户不存在' });
  }

  users.splice(userIndex, 1);
  res.status(204).send();
});

// 用户批量导入接口
app.post('/api/users/import', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: '请上传文件' });
  }

  const parser = csv.parse({
    columns: true,
    skip_empty_lines: true,
    trim: true,
    bom: true  // 添加这行以处理 UTF-8 BOM
  });

  const results = [];
  const errors = [];

  fs.createReadStream(req.file.path, { encoding: 'utf8' })
    .pipe(parser)
    .on('data', (row) => {
      // 验证必填字段
      const requiredFields = ['username', 'email', 'role', 'password'];
      const missingFields = requiredFields.filter(field => !row[field]);
      
      if (missingFields.length > 0) {
        errors.push(`行数据缺少必填字段 ${missingFields.join(', ')}: ${JSON.stringify(row)}`);
        return;
      }
  
      // 验证字段格式
      if (!['1', '2', '3'].includes(row.role)) {
        errors.push(`角色值无效 (${row.role})，应为 1、2 或 3: ${JSON.stringify(row)}`);
        return;
      }
  
      // 创建新用户
      const newUser = {
        id: users.length + 1,
        username: row.username,
        email: row.email,
        role: row.role,  // 修改 roleId 为 role
        status: '2',  // 默认为待审核状态
      };
  
      users.push(newUser);
      results.push(newUser);
    })
    .on('error', (error) => {
      console.error('CSV 解析错误:', error);
      fs.unlinkSync(req.file.path);
      res.status(500).json({ message: '文件处理失败', error: error.message });
    })
    .on('end', () => {
      fs.unlinkSync(req.file.path);
      if (errors.length > 0) {
        return res.status(400).json({
          message: '部分用户导入失败',
          errors: errors
        });
      }
      res.json({
        message: '导入成功',
        importedCount: results.length,
        users: results
      });
    }); // 删除这里多余的分号
    // 删除重复的 error 事件处理
});

// 删除用户接口
app.delete('/api/users/:id', async (req, res) => {
  const userId = parseInt(req.params.id);
  
  // 查找并删除用户
  const userIndex = users.findIndex(user => user.id === userId);
  if (userIndex === -1) {
    return res.status(404).json({ message: '用户不存在' });
  }

  users.splice(userIndex, 1);
  
  // 返回更新后的用户列表
  res.json({ 
    message: '删除成功',
    users: users
  });
});
// 批量更新用户状态
app.put('/api/users/batch/status', (req, res) => {
  const { userIds, status } = req.body;
  
  if (!userIds || !Array.isArray(userIds) || !status) {
    return res.status(400).json({ message: '参数错误' });
  }

  // 更新指定用户的状态
  users = users.map(user => {
    if (userIds.includes(user.id)) {
      return { ...user, status };
    }
    return user;
  });

  res.json({ message: '批量更新成功' });
});
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});