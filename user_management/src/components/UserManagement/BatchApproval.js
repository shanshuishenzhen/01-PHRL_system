import React from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography
} from '@mui/material';
import { updateUser } from '../../services/userService';

function BatchApproval({ open, onClose, userIds, onSuccess }) {
  const handleBatchApprove = async () => {
    try {
      await Promise.all(userIds.map(id => updateUser(id, { status: '3' })));
      onSuccess();
      onClose();
    } catch (error) {
      console.error('批量审批失败:', error);
    }
  };

  const handleBatchReject = async () => {
    try {
      await Promise.all(userIds.map(id => updateUser(id, { status: '4' })));
      onSuccess();
      onClose();
    } catch (error) {
      console.error('批量拒绝失败:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>批量审批用户</DialogTitle>
      <DialogContent>
        <Typography>
          您已选择 {userIds.length} 个用户进行批量审批，请选择审批操作：
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={handleBatchReject} color="error" variant="outlined">
          全部拒绝
        </Button>
        <Button onClick={handleBatchApprove} color="success" variant="contained">
          全部通过
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default BatchApproval;