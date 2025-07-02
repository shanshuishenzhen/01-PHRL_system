const authMiddleware = require('./auth.middleware');

const authJwt = {
  verifyToken: authMiddleware.verifyToken,
  
  // 检查用户是否为考评员或管理员
  isMarkerOrAdmin: (req, res, next) => {
    if (req.userRole === 'examiner' || req.userRole === 'admin') {
      next();
    } else {
      res.status(403).json({ message: '需要考评员或管理员权限' });
    }
  },
  
  // 检查用户是否为考生
  isStudent: (req, res, next) => {
    if (req.userRole === 'student') {
      next();
    } else {
      res.status(403).json({ message: '需要考生权限' });
    }
  },
  
  // 检查用户是否为管理员
  isAdmin: (req, res, next) => {
    if (req.userRole === 'admin') {
      next();
    } else {
      res.status(403).json({ message: '需要管理员权限' });
    }
  }
};

module.exports = {
  authJwt
};