import requests
import os
import json
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:5000/api" # 假设这是用户和考试管理后端的地址

# 获取应用程序的根目录
def get_application_path():
    # 判断是否是PyInstaller打包的应用
    if getattr(sys, 'frozen', False):
        # 如果是打包的应用，使用sys._MEIPASS
        application_path = sys._MEIPASS
    else:
        # 如果不是打包的应用，使用当前文件所在目录的上一级目录
        application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return application_path

# 获取文件的绝对路径
def get_absolute_path(relative_path):
    return os.path.join(get_application_path(), relative_path)

import requests
from .common.network_manager import handle_http_error

def login(username, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        
        # 获取考试列表
        exams_response = requests.get(
            f"{API_BASE_URL}/student/exams",
            headers={"Authorization": f"Bearer {data['token']}"}
        )
        exams_response.raise_for_status()
        
        if not exams_response.json().get('available_exams'):
            raise ValueError('没有可用的考试科目')
            
        return data
    except Exception as e:
        handle_http_error(e)
        return None

def get_exams_for_student(student_id):
    """
    获取指定学生可参加的考试列表
    :param student_id: 学生ID
    :return: 考试列表
    """
    print(f"为学生ID {student_id} 获取考试列表...")
    
    try:
        # 尝试从服务器获取考试列表
        # 实际项目中，这里应该使用requests库发送HTTP请求
        # response = requests.get(f"{API_BASE_URL}/exams/student/{student_id}")
        # exams = response.json()
        
        # 模拟从服务器获取的考试列表
        # 这里我们模拟从exam_management/exams.json文件读取考试数据
        
        exams_data = []
        exams_file_path = get_absolute_path('exam_management/exams.json')
        if os.path.exists(exams_file_path):
            with open(exams_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                server_exams = data.get("exams", [])
                
                # 将服务器端的考试状态映射到客户端的状态
                for exam in server_exams:
                    # 只显示已发布和进行中的考试
                    if exam.get("status") in ["published", "ongoing"]:
                        exams_data.append({
                            "id": exam.get("id"),
                            "name": exam.get("name"),
                            "status": "available"  # 客户端状态：可参加
                        })
                    elif exam.get("status") == "completed":
                        exams_data.append({
                            "id": exam.get("id"),
                            "name": exam.get("name"),
                            "status": "completed"  # 客户端状态：已完成
                        })
        
        # 如果没有找到考试数据，返回模拟数据
        if not exams_data:
            exams_data = [
                {"id": 101, "name": "2024年度计算机基础知识认证", "status": "available"},
                {"id": 102, "name": "大学英语四级模拟考试", "status": "available"},
                {"id": 103, "name": "网络安全意识专项测试", "status": "completed"},
            ]
        
        return exams_data
    
    except Exception as e:
        print(f"获取考试列表失败: {e}")
        # 发生错误时返回模拟数据
        return [
            {"id": 101, "name": "2024年度计算机基础知识认证", "status": "available"},
            {"id": 102, "name": "大学英语四级模拟考试", "status": "available"},
            {"id": 103, "name": "网络安全意识专项测试", "status": "completed"},
        ]

def get_exam_details(exam_id):
    """
    获取考试详情
    :param exam_id: 考试ID
    :return: 考试详情
    """
    print(f"获取考试ID {exam_id} 的详情...")
    
    try:
        # 尝试从服务器获取考试详情
        # 实际项目中，这里应该使用requests库发送HTTP请求
        # response = requests.get(f"{API_BASE_URL}/exams/{exam_id}")
        # exam_details = response.json()
        
        # 模拟从服务器获取的考试详情
        # 这里我们模拟从exam_management/exams.json文件读取考试数据
        
        exams_file_path = get_absolute_path('exam_management/exams.json')
        if os.path.exists(exams_file_path):
            with open(exams_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                server_exams = data.get("exams", [])
                
                # 查找指定ID的考试
                for exam in server_exams:
                    if str(exam.get("id")) == str(exam_id):
                        # 获取考试的问题列表
                        questions = []
                        total_score = exam.get("total_score", 100)  # 默认总分为100
                        pass_score = exam.get("pass_score", 60)    # 默认及格分为60
                        
                        if "questions" in exam:
                            questions = exam["questions"]
                        elif "paper_id" in exam:
                            # 如果考试引用了试卷ID，尝试从papers.json加载试卷
                            paper_id = exam["paper_id"]
                            papers_file_path = get_absolute_path('exam_management/papers.json')
                            if os.path.exists(papers_file_path):
                                with open(papers_file_path, 'r', encoding='utf-8') as pf:
                                    papers_data = json.load(pf)
                                    papers = papers_data.get("papers", [])
                                    for paper in papers:
                                        if str(paper.get("id")) == str(paper_id):
                                            questions = paper.get("questions", [])
                                            # 如果试卷中有总分和及格分信息，优先使用
                                            if "total_score" in paper:
                                                total_score = paper["total_score"]
                                            if "pass_score" in paper:
                                                pass_score = paper["pass_score"]
                                            break
                        
                        # 返回考试详情
                        return {
                            "id": exam.get("id"),
                            "name": exam.get("name"),
                            "duration": exam.get("duration", 60),  # 考试时长（分钟）
                            "total_score": total_score,            # 试卷总分
                            "pass_score": pass_score,              # 及格分数
                            "questions": questions
                        }
        
        # 如果没有找到考试数据，返回模拟数据
        return {
            "id": exam_id,
            "name": "2024年度计算机基础知识认证",
            "duration": 60,  # 考试时长（分钟）
            "total_score": 100,  # 试卷总分
            "pass_score": 60,   # 及格分数
            "questions": [
                {
                    "id": 1,
                    "type": "single_choice",
                    "content": "计算机网络中，常用的局域网技术是？",
                    "options": ["A. 以太网", "B. 广域网", "C. 卫星通信", "D. 蜂窝网络"],
                    "answer": "A",
                    "score": 5
                },
                {
                    "id": 2,
                    "type": "multiple_choice",
                    "content": "以下哪些是操作系统的主要功能？",
                    "options": ["A. 进程管理", "B. 内存管理", "C. 文件系统管理", "D. 图像处理"],
                    "answer": "ABC",
                    "score": 5
                },
                {
                    "id": 3,
                    "type": "true_false",
                    "content": "HTTP协议是一种无状态的协议。",
                    "answer": "T",
                    "score": 5
                },
                {
                    "id": 4,
                    "type": "fill_blank",
                    "content": "在Python中，用于格式化字符串的函数是__________。",
                    "answer": "format",
                    "score": 5
                },
                {
                    "id": 5,
                    "type": "short_answer",
                    "content": "简述计算机病毒的特点和防范措施。",
                    "answer": "计算机病毒的特点：传染性、隐蔽性、潜伏性、破坏性。防范措施：安装杀毒软件、定期更新系统补丁、不打开可疑邮件附件、备份重要数据。",
                    "score": 10
                }
            ]
        }
    
    except Exception as e:
        print(f"获取考试详情失败: {e}")
        # 发生错误时返回模拟数据
        return {
            "id": exam_id,
            "name": "2024年度计算机基础知识认证",
            "duration": 60,  # 考试时长（分钟）
            "total_score": 100,  # 试卷总分
            "pass_score": 60,   # 及格分数
            "questions": [
                {
                    "id": 1,
                    "type": "single_choice",
                    "content": "计算机网络中，常用的局域网技术是？",
                    "options": ["A. 以太网", "B. 广域网", "C. 卫星通信", "D. 蜂窝网络"],
                    "answer": "A",
                    "score": 5
                },
                # 其他问题...
            ]
        }

def submit_answers(exam_id, student_id, answers):
    """
    提交考试答案
    :param exam_id: 考试ID
    :param student_id: 学生ID
    :param answers: 答案字典，格式为 {question_id: answer}
    :return: 提交结果
    """
    print(f"提交考试ID {exam_id} 的答案，学生ID: {student_id}")
    print(f"答案内容: {answers}")
    
    try:
        # 实际项目中，这里应该使用requests库发送HTTP请求
        # response = requests.post(f"{API_BASE_URL}/exams/{exam_id}/submit", 
        #                         json={"student_id": student_id, "answers": answers})
        # result = response.json()
        
        # 获取考试详情，用于计算得分
        exam_details = get_exam_details(exam_id)
        total_score = exam_details.get('total_score', 100)
        
        # 模拟计算得分（实际项目中应该由服务器端计算）
        # 这里简单模拟一个得分，实际应该根据答案和标准答案比对计算
        import random
        score = random.randint(int(total_score * 0.5), total_score)  # 随机生成50%-100%的分数
        
        # 模拟将答案保存到本地文件
        import os
        import json
        from datetime import datetime
        
        # 确保答案目录存在
        answers_dir = get_absolute_path('exam_management/answers')
        os.makedirs(answers_dir, exist_ok=True)
        
        # 生成答案文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(answers_dir, f"exam_{exam_id}_student_{student_id}_{timestamp}.json")
        
        # 保存答案
        answer_data = {
            "exam_id": exam_id,
            "student_id": student_id,
            "submit_time": timestamp,
            "answers": answers,
            "score": score
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(answer_data, f, ensure_ascii=False, indent=4)
        
        print(f"答案已保存到文件: {filename}")
        return {"success": True, "message": "答案提交成功", "score": score}
    
    except Exception as e:
        print(f"提交答案失败: {e}")
        return {"success": False, "message": f"答案提交失败: {str(e)}"}

# 在get_student_exams方法中添加调试标记
def get_student_exams(student_id):
    print(f"[DEBUG] 请求考试列表: {student_id}")  # 新增调试输出
    # ... existing code ...