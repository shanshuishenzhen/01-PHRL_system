# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import json
import os
from collections import defaultdict

app = Flask(__name__)

# --- Data Loading & Caching ---
def load_questions():
    """从 questions.json 加载并缓存题目数据。"""
    try:
        questions_path = os.path.join(os.path.dirname(__file__), 'questions.json')
        with open(questions_path, 'r', encoding='utf-8') as f:
            print("Successfully loaded questions.json")
            return json.load(f).get('questions', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading questions.json: {e}")
        return []

QUESTIONS_CACHE = load_questions()
KNOWLEDGE_TREE_CACHE = None

def get_knowledge_tree():
    """构建或从缓存中获取层级化的知识点树。"""
    global KNOWLEDGE_TREE_CACHE
    if KNOWLEDGE_TREE_CACHE is not None:
        return KNOWLEDGE_TREE_CACHE

    print("Building knowledge tree from cache...")
    tree = defaultdict(lambda: defaultdict(set))
    for q in QUESTIONS_CACHE:
        l1 = q.get('knowledge_point_l1')
        l2 = q.get('knowledge_point_l2')
        l3 = q.get('knowledge_point_l3')
        if l1 and l2 and l3:
            tree[l1][l2].add(l3)
    
    # 转换为排序后的列表
    sorted_tree = {}
    for l1, l2_map in sorted(tree.items()):
        sorted_tree[l1] = {l2: sorted(list(l3_set)) for l2, l3_set in sorted(l2_map.items())}
    
    KNOWLEDGE_TREE_CACHE = sorted_tree
    print("Knowledge tree built and cached.")
    return KNOWLEDGE_TREE_CACHE

# --- Routes ---
@app.route('/')
def index():
    """渲染主管理页面。"""
    return render_template('index.html')

@app.route('/api/knowledge-tree')
def api_knowledge_tree():
    """API 端点：返回知识点树。"""
    return jsonify(get_knowledge_tree())

@app.route('/api/questions')
def api_questions():
    """API 端点：根据筛选条件返回题目列表。"""
    # --- Corrected Pagination & Sorting ---
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 15))
    sort_by = request.args.get('sort')
    sort_order = request.args.get('order', 'asc')
    
    q_type = request.args.get('type')
    k_point_l1 = request.args.get('knowledge_point_l1')
    k_point_l2 = request.args.get('knowledge_point_l2')
    k_point_l3 = request.args.get('knowledge_point_l3')
    search_term = request.args.get('search')

    filtered_questions = QUESTIONS_CACHE

    # 应用筛选（注意筛选逻辑的层级关系）
    if k_point_l3:
        filtered_questions = [q for q in filtered_questions if q.get('knowledge_point_l3') == k_point_l3]
    elif k_point_l2:
        filtered_questions = [q for q in filtered_questions if q.get('knowledge_point_l2') == k_point_l2]
    elif k_point_l1:
        filtered_questions = [q for q in filtered_questions if q.get('knowledge_point_l1') == k_point_l1]
    
    if q_type:
        filtered_questions = [q for q in filtered_questions if q.get('type') == q_type]

    if search_term:
        search_term = search_term.lower()
        filtered_questions = [
            q for q in filtered_questions if search_term in q.get('stem', '').lower() or search_term in q.get('id', '').lower()
        ]
    
    # --- Added Sorting Logic ---
    if sort_by:
        reverse = (sort_order == 'desc')
        # 使用 .get(sort_by, '') 以安全地处理可能不存在的键
        filtered_questions = sorted(filtered_questions, key=lambda q: str(q.get(sort_by, '')), reverse=reverse)

    total = len(filtered_questions)
    # --- Corrected Pagination Logic ---
    paginated_questions = filtered_questions[offset : offset + limit]

    return jsonify({'total': total, 'rows': paginated_questions})

if __name__ == '__main__':
    get_knowledge_tree() # 在启动时预先缓存知识点树
    app.run(debug=True, port=5004) 