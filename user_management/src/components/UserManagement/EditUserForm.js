import React, { useState, useEffect } from 'react';
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
import { updateUser } from '../../services/userService';

function EditUserForm({ open, onClose, onSuccess, user }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    role: '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username,
        email: user.email,
        role: user.role,
      });
    }
  }, [user]);

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
      await updateUser(user.id, formData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('更新用户失败:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>编辑用户</DialogTitle>
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
              <MenuItem value="student">考生</MenuItem>
              <MenuItem value="teacher">考评员</MenuItem>
              <MenuItem value="admin">管理员</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>取消</Button>
          <Button type="submit" variant="contained" color="primary">
            保存
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default EditUserForm;