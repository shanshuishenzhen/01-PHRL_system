module.exports = (sequelize, Sequelize) => {
  const User = sequelize.define("user", {
    id: {
      type: Sequelize.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    username: {
      type: Sequelize.STRING,
      allowNull: false,
      unique: true
    },
    password: {
      type: Sequelize.STRING,
      allowNull: false
    },
    fullName: {
      type: Sequelize.STRING,
      allowNull: false
    },
    role: {
      type: Sequelize.ENUM('student', 'teacher', 'admin'),
      defaultValue: 'student'
    },
    email: {
      type: Sequelize.STRING,
      validate: {
        isEmail: true
      }
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
    tableName: 'users',
    timestamps: true
  });

  return User;
};