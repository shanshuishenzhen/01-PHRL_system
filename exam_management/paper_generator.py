# -*- coding: utf-8 -*-
import json
import random
from collections import defaultdict

class PaperGenerationError(Exception):
    """自定义异常，用于表示组卷过程中发生的错误。"""
    pass

# 修正1：添加必要的属性初始化
class PaperGenerator:
    def __init__(self, all_questions):
        self.all_questions = all_questions
        self.paper_questions = []  # 新增试卷题目初始化
        self.template_knowledge_points = {'C-A-A': 0.6}  # 新增模板知识点

    def generate_validation_report(self):
        report_dir = r'd:\01-PHRL_system\temp_validation'
        
        # 新增NTFS权限检查
        try:
            test_file = os.path.join(report_dir, 'test_permission.txt')
            with open(test_file, 'w') as f:
                f.write('permission_test')
            os.remove(test_file)
        except PermissionError as e:
            print(f"[权限错误] 目录无写入权限: {report_dir}")
            print(f"[解决方案] 请以管理员身份运行: {r'icacls "d:\01-PHRL_system\temp_validation" /grant Everyone:(OI)(CI)F /T /C'}")
            return None
        
        # 新增防病毒软件检测
        print("[安全软件检测] 请暂时禁用以下进程:")
        try:
            import psutil
            print("以下是正在运行的Python进程路径:")
            for proc in psutil.process_iter(['name', 'exe']):
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    print(proc.info['exe'])
        except ImportError:
            print("[警告] 缺少psutil库，请使用 'pip install psutil' 安装后再运行此功能")
        
import psutil
print("当前运行的Python进程:")
for proc in psutil.process_iter(['pid', 'name', 'exe']):
    exe = proc.info.get('exe')
    if exe and 'python' in exe:
        print(proc.info)

        diff_report = {
            '试卷ID': [],
            '题目数量差异': [],
            '三级代码比例（模板）': [],
            '三级代码比例（试卷）': [],
            '比例差异值': [],
            '知识点覆盖率': [],
            '难度系数偏差': []
        }
        
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
                # 增加模板结构验证
                if 'blueprint' not in template:
                    raise PaperGenerationError("模板缺少核心blueprint字段")
                    
                for l1 in template['blueprint']:
                    for l2 in l1.get('children', []):
                        for l3 in l2.get('children', []):
                            # 增加必要字段检查
                            if 'code' not in l3 or 'questions' not in l3:
                                continue
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

        def build_paper_from_blueprint(self, template_path, validation_mode=False):
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
                
            if validation_mode:
                with open('temp_output.json', 'w') as f:
                    json.dump(generated_data, f, indent=2)
            return generated_question_ids

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

def validate_papers(template_path):
    diff_report = {
        '试卷ID': [],
        '题目数量差异': [],
        '三级代码比例（模板）': [],  # 新增
        '三级代码比例（模板）': [],  # 新增
        '比例差异值': [],          # 新增
        '知识点覆盖率': [],
        '难度系数偏差': []
    }

    # 在验证逻辑中添加以下代码
    # 问题1：未正确初始化paper_questions和template_knowledge_points
    paper_questions = self.paper_questions  # self.paper_questions未定义
    
    template_knowledge_points = self.template_knowledge_points  # 该属性不存在
    
    # 问题2：CSV表头与数据列不匹配
    writer.writerow(['试卷ID', '题目总数差异', '三级代码比例（试卷）', ...])  # 表头有8列
    diff_report字段只有7列数据
    
    # 计算三级代码比例
    template_codes = [c for c in template_knowledge_points if len(c.split('-')) >= 3]
    paper_codes = [q['knowledge_code'] for q in paper_questions if len(q['knowledge_code'].split('-')) >= 3]
    
    template_ratio = len(template_codes)/len(template_knowledge_points) if template_knowledge_points else 0
    paper_ratio = len(paper_codes)/len(paper_questions) if paper_questions else 0
    
    diff_report['三级代码比例（模板）'].append(round(template_ratio, 4))
    diff_report['三级代码比例（试卷）'].append(round(paper_ratio, 4))
    diff_report['比例差异值'].append(round(paper_ratio - template_ratio, 4))

    # 添加CSV报告生成
    from datetime import datetime
    import os
    
    report_dir = r'd:\01-PHRL_system\temp_validation'
    report_path = os.path.join(report_dir, f'validation_report_{datetime.now().strftime("%Y%m%d")}.csv')
    print(f'准备写入目录：{report_dir}')
    print(f'当前diff_report记录数：{len(diff_report)}')
    
    # 正确定义字段名称
    fieldnames = [
        '试卷ID', 
        '题目总数差异',
        '三级代码比例（试卷）',
        '三级代码比例（模板）',
        '比例差异值'
    ]

    try:
        # ... existing file writing logic ...
        
        # 新增最终验证
        if os.path.exists(final_path):
            print(f"[SUCCESS] 文件已生成: {final_path}")
            return final_path
        print(f"[ERROR] 文件未生成: {final_path}")
        return None

    except Exception as e:
        # 增强异常信息
        print(f"[CRITICAL ERROR] 文件操作失败: {str(e)}")
        print(f"[TRACEBACK] {traceback.format_exc()}")
        return None
        
        f.flush()
        
        # 双重验证文件
        if os.path.exists(report_path):
            file_stats = os.stat(report_path)
            if file_stats.st_size > 0:
                print(f'✅ 文件验证通过 | 路径: {report_path} | 大小: {file_stats.st_size}字节')
                return report_path
        
        print(f'❌ 文件生成异常: {report_path}')
        return None
        
    except Exception as e:
        print(f'🔥 关键错误: {e.__class__.__name__}: {str(e)}')
        return None

    print(f"正在生成验证报告到: {report_path}")
    print(f"三级代码比例（模板）: {template_ratio}")
    print(f"三级代码比例（试卷）: {paper_ratio}")

if __name__ == '__main__':
    import os
    example_usage()