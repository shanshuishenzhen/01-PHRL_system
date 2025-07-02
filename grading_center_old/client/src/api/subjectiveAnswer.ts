import axios from 'axios';
import { PaginatedResponse } from './config';

export interface MarkerScore {
  markerId: number;
  score: number;
  comments: string;
  markedAt: string;
  markerInfo?: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
}

export interface ArbitrationInfo {
  id: number;
  answerId: number;
  requesterId: number;
  arbitratorId: number;
  reason: string;
  originalScore: number;
  adjustedScore: number;
  status: 'pending' | 'reviewing' | 'approved' | 'rejected';
  resolution: string;
  resolvedAt: string;
  requester?: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
  arbitrator?: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
}

export interface SubjectiveAnswer {
  id: number;
  participantId: number;
  questionId: number;
  answerText: string;
  score: number | null;
  markerId: number | null;
  markedAt: string | null;
  status: 'pending' | 'marking' | 'marked' | 'disputed' | 'arbitrated';
  comments: string | null;
  // 多人评分相关字段
  markerScores?: MarkerScore[];
  markerScoresWithInfo?: MarkerScore[];
  markerCount?: number;
  requiredMarkerCount?: number;
  scoreVariance?: number;
  needArbitration?: boolean;
  arbitrationId?: number;
  arbitrationInfo?: ArbitrationInfo;
  examQuestion?: {
    id: number;
    questionContent: string;
    score: number;
    explanation: string;
    examPaper?: {
      id: number;
      title: string;
      examId: number;
    };
  };
  participant?: {
    id: number;
    userId: number;
    examId: number;
    user?: {
      id: number;
      username: string;
      email: string;
    };
  };
  marker?: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
}

// 获取待阅卷答案列表
export const getPendingAnswers = async (examId: number, page = 1, limit = 10): Promise<PaginatedResponse<SubjectiveAnswer>> => {
  const response = await axios.get(`/api/subjective-answers/pending`, {
    params: { examId, page, limit }
  });
  return response.data;
};

// 获取评阅中的答案列表
export const getMarkingAnswers = async (examId: number, page = 1, limit = 10): Promise<PaginatedResponse<SubjectiveAnswer>> => {
  const response = await axios.get(`/api/subjective-answers/marking`, {
    params: { examId, page, limit }
  });
  return response.data;
};

// 获取单个答案详情
export const getAnswerDetail = async (id: number): Promise<SubjectiveAnswer> => {
  const response = await axios.get(`/api/subjective-answers/${id}`);
  return response.data;
};

// 评分操作
export const markAnswer = async (id: number, score: number, comments: string): Promise<{ message: string; data: SubjectiveAnswer }> => {
  const response = await axios.post(`/api/subjective-answers/${id}/mark`, { score, comments });
  return response.data;
};

// 获取已评阅答案列表
export const getMarkedAnswers = async (examId: number, page = 1, limit = 10): Promise<PaginatedResponse<SubjectiveAnswer>> => {
  const response = await axios.get(`/api/subjective-answers/marked`, {
    params: { examId, page, limit }
  });
  return response.data;
};

// 获取有争议的答案列表
export const getDisputedAnswers = async (examId: number, page = 1, limit = 10): Promise<PaginatedResponse<SubjectiveAnswer>> => {
  const response = await axios.get(`/api/subjective-answers/disputed`, {
    params: { examId, page, limit }
  });
  return response.data;
};

// 提交争议/申请仲裁
export const disputeAnswer = async (id: number, reason: string): Promise<{ message: string }> => {
  const response = await axios.post(`/api/subjective-answers/${id}/dispute`, { reason });
  return response.data;
};

// 仲裁操作
export const arbitrateAnswer = async (id: number, adjustedScore: number, resolution: string): Promise<{ message: string; data: SubjectiveAnswer }> => {
  const response = await axios.post(`/api/subjective-answers/${id}/arbitrate`, { adjustedScore, resolution });
  return response.data;
};