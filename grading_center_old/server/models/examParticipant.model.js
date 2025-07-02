module.exports = (sequelize, Sequelize) => {
  const ExamParticipant = sequelize.define("exam_participant", {
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
    userId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '用户ID'
    },
    status: {
      type: Sequelize.ENUM('invited', 'confirmed', 'completed', 'absent'),
      defaultValue: 'invited',
      comment: '参与状态：已邀请、已确认、已完成、缺席'
    },
    startTime: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '开始考试时间'
    },
    endTime: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '结束考试时间'
    },
    score: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '得分'
    },
    ipAddress: {
      type: Sequelize.STRING,
      allowNull: true,
      comment: 'IP地址'
    },
    deviceInfo: {
      type: Sequelize.STRING,
      allowNull: true,
      comment: '设备信息'
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
    tableName: 'exam_participants',
    timestamps: true,
    comment: '考试参与者表'
  });

  return ExamParticipant;
};