#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import get_db
from models import Question

def check_question_order():
    db = get_db()
    questions = db.query(Question).order_by(Question.id.desc()).limit(20).all()
    
    print('前20个题目的ID和题型:')
    for i, q in enumerate(questions, 1):
        clean_id = q.id.split('#')[0] if '#' in q.id else q.id
        print(f'{i:2d}. {clean_id} - {q.question_type_code}')

if __name__ == '__main__':
    check_question_order()
