module.exports = {
  dialect: "sqlite",
  storage: "./database.sqlite", // SQLite 数据库文件路径
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
  // 以下配置仅在使用 MySQL 时需要
  HOST: "localhost",
  USER: "root",
  PASSWORD: "123456",
  DB: "marking_center_db",
  port: 3306
};