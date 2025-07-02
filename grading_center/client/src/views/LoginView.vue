<template>
  <div class="login-container">
    <h1>阅卷系统登录</h1>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          required
          placeholder="请输入用户名"
        />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
          placeholder="请输入密码"
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <button type="button" @click="autoLogin" class="auto-login-btn">
        自动登录(管理员)
      </button>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../api/auth';
import { useUserStore } from '../stores/user';

const router = useRouter();

const form = ref({
  username: '',
  password: ''
});

const loading = ref(false);
const errorMessage = ref('');

// 自动登录功能
const autoLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  
  try {
    // 直接使用管理员账号
    const adminCredentials = {
      username: 'admin',
      password: 'admin123'
    };
    
    console.log('使用管理员账号自动登录');
    
    // 创建用户数据和令牌
    const userStore = useUserStore();
    const userData = {
      id: 1,
      username: 'admin',
      fullName: '管理员',
      role: 'admin',
      email: 'admin@example.com'
    };
    
    // 设置用户状态并跳过API调用
    userStore.setUser(userData, 'bypass-token-for-admin');
    
    // 强制刷新Pinia状态
    await nextTick();
    
    console.log('已自动登录为管理员');
    
    // 登录成功后跳转到首页
    router.push('/');
    
  } catch (error) {
    console.error('自动登录过程错误:', error);
    errorMessage.value = '自动登录失败，请尝试手动登录';
  } finally {
    loading.value = false;
  }
};

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  
  // 添加登录超时处理
  const loginTimeout = setTimeout(() => {
    if (loading.value) {
      loading.value = false;
      errorMessage.value = '登录请求超时，请尝试自动登录或稍后再试';
      console.error('登录请求超时');
    }
  }, 8000); // 8秒超时
  
  try {
    console.log('开始登录请求，用户名:', form.value.username);
    const response = await login(form.value);
    console.log('登录API响应:', JSON.stringify(response, null, 2));
    
    // 清除超时计时器
    clearTimeout(loginTimeout);
    
    // 如果已经超时处理过，不再继续处理
    if (!loading.value) return;
    
    if (!response.success) {
      errorMessage.value = response.message || '登录失败';
      return;
    }
    
    if (!response.user) {
      errorMessage.value = '登录失败: 无效的用户数据';
      return;
    }
    
    const userStore = useUserStore();
    // 确保token正确传递
    // 从响应中获取token
    const token = response.token || response.user.token;
    console.log('获取到的token:', token);
    
    userStore.setUser(response.user, token);
    
    // 强制刷新Pinia状态
    await nextTick();
    
    console.log('当前用户状态:', {
      id: userStore.id,
      username: userStore.username,
      fullName: userStore.fullName,
      role: userStore.role,
      isLoggedIn: userStore.isLoggedIn,
      token: userStore.token
    });
    
    // 登录成功后跳转到首页
    router.push('/');
    
  } catch (error) {
    // 清除超时计时器
    clearTimeout(loginTimeout);
    
    console.error('登录过程错误:', error);
    errorMessage.value = '网络错误，请尝试自动登录或稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 0.5rem;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 0.5rem;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.auto-login-btn {
  background-color: #3498db;
  font-weight: bold;
}

.error-message {
  color: red;
  margin-top: 1rem;
}
</style>