const db = require("../models");
const SubjectiveAnswer = db.subjectiveAnswer;
const User = db.user;
const ExamQuestion = db.examQuestion;
const { Op } = require("sequelize");

// 获取待阅卷的答案列表
exports.getPendingAnswers = async (req, res) => {
  try {
    const { examId } = req.params;
    const { page = 1, size = 10 } = req.query;
    const limit = parseInt(size);
    const offset = (parseInt(page) - 1) * limit;

    const answers = await SubjectiveAnswer.findAndCountAll({
      where: {
        status: 'pending',
        '$examQuestion.examId$': examId
      },
      include: [
        {
          model: ExamQuestion,
          as: 'examQuestion',
          attributes: ['id', 'questionContent', 'score']
        }
      ],
      limit,
      offset,
      order: [['createdAt', 'DESC']]
    });

    res.status(200).send({
      total: answers.count,
      currentPage: parseInt(page),
      totalPages: Math.ceil(answers.count / limit),
      data: answers.rows
    });
  } catch (error) {
    res.status(500).send({
      message: error.message || "获取待阅卷答案列表时发生错误"
    });
  }
};

// 获取单个答案详情
exports.getAnswerDetail = async (req, res) => {
  try {
    const { id } = req.params;
    
    const answer = await SubjectiveAnswer.findByPk(id, {
      include: [
        {
          model: ExamQuestion,
          as: 'examQuestion',
          include: [
            {
              model: db.examPaper,
              as: 'examPaper'
            }
          ]
        },
        {
          model: db.user,
          as: 'marker',
          attributes: ['id', 'username', 'email', 'role']
        },
        {
          model: db.examParticipant,
          as: 'participant',
          include: [
            {
              model: db.user,
              as: 'user',
              attributes: ['id', 'username', 'email']
            }
          ]
        }
      ]
    });

    if (!answer) {
      return res.status(404).send({
        message: `未找到ID为${id}的答案`
      });
    }

    // 如果有多人评分记录，获取所有评分人的信息
    if (answer.markerScores && answer.markerScores.length > 0) {
      const markerIds = answer.markerScores.map(item => item.markerId);
      const markers = await db.user.findAll({
        where: { id: markerIds },
        attributes: ['id', 'username', 'email', 'role']
      });

      // 将评分人信息添加到评分记录中
      const markerScoresWithInfo = answer.markerScores.map(scoreRecord => {
        const markerInfo = markers.find(marker => marker.id === scoreRecord.markerId);
        return {
          ...scoreRecord,
          markerInfo: markerInfo || null
        };
      });

      // 将处理后的评分记录添加到响应中
      answer.setDataValue('markerScoresWithInfo', markerScoresWithInfo);
    }

    // 如果需要仲裁，获取仲裁信息
    if (answer.needArbitration && answer.arbitrationId) {
      const arbitration = await db.arbitration.findByPk(answer.arbitrationId, {
        include: [
          {
            model: db.user,
            as: 'arbitrator',
            attributes: ['id', 'username', 'email', 'role']
          },
          {
            model: db.user,
            as: 'requester',
            attributes: ['id', 'username', 'email', 'role']
          }
        ]
      });
      
      if (arbitration) {
        answer.setDataValue('arbitrationInfo', arbitration);
      }
    }

    res.status(200).send(answer);
  } catch (error) {
    res.status(500).send({
      message: error.message || "获取答案详情时发生错误"
    });
  }
};

