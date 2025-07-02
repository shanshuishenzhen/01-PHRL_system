const express = require('express');
const router = express.Router();

// 定义一个简单的 GET 接口
router.get('/hello', (req, res) => {
  res.json({ message: 'Hello from the backend API!' });
});

module.exports = router;