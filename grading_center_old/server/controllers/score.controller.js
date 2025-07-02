const db = require('../models');
const Exam = db.exam;
const ExamParticipant = db.examParticipant;
const User = db.user;
const { Op } = require('sequelize');
const fs = require('fs');
const path = require('path');

// 导出成绩数据
exports.exportScores = async (req, res) => {
  try {
    const { examId, format = 'json' } = req.query;
    
    // 构建查询条件
    const whereClause = {};
    if (examId) {
      whereClause.examId = examId;
    }
    
    // 查询成绩数据
    const participants = await ExamParticipant.findAll({
      where: whereClause,
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'realName', 'department']
        },
        {
          model: Exam,
          as: 'exam',
          attributes: ['id', 'examName', 'totalScore']
        }
      ]
    });
    
    // 格式化成绩数据
    const formattedScores = participants.map(participant => {
      const data = participant.toJSON();
      return {
        id: data.id,
        exam_id: data.examId,
        exam_name: data.exam ? data.exam.examName : '',
        student_id: data.userId,
        student_name: data.user ? data.user.realName : '',
        department: data.user ? data.user.department : '',
        score: data.score || 0,
        total_score: data.exam ? data.exam.totalScore : 100,
        percentage: data.score && data.exam ? (data.score / data.exam.totalScore * 100) : 0,
        status: data.status,
        submit_time: data.endTime ? new Date(data.endTime).toISOString() : ''
      };
    });
    
    // 根据请求的格式返回数据
    if (format === 'json') {
      // 将数据保存到文件
      const exportDir = path.join(__dirname, '../../exports');
      
      // 确保导出目录存在
      if (!fs.existsSync(exportDir)) {
        fs.mkdirSync(exportDir, { recursive: true });
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `scores_${timestamp}.json`;
      const filepath = path.join(exportDir, filename);
      
      // 写入文件
      fs.writeFileSync(filepath, JSON.stringify({
        scores: formattedScores,
        exportTime: new Date().toISOString(),
        totalCount: formattedScores.length
      }, null, 2));
      
      // 将文件路径保存到成绩统计模块的导入目录
      const scoreStatsDir = path.join(__dirname, '../../../score_statistics/imports');
      
      // 确保导入目录存在
      if (!fs.existsSync(scoreStatsDir)) {
        fs.mkdirSync(scoreStatsDir, { recursive: true });
      }
      
      const scoreStatsFilepath = path.join(scoreStatsDir, filename);
      fs.copyFileSync(filepath, scoreStatsFilepath);
      
      res.json({
        success: true,
        message: '成绩数据导出成功',
        data: {
          filepath: filepath,
          scoreStatsFilepath: scoreStatsFilepath,
          count: formattedScores.length
        }
      });
    } else if (format === 'csv') {
      // CSV格式导出逻辑
      const exportDir = path.join(__dirname, '../../exports');
      
      // 确保导出目录存在
      if (!fs.existsSync(exportDir)) {
        fs.mkdirSync(exportDir, { recursive: true });
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `scores_${timestamp}.csv`;
      const filepath = path.join(exportDir, filename);
      
      // 创建CSV内容
      const headers = 'ID,考试ID,考试名称,学生ID,学生姓名,部门,成绩,总分,百分比,状态,提交时间\n';
      const rows = formattedScores.map(score => {
        return `${score.id},${score.exam_id},"${score.exam_name}",${score.student_id},"${score.student_name}","${score.department}",${score.score},${score.total_score},${score.percentage.toFixed(2)},"${score.status}","${score.submit_time}"`;
      }).join('\n');
      
      // 写入文件
      fs.writeFileSync(filepath, headers + rows);
      
      // 将文件路径保存到成绩统计模块的导入目录
      const scoreStatsDir = path.join(__dirname, '../../../score_statistics/imports');
      
      // 确保导入目录存在
      if (!fs.existsSync(scoreStatsDir)) {
        fs.mkdirSync(scoreStatsDir, { recursive: true });
      }
      
      const scoreStatsFilepath = path.join(scoreStatsDir, filename);
      fs.copyFileSync(filepath, scoreStatsFilepath);
      
      res.json({
        success: true,
        message: '成绩数据导出成功',
        data: {
          filepath: filepath,
          scoreStatsFilepath: scoreStatsFilepath,
          count: formattedScores.length
        }
      });
    } else {
      res.status(400).json({
        success: false,
        message: '不支持的导出格式'
      });
    }
  } catch (error) {
    console.error('导出成绩数据失败:', error);
    res.status(500).json({
      success: false,
      message: '导出成绩数据失败',
      error: error.message
    });
  }
};

