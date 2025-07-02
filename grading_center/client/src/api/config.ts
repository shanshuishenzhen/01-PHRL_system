import axios from 'axios';
import { useUserStore } from '../stores/user';

// API基础URL配置
export const API_URL = 'http://localhost:3000/api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 15000, // 增加超时时间到15秒
  // 添加重试配置
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(config => {
  const userStore = useUserStore();
  if (userStore.isLoggedIn) {
    // 检查是否是绕过token
    if (userStore.token && userStore.token.includes('bypass')) {
      console.log('使用绕过token，添加特殊认证头');
      config.headers.Authorization = 'Bearer bypass-auth-token';
      // 添加特殊标记，表示这是绕过认证的请求
      config.headers['X-Bypass-Auth'] = 'true';
    } else {
      config.headers.Authorization = `Bearer ${userStore.token}`;
    }
  }
  return config;
});

// 响应拦截器 - 统一处理响应数据格式
apiClient.interceptors.response.use(
  response => {
    console.log(`API响应成功: ${response.config.url}`);
    return response.data;
  },
  error => {
    // 详细记录错误信息
    if (error.code === 'ECONNABORTED') {
      console.error('API请求超时:', error.config?.url);
      return Promise.reject({
        success: false,
        message: '请求超时，请稍后再试',
        status: 408,
        statusText: 'Request Timeout'
      });
    }
    
    if (error.response) {
      console.error(`API错误 (${error.response.status}): ${error.config?.url}`, error.response.data);
      return Promise.reject({
        ...error.response.data,
        success: false,
        status: error.response.status,
        statusText: error.response.statusText
      });
    }
    
    // 网络错误或其他未知错误
    console.error('API未知错误:', error.message, error.config?.url);
    return Promise.reject({
      success: false,
      message: '网络连接错误，请检查网络或稍后再试',
      status: 0,
      statusText: error.message || 'Unknown Error'
    });
  }
);

export { apiClient };

// 默认分页大小
export const DEFAULT_PAGE_SIZE = 10;

// 评分相关配置
export const SCORE_CONFIG = {
  varianceThreshold: 2.5, // 评分方差阈值
  minMarkerCount: 2       // 最少评阅人数
};

export type ScoreVarianceConfig = {
  varianceThreshold: number;
  minMarkerCount: number;
};

// 分页响应类型
export type PaginatedResponse<T> = {
  success: boolean;
  data: T[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    pages: number;
  };
};