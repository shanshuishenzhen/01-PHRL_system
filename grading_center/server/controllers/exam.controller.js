const { Exam, ExamQuestion, ExamParticipant, User } = require('../models');
const { Op } = require('sequelize');

// 创建考试
exports.createExam = async (req, res) => {
  try {
    const examData = {
      ...req.body,
      createdBy: req.user.id
    };

    const exam = await Exam.create(examData);
    
    res.status(201).json({
      success: true,
      message: '考试创建成功',
      data: exam
    });
  } catch (error) {
    console.error('创建考试失败:', error);
    res.status(500).json({
      success: false,
      message: '创建考试失败',
      error: error.message
    });
  }
};

// 获取考试列表
exports.getExams = async (req, res) => {
  try {
    const { page = 1, limit = 10, status, keyword } = req.query;
    const offset = (page - 1) * limit;
    
    const whereClause = {};
    if (status) {
      whereClause.status = status;
    }
    if (keyword) {
      whereClause[Op.or] = [
        { examName: { [Op.like]: `%${keyword}%` } },
        { examCode: { [Op.like]: `%${keyword}%` } }
      ];
    }

    const { count, rows } = await Exam.findAndCountAll({
      where: whereClause,
      include: [
        {
          model: User,
          as: 'creator',
          attributes: ['id', 'username', 'realName']
        }
      ],
      order: [['createdAt', 'DESC']],
      limit: parseInt(limit),
      offset: parseInt(offset)
    });

    res.json({
      success: true,
      data: rows,
      pagination: {
        total: count,
        page: parseInt(page),
        limit: parseInt(limit),
        pages: Math.ceil(count / limit)
      }
    });
  } catch (error) {
    console.error('获取考试列表失败:', error);
    res.status(500).json({
      success: false,
      message: '获取考试列表失败',
      error: error.message
    });
  }
};

// 获取单个考试详情
exports.getExamById = async (req, res) => {
  try {
    const { id } = req.params;
    
    const exam = await Exam.findByPk(id, {
      include: [
        {
          model: ExamQuestion,
          as: 'questions',
          order: [['orderNum', 'ASC']]
        },
        {
          model: ExamParticipant,
          as: 'participants',
          include: [
            {
              model: User,
              as: 'user',
              attributes: ['id', 'username', 'realName', 'email']
            }
          ]
        },
        {
          model: User,
          as: 'creator',
          attributes: ['id', 'username', 'realName']
        }
      ]
    });

    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    res.json({
      success: true,
      data: exam
    });
  } catch (error) {
    console.error('获取考试详情失败:', error);
    res.status(500).json({
      success: false,
      message: '获取考试详情失败',
      error: error.message
    });
  }
};

// 更新考试
exports.updateExam = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = {
      ...req.body,
      updatedBy: req.user.id
    };

    const exam = await Exam.findByPk(id);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    await exam.update(updateData);

    res.json({
      success: true,
      message: '考试更新成功',
      data: exam
    });
  } catch (error) {
    console.error('更新考试失败:', error);
    res.status(500).json({
      success: false,
      message: '更新考试失败',
      error: error.message
    });
  }
};

// 删除考试
exports.deleteExam = async (req, res) => {
  try {
    const { id } = req.params;
    
    const exam = await Exam.findByPk(id);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    // 检查考试状态，已发布的考试不能删除
    if (exam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能删除草稿状态的考试'
      });
    }

    await exam.destroy();

    res.json({
      success: true,
      message: '考试删除成功'
    });
  } catch (error) {
    console.error('删除考试失败:', error);
    res.status(500).json({
      success: false,
      message: '删除考试失败',
      error: error.message
    });
  }
};

// 发布考试
exports.publishExam = async (req, res) => {
  try {
    const { id } = req.params;
    
    const exam = await Exam.findByPk(id);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    if (exam.status !== 'draft') {
      return res.status(400).json({
        success: false,
        message: '只能发布草稿状态的考试'
      });
    }

    // 检查考试是否有题目
    const questionCount = await ExamQuestion.count({
      where: { examId: id }
    });

    if (questionCount === 0) {
      return res.status(400).json({
        success: false,
        message: '考试必须包含至少一道题目才能发布'
      });
    }

    await exam.update({ 
      status: 'published',
      updatedBy: req.user.id
    });

    res.json({
      success: true,
      message: '考试发布成功',
      data: exam
    });
  } catch (error) {
    console.error('发布考试失败:', error);
    res.status(500).json({
      success: false,
      message: '发布考试失败',
      error: error.message
    });
  }
};

// 开始考试
exports.startExam = async (req, res) => {
  try {
    const { id } = req.params;
    
    const exam = await Exam.findByPk(id);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    if (exam.status !== 'published') {
      return res.status(400).json({
        success: false,
        message: '只能开始已发布状态的考试'
      });
    }

    const now = new Date();
    if (now < exam.startTime) {
      return res.status(400).json({
        success: false,
        message: '考试还未到开始时间'
      });
    }

    await exam.update({ 
      status: 'ongoing',
      updatedBy: req.user.id
    });

    res.json({
      success: true,
      message: '考试开始成功',
      data: exam
    });
  } catch (error) {
    console.error('开始考试失败:', error);
    res.status(500).json({
      success: false,
      message: '开始考试失败',
      error: error.message
    });
  }
};

// 结束考试
exports.endExam = async (req, res) => {
  try {
    const { id } = req.params;
    
    const exam = await Exam.findByPk(id);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    if (exam.status !== 'ongoing') {
      return res.status(400).json({
        success: false,
        message: '只能结束进行中状态的考试'
      });
    }

    await exam.update({ 
      status: 'completed',
      updatedBy: req.user.id
    });

    res.json({
      success: true,
      message: '考试结束成功',
      data: exam
    });
  } catch (error) {
    console.error('结束考试失败:', error);
    res.status(500).json({
      success: false,
      message: '结束考试失败',
      error: error.message
    });
  }
};

// 获取考试统计信息
exports.getExamStats = async (req, res) => {
  try {
    const { id } = req.params;
    
    const exam = await Exam.findByPk(id);
    if (!exam) {
      return res.status(404).json({
        success: false,
        message: '考试不存在'
      });
    }

    // 统计参与者信息
    const participantStats = await ExamParticipant.findAll({
      where: { examId: id },
      attributes: [
        'status',
        [ExamParticipant.sequelize.fn('COUNT', '*'), 'count']
      ],
      group: ['status']
    });

    // 统计成绩信息
    const scoreStats = await ExamParticipant.findAll({
      where: { 
        examId: id,
        score: { [Op.not]: null }
      },
      attributes: [
        [ExamParticipant.sequelize.fn('AVG', ExamParticipant.sequelize.col('score')), 'avgScore'],
        [ExamParticipant.sequelize.fn('MAX', ExamParticipant.sequelize.col('score')), 'maxScore'],
        [ExamParticipant.sequelize.fn('MIN', ExamParticipant.sequelize.col('score')), 'minScore'],
        [ExamParticipant.sequelize.fn('COUNT', '*'), 'totalParticipants']
      ]
    });

    res.json({
      success: true,
      data: {
        exam,
        participantStats,
        scoreStats: scoreStats[0] || {}
      }
    });
  } catch (error) {
    console.error('获取考试统计失败:', error);
    res.status(500).json({
      success: false,
      message: '获取考试统计失败',
      error: error.message
    });
  }
}; 