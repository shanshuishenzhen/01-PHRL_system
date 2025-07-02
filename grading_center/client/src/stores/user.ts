import { defineStore } from 'pinia';
import type { UserData } from '../api/auth';

interface UserState {
  id: number | null;
  username: string;
  fullName: string;
  role: string;
  email: string;
  isLoggedIn: boolean;
  token: string;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    id: null,
    username: '',
    fullName: '',
    role: '',
    email: '',
    isLoggedIn: false,
    token: '',
  }),
  getters: {
    isAdmin: (state) => state.role === 'admin',
    isTeacher: (state) => state.role === 'examiner', // 考评员
    isStudent: (state) => state.role === 'student', // 考生
  },
  // 使用localStorage手动实现持久化
  actions: {
    setUser(userData: UserData, token?: string) {
      this.id = userData.id;
      this.username = userData.username;
      this.fullName = userData.fullName;
      this.role = userData.role;
      this.email = userData.email;
      this.isLoggedIn = true;
      if (token) this.token = token;
      
      // 保存到localStorage
      localStorage.setItem('user-store', JSON.stringify({
        id: this.id,
        username: this.username,
        fullName: this.fullName,
        role: this.role,
        email: this.email,
        isLoggedIn: this.isLoggedIn,
        token: this.token
      }));
    },
    logout() {
      this.id = null;
      this.username = '';
      this.fullName = '';
      this.role = '';
      this.email = '';
      this.isLoggedIn = false;
      this.token = '';
      
      // 清除localStorage
      localStorage.removeItem('user-store');
    },
    // 初始化时从localStorage加载状态
    initFromStorage() {
      const storedData = localStorage.getItem('user-store');
      if (storedData) {
        const userData = JSON.parse(storedData);
        this.id = userData.id;
        this.username = userData.username;
        this.fullName = userData.fullName;
        this.role = userData.role;
        this.email = userData.email;
        this.isLoggedIn = userData.isLoggedIn;
        this.token = userData.token;
      }
    }
  },
});