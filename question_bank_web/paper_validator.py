#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷组题复核程序
用于分析试卷的三级代码比例并生成对比Excel表格
"""

import pandas as pd
import os
from collections import defaultdict, Counter
from datetime import datetime
from models import Paper, PaperQuestion, Question
import json

# 导入数据库连接函数
def get_db():
    """获取数据库会话"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # 数据库配置
    DATABASE_URL = "sqlite:///questions.db"
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return SessionLocal()

def close_db(db):
    """关闭数据库会话"""
    if db:
        db.close()

class PaperValidator:
    """试卷组题验证器"""
    
    def __init__(self):
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    def validate_paper_composition(self, paper_id, template_path=None, output_dir="paper_validation_reports"):
        """
        验证试卷组题结果，分析三级代码比例
        
        Args:
            paper_id: 试卷ID
            template_path: 组题模板文件路径（可选）
            output_dir: 验证报告输出目录
        
        Returns:
            dict: 验证结果
        """
        print(f"开始验证试卷 {paper_id} 的组题结果...")
        
        # 1. 获取试卷信息和题目
        paper_info = self._get_paper_info(paper_id)
        if not paper_info:
            return {"status": "error", "message": "无法获取试卷信息"}
        
        # 2. 分析试卷的三级代码分布
        paper_analysis = self._analyze_paper_composition(paper_info)
        
        # 3. 如果提供了模板，加载并分析模板要求
        template_analysis = None
        if template_path and os.path.exists(template_path):
            template_analysis = self._analyze_template_requirements(template_path)
        
        # 4. 生成对比报告
        report_path = self._generate_paper_validation_report(
            paper_info, paper_analysis, template_analysis, output_dir
        )
        
        # 5. 返回结果
        result = {
            "status": "success",
            "paper_id": paper_id,
            "paper_name": paper_info["name"],
            "total_questions": paper_analysis["total_questions"],
            "l3_code_distribution": paper_analysis["l3_code_distribution"],
            "type_distribution": paper_analysis["type_distribution"],
            "report_path": report_path,
            "template_comparison": template_analysis,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        print(f"验证完成！报告已保存至: {report_path}")
        return result
    
    def validate_multiple_papers(self, paper_ids, template_path=None, output_dir="paper_validation_reports"):
        """
        批量验证多套试卷
        
        Args:
            paper_ids: 试卷ID列表
            template_path: 组题模板文件路径（可选）
            output_dir: 验证报告输出目录
        
        Returns:
            dict: 批量验证结果
        """
        print(f"开始批量验证 {len(paper_ids)} 套试卷...")
        
        all_results = []
        template_analysis = None
        
        # 加载模板（如果提供）
        if template_path and os.path.exists(template_path):
            template_analysis = self._analyze_template_requirements(template_path)
        
        # 逐个验证试卷
        for paper_id in paper_ids:
            paper_info = self._get_paper_info(paper_id)
            if paper_info:
                paper_analysis = self._analyze_paper_composition(paper_info)
                all_results.append({
                    "paper_id": paper_id,
                    "paper_name": paper_info["name"],
                    "analysis": paper_analysis
                })
        
        # 生成批量对比报告
        report_path = self._generate_batch_validation_report(
            all_results, template_analysis, output_dir
        )
        
        result = {
            "status": "success",
            "total_papers": len(all_results),
            "papers_analyzed": all_results,
            "template_comparison": template_analysis,
            "report_path": report_path,
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        print(f"批量验证完成！报告已保存至: {report_path}")
        return result
    
    def _get_paper_info(self, paper_id):
        """获取试卷信息和题目列表"""
        db = get_db()
        try:
            # 获取试卷基本信息
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            if not paper:
                self.errors.append(f"试卷 {paper_id} 不存在")
                return None
            
            # 获取试卷题目
            paper_questions = db.query(PaperQuestion, Question).join(
                Question, PaperQuestion.question_id == Question.id
            ).filter(PaperQuestion.paper_id == paper_id).order_by(PaperQuestion.question_order).all()
            
            questions = []
            for pq, q in paper_questions:
                questions.append({
                    "question_id": q.id,
                    "question_type": q.question_type_code,
                    "order": pq.question_order,
                    "score": pq.score,
                    "section_name": pq.section_name
                })
            
            return {
                "id": paper.id,
                "name": paper.name,
                "description": paper.description,
                "total_score": paper.total_score,
                "duration": paper.duration,
                "questions": questions
            }
            
        except Exception as e:
            self.errors.append(f"获取试卷信息失败: {e}")
            return None
        finally:
            close_db(db)
    
    def _analyze_paper_composition(self, paper_info):
        """分析试卷的组成结构"""
        analysis = {
            "total_questions": len(paper_info["questions"]),
            "total_score": paper_info["total_score"],
            "l3_code_distribution": defaultdict(int),
            "l3_code_percentage": {},
            "type_distribution": defaultdict(int),
            "type_percentage": {},
            "l3_type_matrix": defaultdict(lambda: defaultdict(int)),
            "score_distribution": defaultdict(float),
            "detailed_breakdown": []
        }
        
        # 分析每道题目
        for q in paper_info["questions"]:
            question_id = q["question_id"]
            question_type = q["question_type"]
            score = q["score"]
            
            # 解析题目ID获取三级代码 (格式: B-A-B-C-001-002)
            try:
                # 去除可能的UUID后缀
                clean_id = question_id.split('#')[0] if '#' in question_id else question_id
                parts = clean_id.split('-')
                
                if len(parts) >= 6:
                    l1_code = parts[1]
                    l2_code = parts[2]
                    l3_code = parts[3]
                    l3_full_code = f"{l1_code}-{l2_code}-{l3_code}"
                    
                    # 统计分布
                    analysis["l3_code_distribution"][l3_full_code] += 1
                    analysis["type_distribution"][question_type] += 1
                    analysis["l3_type_matrix"][l3_full_code][question_type] += 1
                    analysis["score_distribution"][l3_full_code] += score
                    
                    # 详细记录
                    analysis["detailed_breakdown"].append({
                        "question_id": clean_id,
                        "question_type": question_type,
                        "l3_code": l3_full_code,
                        "score": score,
                        "order": q["order"]
                    })
                else:
                    self.warnings.append(f"题目ID格式异常: {question_id}")
                    
            except Exception as e:
                self.warnings.append(f"解析题目ID失败: {question_id}, 错误: {e}")
        
        # 计算百分比
        total_questions = analysis["total_questions"]
        if total_questions > 0:
            for l3_code, count in analysis["l3_code_distribution"].items():
                analysis["l3_code_percentage"][l3_code] = (count / total_questions) * 100
            
            for q_type, count in analysis["type_distribution"].items():
                analysis["type_percentage"][q_type] = (count / total_questions) * 100
        
        return analysis
    
    def _analyze_template_requirements(self, template_path):
        """分析组题模板要求"""
        try:
            # 读取Excel模板
            df1 = pd.read_excel(template_path, sheet_name='题型分布')
            df2 = pd.read_excel(template_path, sheet_name='知识点分布')
            
            template_analysis = {
                "type_requirements": {},
                "l3_requirements": {},
                "total_questions_required": 0
            }
            
            # 分析题型分布要求
            for _, row in df1.iterrows():
                q_type = str(row.get('题型', '')).strip()
                count = int(row.get('题量', 0))
                template_analysis["type_requirements"][q_type] = count
                template_analysis["total_questions_required"] += count
            
            # 分析知识点分布要求
            for _, row in df2.iterrows():
                l1_code = str(row.get('1级代码', '')).strip()
                l2_code = str(row.get('2级代码', '')).strip()
                l3_code = str(row.get('3级代码', '')).strip()
                l3_ratio = float(row.get('3级比重(%)', 0))
                
                if l1_code and l2_code and l3_code:
                    l3_full_code = f"{l1_code}-{l2_code}-{l3_code}"
                    template_analysis["l3_requirements"][l3_full_code] = l3_ratio
            
            return template_analysis
            
        except Exception as e:
            self.warnings.append(f"分析模板文件失败: {e}")
            return None
    
    def _generate_paper_validation_report(self, paper_info, paper_analysis, template_analysis, output_dir):
        """生成单套试卷验证报告"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"paper_validation_{paper_info['id']}_{timestamp}.xlsx")
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Sheet 1: 试卷基本信息
            basic_info = {
                "项目": ["试卷ID", "试卷名称", "总题数", "总分", "考试时长"],
                "值": [
                    paper_info["id"],
                    paper_info["name"],
                    paper_analysis["total_questions"],
                    paper_info["total_score"],
                    f"{paper_info['duration']}分钟"
                ]
            }
            pd.DataFrame(basic_info).to_excel(writer, sheet_name="试卷信息", index=False)
            
            # Sheet 2: 三级代码分布
            l3_distribution_data = []
            for l3_code, count in paper_analysis["l3_code_distribution"].items():
                percentage = paper_analysis["l3_code_percentage"][l3_code]
                score = paper_analysis["score_distribution"][l3_code]
                
                row_data = {
                    "三级代码": l3_code,
                    "题目数量": count,
                    "占比(%)": round(percentage, 2),
                    "总分值": score
                }
                
                # 如果有模板，添加对比
                if template_analysis and l3_code in template_analysis["l3_requirements"]:
                    required_percentage = template_analysis["l3_requirements"][l3_code]
                    row_data["模板要求(%)"] = required_percentage
                    row_data["差异(%)"] = round(percentage - required_percentage, 2)
                
                l3_distribution_data.append(row_data)
            
            pd.DataFrame(l3_distribution_data).to_excel(writer, sheet_name="三级代码分布", index=False)
            
            # Sheet 3: 题型分布
            type_distribution_data = []
            for q_type, count in paper_analysis["type_distribution"].items():
                percentage = paper_analysis["type_percentage"][q_type]
                
                row_data = {
                    "题型": q_type,
                    "题目数量": count,
                    "占比(%)": round(percentage, 2)
                }
                
                # 如果有模板，添加对比
                if template_analysis and q_type in template_analysis["type_requirements"]:
                    required_count = template_analysis["type_requirements"][q_type]
                    row_data["模板要求"] = required_count
                    row_data["差异"] = count - required_count
                
                type_distribution_data.append(row_data)
            
            pd.DataFrame(type_distribution_data).to_excel(writer, sheet_name="题型分布", index=False)
            
            # Sheet 4: 三级代码-题型交叉分析
            cross_analysis_data = []
            for l3_code, type_counts in paper_analysis["l3_type_matrix"].items():
                for q_type, count in type_counts.items():
                    cross_analysis_data.append({
                        "三级代码": l3_code,
                        "题型": q_type,
                        "题目数量": count
                    })
            
            pd.DataFrame(cross_analysis_data).to_excel(writer, sheet_name="交叉分析", index=False)
            
            # Sheet 5: 详细题目列表
            detailed_data = paper_analysis["detailed_breakdown"]
            pd.DataFrame(detailed_data).to_excel(writer, sheet_name="详细题目列表", index=False)
        
        return report_path
    
    def _generate_batch_validation_report(self, all_results, template_analysis, output_dir):
        """生成批量验证报告"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"batch_paper_validation_{timestamp}.xlsx")
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Sheet 1: 批量对比摘要
            summary_data = []
            for result in all_results:
                paper_id = result["paper_id"]
                paper_name = result["paper_name"]
                analysis = result["analysis"]
                
                summary_data.append({
                    "试卷ID": paper_id,
                    "试卷名称": paper_name,
                    "总题数": analysis["total_questions"],
                    "三级代码种类数": len(analysis["l3_code_distribution"]),
                    "题型种类数": len(analysis["type_distribution"])
                })
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="批量对比摘要", index=False)
            
            # Sheet 2: 三级代码分布对比
            all_l3_codes = set()
            for result in all_results:
                all_l3_codes.update(result["analysis"]["l3_code_distribution"].keys())
            
            l3_comparison_data = []
            for l3_code in sorted(all_l3_codes):
                row_data = {"三级代码": l3_code}
                
                # 添加模板要求（如果有）
                if template_analysis and l3_code in template_analysis["l3_requirements"]:
                    row_data["模板要求(%)"] = template_analysis["l3_requirements"][l3_code]
                
                # 添加每套试卷的数据
                for result in all_results:
                    paper_name = result["paper_name"]
                    analysis = result["analysis"]
                    percentage = analysis["l3_code_percentage"].get(l3_code, 0)
                    row_data[f"{paper_name}_占比(%)"] = round(percentage, 2)
                
                l3_comparison_data.append(row_data)
            
            pd.DataFrame(l3_comparison_data).to_excel(writer, sheet_name="三级代码分布对比", index=False)
            
            # Sheet 3: 题型分布对比
            all_types = set()
            for result in all_results:
                all_types.update(result["analysis"]["type_distribution"].keys())
            
            type_comparison_data = []
            for q_type in sorted(all_types):
                row_data = {"题型": q_type}
                
                # 添加模板要求（如果有）
                if template_analysis and q_type in template_analysis["type_requirements"]:
                    row_data["模板要求"] = template_analysis["type_requirements"][q_type]
                
                # 添加每套试卷的数据
                for result in all_results:
                    paper_name = result["paper_name"]
                    analysis = result["analysis"]
                    count = analysis["type_distribution"].get(q_type, 0)
                    row_data[f"{paper_name}_数量"] = count
                
                type_comparison_data.append(row_data)
            
            pd.DataFrame(type_comparison_data).to_excel(writer, sheet_name="题型分布对比", index=False)
        
        return report_path

def validate_paper_from_command_line(paper_id, template_path=None):
    """命令行接口函数"""
    validator = PaperValidator()
    result = validator.validate_paper_composition(paper_id, template_path)
    
    print("\n" + "="*50)
    print("试卷组题验证结果")
    print("="*50)
    print(f"试卷ID: {result.get('paper_id', 'N/A')}")
    print(f"试卷名称: {result.get('paper_name', 'N/A')}")
    print(f"总题数: {result.get('total_questions', 0)}")
    print(f"详细报告: {result.get('report_path', 'N/A')}")
    
    if result.get('l3_code_distribution'):
        print("\n三级代码分布:")
        for l3_code, count in result['l3_code_distribution'].items():
            percentage = result['l3_code_distribution'][l3_code] / result['total_questions'] * 100
            print(f"  {l3_code}: {count}题 ({percentage:.1f}%)")
    
    return result
