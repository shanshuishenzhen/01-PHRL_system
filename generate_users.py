# -*- coding: utf-8 -*-
import json
import os
import uuid
import random

# 用户数据文件路径
USER_DATA_FILE = os.path.join('user_management', 'users.json')

def create_user_entry(username, role, role_name):
    return {
        "id": str(uuid.uuid4()),
        "username": username,
        "password_hash": "123456", # 设置默认密码为123456方便调试
        "real_name": f"{role_name}_{username}",
        "role": role,
        "department": random.choice(["技术部", "市场部", "人力资源部", "后勤部"]),
        "ID": ''.join([str(random.randint(0, 9)) for _ in range(18)]) # 自动生成18位数字作为身份证号
    }

def generate_users(student=100, evaluator=0, admin=0):
    if not os.path.exists(USER_DATA_FILE):
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"users": []}, f, ensure_ascii=False, indent=4)
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = {"users": []}

    users = data.get("users", [])
    initial_user_count = len(users)
    generated_students = []

    role_map = {
        "admin": (admin, "admin", "管理员"),
        "evaluator": (evaluator, "evaluator", "考评员"),
        "student": (student, "student", "考生"),
    }

    for role_key, (count, role_val, role_name) in role_map.items():
        for i in range(count):
            username = f"{role_key}_{i+1:04d}"
            user_entry = create_user_entry(username, role_val, role_name)
            users.append(user_entry)
            if role_key == "student":
                generated_students.append(username)
    
    data["users"] = users
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    generated_count = len(users) - initial_user_count
    print(f"成功生成 {admin} 个管理员, {evaluator} 个考评员, {student} 个考生。总计: {generated_count}")
    return generated_count, generated_students

if __name__ == "__main__":
    # 生成100个用户
    generate_users(student=100, evaluator=0, admin=0)
    print("用户生成完成，请重新启动用户管理系统查看效果。")