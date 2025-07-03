// d:\Documents\Python_Project\02-Trae_system\Trae_OLE_05\server\models\db.js
const { Sequelize } = require('sequelize');
const dbConfig = require('../config/db.config.js');

// 使用 Sequelize 创建一个新的数据库连接实例
let sequelize;

if (dbConfig.dialect === 'sqlite') {
  sequelize = new Sequelize({
    dialect: dbConfig.dialect,
    storage: dbConfig.storage,
    pool: {
      max: dbConfig.pool.max,
      min: dbConfig.pool.min,
      acquire: dbConfig.pool.acquire,
      idle: dbConfig.pool.idle
    },
    // 禁用SQL查询日志以提高性能
    logging: false
  });
} else {
  sequelize = new Sequelize(
    dbConfig.DB,
    dbConfig.USER,
    dbConfig.PASSWORD,
    {
      host: dbConfig.HOST,
      dialect: dbConfig.dialect,
      port: dbConfig.port,
      pool: {
        max: dbConfig.pool.max,
        min: dbConfig.pool.min,
        acquire: dbConfig.pool.acquire,
        idle: dbConfig.pool.idle
      },
      // 禁用SQL查询日志以提高性能
      logging: false
    }
  );
}

// 测试连接
sequelize.authenticate()
  .then(() => {
    console.log('✅ Successfully connected to the database via Sequelize.');
  })
  .catch(err => {
    console.error('❌ Unable to connect to the database:', err);
  });

const db = {};
db.Sequelize = Sequelize;
db.sequelize = sequelize;

// 在这里可以引入模型，但在模型的 index.js 中处理更常见
// e.g., db.exams = require("./exam.model.js")(sequelize, Sequelize);

module.exports = sequelize; // 直接导出 sequelize 实例