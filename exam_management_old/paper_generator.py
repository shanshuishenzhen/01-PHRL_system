# -*- coding: utf-8 -*-
import json
import random
from collections import defaultdict

class PaperGenerationError(Exception):
    """自定义异常，用于表示组卷过程中发生的错误。"""
    pass

class PaperGenerator:
    """
    智能组卷器
    负责根据指定的模板从题库中抽取题目，生成试卷。
    """
    def __init__(self, all_questions):
        self.all_questions = all_questions
        self.question_map = self._build_question_map()

    def _build_question_map(self):
        """
        构建一个按"题型-知识点"组织的题目映射，以加速查找。
        数据结构: { "B": { "C-A-A": [q1, q2, ...], ... }, ... }
        """
        q_map = defaultdict(lambda: defaultdict(list))
        for q in self.all_questions:
            q_type = q.get('type')
            k_point_l3 = q.get('knowledge_point_l3')
            if q_type and k_point_l3:
                q_map[q_type][k_point_l3].append(q)
        return q_map

    def generate_paper(self, template):
        """
        根据模板生成试卷。
        template: 一个描述试卷结构的字典。
        返回: 一个包含试卷题目ID的列表。
        """
        generated_question_ids = []
        
        # 模板的格式应与 aquestion_bank_blueprint.json 类似
        # 这里我们只关心三级知识点下的题目要求
        template_requirements = self._flatten_template(template)

        for req in template_requirements:
            k_point_l3 = req['knowledge_point']
            q_type = req['type']
            num_to_draw = req['count']

            if num_to_draw == 0:
                continue

            # 从预构建的映射中获取候选题目池
            candidate_pool = self.question_map.get(q_type, {}).get(k_point_l3, [])

            if len(candidate_pool) < num_to_draw:
                raise PaperGenerationError(
                    f"组卷失败：题库资源不足！\n\n"
                    f"知识点: {k_point_l3}\n"
                    f"题型: {template['question_types'].get(q_type, q_type)}\n"
                    f"要求数量: {num_to_draw}\n"
                    f"库存数量: {len(candidate_pool)}"
                )
            
            # 随机抽取指定数量的不重复题目
            drawn_questions = random.sample(candidate_pool, num_to_draw)
            generated_question_ids.extend([q['id'] for q in drawn_questions])
            
        return generated_question_ids

    def _flatten_template(self, template):
        """将层级化的模板展开为扁平的需求列表。"""
        requirements = []
        try:
            for l1 in template['blueprint']:
                for l2 in l1['children']:
                    for l3 in l2['children']:
                        k_point_l3 = l3['code']
                        for q_type, count in l3.get('questions', {}).items():
                            requirements.append({
                                'knowledge_point': k_point_l3,
                                'type': q_type,
                                'count': int(count)
                            })
        except (KeyError, TypeError) as e:
            raise PaperGenerationError(f"模板格式错误，无法解析: {e}")
            
        return requirements

# --- 这是一个使用示例，展示了如何调用该模块 ---
def example_usage():
    # 1. 加载题库
    try:
        q_bank_path = os.path.join(os.path.dirname(__file__), '..', 'question_bank_web', 'questions.json')
        with open(q_bank_path, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)['questions']
    except FileNotFoundError:
        print("错误：找不到题库文件 questions.json")
        return

    # 2. 加载一个组卷模板 (这里为了示例，直接使用总蓝图)
    try:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'developer_tools', 'question_bank_blueprint.json')
        with open(template_path, 'r', encoding='utf-8') as f:
            # 假设我们要创建一份小规模的抽查试卷，将所有题目要求数量减少
            paper_template = json.load(f)
            for l1 in paper_template['blueprint']:
                for l2 in l1['children']:
                    for l3 in l2['children']:
                        for q_type in l3['questions']:
                            # 将题目数量减少到1或0，用于测试
                            l3['questions'][q_type] = random.choice([0, 1]) 
    except FileNotFoundError:
        print("错误：找不到模板文件 question_bank_blueprint.json")
        return

    # 3. 初始化组卷器并生成试卷
    generator = PaperGenerator(all_questions)
    try:
        print("正在根据模板生成试卷...")
        paper_question_ids = generator.generate_paper(paper_template)
        print("\n组卷成功！")
        print(f"试卷总题量: {len(paper_question_ids)}")
        print("部分题目ID示例:")
        for q_id in paper_question_ids[:10]:
            print(f"  - {q_id}")

    except PaperGenerationError as e:
        print(f"\n组卷过程中发生错误:\n{e}")

if __name__ == '__main__':
    import os
    example_usage() 