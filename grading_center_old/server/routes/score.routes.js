const express = require('express');
const router = express.Router();
const scoreController = require('../controllers/score.controller');

// 成绩数据导出路由
router.get('/export', scoreController.exportScores);

// 获取所有成绩数据
router.get('/', scoreController.getAllScores);

// 按考试ID获取成绩数据
router.get('/exam/:examId', scoreController.getScoresByExam);

// 按学生ID获取成绩数据
router.get('/student/:studentId', scoreController.getScoresByStudent);

// 按部门获取成绩数据
router.get('/department/:department', scoreController.getScoresByDepartment);

module.exports = router;