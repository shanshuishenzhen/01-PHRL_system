import { useEffect, useState } from 'react';
import { fetchUsers } from '../../services/userService';

export default function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await fetchUsers();
        setUsers(data);
      } catch (error) {
        console.error('加载用户列表失败:', error);
      }
    };
    loadUsers();
  }, []);

  return (
    <div className="user-list">
      {/* 表格实现 */}
    </div>
  );
}