#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复用户ID问题
"""

import sqlite3
import uuid

def fix_user_ids():
    """为用户添加有效的ID"""
    conn = sqlite3.connect('user_management/users.db')
    cursor = conn.cursor()

    # 为student用户设置ID
    student_id = str(uuid.uuid4())
    cursor.execute('UPDATE users SET id = ? WHERE username = ?', (student_id, 'student'))

    # 为test用户设置ID  
    test_id = str(uuid.uuid4())
    cursor.execute('UPDATE users SET id = ? WHERE username = ?', (test_id, 'test'))

    conn.commit()

    # 验证更新
    cursor.execute('SELECT id, username FROM users WHERE username = ?', ('student',))
    student = cursor.fetchone()
    if student:
        print('Student用户 - ID:', student[0], ', 用户名:', student[1])

    cursor.execute('SELECT id, username FROM users WHERE username = ?', ('test',))
    test = cursor.fetchone()
    if test:
        print('Test用户 - ID:', test[0], ', 用户名:', test[1])

    conn.close()
    print('用户ID更新完成！')

if __name__ == "__main__":
    fix_user_ids()
