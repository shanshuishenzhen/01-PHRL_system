module.exports = (sequelize, Sequelize) => {
  const SubjectiveAnswer = sequelize.define("subjective_answer", {
    id: {
      type: Sequelize.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    participantId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '参与者ID'
    },
    questionId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '题目ID'
    },
    answerText: {
      type: Sequelize.TEXT,
      allowNull: true,
      comment: '答案文本'
    },
    score: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '最终得分'
    },
    markerId: {
      type: Sequelize.INTEGER,
      allowNull: true,
      comment: '主评阅人ID'
    },
    markedAt: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '评阅时间'
    },
    status: {
      type: Sequelize.ENUM('pending', 'marking', 'marked', 'disputed', 'arbitrated'),
      defaultValue: 'pending',
      comment: '状态：待评阅、评阅中、已评阅、有争议、已仲裁'
    },
    comments: {
      type: Sequelize.TEXT,
      allowNull: true,
      comment: '评阅意见'
    },
    // 多人评分相关字段
    markerScores: {
      type: Sequelize.JSON,
      allowNull: true,
      comment: '多位评阅人的评分记录，格式：[{markerId, score, comments, markedAt}]'
    },
    markerCount: {
      type: Sequelize.INTEGER,
      defaultValue: 0,
      comment: '已评阅的评阅人数量'
    },
    requiredMarkerCount: {
      type: Sequelize.INTEGER,
      defaultValue: 3,
      comment: '需要的评阅人数量，默认为3'
    },
    scoreVariance: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '评分方差，用于检测评分一致性'
    },
    needArbitration: {
      type: Sequelize.BOOLEAN,
      defaultValue: false,
      comment: '是否需要仲裁（评分差异过大时）'
    },
    arbitrationId: {
      type: Sequelize.INTEGER,
      allowNull: true,
      comment: '关联的仲裁记录ID'
    }
  }, {
    timestamps: true,
    underscored: false,
    tableName: 'subjective_answers'
  });

  return SubjectiveAnswer;
};