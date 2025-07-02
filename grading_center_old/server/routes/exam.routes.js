const express = require('express');
const router = express.Router();
const examController = require('../controllers/exam.controller');
const examQuestionController = require('../controllers/examQuestion.controller');

// 考试管理路由
router.post('/', examController.createExam);
router.get('/', examController.getExams);
router.get('/:id', examController.getExamById);
router.put('/:id', examController.updateExam);
router.delete('/:id', examController.deleteExam);

// 考试状态管理
router.post('/:id/publish', examController.publishExam);
router.post('/:id/start', examController.startExam);
router.post('/:id/end', examController.endExam);

// 考试统计
router.get('/:id/stats', examController.getExamStats);

// 考试题目管理
router.post('/:examId/questions', examQuestionController.createQuestion);
router.get('/:examId/questions', examQuestionController.getQuestions);
router.get('/questions/:id', examQuestionController.getQuestionById);
router.put('/questions/:id', examQuestionController.updateQuestion);
router.delete('/questions/:id', examQuestionController.deleteQuestion);
router.put('/:examId/questions/order', examQuestionController.updateQuestionOrder);
router.post('/questions/:id/copy', examQuestionController.copyQuestion);

module.exports = router; 