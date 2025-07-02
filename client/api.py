import os
import json
import sys
import logging
from datetime import datetime

# 获取logger
logger = logging.getLogger('client_app.api')

# 注意：这是一个概念性的API文件。
# 实际的Python实现将使用 `requests` 库。
# 这里的URL和数据结构是根据服务器端开发计划预设的。

# 默认API基础URL
DEFAULT_API_BASE_URL = "http://localhost:5000/api"

# 从配置文件加载服务器地址
def load_server_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'settings.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                server = config.get('server', {})
                host = server.get('host', 'localhost')
                port = server.get('port', 5000)
                protocol = server.get('protocol', 'http')
                return f"{protocol}://{host}:{port}/api"
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
    return DEFAULT_API_BASE_URL

# 加载API基础URL
API_BASE_URL = load_server_config()

# 获取应用程序的根目录
def get_application_path():
    # 判断是否是PyInstaller打包的应用
    if getattr(sys, 'frozen', False):
        # 如果是打包的应用，使用sys._MEIPASS
        application_path = getattr(sys, '_MEIPASS', '')
    else:
        # 如果不是打包的应用，使用当前文件所在目录的上一级目录
        application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return application_path

# 获取文件的绝对路径
def get_absolute_path(relative_path):
    return os.path.join(get_application_path(), relative_path)

