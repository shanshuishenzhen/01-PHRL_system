import axios from 'axios';
import { API_URL } from './config';

const API = `${API_URL}/exams`;

export interface Exam {
  id: number;
  examName: string;
  examCode: string;
  description?: string;
  startTime: string;
  endTime: string;
  duration: number;
  totalScore: number;
  passingScore: number;
  status: 'draft' | 'published' | 'in_progress' | 'completed' | 'archived';
  creatorId: number;
  isRandomOrder: boolean;
  allowReview: boolean;
  showResult: boolean;
  showAnalysis: boolean;
  createdAt: string;
  updatedAt: string;
  creator?: {
    id: number;
    username: string;
    realName: string;
  };
  questions?: ExamQuestion[];
}

export interface ExamQuestion {
  id: number;
  examId: number;
  questionContent: string;
  questionType: string;
  score: number;
  orderNum: number;
  options?: any[];
  correctAnswer?: string;
  explanation?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    pages: number;
  };
}

// 获取考试列表
export const getExams = async (page = 1, limit = 10, status?: string, keyword?: string) => {
  const params = { page, limit };
  if (status) Object.assign(params, { status });
  if (keyword) Object.assign(params, { keyword });
  
  const response = await axios.get<PaginatedResponse<Exam>>(API, { params });
  return response.data;
};

// 获取单个考试详情
export const getExamById = async (id: number) => {
  const response = await axios.get<{ success: boolean; data: Exam }>(`${API}/${id}`);
  return response.data;
};

// 创建考试
export const createExam = async (examData: Partial<Exam>) => {
  const response = await axios.post<{ success: boolean; message: string; data: Exam }>(API, examData);
  return response.data;
};

// 更新考试
export const updateExam = async (id: number, examData: Partial<Exam>) => {
  const response = await axios.put<{ success: boolean; message: string; data: Exam }>(`${API}/${id}`, examData);
  return response.data;
};

// 删除考试
export const deleteExam = async (id: number) => {
  const response = await axios.delete<{ success: boolean; message: string }>(`${API}/${id}`);
  return response.data;
};

// 发布考试
export const publishExam = async (id: number) => {
  const response = await axios.post<{ success: boolean; message: string; data: Exam }>(`${API}/${id}/publish`);
  return response.data;
};

// 开始考试
export const startExam = async (id: number) => {
  const response = await axios.post<{ success: boolean; message: string; data: Exam }>(`${API}/${id}/start`);
  return response.data;
};

// 结束考试
export const endExam = async (id: number) => {
  const response = await axios.post<{ success: boolean; message: string; data: Exam }>(`${API}/${id}/end`);
  return response.data;
};

// 获取考试统计数据
export const getExamStats = async (id: number) => {
  const response = await axios.get<{ success: boolean; data: any }>(`${API}/${id}/stats`);
  return response.data;
};