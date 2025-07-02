module.exports = app => {
  const subjectiveAnswers = require("../controllers/subjectiveAnswer.controller.js");
  const { authJwt } = require("../middlewares");
  const router = require("express").Router();

  // 应用中间件验证token和角色权限
  router.use(authJwt.verifyToken);
  
  // 获取待阅卷的答案列表（仅阅卷员和管理员可访问）
  router.get(
    "/pending/:examId", 
    [authJwt.isMarkerOrAdmin], 
    subjectiveAnswers.getPendingAnswers
  );
  
  // 获取单个答案详情
  router.get(
    "/:id", 
    [authJwt.isMarkerOrAdmin], 
    subjectiveAnswers.getAnswerById
  );
  
  // 评分操作（仅阅卷员和管理员可操作）
  router.put(
    "/mark/:id", 
    [authJwt.isMarkerOrAdmin], 
    subjectiveAnswers.markAnswer
  );
  
  // 获取已评阅的答案列表
  router.get(
    "/marked/:examId", 
    [authJwt.isMarkerOrAdmin], 
    subjectiveAnswers.getMarkedAnswers
  );
  
  // 提交争议/申请仲裁（学生可操作）
  router.put(
    "/dispute/:id", 
    [authJwt.isStudent], 
    subjectiveAnswers.disputeAnswer
  );

  app.use("/api/subjective-answers", router);
};