import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Checkbox
} from '@mui/material';
import { fetchUsers, deleteUser } from '../../services/userService';
import AddUserForm from './AddUserForm';
import EditUserForm from './EditUserForm';
import UserApproval from './UserApproval';
import UserImport from './UserImport';
import BatchApproval from './BatchApproval';
import { TextField, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isEditUserOpen, setIsEditUserOpen] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [isBatchApprovalOpen, setIsBatchApprovalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || 
                       (roleFilter === '考生' && (user.roleId === '1' || user.role === '1' || user.role === 'student')) ||
                       (roleFilter === '考评员' && (user.roleId === '2' || user.role === '2' || user.role === 'teacher')) ||
                       (roleFilter === '管理员' && (user.roleId === '3' || user.role === '3' || user.role === 'admin'));
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter;
    return matchesSearch && matchesRole && matchesStatus;
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const handleSelectAllUsers = (event) => {
    if (event.target.checked) {
      setSelectedUsers(filteredUsers.map(user => user.id));
    } else {
      setSelectedUsers([]);
    }
  };

  const handleAddUserSuccess = () => {
    loadUsers(); // 重新加载用户列表
    setIsAddUserOpen(false); // 关闭添加用户对话框
  };

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await fetchUsers();
      setUsers(data.users);  // 修改这里，使用 data.users 而不是直接使用 data
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectUser = (userId) => {
    setSelectedUsers(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleDeleteClick = async (userId) => {
    if (window.confirm('确定要删除这个用户吗？')) {
      try {
        await deleteUser(userId);
        loadUsers();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const handleEditClick = (user) => {
    setSelectedUser(user);
    setIsEditUserOpen(true);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2>用户管理</h2>
        <div>
          {selectedUsers.length > 0 && (
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => setIsBatchApprovalOpen(true)}
              style={{ marginRight: '8px' }}
            >
              批量审批 ({selectedUsers.length})
            </Button>
          )}
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => setIsImportOpen(true)}
            style={{ marginRight: '8px' }}
          >
            批量导入
          </Button>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => setIsAddUserOpen(true)}
          >
            添加用户
          </Button>
        </div>
      </div>

      <div style={{ marginBottom: '20px', display: 'flex', gap: '16px' }}>
        <TextField
          label="搜索用户"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FormControl size="small" style={{ minWidth: 120 }}>
          <InputLabel>角色</InputLabel>
          <Select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            label="角色"
          >
            <MenuItem value="all">全部</MenuItem>
            <MenuItem value="考生">考生</MenuItem>
            <MenuItem value="考评员">考评员</MenuItem>
            <MenuItem value="管理员">管理员</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" style={{ minWidth: 120 }}>
          <InputLabel>状态</InputLabel>
          <Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            label="状态"
          >
            <MenuItem value="all">全部</MenuItem>
            <MenuItem value="1">正常</MenuItem>
            <MenuItem value="2">待审核</MenuItem>
            <MenuItem value="3">已通过</MenuItem>
            <MenuItem value="4">已拒绝</MenuItem>
            <MenuItem value="5">冻结</MenuItem>
          </Select>
        </FormControl>
      </div>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  onChange={handleSelectAllUsers}
                  checked={selectedUsers.length > 0 && selectedUsers.length === users.length}
                  indeterminate={selectedUsers.length > 0 && selectedUsers.length < users.length}
                />
              </TableCell>
              <TableCell>用户名</TableCell>
              <TableCell>邮箱</TableCell>
              <TableCell>角色</TableCell>
              <TableCell>状态</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredUsers.map((user) => (
              <TableRow key={user.id}>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedUsers.includes(user.id)}
                    onChange={() => handleSelectUser(user.id)}
                  />
                </TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  {user.roleId === '1' || user.role === '1' || user.role === 'student' ? '考生' :
                   user.roleId === '2' || user.role === '2' || user.role === 'teacher' ? '考评员' :
                   user.roleId === '3' || user.role === '3' || user.role === 'admin' ? '管理员' : 
                   user.roleId || user.role}
                </TableCell>
                <TableCell>
                  {user.status === '1' ? '正常' :
                   user.status === '2' ? '待审核' :
                   user.status === '3' ? '已通过' :
                   user.status === '4' ? '已拒绝' :
                   user.status === '5' ? '冻结' : user.status}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => handleEditClick(user)}
                    style={{ marginRight: '8px' }}
                  >
                    编辑
                  </Button>
                  <Button
                    variant="outlined"
                    color="warning"
                    onClick={() => handleApprovalClick(user)}
                    style={{ marginRight: '8px' }}
                  >
                    审批
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => handleDeleteClick(user.id)}
                  >
                    删除
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <AddUserForm
        open={isAddUserOpen}
        onClose={() => setIsAddUserOpen(false)}
        onSuccess={handleAddUserSuccess}
      />
      
      <EditUserForm
        open={isEditUserOpen}
        onClose={() => setIsEditUserOpen(false)}
        onSuccess={() => {
          loadUsers();
          setIsEditUserOpen(false);
        }}
        user={selectedUser}
      />

      <UserApproval
        open={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        onSuccess={loadUsers}
        user={selectedUser}
      />

      <UserImport
        open={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        onSuccess={loadUsers}
      />

      <BatchApproval
        open={isBatchApprovalOpen}
        onClose={() => setIsBatchApprovalOpen(false)}
        onSuccess={() => {
          loadUsers();
          setSelectedUsers([]);
        }}
        userIds={selectedUsers}
      />
    </div>
  );
}

export default UserList;