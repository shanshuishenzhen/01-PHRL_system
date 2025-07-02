import axios from 'axios';

// 配置axios默认设置
axios.defaults.baseURL = 'http://localhost:3001';

export const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/users');
    return response.data;
  } catch (error) {
    handleServiceError(error, '获取用户列表失败');
  }
};

export const updateUser = async (userId, data) => {
  try {
    const response = await axios.put(`/api/users/${userId}`, data);
    return response.data;
  } catch (error) {
    handleServiceError(error, '更新用户失败');
  }
};

export const createUser = async (userData) => {
  try {
    const response = await axios.post('/api/users', userData);
    return response.data;
  } catch (error) {
    handleServiceError(error, '创建用户失败');
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await axios.delete(`/api/users/${userId}`);
    return response.data;
  } catch (error) {
    handleServiceError(error, '删除用户失败');
  }
};

export const importUsers = async (formData) => {
  try {
    const response = await axios.post('/api/users/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    handleServiceError(error, '导入用户失败');
  }
};

export const batchUpdateUserStatus = async (userIds, status) => {
  try {
    const response = await axios.put('/api/users/batch/status', { userIds, status });
    return response.data;
  } catch (error) {
    handleServiceError(error, '批量更新用户状态失败');
  }
};

const handleServiceError = (error, defaultMsg) => {
  console.error('API Error:', error.response?.data);
  throw new Error(error.response?.data?.message || defaultMsg);
};

