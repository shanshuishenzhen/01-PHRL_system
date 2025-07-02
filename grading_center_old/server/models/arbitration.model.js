module.exports = (sequelize, Sequelize) => {
  const Arbitration = sequelize.define("arbitration", {
    id: {
      type: Sequelize.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    answerId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '主观题答案ID'
    },
    requesterId: {
      type: Sequelize.INTEGER,
      allowNull: false,
      comment: '申请人ID'
    },
    arbitratorId: {
      type: Sequelize.INTEGER,
      allowNull: true,
      comment: '仲裁人ID'
    },
    reason: {
      type: Sequelize.TEXT,
      allowNull: false,
      comment: '申请原因'
    },
    originalScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '原始分数'
    },
    adjustedScore: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: true,
      comment: '调整后分数'
    },
    status: {
      type: Sequelize.ENUM('pending', 'in_review', 'approved', 'rejected'),
      defaultValue: 'pending',
      comment: '状态：待处理、审核中、已批准、已拒绝'
    },
    resolution: {
      type: Sequelize.TEXT,
      allowNull: true,
      comment: '处理结果说明'
    },
    resolvedAt: {
      type: Sequelize.DATE,
      allowNull: true,
      comment: '处理时间'
    }
  }, {
    timestamps: true,
    underscored: false,
    tableName: 'arbitrations'
  });

  return Arbitration;
};