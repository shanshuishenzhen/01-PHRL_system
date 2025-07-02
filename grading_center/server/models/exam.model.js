module.exports = (sequelize, Sequelize) => {
  const Exam = sequelize.define("exam", {
    id: {
      type: Sequelize.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    examName: {
      type: Sequelize.STRING(100),
      allowNull: false,
      comment: '考试名称'
    },
    examCode: {
      type: Sequelize.STRING(20),
      allowNull: false,
      unique: true,
      comment: '考试代码'
    },
    description: {
      type: Sequelize.TEXT,
      allowNull: true,
      comment: '考试描述'
    },
    startTime: {
      type: Sequelize.DATE,
      allowNull: false,
      comment: '考试开始时间'
    },
    endTime: {
      type: Sequelize.DATE,
      allowNull: false,
      comment: '考试结束时间'
    },
    duration: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '考试时长（分钟）'
    },
    totalScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: false,
      comment: '总分'
    },
    passingScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: false,
      comment: '及格分数'
    },
    status: {
      type: Sequelize.ENUM('draft', 'published', 'in_progress', 'completed', 'archived'),
      defaultValue: 'draft',
      comment: '考试状态：草稿、已发布、进行中、已完成、已归档'
    },
    creatorId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '创建者ID'
    },
    isRandomOrder: {
      type: Sequelize.BOOLEAN,
      defaultValue: false,
      comment: '是否随机顺序'
    },
    allowReview: {
      type: Sequelize.BOOLEAN,
      defaultValue: true,
      comment: '是否允许复查'
    },
    showResult: {
      type: Sequelize.BOOLEAN,
      defaultValue: true,
      comment: '是否显示结果'
    },
    showAnalysis: {
      type: Sequelize.BOOLEAN,
      defaultValue: true,
      comment: '是否显示解析'
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
    tableName: 'exams',
    timestamps: true,
    comment: '考试信息表'
  });

  return Exam;
};