// 初始化用户数据脚本
const db = require('../models');
const User = db.user;
const bcrypt = require('bcrypt');

// 密码加密函数
async function hashPassword(password) {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
}

// 初始化用户数据
async function initUsers() {
  try {
    // 清空用户表
    await User.destroy({ where: {}, truncate: true });

    // 创建测试用户
    const users = [{
        username: 'admin',
        password: 'admin123', // 使用明文密码，确保登录功能正常
        fullName: '管理员',
        role: 'admin',
        email: 'admin@example.com'
      },
      {
        username: 'teacher1',
        password: await hashPassword('teacher123'),
        fullName: '考评员一',
        role: 'examiner',
        email: 'teacher1@example.com'
      },
      {
        username: 'student1',
        password: await hashPassword('student123'),
        fullName: '学生一',
        role: 'student',
        email: 'student1@example.com'
      }
    ];

    // 批量创建用户
    await User.bulkCreate(users);

    console.log('✅ 用户数据初始化成功');
  } catch (error) {
    console.error('❌ 用户数据初始化失败:', error);
  } finally {
    // 关闭数据库连接
    process.exit();
  }
}

// 导出初始化函数
exports.initUsers = initUsers;

// 如果直接运行此文件，则执行初始化
if (require.main === module) {
  initUsers();
}