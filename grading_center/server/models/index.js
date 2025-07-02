const sequelize = require('./db');
const { Sequelize, DataTypes } = require('sequelize');

// 初始化 db 对象
const db = {};
db.sequelize = sequelize;
db.Sequelize = Sequelize;

// 导入模型
db.user = require('./user.model')(sequelize, Sequelize);
db.exam = require('./exam.model')(sequelize, Sequelize);
db.examQuestion = require('./examQuestion.model')(sequelize, Sequelize);
db.examParticipant = require('./examParticipant.model')(sequelize, Sequelize);
db.examPaper = require('./examPaper.model')(sequelize, Sequelize);
db.subjectiveAnswer = require('./subjectiveAnswer.model')(sequelize, Sequelize);
db.markingTask = require('./markingTask.model')(sequelize, Sequelize);
db.arbitration = require('./arbitration.model')(sequelize, Sequelize);

// 定义模型关联关系
db.exam.hasMany(db.examQuestion, { foreignKey: 'examId', as: 'questions' });
db.examQuestion.belongsTo(db.exam, { foreignKey: 'examId', as: 'exam' });

db.exam.hasMany(db.examParticipant, { foreignKey: 'examId', as: 'participants' });
db.examParticipant.belongsTo(db.exam, { foreignKey: 'examId', as: 'exam' });

db.user.hasMany(db.examParticipant, { foreignKey: 'userId', as: 'examParticipations' });
db.examParticipant.belongsTo(db.user, { foreignKey: 'userId', as: 'user' });

db.exam.hasMany(db.examPaper, { foreignKey: 'examId', as: 'papers' });
db.examPaper.belongsTo(db.exam, { foreignKey: 'examId', as: 'exam' });

db.user.hasMany(db.examPaper, { foreignKey: 'studentId', as: 'examPapers' });
db.examPaper.belongsTo(db.user, { foreignKey: 'studentId', as: 'student' });

db.examQuestion.hasMany(db.subjectiveAnswer, { foreignKey: 'questionId', as: 'answers' });
db.subjectiveAnswer.belongsTo(db.examQuestion, { foreignKey: 'questionId', as: 'question' });

// 阅卷任务关联
db.user.hasMany(db.markingTask, { foreignKey: 'markerId' });
db.markingTask.belongsTo(db.user, { foreignKey: 'markerId' });
db.exam.hasMany(db.markingTask, { foreignKey: 'examId' });
db.markingTask.belongsTo(db.exam, { foreignKey: 'examId' });

// 仲裁关联
db.subjectiveAnswer.hasMany(db.arbitration, { foreignKey: 'answerId' });
db.arbitration.belongsTo(db.subjectiveAnswer, { foreignKey: 'answerId' });
db.user.hasMany(db.arbitration, { foreignKey: 'requesterId', as: 'requester' });
db.arbitration.belongsTo(db.user, { foreignKey: 'requesterId', as: 'requester' });
db.user.hasMany(db.arbitration, { foreignKey: 'arbitratorId', as: 'arbitrator' });
db.arbitration.belongsTo(db.user, { foreignKey: 'arbitratorId', as: 'arbitrator' });

// 主观题答案与考试题目的关联 - 已在上面定义，这里不再重复
// db.examQuestion.hasMany(db.subjectiveAnswer, { as: "answers", foreignKey: "questionId" });
db.subjectiveAnswer.belongsTo(db.examQuestion, { as: "examQuestion", foreignKey: "questionId" });

// 主观题答案与评阅人的关联
db.user.hasMany(db.subjectiveAnswer, { as: "markedAnswers", foreignKey: "markerId" });
db.subjectiveAnswer.belongsTo(db.user, { as: "marker", foreignKey: "markerId" });

// 主观题答案与考试参与者的关联
db.examParticipant.hasMany(db.subjectiveAnswer, { as: "participantAnswers", foreignKey: "participantId" });
db.subjectiveAnswer.belongsTo(db.examParticipant, { as: "participant", foreignKey: "participantId" });

module.exports = db;