// 获取所有成绩数据
exports.getAllScores = async (req, res) => {
  try {
    const participants = await ExamParticipant.findAll({
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'realName', 'department']
        },
        {
          model: Exam,
          as: 'exam',
          attributes: ['id', 'examName', 'totalScore']
        }
      ]
    });
    
    // 格式化成绩数据
    const formattedScores = participants.map(participant => {
      const data = participant.toJSON();
      return {
        id: data.id,
        exam_id: data.examId,
        exam_name: data.exam ? data.exam.examName : '',
        student_id: data.userId,
        student_name: data.user ? data.user.realName : '',
        department: data.user ? data.user.department : '',
        score: data.score || 0,
        total_score: data.exam ? data.exam.totalScore : 100,
        percentage: data.score && data.exam ? (data.score / data.exam.totalScore * 100) : 0,
        status: data.status,
        submit_time: data.endTime ? new Date(data.endTime).toISOString() : ''
      };
    });
    
    res.json({
      success: true,
      data: formattedScores
    });
  } catch (error) {
    console.error('获取成绩数据失败:', error);
    res.status(500).json({
      success: false,
      message: '获取成绩数据失败',
      error: error.message
    });
  }
};

// 按考试ID获取成绩数据
exports.getScoresByExam = async (req, res) => {
  try {
    const { examId } = req.params;
    
    const participants = await ExamParticipant.findAll({
      where: { examId },
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'realName', 'department']
        },
        {
          model: Exam,
          as: 'exam',
          attributes: ['id', 'examName', 'totalScore']
        }
      ]
    });
    
    // 格式化成绩数据
    const formattedScores = participants.map(participant => {
      const data = participant.toJSON();
      return {
        id: data.id,
        exam_id: data.examId,
        exam_name: data.exam ? data.exam.examName : '',
        student_id: data.userId,
        student_name: data.user ? data.user.realName : '',
        department: data.user ? data.user.department : '',
        score: data.score || 0,
        total_score: data.exam ? data.exam.totalScore : 100,
        percentage: data.score && data.exam ? (data.score / data.exam.totalScore * 100) : 0,
        status: data.status,
        submit_time: data.endTime ? new Date(data.endTime).toISOString() : ''
      };
    });
    
    res.json({
      success: true,
      data: formattedScores
    });
  } catch (error) {
    console.error('获取考试成绩数据失败:', error);
    res.status(500).json({
      success: false,
      message: '获取考试成绩数据失败',
      error: error.message
    });
  }
};

// 按学生ID获取成绩数据
exports.getScoresByStudent = async (req, res) => {
  try {
    const { studentId } = req.params;
    
    const participants = await ExamParticipant.findAll({
      where: { userId: studentId },
      include: [
        {
          model: User,
          as: 'user',
          attributes: ['id', 'username', 'realName', 'department']
        },
        {
          model: Exam,
          as: 'exam',
          attributes: ['id', 'examName', 'totalScore']
        }
      ]
    });
    
    // 格式化成绩数据
    const formattedScores = participants.map(participant => {
      const data = participant.toJSON();
      return {
        id: data.id,
        exam_id: data.examId,
        exam_name: data.exam ? data.exam.examName : '',
        student_id: data.userId,
        student_name: data.user ? data.user.realName : '',
        department: data.user ? data.user.department : '',
        score: data.score || 0,
        total_score: data.exam ? data.exam.totalScore : 100,
        percentage: data.score && data.exam ? (data.score / data.exam.totalScore * 100) : 0,
        status: data.status,
        submit_time: data.endTime ? new Date(data.endTime).toISOString() : ''
      };
    });
    
    res.json({
      success: true,
      data: formattedScores
    });
  } catch (error) {
    console.error('获取学生成绩数据失败:', error);
    res.status(500).json({
      success: false,
      message: '获取学生成绩数据失败',
      error: error.message
    });
  }
};

// 按部门获取成绩数据
exports.getScoresByDepartment = async (req, res) => {
  try {
    const { department } = req.params;
    
    const participants = await ExamParticipant.findAll({
      include: [
        {
          model: User,
          as: 'user',
          where: { department },
          attributes: ['id', 'username', 'realName', 'department']
        },
        {
          model: Exam,
          as: 'exam',
          attributes: ['id', 'examName', 'totalScore']
        }
      ]
    });
    
    // 格式化成绩数据
    const formattedScores = participants.map(participant => {
      const data = participant.toJSON();
      return {
        id: data.id,
        exam_id: data.examId,
        exam_name: data.exam ? data.exam.examName : '',
        student_id: data.userId,
        student_name: data.user ? data.user.realName : '',
        department: data.user ? data.user.department : '',
        score: data.score || 0,
        total_score: data.exam ? data.exam.totalScore : 100,
        percentage: data.score && data.exam ? (data.score / data.exam.totalScore * 100) : 0,
        status: data.status,
        submit_time: data.endTime ? new Date(data.endTime).toISOString() : ''
      };
    });
    
    res.json({
      success: true,
      data: formattedScores
    });
  } catch (error) {
    console.error('获取部门成绩数据失败:', error);
    res.status(500).json({
      success: false,
      message: '获取部门成绩数据失败',
      error: error.message
    });
  }
};