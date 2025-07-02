// 检查admin用户密码脚本
const db = require('./models');
const User = db.user;

async function checkAdminUser() {
  try {
    // 查找admin用户
    const adminUser = await User.findOne({ where: { username: 'admin' } });
    
    if (!adminUser) {
      console.log('❌ Admin用户不存在');
      return;
    }
    
    console.log('✅ 找到Admin用户:');
    console.log({
      id: adminUser.id,
      username: adminUser.username,
      password: adminUser.password, // 显示密码用于调试
      fullName: adminUser.fullName,
      role: adminUser.role,
      email: adminUser.email
    });
    
  } catch (error) {
    console.error('❌ 查询失败:', error);
  } finally {
    process.exit();
  }
}

// 执行查询
checkAdminUser();