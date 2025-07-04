#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库生成自动复核程序
用于验证生成的题库是否与给定的规则表完全一致
"""

import pandas as pd
import json
import os
from collections import defaultdict, Counter
from datetime import datetime
import sys

class QuestionBankValidator:
    """题库生成验证器"""
    
    def __init__(self):
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    def validate_generated_bank(self, blueprint_path, generated_questions_path, output_dir="validation_reports"):
        """
        验证生成的题库是否与蓝图规则一致
        
        Args:
            blueprint_path: 蓝图JSON文件路径
            generated_questions_path: 生成的题库JSON/Excel文件路径
            output_dir: 验证报告输出目录
        
        Returns:
            dict: 验证结果
        """
        print("开始题库生成验证...")
        
        # 1. 加载蓝图规则
        blueprint = self._load_blueprint(blueprint_path)
        if not blueprint:
            return {"status": "error", "message": "无法加载蓝图文件"}
        
        # 2. 加载生成的题库
        generated_questions = self._load_generated_questions(generated_questions_path)
        if not generated_questions:
            return {"status": "error", "message": "无法加载生成的题库文件"}
        
        # 3. 统计生成的题库数据
        generated_stats = self._analyze_generated_questions(generated_questions)
        
        # 4. 从蓝图计算期望的统计数据
        expected_stats = self._calculate_expected_stats(blueprint)
        
        # 5. 对比验证
        validation_result = self._compare_stats(expected_stats, generated_stats)
        
        # 6. 生成详细报告
        report_path = self._generate_validation_report(
            blueprint, expected_stats, generated_stats, validation_result, output_dir
        )
        
        # 7. 返回结果
        result = {
            "status": "success" if validation_result["is_valid"] else "failed",
            "is_valid": validation_result["is_valid"],
            "total_questions_expected": expected_stats["total_questions"],
            "total_questions_generated": generated_stats["total_questions"],
            "accuracy_rate": validation_result["accuracy_rate"],
            "errors": self.errors,
            "warnings": self.warnings,
            "report_path": report_path,
            "detailed_comparison": validation_result["detailed_comparison"]
        }
        
        print(f"验证完成！准确率: {validation_result['accuracy_rate']:.2%}")
        print(f"详细报告已保存至: {report_path}")
        
        return result
    
    def _load_blueprint(self, blueprint_path):
        """加载蓝图文件"""
        try:
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.errors.append(f"加载蓝图文件失败: {e}")
            return None
    
    def _load_generated_questions(self, questions_path):
        """加载生成的题库文件"""
        try:
            if questions_path.endswith('.json'):
                with open(questions_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif questions_path.endswith('.xlsx'):
                df = pd.read_excel(questions_path)
                return df.to_dict('records')
            else:
                raise ValueError("不支持的文件格式，仅支持JSON和Excel文件")
        except Exception as e:
            self.errors.append(f"加载生成题库文件失败: {e}")
            return None
    
    def _analyze_generated_questions(self, questions):
        """分析生成的题库统计数据"""
        stats = {
            "total_questions": len(questions),
            "by_type": defaultdict(int),
            "by_knowledge_point": defaultdict(lambda: defaultdict(int)),
            "by_level": defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
            "question_distribution": defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        }
        
        for q in questions:
            # 解析题目ID获取结构信息
            if isinstance(q, dict):
                q_id = q.get('id', q.get('ID', ''))
                q_type = q.get('type', q.get('题型代码', ''))
            else:
                continue
            
            # 解析ID结构 (格式: B-A-B-C-001-002)
            try:
                parts = str(q_id).split('-')
                if len(parts) >= 6:
                    type_code = parts[0]
                    l1_code = parts[1]
                    l2_code = parts[2]
                    l3_code = parts[3]
                    knowledge_point = parts[4]
                    
                    # 统计各维度数据
                    stats["by_type"][type_code] += 1
                    stats["by_level"][l1_code][l2_code][l3_code] += 1
                    stats["by_knowledge_point"][f"{l1_code}-{l2_code}-{l3_code}"][type_code] += 1
                    stats["question_distribution"][l1_code][l2_code][l3_code] += 1
                    
            except Exception as e:
                self.warnings.append(f"解析题目ID失败: {q_id}, 错误: {e}")
        
        return stats
    
    def _calculate_expected_stats(self, blueprint):
        """从蓝图计算期望的统计数据"""
        stats = {
            "total_questions": 0,
            "by_type": defaultdict(int),
            "by_knowledge_point": defaultdict(lambda: defaultdict(int)),
            "by_level": defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
            "question_distribution": defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        }
        
        parallel_points = blueprint.get('config', {}).get('parallel_knowledge_points', 5)
        
        # 遍历蓝图结构
        for l1 in blueprint.get('blueprint', []):
            l1_code = l1['code']
            for l2 in l1.get('children', []):
                l2_code = l2['code']
                for l3 in l2.get('children', []):
                    l3_code = l3['code']
                    questions_config = l3.get('questions', {})
                    
                    for q_type, count_per_point in questions_config.items():
                        if count_per_point > 0:
                            # 每个三级知识点有parallel_points个并行点
                            # 每个并行点有count_per_point个题目
                            total_count = parallel_points * count_per_point
                            
                            stats["total_questions"] += total_count
                            stats["by_type"][q_type] += total_count
                            stats["by_knowledge_point"][f"{l1_code}-{l2_code}-{l3_code}"][q_type] += total_count
                            stats["by_level"][l1_code][l2_code][l3_code] += total_count
                            stats["question_distribution"][l1_code][l2_code][l3_code] += total_count
        
        return stats
    
    def _compare_stats(self, expected, generated):
        """对比期望和实际统计数据"""
        comparison = {
            "is_valid": True,
            "accuracy_rate": 0.0,
            "detailed_comparison": {
                "total_questions": {
                    "expected": expected["total_questions"],
                    "generated": generated["total_questions"],
                    "match": expected["total_questions"] == generated["total_questions"]
                },
                "by_type": {},
                "by_knowledge_point": {},
                "missing_questions": [],
                "extra_questions": []
            }
        }
        
        # 1. 总题目数量对比
        total_match = expected["total_questions"] == generated["total_questions"]
        if not total_match:
            comparison["is_valid"] = False
            self.errors.append(f"总题目数量不匹配: 期望{expected['total_questions']}, 实际{generated['total_questions']}")
        
        # 2. 按题型对比
        all_types = set(expected["by_type"].keys()) | set(generated["by_type"].keys())
        type_matches = 0
        for q_type in all_types:
            exp_count = expected["by_type"][q_type]
            gen_count = generated["by_type"][q_type]
            match = exp_count == gen_count
            
            comparison["detailed_comparison"]["by_type"][q_type] = {
                "expected": exp_count,
                "generated": gen_count,
                "match": match
            }
            
            if match:
                type_matches += 1
            else:
                comparison["is_valid"] = False
                self.errors.append(f"题型{q_type}数量不匹配: 期望{exp_count}, 实际{gen_count}")
        
        # 3. 按知识点对比
        all_kps = set(expected["by_knowledge_point"].keys()) | set(generated["by_knowledge_point"].keys())
        kp_matches = 0
        for kp in all_kps:
            exp_types = expected["by_knowledge_point"][kp]
            gen_types = generated["by_knowledge_point"][kp]
            
            kp_comparison = {}
            kp_match = True
            
            all_kp_types = set(exp_types.keys()) | set(gen_types.keys())
            for q_type in all_kp_types:
                exp_count = exp_types[q_type]
                gen_count = gen_types[q_type]
                type_match = exp_count == gen_count
                
                kp_comparison[q_type] = {
                    "expected": exp_count,
                    "generated": gen_count,
                    "match": type_match
                }
                
                if not type_match:
                    kp_match = False
                    self.errors.append(f"知识点{kp}的{q_type}题型数量不匹配: 期望{exp_count}, 实际{gen_count}")
            
            comparison["detailed_comparison"]["by_knowledge_point"][kp] = {
                "match": kp_match,
                "by_type": kp_comparison
            }
            
            if kp_match:
                kp_matches += 1
        
        # 4. 计算准确率
        total_checks = len(all_types) + len(all_kps) + 1  # +1 for total count
        successful_checks = type_matches + kp_matches + (1 if total_match else 0)
        comparison["accuracy_rate"] = successful_checks / total_checks if total_checks > 0 else 0.0
        
        return comparison
    
    def _generate_validation_report(self, blueprint, expected, generated, validation_result, output_dir):
        """生成详细的验证报告Excel文件"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"question_bank_validation_report_{timestamp}.xlsx")
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Sheet 1: 验证摘要
            summary_data = {
                "验证项目": ["总题目数量", "题型分布", "知识点分布", "整体准确率"],
                "期望值": [
                    expected["total_questions"],
                    f"{len(expected['by_type'])}种题型",
                    f"{len(expected['by_knowledge_point'])}个知识点",
                    "100%"
                ],
                "实际值": [
                    generated["total_questions"],
                    f"{len(generated['by_type'])}种题型",
                    f"{len(generated['by_knowledge_point'])}个知识点",
                    f"{validation_result['accuracy_rate']:.2%}"
                ],
                "验证结果": [
                    "✓" if validation_result["detailed_comparison"]["total_questions"]["match"] else "✗",
                    "✓" if all(v["match"] for v in validation_result["detailed_comparison"]["by_type"].values()) else "✗",
                    "✓" if all(v["match"] for v in validation_result["detailed_comparison"]["by_knowledge_point"].values()) else "✗",
                    "✓" if validation_result["is_valid"] else "✗"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="验证摘要", index=False)
            
            # Sheet 2: 题型分布对比
            type_comparison_data = []
            for q_type, data in validation_result["detailed_comparison"]["by_type"].items():
                type_comparison_data.append({
                    "题型": q_type,
                    "期望数量": data["expected"],
                    "实际数量": data["generated"],
                    "差异": data["generated"] - data["expected"],
                    "验证结果": "✓" if data["match"] else "✗"
                })
            pd.DataFrame(type_comparison_data).to_excel(writer, sheet_name="题型分布对比", index=False)
            
            # Sheet 3: 知识点分布对比
            kp_comparison_data = []
            for kp, data in validation_result["detailed_comparison"]["by_knowledge_point"].items():
                for q_type, type_data in data["by_type"].items():
                    kp_comparison_data.append({
                        "知识点": kp,
                        "题型": q_type,
                        "期望数量": type_data["expected"],
                        "实际数量": type_data["generated"],
                        "差异": type_data["generated"] - type_data["expected"],
                        "验证结果": "✓" if type_data["match"] else "✗"
                    })
            pd.DataFrame(kp_comparison_data).to_excel(writer, sheet_name="知识点分布对比", index=False)
            
            # Sheet 4: 错误和警告
            issues_data = []
            for error in self.errors:
                issues_data.append({"类型": "错误", "描述": error})
            for warning in self.warnings:
                issues_data.append({"类型": "警告", "描述": warning})
            pd.DataFrame(issues_data).to_excel(writer, sheet_name="问题列表", index=False)
        
        return report_path

def main():
    """主函数 - 命令行接口"""
    if len(sys.argv) < 3:
        print("使用方法: python question_bank_validator.py <蓝图文件路径> <生成题库文件路径> [输出目录]")
        print("示例: python question_bank_validator.py blueprint.json generated_questions.json")
        return
    
    blueprint_path = sys.argv[1]
    generated_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "validation_reports"
    
    validator = QuestionBankValidator()
    result = validator.validate_generated_bank(blueprint_path, generated_path, output_dir)
    
    print("\n" + "="*50)
    print("题库生成验证结果")
    print("="*50)
    print(f"验证状态: {'通过' if result['is_valid'] else '失败'}")
    print(f"准确率: {result['accuracy_rate']:.2%}")
    print(f"期望题目数: {result['total_questions_expected']}")
    print(f"实际题目数: {result['total_questions_generated']}")
    print(f"详细报告: {result['report_path']}")
    
    if result['errors']:
        print(f"\n发现 {len(result['errors'])} 个错误:")
        for error in result['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main()
