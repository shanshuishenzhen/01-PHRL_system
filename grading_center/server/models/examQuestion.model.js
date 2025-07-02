module.exports = (sequelize, Sequelize) => {
  const ExamQuestion = sequelize.define("exam_question", {
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
    questionType: {
      type: Sequelize.ENUM('single', 'multiple', 'true_false', 'fill_blank', 'essay'),
      allowNull: false,
      comment: '题目类型：单选、多选、判断、填空、简答'
    },
    questionContent: {
      type: Sequelize.TEXT,
      allowNull: false,
      comment: '题目内容'
    },
    options: {
      type: Sequelize.JSON,
      allowNull: true,
      comment: '选项（JSON格式）'
    },
    correctAnswer: {
      type: Sequelize.TEXT,
      allowNull: true,
      comment: '正确答案'
    },
    score: {
      type: Sequelize.DECIMAL(5, 2),
      allowNull: false,
      comment: '分值'
    },
    difficulty: {
      type: Sequelize.ENUM('easy', 'medium', 'hard'),
      defaultValue: 'medium',
      comment: '难度：简单、中等、困难'
    },
    analysis: {
      type: Sequelize.TEXT,
      allowNull: true,
      comment: '解析'
    },
    orderNum: {
      type: Sequelize.INTEGER,
      allowNull: false,
      defaultValue: 0,
      comment: '题目顺序'
    },
    isSubjective: {
      type: Sequelize.BOOLEAN,
      allowNull: false,
      defaultValue: false,
      comment: '是否主观题'
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
    tableName: 'exam_questions',
    timestamps: true
  });

  return ExamQuestion;
};