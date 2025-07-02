// 验证令牌中间件
const db = require('../models');
const User = db.user;

// 验证令牌
exports.verifyToken = async (req, res, next) => {
  try {
    // 从请求头获取令牌
    const authHeader = req.headers.authorization;

    // 验证令牌是否存在
    if (!authHeader) {
      return res.status(401).json({ message: '未提供认证令牌' });
    }

    // 提取令牌（移除Bearer前缀，如果有的话）
    const token = authHeader.startsWith('Bearer ') ? authHeader.substring(7) : authHeader;

    // 简单验证令牌格式（实际应该使用JWT验证）
    const tokenParts = token.split('-');
    if (tokenParts.length !== 3 || tokenParts[0] !== 'token') {
      return res.status(401).json({ message: '无效的令牌格式' });
    }

    // 从令牌中提取用户ID
    const userId = parseInt(tokenParts[1]);

    // 查找用户
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(401).json({ message: '无效的用户令牌' });
    }

    // 将用户ID添加到请求对象
    req.userId = userId;
    req.userRole = user.role; // 添加用户角色，便于权限控制

    // 继续下一个中间件
    next();
  } catch (error) {
    console.error('令牌验证失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};