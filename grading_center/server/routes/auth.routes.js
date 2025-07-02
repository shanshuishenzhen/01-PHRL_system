const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth.controller');
const { verifyToken } = require('../middlewares/auth.middleware');

// 登录路由
router.post('/login', authController.login);

// 获取当前用户信息路由
router.get('/me', verifyToken, authController.getCurrentUser);

// 登出路由
router.post('/logout', verifyToken, authController.logout);

module.exports = router;