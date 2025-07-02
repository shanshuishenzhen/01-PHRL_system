const db = require('../models');
const User = db.user;
const bcrypt = require('bcrypt');

// 登录控制器
exports.login = async (req, res) => {
  console.log('收到登录请求:', { username: req.body.username });
  
  // 设置响应超时处理
  let isResponseSent = false;
  const responseTimeout = setTimeout(() => {
    if (!isResponseSent) {
      isResponseSent = true;
      console.error('登录处理超时');
      return res.status(408).json({
        success: false,
        message: '登录处理超时，请稍后再试'
      });
    }
  }, 5000); // 5秒超时
  
  try {
    const { username, password } = req.body;

    // 基本验证
    if (!username || !password) {
      clearTimeout(responseTimeout);
      isResponseSent = true;
      return res.status(400).json({
        success: false,
        message: '用户名和密码不能为空'
      });
    }

    // 查找用户
    console.log('查找用户:', username);
    const user = await User.findOne({ where: { username } });

    // 验证用户是否存在
    if (!user) {
      clearTimeout(responseTimeout);
      isResponseSent = true;
      return res.status(404).json({
        success: false,
        message: '用户不存在'
      });
    }

    console.log('找到用户:', { id: user.id, role: user.role });
    
    // 验证密码 - 检查是否为明文密码或使用bcrypt比较加密密码
    let passwordMatch = false;
    
    // 特殊处理admin账户
    if (username === 'admin') {
      console.log('检测到admin账户登录尝试');
      // 对于admin账户，直接比较明文密码
      if (password === user.password) {
        passwordMatch = true;
        console.log('admin账户明文密码验证成功');
      }
    } else {
      // 首先检查是否为明文密码
      if (password === user.password) {
        passwordMatch = true;
        console.log('使用明文密码验证成功');
      } else {
        // 尝试使用bcrypt比较
        try {
          passwordMatch = await bcrypt.compare(password, user.password);
          console.log('使用bcrypt验证结果:', passwordMatch);
        } catch (error) {
          console.error('密码比较错误:', error);
        }
      }
    }
    
    if (!passwordMatch) {
      clearTimeout(responseTimeout);
      isResponseSent = true;
      return res.status(401).json({
        success: false,
        message: '密码错误'
      });
    }

    // 生成令牌（简单实现，实际项目中应该使用更安全的JWT实现）
    const token = `token-${user.id}-${Date.now()}`;
    console.log('生成token成功:', { userId: user.id });

    // 返回用户信息和令牌
    clearTimeout(responseTimeout);
    isResponseSent = true;
    return res.status(200).json({
      success: true,
      message: '登录成功',
      user: {
        id: user.id,
        username: user.username,
        fullName: user.fullName,
        role: user.role,
        email: user.email
      },
      token: token // 确保token字段名称一致
    });
  } catch (error) {
    console.error('登录失败:', error);
    
    // 确保超时处理被清除
    clearTimeout(responseTimeout);
    
    // 避免重复发送响应
    if (!isResponseSent) {
      isResponseSent = true;
      return res.status(500).json({
        success: false,
        message: '服务器错误: ' + (error.message || '未知错误')
      });
    }
  }
};

// 获取当前用户信息
exports.getCurrentUser = async (req, res) => {
  try {
    // 从请求中获取用户ID（由认证中间件设置）
    const userId = req.userId;

    if (!userId) {
      return res.status(401).json({ message: '未授权，请先登录' });
    }

    // 查找用户
    const user = await User.findByPk(userId, {
      attributes: { exclude: ['password'] } // 排除密码字段
    });

    // 验证用户是否存在
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    // 返回用户信息
    res.status(200).json({
      success: true,
      user: user
    });
  } catch (error) {
    console.error('获取用户信息失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 登出
exports.logout = (req, res) => {
  try {
    // 在实际的JWT实现中，这里应该将令牌加入黑名单或使其失效
    // 由于我们使用的是简单令牌，客户端只需要删除本地存储的令牌即可
    
    res.status(200).json({ 
      success: true,
      message: '登出成功' 
    });
  } catch (error) {
    console.error('登出失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};