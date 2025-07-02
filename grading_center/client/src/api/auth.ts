import { apiClient } from './config';
import { useUserStore } from '../stores/user';
import type { AxiosResponse } from 'axios';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserData {
  id: number;
  username: string;
  fullName: string;
  role: string;
  email: string;
  token?: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  token: string; // 确保token字段存在
  user: {
    id: number;
    username: string;
    fullName: string;
    role: string;
    email: string;
  };
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  token?: string;
  user?: UserData;
}

// 登录API
export const login = async (credentials: LoginRequest): Promise<ApiResponse> => {
  try {
    console.log('发送登录请求:', { username: credentials.username });
    
    // 添加超时处理
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
    
    const response = await apiClient.post('/auth/login', credentials, {
      signal: controller.signal
    });
    
    // 清除超时
    clearTimeout(timeoutId);
    
    console.log('登录API原始响应:', response);
    
    // 验证响应格式
    if (!response || typeof response !== 'object') {
      console.error('登录响应格式错误:', response);
      return {
        success: false,
        message: '服务器响应格式错误'
      };
    }
    
    // 确保response是正确的LoginResponse类型
    const loginResponse = response as unknown as LoginResponse;
    console.log('处理后的登录响应:', loginResponse);
    
    // 验证必要字段
    if (!loginResponse.token) {
      console.error('登录响应缺少token:', loginResponse);
      return {
        success: false,
        message: '登录成功但未获取到有效令牌'
      };
    }
    
    if (!loginResponse.user) {
      console.error('登录响应缺少用户数据:', loginResponse);
      return {
        success: false,
        message: '登录成功但未获取到用户信息'
      };
    }
    
    // 确保token正确传递
    // 确保返回正确的响应格式，包括token
    return {
      success: true,
      message: loginResponse.message || '登录成功',
      token: loginResponse.token, // 直接传递token
      user: {
        id: loginResponse.user.id,
        username: loginResponse.user.username,
        fullName: loginResponse.user.fullName,
        role: loginResponse.user.role,
        email: loginResponse.user.email
      }
    };
  } catch (error: any) {
    console.error('登录错误:', error);
    
    // 处理不同类型的错误
    if (error.name === 'AbortError') {
      return {
        success: false,
        message: '登录请求超时，请稍后再试'
      };
    }
    
    if (error.status === 401) {
      return {
        success: false,
        message: '用户名或密码错误'
      };
    }
    
    return {
      success: false,
      message: error?.message || '登录失败，请检查网络连接或稍后再试'
    };
  }
};

// 获取当前用户信息
export const getCurrentUser = async (): Promise<ApiResponse> => {
  try {
    const response = await apiClient.get('/auth/me');
    return response as ApiResponse;
  } catch (error: any) {
    return {
      success: false,
      message: error?.response?.data?.message || error?.message || '获取用户信息失败'
    };
  }
};

// 登出API
export const logout = async (): Promise<ApiResponse> => {
  try {
    const response = await apiClient.post('/auth/logout');
    const userStore = useUserStore();
    userStore.logout();
    return response as ApiResponse;
  } catch (error: any) {
    // 即使API调用失败，也清除本地用户状态
    const userStore = useUserStore();
    userStore.logout();
    
    return {
      success: false,
      message: error?.response?.data?.message || error?.message || '登出失败'
    };
  }
};