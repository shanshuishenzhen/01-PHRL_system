import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { createUser } from '../../services/userService';

function AddUserForm({ open, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: '1',  // 修改默认角色为考生的roleId
    password: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createUser(formData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('添加用户失败:', error);
      // TODO: 添加错误提示
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>添加新用户</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="username"
            label="用户名"
            type="text"
            fullWidth
            value={formData.username}
            onChange={handleChange}
            required
          />
          <TextField
            margin="dense"
            name="email"
            label="邮箱"
            type="email"
            fullWidth
            value={formData.email}
            onChange={handleChange}
            required
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>角色</InputLabel>
            <Select
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
            >
              <MenuItem value="1">考生</MenuItem>
              <MenuItem value="2">考评员</MenuItem>
              <MenuItem value="3">管理员</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            name="password"
            label="密码"
            type="password"
            fullWidth
            value={formData.password}
            onChange={handleChange}
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>取消</Button>
          <Button type="submit" variant="contained" color="primary">
            添加
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default AddUserForm;