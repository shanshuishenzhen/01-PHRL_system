const db = require('../models');
const User = db.user;
const bcrypt = require('bcrypt');

// 创建新用户
exports.createUser = async (req, res) => {
  try {
    const { username, password, fullName, role, email } = req.body;

    // 基本验证
    if (!username || !password) {
      return res.status(400).json({ message: '用户名和密码不能为空' });
    }

    // 检查用户名是否已存在
    const existingUser = await User.findOne({ where: { username } });
    if (existingUser) {
      return res.status(400).json({ message: '用户名已存在' });
    }

    // 密码加密
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // 创建用户
    const user = await User.create({
      username,
      password: hashedPassword,
      fullName: fullName || username,
      role: role || 'student',
      email: email || null
    });

    // 返回用户信息（不包含密码）
    res.status(201).json({
      message: '用户创建成功',
      user: {
        id: user.id,
        username: user.username,
        fullName: user.fullName,
        role: user.role,
        email: user.email
      }
    });
  } catch (error) {
    console.error('创建用户失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 获取所有用户
exports.getAllUsers = async (req, res) => {
  try {
    const users = await User.findAll({
      attributes: { exclude: ['password'] } // 排除密码字段
    });
    res.status(200).json(users);
  } catch (error) {
    console.error('获取用户列表失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 获取单个用户
exports.getUserById = async (req, res) => {
  try {
    const userId = req.params.id;
    const user = await User.findByPk(userId, {
      attributes: { exclude: ['password'] } // 排除密码字段
    });

    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    res.status(200).json(user);
  } catch (error) {
    console.error('获取用户信息失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 更新用户
exports.updateUser = async (req, res) => {
  try {
    const userId = req.params.id;
    const { username, password, fullName, role, email } = req.body;

    // 查找用户
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    // 如果更新用户名，检查是否已存在
    if (username && username !== user.username) {
      const existingUser = await User.findOne({ where: { username } });
      if (existingUser) {
        return res.status(400).json({ message: '用户名已存在' });
      }
      user.username = username;
    }

    // 如果更新密码，进行加密
    if (password) {
      const saltRounds = 10;
      user.password = await bcrypt.hash(password, saltRounds);
    }

    // 更新其他字段
    if (fullName) user.fullName = fullName;
    if (role) user.role = role;
    if (email) user.email = email;

    // 保存更新
    await user.save();

    // 返回更新后的用户信息（不包含密码）
    res.status(200).json({
      message: '用户更新成功',
      user: {
        id: user.id,
        username: user.username,
        fullName: user.fullName,
        role: user.role,
        email: user.email
      }
    });
  } catch (error) {
    console.error('更新用户失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 删除用户
exports.deleteUser = async (req, res) => {
  try {
    const userId = req.params.id;

    // 查找用户
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    // 删除用户
    await user.destroy();

    res.status(200).json({ message: '用户删除成功' });
  } catch (error) {
    console.error('删除用户失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};

// 修改用户密码
exports.changePassword = async (req, res) => {
  try {
    const userId = req.params.id;
    const { currentPassword, newPassword } = req.body;

    // 基本验证
    if (!currentPassword || !newPassword) {
      return res.status(400).json({ message: '当前密码和新密码不能为空' });
    }

    // 查找用户
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ message: '用户不存在' });
    }

    // 验证当前密码
    const passwordMatch = await bcrypt.compare(currentPassword, user.password);
    if (!passwordMatch) {
      return res.status(401).json({ message: '当前密码错误' });
    }

    // 加密新密码
    const saltRounds = 10;
    user.password = await bcrypt.hash(newPassword, saltRounds);

    // 保存更新
    await user.save();

    res.status(200).json({ message: '密码修改成功' });
  } catch (error) {
    console.error('修改密码失败:', error);
    res.status(500).json({ message: '服务器错误' });
  }
};