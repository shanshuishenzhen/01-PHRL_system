module.exports = (sequelize, Sequelize) => {
  const ExamPaper = sequelize.define("exam_paper", {
    id: {
      type: Sequelize.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    examId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '考试ID'
    },
    studentId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '学生ID'
    },
    totalScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '总分'
    },
    objectiveScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '客观题得分'
    },
    subjectiveScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '主观题得分'
    },
    status: {
      type: Sequelize.ENUM('submitted', 'grading', 'completed'),
      defaultValue: 'submitted',
      comment: '试卷状态：已提交、评分中、已完成'
    },
    submissionTime: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '提交时间'
    },
    completionTime: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '完成评分时间'
    },
    answers: {
      type: Sequelize.JSON,
      allowNull: true,
      comment: '答案JSON'
    },
    createdAt: {
      type: Sequelize.DATE,
      defaultValue: Sequelize.NOW
    },
    updatedAt: {
      type: Sequelize.DATE,
      defaultValue: Sequelize.NOW
    }
  }, {
    tableName: 'exam_papers',
    timestamps: true
  });

  return ExamPaper;
};