def login(username, password):
    """
    登录API调用
    :param username: 用户名/准考证号/身份证号
    :param password: 密码
    :return: 成功则返回用户信息，失败则返回None
    """
    print(f"尝试使用 {username} 登录...")
    
    # 尝试从数据库获取用户信息
    user_info = None
    db_path = get_absolute_path('user_management/users.db')
    
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查找匹配的用户（通过用户名或身份证号）
            cursor.execute("""
                SELECT * FROM users 
                WHERE (username = ? OR id_card = ?) AND password = ?
            """, (username, username, password))
            
            user = cursor.fetchone()
            if user:
                # 找到匹配的用户
                user_info = {
                    "id": user['id'],
                    "username": user['username'],
                    "role": user['role'],
                    "real_name": user['real_name'] or "",
                    "department": user['department'] or "",
                    "ID": user['id_card'] or "",
                    "token": "fake-jwt-token"
                }
            conn.close()
        except Exception as e:
            print(f"从数据库读取用户数据失败: {e}")
            
    # 如果数据库查询失败，尝试从JSON文件获取用户信息（作为备选方案）
    if user_info is None:
        users_file_path = get_absolute_path('user_management/users.json')
        if os.path.exists(users_file_path):
            try:
                with open(users_file_path, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    users = users_data.get("users", [])
                    
                    # 查找匹配的用户
                    for user in users:
                        # 检查用户名/身份证号和密码是否匹配
                        if ((user.get("username") == username or user.get("ID") == username) and 
                            (user.get("password") == password or user.get("password_hash") == password)):
                            # 找到匹配的用户
                            user_info = {
                                "id": user.get("id"),
                                "username": user.get("username"),
                                "role": user.get("role"),
                                "real_name": user.get("real_name", ""),
                                "department": user.get("department", ""),
                                "ID": user.get("ID", ""),
                                "token": "fake-jwt-token"
                            }
                            break
            except Exception as e:
                print(f"读取JSON用户数据失败: {e}")
    
    # 如果找不到用户信息，使用模拟数据（仅用于测试）
    if user_info is None and username == "student" and password == "123456":
        user_info = {"id": 1, "username": "student", "role": "student", "token": "fake-jwt-token"}
    
    # 特殊处理admin用户，避免卡死
    if username == "admin" and password == "admin":
        print(f"管理员用户 {username} 登录成功 (特殊处理)")
        return {"id": 999, "username": "admin", "role": "admin", "real_name": "系统管理员", "department": "系统管理", "token": "admin-token"}
    
    # 如果找到用户信息，允许 admin、admin_开头、evaluator、student 角色登录并显示考试
    if user_info is not None:
        # 允许所有管理员、考评员、学生登录
        if user_info["role"] in ["admin", "super_admin", "student", "evaluator"] or \
           (isinstance(user_info["username"], str) and user_info["username"].startswith("admin_")):
            return user_info
        else:
            # 其它角色允许登录但不显示考试
            return user_info
    
    return user_info

def check_student_has_exam(student_id):
    """
    检查学生/考评员是否有待进行的考试信息
    :param student_id: 学生ID或考评员ID
    :return: 如果有待进行的考试信息返回True，否则返回False
    """
    print(f"检查学生ID {student_id} 是否有待进行的考试信息...")
    
    # 获取考试报名信息和考试状态
    enrolled_exam_ids = []
    enrollments_file_path = get_absolute_path('exam_management/enrollments.json')
    if os.path.exists(enrollments_file_path):
        try:
            with open(enrollments_file_path, 'r', encoding='utf-8') as f:
                enrollments_data = json.load(f)
                enrollments = enrollments_data.get("enrollments", [])
                
                # 获取报名的所有考试ID
                for enrollment in enrollments:
                    user_ids = enrollment.get("user_ids", [])
                    # 将student_id转换为字符串进行比较，因为JSON中可能是数字
                    if str(student_id) in [str(uid) for uid in user_ids]:
                        enrolled_exam_ids.append(enrollment.get("exam_id"))
        except Exception as e:
            print(f"读取考试报名数据失败: {e}")
    
    # 如果没有报名任何考试，直接返回False
    if not enrolled_exam_ids:
        return False
    
    # 检查报名的考试中是否有待进行的考试（已发布或进行中）
    exams_file_path = get_absolute_path('exam_management/exams.json')
    if os.path.exists(exams_file_path):
        try:
            with open(exams_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                server_exams = data.get("exams", [])
                
                # 检查是否有待进行的考试
                for exam in server_exams:
                    if exam.get("id") in enrolled_exam_ids and exam.get("status") in ["published", "ongoing"]:
                        return True
        except Exception as e:
            print(f"读取考试数据失败: {e}")
    
    # 如果没有找到待进行的考试，返回False
    return False

def get_published_exams_for_student(student_id):
    """
    从考试发布模块获取学生可参加的已发布考试
    """
    try:
        # 1. 获取已发布的考试
        published_exams_file = get_absolute_path('exam_management/published_exams.json')
        if not os.path.exists(published_exams_file):
            return []

        with open(published_exams_file, 'r', encoding='utf-8') as f:
            published_exams = json.load(f)

        # 2. 获取学生的考试分配
        enrollments_file = get_absolute_path('exam_management/enrollments.json')
        if not os.path.exists(enrollments_file):
            return []

        with open(enrollments_file, 'r', encoding='utf-8') as f:
            enrollments_data = json.load(f)

        # 处理两种格式的enrollments数据
        if isinstance(enrollments_data, dict) and "enrollments" in enrollments_data:
            enrollments = enrollments_data["enrollments"]
        elif isinstance(enrollments_data, list):
            enrollments = enrollments_data
        else:
            enrollments = []

        # 3. 找到分配给该学生的考试
        student_exam_ids = []
        for enrollment in enrollments:
            # 新格式：每个考试一个记录，包含user_ids数组
            if "user_ids" in enrollment:
                if student_id in enrollment.get("user_ids", []):
                    student_exam_ids.append(enrollment.get("exam_id"))
            # 旧格式：每个学生一个记录
            elif enrollment.get('student_id') == student_id and enrollment.get('status') == 'assigned':
                student_exam_ids.append(enrollment.get('exam_id'))

        # 4. 获取学生可参加的已发布考试
        student_exams = []
        for exam in published_exams:
            if (exam.get('status') == 'published' and
                exam.get('id') in student_exam_ids):

                # 转换为客户端格式
                client_exam = {
                    "id": exam.get("id"),
                    "name": exam.get("title"),
                    "status": "available",
                    "description": exam.get("description", ""),
                    "time_limit": exam.get("duration", 60),
                    "total_score": exam.get("total_score", 100),
                    "start_time": exam.get("start_time", ""),
                    "end_time": exam.get("end_time", ""),
                    "paper_id": exam.get("paper_id"),
                    "exam_type": "published"  # 标记为已发布考试
                }
                student_exams.append(client_exam)

        return student_exams

    except Exception as e:
        print(f"获取已发布考试失败: {e}")
        return []


def get_exams_for_student(student_id, user_info=None):
    """
    获取学生可参加的考试列表
    优先从考试发布模块获取，然后从客户端同步的考试列表获取
    """
    try:
        # 使用用户信息进行日志记录
        user_name = user_info.get('username', 'unknown') if user_info else 'unknown'
        print(f"正在为学生 {student_id} (用户: {user_name}) 获取考试列表...")

        # 1. 优先从考试发布模块获取已发布的考试
        published_exams = get_published_exams_for_student(student_id)
        if published_exams:
            print(f"从考试发布模块获取到 {len(published_exams)} 个已发布考试")
            return published_exams

        # 2. 从客户端同步的考试列表获取（备用）- 但也要检查学生分配
        client_exams_file = get_absolute_path('client/available_exams.json')
        if os.path.exists(client_exams_file):
            print(f"从客户端考试列表文件获取: {client_exams_file}")
            try:
                with open(client_exams_file, 'r', encoding='utf-8') as f:
                    available_exams = json.load(f)

                # 获取学生分配信息
                student_assigned_exam_ids = []
                enrollments_file = get_absolute_path('exam_management/enrollments.json')
                if os.path.exists(enrollments_file):
                    with open(enrollments_file, 'r', encoding='utf-8') as f:
                        enrollments_data = json.load(f)

                    if isinstance(enrollments_data, dict) and "enrollments" in enrollments_data:
                        enrollments = enrollments_data["enrollments"]
                    elif isinstance(enrollments_data, list):
                        enrollments = enrollments_data
                    else:
                        enrollments = []

                    for enrollment in enrollments:
                        if "user_ids" in enrollment:
                            if student_id in enrollment.get("user_ids", []):
                                student_assigned_exam_ids.append(enrollment.get("exam_id"))
                        elif enrollment.get('student_id') == student_id:
                            student_assigned_exam_ids.append(enrollment.get('exam_id'))

                exams_data = []
                for exam in available_exams:
                    # 只返回学生被分配的考试
                    if (exam.get('status') == 'available' and
                        exam.get('exam_id') in student_assigned_exam_ids):
                        exams_data.append({
                            "id": exam.get("exam_id"),
                            "name": exam.get("title"),
                            "status": "available",
                            "description": exam.get("description", ""),
                            "time_limit": exam.get("time_limit", 60),
                            "total_score": exam.get("total_score", 100),
                            "exam_type": "published"  # 标记为已发布考试
                        })

                if exams_data:
                    print(f"从客户端考试列表获取到 {len(exams_data)} 个已分配考试")
                    return exams_data
            except Exception as e:
                print(f"读取客户端考试列表失败: {e}")

        # 3. 最后尝试从已发布考试系统获取（不使用样例考试）
        print("尝试从已发布考试系统获取...")

        # 检查注册信息
        enrolled_exam_ids = []
        enrollments_file_path = get_absolute_path('exam_management/enrollments.json')
        if os.path.exists(enrollments_file_path):
            with open(enrollments_file_path, 'r', encoding='utf-8') as f:
                enrollments_data = json.load(f)
                enrollments = enrollments_data.get("enrollments", [])
                for enrollment in enrollments:
                    user_ids = enrollment.get("user_ids", [])
                    if str(student_id) in [str(uid) for uid in user_ids]:
                        enrolled_exam_ids.append(enrollment.get("exam_id"))

        # 优先从已发布考试获取
        exams_data = []
        published_exams_file = get_absolute_path('exam_management/published_exams.json')
        if os.path.exists(published_exams_file):
            with open(published_exams_file, 'r', encoding='utf-8') as f:
                published_exams = json.load(f)

                for exam in published_exams:
                    # 只返回已发布且学生被分配的考试
                    if (exam.get("status") == "published" and
                        exam.get("id") in enrolled_exam_ids):
                        exams_data.append({
                            "id": exam.get("id"),
                            "name": exam.get("title"),
                            "status": "available",
                            "description": exam.get("description", ""),
                            "time_limit": exam.get("duration", 60),
                            "total_score": exam.get("total_score", 100),
                            "exam_type": "published"
                        })

                if exams_data:
                    print(f"从已发布考试系统获取到 {len(exams_data)} 个考试")
                    return exams_data

        # 4. 最后的备用：从样例考试系统获取（仅当没有已发布考试时）
        print("没有已发布考试，尝试从样例考试系统获取...")
        exams_file_path = get_absolute_path('exam_management/exams.json')
        if os.path.exists(exams_file_path):
            with open(exams_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                server_exams = data if isinstance(data, list) else data.get("exams", [])

                for exam in server_exams:
                    # 如果有注册限制，检查是否已注册
                    if enrolled_exam_ids and exam.get("id") not in enrolled_exam_ids:
                        continue

                    if exam.get("status") == "archived":
                        continue

                    # 状态映射
                    if exam.get("status") in ["published", "ongoing", "available"]:
                        status = "available"
                    elif exam.get("status") == "completed":
                        status = "completed"
                    elif exam.get("status") == "draft":
                        status = "draft"
                    else:
                        status = exam.get("status", "available")

                    exams_data.append({
                        "id": exam.get("id"),
                        "name": exam.get("name") or exam.get("title"),
                        "status": status,
                        "description": exam.get("description", ""),
                        "time_limit": exam.get("time_limit", 60),
                        "total_score": exam.get("total_score", 100)
                    })

        # 3. 如果还是没有考试，创建一个示例考试（用于测试）
        if not exams_data:
            print("没有找到考试数据，创建示例考试用于测试...")
            exams_data = [{
                "id": "demo_exam_001",
                "name": "系统测试考试",
                "status": "available",
                "description": "这是一个系统测试考试，用于验证考试功能。",
                "time_limit": 30,
                "total_score": 100
            }]

        print(f"最终获取到 {len(exams_data)} 个考试")
        return exams_data

    except Exception as e:
        print(f"获取考试列表失败: {e}")
        # 返回一个默认的测试考试
        return [{
            "id": "error_recovery_exam",
            "name": "错误恢复测试考试",
            "status": "available",
            "description": "系统在获取考试列表时遇到错误，这是一个恢复用的测试考试。",
            "time_limit": 30,
            "total_score": 100
        }]


def get_paper_from_question_bank(paper_id_or_exam_id):
    """
    从题库数据库获取试卷详情和题目
    支持UUID格式的paper_id和传统的数字ID
    """
    try:
        # 尝试确定paper_id
        paper_id = None

        # 1. 如果是UUID格式，直接使用
        if isinstance(paper_id_or_exam_id, str) and len(paper_id_or_exam_id) > 20 and '-' in paper_id_or_exam_id:
            paper_id = paper_id_or_exam_id
            print(f"使用UUID格式的paper_id: {paper_id}")

        # 2. 如果是exam_数字格式，提取数字
        elif isinstance(paper_id_or_exam_id, str) and paper_id_or_exam_id.startswith("exam_"):
            parts = paper_id_or_exam_id.split("_")
            if len(parts) >= 2:
                try:
                    paper_id = int(parts[1])
                    print(f"从exam_id提取到数字paper_id: {paper_id}")
                except ValueError:
                    pass

        # 3. 如果是纯数字，直接使用
        elif isinstance(paper_id_or_exam_id, (int, str)) and str(paper_id_or_exam_id).isdigit():
            paper_id = int(paper_id_or_exam_id)
            print(f"使用数字paper_id: {paper_id}")

        if paper_id is None:
            print(f"无法识别paper_id格式: {paper_id_or_exam_id}")
            return None

        # 连接题库数据库
        db_path = get_absolute_path('question_bank_web/local_dev.db')
        if not os.path.exists(db_path):
            print(f"题库数据库不存在: {db_path}")
            return None

        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 获取试卷信息
        cursor.execute("""
            SELECT id, name, description, duration, total_score
            FROM papers
            WHERE id = ?
        """, (paper_id,))

        paper = cursor.fetchone()
        if not paper:
            print(f"未找到试卷 ID: {paper_id}")
            conn.close()
            return None

        print(f"找到试卷: {paper[1]}")  # paper[1] 是 name 列

        # 获取试卷的题目
        cursor.execute("""
            SELECT q.id, q.stem, q.question_type_code, q.option_a, q.option_b,
                   q.option_c, q.option_d, q.option_e, q.correct_answer,
                   pq.score, pq.question_order
            FROM questions q
            JOIN paper_questions pq ON q.id = pq.question_id
            WHERE pq.paper_id = ?
            ORDER BY pq.question_order
        """, (paper_id,))

        questions_data = cursor.fetchall()
        conn.close()

        if not questions_data:
            print(f"试卷 {paper_id} 没有题目")
            return None

        # 转换题目格式
        questions = []
        for q in questions_data:
            # 映射题目类型
            question_type_map = {
                'A': 'single_choice',
                'B': 'multiple_choice',
                'C': 'true_false',
                'D': 'fill_blank',
                'E': 'essay'
            }

            # 使用索引访问而不是字典键
            question_type = question_type_map.get(q[2], 'single_choice')  # q[2] 是 question_type_code

            question = {
                "id": q[0],  # q[0] 是 id
                "type": question_type,
                "content": q[1] or "题目内容",  # q[1] 是 stem
                "score": q[9] or 10,  # q[9] 是 score，默认10分
                "order": q[10]  # q[10] 是 question_order
            }

            # 处理选择题的选项
            if question_type in ['single_choice', 'multiple_choice']:
                options = []
                # q[3] 到 q[7] 是 option_a 到 option_e
                for i in range(3, 8):
                    option_value = q[i]
                    if option_value and option_value.strip():
                        options.append(option_value.strip())
                question["options"] = options

            # 注意：不在客户端暴露正确答案
            questions.append(question)

        # 构建考试详情
        exam_details = {
            "id": paper_id_or_exam_id,
            "paper_id": paper_id,
            "title": paper[1],  # paper[1] 是 name
            "name": paper[1],   # paper[1] 是 name
            "description": paper[2] or "请认真作答，注意考试时间。",  # paper[2] 是 description
            "duration": paper[3] or 60,  # paper[3] 是 duration
            "total_score": paper[4] or 100,  # paper[4] 是 total_score
            "pass_score": 60,  # 默认及格分
            "questions": questions,
            "question_count": len(questions)
        }

        print(f"成功从题库获取试卷: {paper['title']}, 共 {len(questions)} 道题")
        return exam_details

    except Exception as e:
        print(f"从题库获取试卷失败: {e}")
        return None


def get_exam_from_client_data(exam_id):
    """
    从客户端数据获取考试详情
    """
    try:
        # 尝试从客户端考试列表获取基本信息
        client_exams_file = get_absolute_path('client/available_exams.json')
        if os.path.exists(client_exams_file):
            with open(client_exams_file, 'r', encoding='utf-8') as f:
                available_exams = json.load(f)

            for exam in available_exams:
                if exam.get('exam_id') == exam_id or exam.get('paper_id') == exam_id:
                    # 创建基本的考试详情
                    exam_details = {
                        "id": exam_id,
                        "name": exam.get('title', '考试'),
                        "description": exam.get('description', '请认真作答'),
                        "duration": exam.get('time_limit', 60),
                        "total_score": exam.get('total_score', 100),
                        "pass_score": 60,
                        "questions": create_sample_questions(),  # 创建示例题目
                        "question_count": 5
                    }
                    return exam_details

        return None

    except Exception as e:
        print(f"从客户端数据获取考试详情失败: {e}")
        return None


def create_sample_questions():
    """
    创建示例题目（当无法从题库获取真实题目时使用）
    """
    return [
        {
            "id": "sample_1",
            "type": "single_choice",
            "content": "这是一道单选题示例，请选择正确答案。",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "score": 20,
            "order": 1
        },
        {
            "id": "sample_2",
            "type": "multiple_choice",
            "content": "这是一道多选题示例，请选择所有正确答案。",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "score": 20,
            "order": 2
        },
        {
            "id": "sample_3",
            "type": "true_false",
            "content": "这是一道判断题示例，请判断对错。",
            "score": 20,
            "order": 3
        },
        {
            "id": "sample_4",
            "type": "fill_blank",
            "content": "这是一道填空题示例，请填写答案：______。",
            "score": 20,
            "order": 4
        },
        {
            "id": "sample_5",
            "type": "essay",
            "content": "这是一道简答题示例，请简要回答。",
            "score": 20,
            "order": 5
        }
    ]


def submit_exam_result(exam_id, user_info, answers, exam_duration):
    """
    提交考试结果
    :param exam_id: 考试ID
    :param user_info: 用户信息
    :param answers: 答案字典 {question_id: answer}
    :param exam_duration: 考试用时（秒）
    :return: 提交结果
    """
    try:
        print(f"正在提交考试结果: 考试ID={exam_id}, 用户={user_info.get('username')}")

        # 构建考试结果数据
        exam_result = {
            "exam_id": exam_id,
            "user_id": user_info.get('id'),
            "user_name": user_info.get('real_name') or user_info.get('username'),
            "username": user_info.get('username'),
            "department": user_info.get('department', ''),
            "answers": answers,
            "exam_duration": exam_duration,
            "submit_time": datetime.now().isoformat(),
            "status": "submitted",
            "client_info": {
                "submit_method": "client_app",
                "timestamp": datetime.now().isoformat()
            }
        }

        # 1. 保存到本地结果目录
        results_dir = get_absolute_path('exam_management/results')
        os.makedirs(results_dir, exist_ok=True)

        result_filename = f"result_{exam_id}_{user_info.get('id')}_{int(datetime.now().timestamp())}.json"
        result_file_path = os.path.join(results_dir, result_filename)

        with open(result_file_path, 'w', encoding='utf-8') as f:
            json.dump(exam_result, f, ensure_ascii=False, indent=2)

        print(f"考试结果已保存到本地: {result_file_path}")

        # 2. 尝试提交到数据同步管理器
        try:
            # 导入数据同步管理器
            sys.path.append(get_absolute_path('common'))
            from common.data_sync_manager import DataSyncManager

            sync_manager = DataSyncManager()
            success = sync_manager.submit_exam_result(exam_result)

            if success:
                print("考试结果已成功提交到阅卷系统")
                return {
                    "success": True,
                    "message": "考试结果提交成功，请等待阅卷结果。",
                    "result_id": result_filename
                }
            else:
                print("提交到阅卷系统失败，但已保存到本地")

        except Exception as e:
            print(f"调用数据同步管理器失败: {e}")

        # 3. 如果同步管理器不可用，直接保存到阅卷队列
        grading_queue_dir = get_absolute_path('grading_center/queue')
        os.makedirs(grading_queue_dir, exist_ok=True)

        queue_filename = f"pending_{int(datetime.now().timestamp())}_{user_info.get('id')}.json"
        queue_file_path = os.path.join(grading_queue_dir, queue_filename)

        with open(queue_file_path, 'w', encoding='utf-8') as f:
            json.dump(exam_result, f, ensure_ascii=False, indent=2)

        print(f"考试结果已添加到阅卷队列: {queue_file_path}")

        return {
            "success": True,
            "message": "考试结果提交成功，已加入阅卷队列。",
            "result_id": result_filename,
            "queue_id": queue_filename
        }

    except Exception as e:
        print(f"提交考试结果失败: {e}")
        return {
            "success": False,
            "message": f"提交失败: {str(e)}",
            "error": str(e)
        }


def get_exam_result_status(exam_id, user_id):
    """
    查询考试结果状态
    :param exam_id: 考试ID
    :param user_id: 用户ID
    :return: 结果状态
    """
    try:
        # 检查是否有已完成的阅卷结果
        graded_dir = get_absolute_path('grading_center/graded')
        if os.path.exists(graded_dir):
            for filename in os.listdir(graded_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(graded_dir, filename), 'r', encoding='utf-8') as f:
                            result = json.load(f)

                        if (result.get('exam_id') == exam_id and
                            str(result.get('user_id')) == str(user_id)):
                            return {
                                "status": "graded",
                                "score": result.get('final_score'),
                                "total_score": result.get('total_score'),
                                "grading_time": result.get('grading_time'),
                                "details": result.get('question_scores', [])
                            }
                    except Exception as e:
                        print(f"读取阅卷结果文件失败 {filename}: {e}")

        # 检查是否在阅卷队列中
        queue_dir = get_absolute_path('grading_center/queue')
        if os.path.exists(queue_dir):
            for filename in os.listdir(queue_dir):
                if filename.endswith('.json') and str(user_id) in filename:
                    return {
                        "status": "pending_grading",
                        "message": "考试结果已提交，正在等待阅卷。"
                    }

        # 检查本地结果目录
        results_dir = get_absolute_path('exam_management/results')
        if os.path.exists(results_dir):
            for filename in os.listdir(results_dir):
                if (filename.startswith(f"result_{exam_id}_{user_id}_") and
                    filename.endswith('.json')):
                    return {
                        "status": "submitted",
                        "message": "考试结果已提交，正在处理中。"
                    }

        return {
            "status": "not_found",
            "message": "未找到考试结果。"
        }

    except Exception as e:
        print(f"查询考试结果状态失败: {e}")
        return {
            "status": "error",
            "message": f"查询失败: {str(e)}"
        }

def get_paper_id_from_published_exam(exam_id):
    """
    从已发布考试中获取paper_id
    """
    try:
        # 1. 从已发布考试文件获取
        published_exams_file = get_absolute_path('exam_management/published_exams.json')
        if os.path.exists(published_exams_file):
            with open(published_exams_file, 'r', encoding='utf-8') as f:
                published_exams = json.load(f)

            for exam in published_exams:
                if exam.get('id') == exam_id:
                    return exam.get('paper_id')

        # 2. 从客户端考试列表获取
        client_exams_file = get_absolute_path('client/available_exams.json')
        if os.path.exists(client_exams_file):
            with open(client_exams_file, 'r', encoding='utf-8') as f:
                client_exams = json.load(f)

            for exam in client_exams:
                if exam.get('exam_id') == exam_id:
                    return exam.get('paper_id')

        return None

    except Exception as e:
        print(f"获取paper_id失败: {e}")
        return None


def get_exam_details(exam_id):
    """
    获取考试详情，包括试题内容
    优先从题库数据库获取真实题目，如果失败则使用模拟数据
    :param exam_id: 考试ID
    :return: 考试详情
    """
    logger.info(f"获取考试ID {exam_id} 的详情...")
    logger.debug("=== 调试信息：开始获取考试详情 ===")

    # 记录当前工作目录，便于调试
    logger.debug(f"当前工作目录: {os.getcwd()}")

    try:
        # 1. 首先尝试从已发布考试获取paper_id，然后从题库获取真实题目
        paper_id = get_paper_id_from_published_exam(exam_id)
        if paper_id:
            print(f"从已发布考试获取到paper_id: {paper_id}")
            paper_details = get_paper_from_question_bank(paper_id)
            if paper_details:
                print(f"从题库数据库获取到考试详情: {paper_details.get('title')}")
                return paper_details

        # 2. 如果上述方法失败，尝试直接用exam_id从题库获取
        paper_details = get_paper_from_question_bank(exam_id)
        if paper_details:
            print(f"从题库数据库获取到考试详情: {paper_details.get('title')}")
            return paper_details

        # 3. 如果题库中没有，尝试从客户端同步的考试数据获取
        client_exam_details = get_exam_from_client_data(exam_id)
        if client_exam_details:
            print(f"从客户端数据获取到考试详情: {client_exam_details.get('name')}")
            return client_exam_details

        # 3. 特殊处理admin用户的考试详情
        if exam_id in [901, 902, 903]:  # admin用户的考试ID
            print(f"检测到管理员考试ID {exam_id}，返回管理员专用考试详情")
            admin_exam_details = {
            "id": exam_id,
            "name": "管理员测试考试" if exam_id == 901 else "系统性能评估" if exam_id == 902 else "用户体验测试",
            "duration": 60,  # 考试时长（分钟）
            "total_score": 100,  # 总分
            "pass_score": 60,  # 及格分
            "questions": [
                {
                    "id": f"{exam_id}_1",
                    "type": "single_choice",
                    "content": "这是一个管理员测试题目，请选择正确答案。",
                    "options": ["选项A", "选项B", "选项C", "选项D"],
                    "answer": "选项A",
                    "score": 20
                },
                {
                    "id": f"{exam_id}_2",
                    "type": "multiple_choice",
                    "content": "这是一个多选题，请选择所有正确答案。",
                    "options": ["选项A", "选项B", "选项C", "选项D"],
                    "answer": ["选项A", "选项C"],
                    "score": 20
                },
                {
                    "id": f"{exam_id}_3",
                    "type": "true_false",
                    "content": "这是一个判断题，请判断对错。",
                    "answer": True,
                    "score": 20
                },
                {
                    "id": f"{exam_id}_4",
                    "type": "fill_blank",
                    "content": "这是一个填空题，请填写正确答案。",
                    "answer": "正确答案",
                    "score": 20
                },
                {
                    "id": f"{exam_id}_5",
                    "type": "essay",
                    "content": "这是一个简答题，请简要回答。",
                    "answer": "这是参考答案",
                    "score": 20
                }
            ]
            }
            return admin_exam_details

        # 4. 尝试从服务器获取考试详情
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
                        elif "question_ids" in exam and exam["question_ids"]:
                            # 如果考试有question_ids字段，从question_bank_web获取题目
                            question_ids = exam["question_ids"]
                            logger.info(f"考试 {exam_id} 包含 {len(question_ids)} 个题目ID，正在从题库获取题目...")
                            
                            # 从question_bank_web获取题目
                            try:
                                # 实际项目中应该使用requests库发送HTTP请求
                                import requests
                                questions = []
                                
                                # 获取question_bank_web的基础URL
                                question_bank_url = "http://localhost:5000"
                                
                                # 尝试批量获取题目
                                try:
                                    # 构建批量请求URL
                                    batch_url = f"{question_bank_url}/api/questions"
                                    # 将question_ids作为参数传递
                                    params = {"ids": ",".join(question_ids)}
                                    
                                    logger.debug(f"尝试批量获取题目，URL: {batch_url}, 参数: {params}")
                                    
                                    # 发送请求
                                    response = requests.get(batch_url, params=params)
                                    
                                    # 检查响应状态
                                    if response.status_code == 200:
                                        # 解析响应数据
                                        data = response.json()
                                        questions = data.get("questions", [])
                                        logger.info(f"成功批量获取了 {len(questions)} 道题目")
                                    else:
                                        logger.warning(f"批量获取题目失败，状态码: {response.status_code}")
                                        # 如果批量获取失败，回退到单个获取
                                        raise Exception("批量获取题目失败")
                                        
                                except Exception as batch_error:
                                    logger.warning(f"批量获取题目失败，将尝试单个获取: {batch_error}")
                                    
                                    # 如果批量获取失败，尝试单个获取
                                    for q_id in question_ids:
                                        try:
                                            # 构建单个请求URL
                                            single_url = f"{question_bank_url}/api/questions/{q_id}"
                                            logger.debug(f"尝试获取题目，URL: {single_url}")
                                            
                                            # 发送请求
                                            response = requests.get(single_url)
                                            
                                            # 检查响应状态
                                            if response.status_code == 200:
                                                # 解析响应数据
                                                question = response.json()
                                                questions.append(question)
                                                logger.debug(f"成功获取题目 {q_id}")
                                            else:
                                                logger.warning(f"获取题目 {q_id} 失败，状态码: {response.status_code}")
                                                # 创建一个模拟题目作为后备
                                                question = {
                                                    "id": q_id,
                                                    "type": "single_choice",
                                                    "content": f"题目ID为 {q_id} 的内容（获取失败）",
                                                    "options": ["选项A", "选项B", "选项C", "选项D"],
                                                    "answer": "选项A",
                                                    "score": 1
                                                }
                                                questions.append(question)
                                        except Exception as single_error:
                                            logger.error(f"获取题目 {q_id} 失败: {single_error}")
                                            # 创建一个模拟题目作为后备
                                            question = {
                                                "id": q_id,
                                                "type": "single_choice",
                                                "content": f"题目ID为 {q_id} 的内容（获取失败）",
                                                "options": ["选项A", "选项B", "选项C", "选项D"],
                                                "answer": "选项A",
                                                "score": 1
                                            }
                                            questions.append(question)
                                
                                logger.info(f"从题库获取了 {len(questions)} 道题目")
                                
                                # 如果没有成功获取任何题目，使用模拟数据
                                if not questions:
                                    logger.warning("未能从题库获取任何题目，将使用模拟数据")
                                    for q_id in question_ids:
                                        # 创建一个模拟题目
                                        question = {
                                            "id": q_id,
                                            "type": "single_choice",
                                            "content": f"题目ID为 {q_id} 的内容（模拟数据）",
                                            "options": ["选项A", "选项B", "选项C", "选项D"],
                                            "answer": "选项A",
                                            "score": 1
                                        }
                                        questions.append(question)
                            except Exception as e:
                                logger.error(f"从题库获取题目失败: {e}")
                        elif "paper_id" in exam:
                            # 如果考试引用了试卷ID，尝试从papers.json加载试卷
                            paper_id = exam["paper_id"]
                            papers_file_path = get_absolute_path('exam_management/papers.json')
                            
                            logger.info(f"考试 {exam_id} 引用了试卷ID: {paper_id}，正在加载试卷内容...")
                            
                            # 检查paper_id是否为UUID格式
                            import re
                            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
                            
                            # 记录试卷ID和试卷文件路径
                            logger.debug(f"试卷ID: {paper_id}, 试卷文件路径: {papers_file_path}")
                            
                            # 首先尝试直接按ID查找试卷
                            found_paper = False
                            if os.path.exists(papers_file_path):
                                with open(papers_file_path, 'r', encoding='utf-8') as pf:
                                    papers_data = json.load(pf)
                                    papers = papers_data.get("papers", [])
                                    logger.debug(f"试卷文件中共有 {len(papers)} 套试卷")
                                    
                                    # 遍历所有试卷，查找匹配的ID
                                    for i, paper in enumerate(papers):
                                        paper_id_in_file = paper.get("id")
                                        logger.debug(f"检查第 {i+1} 套试卷，ID: {paper_id_in_file}, 名称: {paper.get('name')}")
                                        # 确保ID比较时都是字符串类型
                                        if str(paper.get("id")) == str(paper_id):
                                            logger.info(f"找到匹配的试卷: {paper.get('name')}")
                                            questions = paper.get("questions", [])
                                            logger.debug(f"试卷 '{paper.get('name')}' 包含 {len(questions)} 道题目")
                                            # 如果试卷中有总分和及格分信息，优先使用
                                            if "total_score" in paper:
                                                total_score = paper["total_score"]
                                            if "pass_score" in paper:
                                                pass_score = paper["pass_score"]
                                            found_paper = True
                                            break
                            
                            # 如果没有找到对应的试卷，检查是否是UUID格式
                            if not found_paper and uuid_pattern.match(str(paper_id)):
                                logger.warning(f"未找到试卷ID {paper_id}，但检测到UUID格式，尝试再次查找")
                                # 再次尝试查找UUID格式的试卷ID
                                if os.path.exists(papers_file_path):
                                    try:
                                        with open(papers_file_path, 'r', encoding='utf-8') as pf:
                                            papers_data = json.load(pf)
                                            papers = papers_data.get("papers", [])
                                            # 遍历所有试卷，查找匹配的UUID
                                            for i, paper in enumerate(papers):
                                                # 检查试卷是否有id字段，且是否为UUID格式
                                                paper_id_in_file = paper.get("id")
                                                if str(paper_id_in_file) == str(paper_id):
                                                    logger.info(f"找到匹配的UUID试卷: {paper.get('name')}")
                                                    questions = paper.get("questions", [])
                                                    logger.debug(f"UUID试卷 '{paper.get('name')}' 包含 {len(questions)} 道题目")
                                                    # 如果试卷中有总分和及格分信息，优先使用
                                                    if "total_score" in paper:
                                                        total_score = paper["total_score"]
                                                    if "pass_score" in paper:
                                                        pass_score = paper["pass_score"]
                                                    found_paper = True
                                                    break
                                            
                                            # 如果仍未找到匹配的UUID试卷，则记录警告
                                            if not found_paper:
                                                logger.warning(f"在papers.json中未找到匹配的UUID试卷ID: {paper_id}")
                                    except Exception as e:
                                        logger.error(f"读取UUID试卷数据失败: {e}")
                            
                            # 如果仍然没有找到试卷，记录警告但不使用默认试卷
                            if not found_paper:
                                logger.warning(f"未找到试卷ID {paper_id}，无法加载试卷内容")
                        
                        # 返回考试详情
                        result = {
                            "id": exam.get("id"),
                            "name": exam.get("name"),
                            "duration": exam.get("duration_minutes", 60),  # 考试时长（分钟）
                            "total_score": total_score,            # 试卷总分
                            "pass_score": pass_score,              # 及格分数
                            "questions": questions
                        }
                        
                        # 使用logger记录调试信息
                        logger.debug(f"=== 考试详情获取成功 ===")
                        logger.debug(f"考试名称: {result['name']}")
                        logger.debug(f"试题数量: {len(questions)}")
                        if questions:
                            logger.debug(f"第一道题: {questions[0].get('content', '无内容')}")
                        
                        return result
        
        # 如果没有找到考试数据，返回错误信息
        logger.error(f"未找到考试ID {exam_id} 的数据")
        return {
            "id": exam_id,
            "name": f"未找到考试ID {exam_id} 的数据",
            "duration": 60,  # 考试时长（分钟）
            "total_score": 0,  # 试卷总分
            "pass_score": 0,   # 及格分数
            "questions": [],
            "error": "未找到考试数据"
        }
    
    except Exception as e:
        logger.error(f"获取考试详情失败: {e}")
        # 发生错误时返回错误信息
        return {
            "id": exam_id,
            "name": f"获取考试详情失败: {e}",
            "duration": 60,  # 考试时长（分钟）
            "total_score": 0,  # 试卷总分
            "pass_score": 0,   # 及格分数
            "questions": [],
            "error": f"获取考试详情失败: {e}"
        }

def submit_answers(exam_id, student_id, answers):
    """
    提交考试答案
    :param exam_id: 考试ID
    :param student_id: 学生ID
    :param answers: 答案字典，格式为 {question_id: answer}
    :return: 提交结果
    """
    logger.info(f"提交考试ID {exam_id} 的答案，学生ID: {student_id}")
    logger.debug(f"答案内容: {answers}")
    
    # 特殊处理admin用户的考试答案提交
    if exam_id in [901, 902, 903] and student_id == 999:  # admin用户的考试ID和用户ID
        print(f"检测到管理员考试ID {exam_id} 的答案提交，特殊处理")
        # 管理员考试总是返回满分
        return {"success": True, "message": "管理员测试答案提交成功", "score": 100}
    
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
        
        logger.info(f"答案已保存到文件: {filename}")
        return {"success": True, "message": "答案提交成功", "score": score}
    
    except Exception as e:
        logger.error(f"提交答案失败: {e}")
        return {"success": False, "message": f"答案提交失败: {str(e)}"}