// 评分操作
exports.markAnswer = async (req, res) => {
  try {
    const { id } = req.params;
    const { score, comments } = req.body;
    const markerId = req.userId; // 假设通过中间件获取当前用户ID

    // 验证分数
    if (score < 0) {
      return res.status(400).send({
        message: "分数不能为负数"
      });
    }

    const answer = await SubjectiveAnswer.findByPk(id, {
      include: [{
        model: ExamQuestion,
        as: 'examQuestion'
      }]
    });

    if (!answer) {
      return res.status(404).send({
        message: `未找到ID为${id}的答案`
      });
    }

    // 检查分数是否超过题目满分
    if (answer.examQuestion && score > answer.examQuestion.score) {
      return res.status(400).send({
        message: `分数不能超过题目满分${answer.examQuestion.score}`
      });
    }

    // 检查该评阅人是否已经评过分
    let markerScores = answer.markerScores || [];
    const existingScoreIndex = markerScores.findIndex(item => item.markerId === markerId);
    
    const newScoreRecord = {
      markerId,
      score,
      comments,
      markedAt: new Date()
    };

    // 如果已评过分，更新评分记录
    if (existingScoreIndex >= 0) {
      markerScores[existingScoreIndex] = newScoreRecord;
    } else {
      // 否则添加新的评分记录
      markerScores.push(newScoreRecord);
    }

    // 计算已评阅人数
    const markerCount = markerScores.length;
    
    // 计算评分的平均值和方差
    const scores = markerScores.map(item => parseFloat(item.score));
    const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    
    // 计算方差
    const scoreVariance = scores.length > 1 
      ? scores.reduce((sum, score) => sum + Math.pow(score - averageScore, 2), 0) / scores.length
      : 0;
    
    // 配置参数
    const varianceThreshold = process.env.SCORE_VARIANCE_THRESHOLD || 2.5; // 从环境变量获取或默认2.5
    const minMarkerCount = Math.max(2, answer.requiredMarkerCount || 3); // 至少需要2位评阅人
    
    // 判断是否需要仲裁（方差大于设定阈值）
    const needArbitration = scoreVariance > varianceThreshold;
    
    // 确定状态
    let status = answer.status;
    if (markerCount >= minMarkerCount) {
      status = needArbitration ? 'disputed' : 'marked';
    } else if (markerCount > 0) {
      status = 'marking';
    } else {
      status = 'pending'; // 无评阅人时保持待评状态
    }

    // 确保状态转换有效
    const validTransitions = {
      pending: ['marking'],
      marking: ['marked', 'disputed', 'marking'],
      marked: ['disputed'],
      disputed: ['arbitrated']
    };
    
    if (!validTransitions[answer.status]?.includes(status)) {
      status = answer.status; // 保持原状态如果转换无效
    }

    // 更新答案评分信息
    const updateData = {
      markerScores,
      markerCount,
      scoreVariance,
      needArbitration,
      status
    };
    
    // 如果评分完成且不需要仲裁，设置最终分数
    if (status === 'marked') {
      updateData.score = averageScore;
      updateData.markerId = markerId; // 最后一个评分的人作为主评阅人
      updateData.markedAt = new Date();
      updateData.comments = comments; // 最后一个评分的评语作为最终评语
    }

    await answer.update(updateData);

    res.status(200).send({
      message: markerCount >= answer.requiredMarkerCount 
        ? (needArbitration ? "评分完成，但需要仲裁" : "评分完成") 
        : `评分成功，当前已有 ${markerCount}/${answer.requiredMarkerCount} 位评阅人完成评分`,
      data: answer
    });
  } catch (error) {
    res.status(500).send({
      message: error.message || "评分操作时发生错误"
    });
  }
};

// 获取已评阅的答案列表
exports.getMarkedAnswers = async (req, res) => {
  try {
    const { examId } = req.params;
    const { page = 1, size = 10 } = req.query;
    const limit = parseInt(size);
    const offset = (parseInt(page) - 1) * limit;

    const answers = await SubjectiveAnswer.findAndCountAll({
      where: {
        status: 'marked',
        '$examQuestion.examId$': examId
      },
      include: [
        {
          model: ExamQuestion,
          as: 'examQuestion',
          attributes: ['id', 'questionContent', 'score']
        },
        {
          model: User,
          as: 'marker',
          attributes: ['id', 'username']
        }
      ],
      limit,
      offset,
      order: [['markedAt', 'DESC']]
    });

    res.status(200).send({
      total: answers.count,
      currentPage: parseInt(page),
      totalPages: Math.ceil(answers.count / limit),
      data: answers.rows
    });
  } catch (error) {
    res.status(500).send({
      message: error.message || "获取已评阅答案列表时发生错误"
    });
  }
};

// 提交争议/申请仲裁
exports.disputeAnswer = async (req, res) => {
  try {
    const { id } = req.params;
    const { reason } = req.body;
    
    if (!reason) {
      return res.status(400).send({
        message: "必须提供争议理由"
      });
    }

    const answer = await SubjectiveAnswer.findByPk(id);

    if (!answer) {
      return res.status(404).send({
        message: `未找到ID为${id}的答案`
      });
    }

    if (answer.status !== 'marked') {
      return res.status(400).send({
        message: "只有已评阅的答案才能提出争议"
      });
    }

    // 更新答案状态为有争议
    await answer.update({
      status: 'disputed',
      disputeReason: reason,
      disputedAt: new Date()
    });

    res.status(200).send({
      message: "争议提交成功",
      data: answer
    });
  } catch (error) {
    res.status(500).send({
      message: error.message || "提交争议时发生错误"
    });
  }
};