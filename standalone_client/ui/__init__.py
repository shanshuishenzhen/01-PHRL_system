#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户界面模块

包含所有的用户界面组件和视图。
"""

from .login import LoginView
from .components import *

# 延迟导入其他UI模块，避免循环导入
def get_exam_list_view():
    from .exam_list import ExamListView
    return ExamListView

def get_exam_window_view():
    from .exam_window import ExamWindowView
    return ExamWindowView

__all__ = [
    'LoginView',
    'get_exam_list_view',
    'get_exam_window_view'
]
