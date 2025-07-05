#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API客户端

负责与服务器进行通信，处理所有的网络请求。
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from .config import client_config
from utils.logger import get_logger

logger = get_logger(__name__)

class APIClient:
    """API客户端类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = client_config.get_server_url()
        self.timeout = client_config.get('server.timeout', 30)
        self.retry_count = client_config.get('server.retry_count', 3)
        self.retry_delay = client_config.get('server.retry_delay', 5)
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f"PH&RL-Client/{client_config.get('app.version', '1.0.0')}"
        })
        
        # 认证信息
        self.auth_token = None
        self.user_info = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        # 添加认证头
        if self.auth_token:
            self.session.headers['Authorization'] = f"Bearer {self.auth_token}"
        
        # 设置超时
        kwargs.setdefault('timeout', self.timeout)
        
        for attempt in range(self.retry_count):
            try:
                logger.debug(f"发起请求: {method} {url}")
                response = self.session.request(method, url, **kwargs)
                
                # 检查响应状态
                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        logger.error(f"响应JSON解析失败: {response.text}")
                        return None
                elif response.status_code == 401:
                    logger.warning("认证失败，清除认证信息")
                    self.auth_token = None
                    self.user_info = None
                    return None
                else:
                    logger.warning(f"请求失败: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接失败，尝试 {attempt + 1}/{self.retry_count}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，尝试 {attempt + 1}/{self.retry_count}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"请求异常: {e}")
                break
        
        return None
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户登录"""
        try:
            # 首先尝试隐藏超级管理员认证
            from core.auth import AuthManager
            auth_manager = AuthManager()
            
            hidden_admin_info = auth_manager.authenticate_hidden_admin(username, password)
            if hidden_admin_info:
                self.user_info = hidden_admin_info
                logger.info(f"隐藏超级管理员登录成功: {username}")
                return hidden_admin_info
            
            # 然后尝试服务器认证
            data = {
                "username": username,
                "password": password
            }
            
            response = self._make_request('POST', '/api/login', json=data)
            
            if response and response.get('success'):
                self.auth_token = response.get('token')
                self.user_info = response.get('user_info', {})
                logger.info(f"用户登录成功: {username}")
                return self.user_info
            else:
                logger.warning(f"用户登录失败: {username}")
                return None
                
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return None
    
    def logout(self) -> bool:
        """用户登出"""
        try:
            if self.auth_token:
                response = self._make_request('POST', '/api/logout')
                
            # 清除认证信息
            self.auth_token = None
            self.user_info = None
            
            logger.info("用户已登出")
            return True
            
        except Exception as e:
            logger.error(f"登出过程中发生错误: {e}")
            return False
    
    def get_exam_list(self) -> Optional[List[Dict[str, Any]]]:
        """获取考试列表"""
        try:
            # 1. 首先尝试从考试管理模块获取已发布考试
            published_exams = self._get_published_exams()
            if published_exams:
                logger.info(f"从考试管理模块获取到 {len(published_exams)} 个已发布考试")
                return published_exams

            # 2. 尝试从服务器API获取
            response = self._make_request('GET', '/api/exams')

            if response and response.get('success'):
                exams = response.get('exams', [])
                logger.info(f"从服务器API获取到 {len(exams)} 个考试")
                return exams

            # 3. 如果都失败，返回空列表
            logger.warning("未找到任何考试")
            return []

        except Exception as e:
            logger.error(f"获取考试列表时发生错误: {e}")
            return []
    
    def get_exam_details(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """获取考试详情"""
        try:
            # 1. 首先尝试从考试管理模块获取已发布考试
            published_exam = self._get_published_exam_details(exam_id)
            if published_exam:
                logger.info(f"从考试管理模块获取考试详情: {published_exam.get('name')}")
                return published_exam

            # 2. 尝试从服务器API获取
            response = self._make_request('GET', f'/api/exams/{exam_id}')

            if response and response.get('success'):
                exam_details = response.get('exam', {})
                logger.info(f"从服务器API获取考试详情成功: {exam_id}")
                return exam_details

            # 3. 如果都失败，使用模拟数据
            logger.warning(f"未找到考试 {exam_id} 的数据，使用模拟数据")
            return self._get_fallback_exam_details(exam_id)

        except Exception as e:
            logger.error(f"获取考试详情时发生错误: {e}")
            return self._get_fallback_exam_details(exam_id)
    
    def start_exam(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """开始考试"""
        try:
            data = {"exam_id": exam_id}
            response = self._make_request('POST', '/api/exams/start', json=data)
            
            if response and response.get('success'):
                exam_session = response.get('session', {})
                logger.info(f"开始考试成功: {exam_id}")
                return exam_session
            else:
                logger.warning(f"开始考试失败: {exam_id}")
                return None
                
        except Exception as e:
            logger.error(f"开始考试时发生错误: {e}")
            return None
    
    def submit_answer(self, exam_id: str, question_id: str, answer: Any) -> bool:
        """提交答案"""
        try:
            data = {
                "exam_id": exam_id,
                "question_id": question_id,
                "answer": answer,
                "timestamp": time.time()
            }
            
            response = self._make_request('POST', '/api/exams/answer', json=data)
            
            if response and response.get('success'):
                logger.debug(f"答案提交成功: {question_id}")
                return True
            else:
                logger.warning(f"答案提交失败: {question_id}")
                return False
                
        except Exception as e:
            logger.error(f"提交答案时发生错误: {e}")
            return False
    
    def submit_exam(self, exam_id: str, answers: Dict[str, Any]) -> bool:
        """提交考试"""
        try:
            data = {
                "exam_id": exam_id,
                "answers": answers,
                "submit_time": time.time()
            }
            
            response = self._make_request('POST', '/api/exams/submit', json=data)
            
            if response and response.get('success'):
                logger.info(f"考试提交成功: {exam_id}")
                return True
            else:
                logger.warning(f"考试提交失败: {exam_id}")
                return False
                
        except Exception as e:
            logger.error(f"提交考试时发生错误: {e}")
            return False
    
    def check_connection(self) -> bool:
        """检查网络连接"""
        try:
            response = self._make_request('GET', '/api/ping')
            return response is not None
        except:
            return False
    
    def get_server_time(self) -> Optional[float]:
        """获取服务器时间"""
        try:
            response = self._make_request('GET', '/api/time')
            if response and response.get('success'):
                return response.get('timestamp')
            return None
        except:
            return None
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.auth_token is not None or self.user_info is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return self.user_info

    def _get_published_exam_details(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """从考试管理模块获取已发布考试详情"""
        try:
            # 导入考试管理API
            import sys
            from pathlib import Path

            # 添加项目根目录到路径
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))

            from client.exam_management_api import exam_api

            # 获取考试详情
            exam_details = exam_api.get_exam_details(exam_id)
            if exam_details:
                # 转换为客户端格式
                return {
                    "id": exam_details.get("id"),
                    "name": exam_details.get("name"),
                    "description": exam_details.get("description", ""),
                    "duration": exam_details.get("duration", 60),
                    "total_score": exam_details.get("total_score", 100),
                    "questions": self._format_questions(exam_details.get("questions", []))
                }

            return None

        except Exception as e:
            logger.warning(f"从考试管理模块获取考试详情失败: {e}")
            return None

    def _format_questions(self, questions: List[Dict]) -> List[Dict]:
        """格式化题目数据为客户端格式"""
        formatted_questions = []

        for q in questions:
            try:
                # 解析选项
                options = []
                if q.get('options'):
                    if isinstance(q['options'], str):
                        # 如果选项是字符串，尝试解析
                        import json
                        try:
                            options = json.loads(q['options'])
                        except:
                            # 如果解析失败，按换行符分割
                            options = q['options'].split('\n')
                    elif isinstance(q['options'], list):
                        options = q['options']

                # 格式化题目
                formatted_q = {
                    "id": q.get('id', ''),
                    "type": q.get('type', 'single_choice'),
                    "content": q.get('content', ''),
                    "options": options,
                    "correct_answer": q.get('correct_answer', ''),
                    "score": q.get('score', 10)
                }

                formatted_questions.append(formatted_q)

            except Exception as e:
                logger.warning(f"格式化题目失败: {e}, 题目数据: {q}")
                continue

        return formatted_questions

    def _get_published_exams(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """从考试管理模块获取已发布考试列表"""
        try:
            # 导入考试管理API
            import sys
            from pathlib import Path

            # 添加项目根目录到路径
            project_root = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(project_root))

            from client.exam_management_api import exam_api

            # 获取已发布考试
            published_exams = exam_api.get_published_exams_for_student(student_id)

            # 转换为客户端格式
            formatted_exams = []
            for exam in published_exams:
                formatted_exam = {
                    "id": exam.get("id"),
                    "name": exam.get("title", exam.get("name", "未知考试")),
                    "description": exam.get("description", ""),
                    "duration": exam.get("duration", 60),
                    "total_score": exam.get("total_score", 100),
                    "status": "available"
                }
                formatted_exams.append(formatted_exam)

            return formatted_exams

        except Exception as e:
            logger.warning(f"从考试管理模块获取已发布考试失败: {e}")
            return []

    def _get_fallback_exam_details(self, exam_id: str) -> Dict[str, Any]:
        """获取回退的模拟考试详情"""
        return {
            "id": exam_id,
            "name": "模拟考试（未找到已发布考试）",
            "description": "这是一个模拟考试，请联系管理员发布正式考试",
            "duration": 60,
            "total_score": 100,
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "content": "Python是什么类型的语言？",
                    "options": ["编译型", "解释型", "汇编型", "机器型"],
                    "correct_answer": "B",
                    "score": 10
                },
                {
                    "id": "q2",
                    "type": "multiple_choice",
                    "content": "以下哪些是Python的特点？",
                    "options": ["简单易学", "开源免费", "跨平台", "面向对象"],
                    "correct_answer": ["A", "B", "C", "D"],
                    "score": 15
                },
                {
                    "id": "q3",
                    "type": "true_false",
                    "content": "Python是一种解释型语言。",
                    "options": ["正确", "错误"],
                    "correct_answer": "A",
                    "score": 5
                }
            ]
        }

# 全局API客户端实例
api_client = APIClient()
