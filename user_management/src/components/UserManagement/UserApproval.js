import React from 'react';
import {
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { updateUser } from '../../services/userService';

function UserApproval({ open, onClose, user, onSuccess }) {
  const handleApprove = async () => {
    try {
      await updateUser(user.id, { status: '3' });  // 已通过
      onSuccess();
      onClose();
    } catch (error) {
      console.error('审批用户失败:', error);
    }
  };

  const handleReject = async () => {
    try {
      await updateUser(user.id, { status: '4' });  // 已拒绝
      onSuccess();
      onClose();
    } catch (error) {
      console.error('拒绝用户失败:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>用户审批</DialogTitle>
      <DialogContent>
        <div>
          <p><strong>用户名：</strong> {user?.username}</p>
          <p><strong>邮箱：</strong> {user?.email}</p>
          <p><strong>角色：</strong> {user?.role}</p>
          <p><strong>当前状态：</strong> 
            <Chip 
              label={user?.status === '2' ? '待审核' : 
                     user?.status === '3' ? '已通过' : 
                     user?.status === '4' ? '已拒绝' :
                     user?.status === '5' ? '冻结' : '正常'}
              color={user?.status === '3' ? 'success' : 
                     user?.status === '4' ? 'error' : 
                     user?.status === '5' ? 'error' : 'warning'}
            />
          </p>
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={handleReject} color="error" variant="outlined">
          拒绝
        </Button>
        <Button onClick={handleApprove} color="success" variant="contained">
          通过
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default UserApproval;