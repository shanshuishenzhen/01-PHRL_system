const express = require('express');
const router = express.Router();
const userController = require('../controllers/user.controller');
const { verifyToken } = require('../middlewares/auth.middleware');
const { isAdmin, isAdminOrSelf, isExaminerOrAdmin } = require('../middlewares/user.middleware');

// 创建新用户路由 - 需要管理员权限
router.post('/', verifyToken, isAdmin, userController.createUser);

// 获取所有用户路由 - 需要管理员权限
router.get('/', verifyToken, isAdmin, userController.getAllUsers);

// 获取单个用户路由 - 需要管理员权限或者是用户本人
router.get('/:id', verifyToken, isAdminOrSelf, userController.getUserById);

// 更新用户路由 - 需要管理员权限或者是用户本人
router.put('/:id', verifyToken, isAdminOrSelf, userController.updateUser);

// 删除用户路由 - 需要管理员权限
router.delete('/:id', verifyToken, isAdmin, userController.deleteUser);

// 修改用户密码路由 - 需要管理员权限或者是用户本人
router.put('/:id/change-password', verifyToken, isAdminOrSelf, userController.changePassword);

module.exports = router;