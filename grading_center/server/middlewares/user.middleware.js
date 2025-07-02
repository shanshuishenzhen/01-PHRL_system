// 用户权限中间件
const db = require('../models');
const User = db.user;

// 验证是否为管理员
exports.isAdmin = async (req, res, next) => {
  try {
    // 从请求对象获取用户角色（由认证中间件设置）
    const userRole = req.userRole;

    if (userRole !== 'admin') {
      return res.status(403).json({ message: '需要管理员权限' });
    }

    // 继续下一个中间件
    next();
  } catch (error) {
    console.error('权限验证失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 验证是否为管理员或用户本人
exports.isAdminOrSelf = async (req, res, next) => {
  try {
    // 从请求对象获取用户ID和角色（由认证中间件设置）
    const userId = req.userId;
    const userRole = req.userRole;
    const targetUserId = parseInt(req.params.id);

    // 验证是否为管理员或用户本人
    if (userRole !== 'admin' && userId !== targetUserId) {
      return res.status(403).json({ message: '权限不足' });
    }

    // 继续下一个中间件
    next();
  } catch (error) {
    console.error('权限验证失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 验证是否为考评员或管理员
exports.isExaminerOrAdmin = async (req, res, next) => {
  try {
    // 从请求对象获取用户角色（由认证中间件设置）
    const userRole = req.userRole;

    if (userRole !== 'examiner' && userRole !== 'admin') {
      return res.status(403).json({ message: '需要考评员或管理员权限' });
    }

    // 继续下一个中间件
    next();
  } catch (error) {
    console.error('权限验证失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};