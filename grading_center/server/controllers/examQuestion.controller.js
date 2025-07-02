const { ExamQuestion, Exam } = require('../models');

// 创建考试题目
exports.createQuestion = async (req, res) => {
  try {
    const { examId } = req.params;
    const questionData = {
      ...req.body,
      examId: parseInt(examId),
      createdBy: req.user.id
    };

    // 检查考试是否存在
    const exam = await Exam.findByPk(examId);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    // 检查考试状态，已发布的考试不能添加题目
    if (exam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能为草稿状态的考试添加题目'
      });
    }

    const question = await ExamQuestion.create(questionData);
    
    res.status(201).json({
      success: true,
      message: '题目创建成功',
      data: question
    });
  } catch (error) {
    console.error('创建题目失败:', error);
    res.status(500).json({
      success: false,
      message: '创建题目失败',
      error: error.message
    });
  }
};

// 获取考试题目列表
exports.getQuestions = async (req, res) => {
  try {
    const { examId } = req.params;
    
    const questions = await ExamQuestion.findAll({
      where: { examId: parseInt(examId) },
      order: [['orderNum', 'ASC']]
    });

    res.json({
      success: true,
      data: questions
    });
  } catch (error) {
    console.error('获取题目列表失败:', error);
    res.status(500).json({
      success: false,
      message: '获取题目列表失败',
      error: error.message
    });
  }
};

// 获取单个题目详情
exports.getQuestionById = async (req, res) => {
  try {
    const { id } = req.params;
    
    const question = await ExamQuestion.findByPk(id);
    if (!question) {
      return res.status(404).json({
        success: false,
        message: '题目不存在'
      });
    }

    res.json({
      success: true,
      data: question
    });
  } catch (error) {
    console.error('获取题目详情失败:', error);
    res.status(500).json({
      success: false,
      message: '获取题目详情失败',
      error: error.message
    });
  }
};

// 更新题目
exports.updateQuestion = async (req, res) => {
  try {
    const { id } = req.params;
    
    const question = await ExamQuestion.findByPk(id);
    if (!question) {
      return res.status(404).json({
        success: false,
        message: '题目不存在'
      });
    }

    // 检查考试状态
    const exam = await Exam.findByPk(question.examId);
    if (exam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能修改草稿状态考试的题目'
      });
    }

    await question.update(req.body);

    res.json({
      success: true,
      message: '题目更新成功',
      data: question
    });
  } catch (error) {
    console.error('更新题目失败:', error);
    res.status(500).json({
      success: false,
      message: '更新题目失败',
      error: error.message
    });
  }
};

// 删除题目
exports.deleteQuestion = async (req, res) => {
  try {
    const { id } = req.params;
    
    const question = await ExamQuestion.findByPk(id);
    if (!question) {
      return res.status(404).json({
        success: false,
        message: '题目不存在'
      });
    }

    // 检查考试状态
    const exam = await Exam.findByPk(question.examId);
    if (exam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能删除草稿状态考试的题目'
      });
    }

    await question.destroy();

    res.json({
      success: true,
      message: '题目删除成功'
    });
  } catch (error) {
    console.error('删除题目失败:', error);
    res.status(500).json({
      success: false,
      message: '删除题目失败',
      error: error.message
    });
  }
};

// 批量更新题目顺序
exports.updateQuestionOrder = async (req, res) => {
  try {
    const { examId } = req.params;
    const { questions } = req.body; // [{id, orderNum}, ...]

    // 检查考试状态
    const exam = await Exam.findByPk(examId);
    if (exam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能修改草稿状态考试的题目顺序'
      });
    }

    // 批量更新题目顺序
    for (const item of questions) {
      await ExamQuestion.update(
        { orderNum: item.orderNum },
        { where: { id: item.id, examId: parseInt(examId) } }
      );
    }

    res.json({
      success: true,
      message: '题目顺序更新成功'
    });
  } catch (error) {
    console.error('更新题目顺序失败:', error);
    res.status(500).json({
      success: false,
      message: '更新题目顺序失败',
      error: error.message
    });
  }
};

// 复制题目到其他考试
exports.copyQuestion = async (req, res) => {
  try {
    const { id } = req.params;
    const { targetExamId } = req.body;
    
    const sourceQuestion = await ExamQuestion.findByPk(id);
    if (!sourceQuestion) {
      return res.status(404).json({
        success: false,
        message: '源题目不存在'
      });
    }

    // 检查目标考试
    const targetExam = await Exam.findByPk(targetExamId);
    if (!targetExam) {
      return res.status(404).json({
        success: false,
        message: '目标考试不存在'
      });
    }

    if (targetExam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能复制到草稿状态的考试'
      });
    }

    // 复制题目
    const newQuestion = await ExamQuestion.create({
      examId: targetExamId,
      questionType: sourceQuestion.questionType,
      questionContent: sourceQuestion.questionContent,
      options: sourceQuestion.options,
      correctAnswer: sourceQuestion.correctAnswer,
      score: sourceQuestion.score,
      difficulty: sourceQuestion.difficulty,
      isRequired: sourceQuestion.isRequired,
      explanation: sourceQuestion.explanation,
      createdBy: req.user.id
    });

    res.status(201).json({
      success: true,
      message: '题目复制成功',
      data: newQuestion
    });
  } catch (error) {
    console.error('复制题目失败:', error);
    res.status(500).json({
      success: false,
      message: '复制题目失败',
      error: error.message
    });
  }
}; 