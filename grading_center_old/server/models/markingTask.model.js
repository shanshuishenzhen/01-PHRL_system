module.exports = (sequelize, Sequelize) => {
  const MarkingTask = sequelize.define("marking_task", {
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
    markerId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '评阅人ID'
    },
    questionIds: {
      type: Sequelize.JSON,
      allowNull: true,
      comment: '负责评阅的题目ID列表'
    },
    participantIds: {
      type: Sequelize.JSON,
      allowNull: true,
      comment: '负责评阅的考生ID列表'
    },
    status: {
      type: Sequelize.ENUM('pending', 'in_progress', 'completed'),
      defaultValue: 'pending',
      comment: '任务状态：待处理、进行中、已完成'
    },
    startTime: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '开始评阅时间'
    },
    endTime: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '结束评阅时间'
    },
    progress: {
      type: Sequelize.FLOAT,
      defaultValue: 0,
      comment: '评阅进度百分比'
    },
    priority: {
      type: Sequelize.INTEGER,
      defaultValue: 1,
      comment: '任务优先级'
    }
  }, {
    timestamps: true,
    underscored: false,
    tableName: 'marking_tasks'
  });

  return MarkingTask;
};