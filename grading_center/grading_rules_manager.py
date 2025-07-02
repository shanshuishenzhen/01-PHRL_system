#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分规则管理器

管理和配置各种题型的评分规则，支持：
- 规则模板管理
- 自定义评分标准
- 规则验证和测试
- 规则导入导出
- 动态规则调整
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ScoringCriteria:
    """评分标准"""
    name: str
    description: str
    score_percentage: float  # 得分百分比 (0.0-1.0)
    conditions: List[str]    # 满足条件
    keywords: List[str] = None
    min_similarity: float = 0.0
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class QuestionTypeRule:
    """题型评分规则"""
    question_type: str
    name: str
    description: str
    scoring_criteria: List[ScoringCriteria]
    default_score: float = 0.0
    case_sensitive: bool = False
    ignore_punctuation: bool = True
    similarity_threshold: float = 0.8
    keyword_weight: float = 0.3
    partial_credit: bool = True
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


class GradingRulesManager:
    """评分规则管理器"""
    
    def __init__(self, rules_dir: str = "grading_rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        
        self.setup_logging()
        self.rules: Dict[str, QuestionTypeRule] = {}
        self.load_default_rules()
        self.load_custom_rules()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_default_rules(self):
        """加载默认评分规则"""
        # 单选题规则
        single_choice_rule = QuestionTypeRule(
            question_type="single_choice",
            name="单选题标准规则",
            description="单选题精确匹配评分规则",
            scoring_criteria=[
                ScoringCriteria(
                    name="完全正确",
                    description="答案完全匹配",
                    score_percentage=1.0,
                    conditions=["exact_match"]
                ),
                ScoringCriteria(
                    name="完全错误",
                    description="答案不匹配",
                    score_percentage=0.0,
                    conditions=["no_match"]
                )
            ],
            case_sensitive=False,
            partial_credit=False
        )
        
        # 多选题规则
        multiple_choice_rule = QuestionTypeRule(
            question_type="multiple_choice",
            name="多选题标准规则",
            description="多选题集合匹配评分规则",
            scoring_criteria=[
                ScoringCriteria(
                    name="完全正确",
                    description="所有选项完全匹配",
                    score_percentage=1.0,
                    conditions=["exact_set_match"]
                ),
                ScoringCriteria(
                    name="部分正确",
                    description="部分选项正确",
                    score_percentage=0.6,
                    conditions=["partial_set_match"]
                ),
                ScoringCriteria(
                    name="完全错误",
                    description="没有正确选项",
                    score_percentage=0.0,
                    conditions=["no_match"]
                )
            ],
            partial_credit=True
        )
        
        # 填空题规则
        fill_blank_rule = QuestionTypeRule(
            question_type="fill_blank",
            name="填空题智能规则",
            description="填空题智能匹配评分规则",
            scoring_criteria=[
                ScoringCriteria(
                    name="完全正确",
                    description="答案完全匹配",
                    score_percentage=1.0,
                    conditions=["exact_match"]
                ),
                ScoringCriteria(
                    name="基本正确",
                    description="高相似度匹配",
                    score_percentage=0.8,
                    conditions=["high_similarity"],
                    min_similarity=0.9
                ),
                ScoringCriteria(
                    name="部分正确",
                    description="中等相似度或包含关键词",
                    score_percentage=0.5,
                    conditions=["medium_similarity", "keyword_match"],
                    min_similarity=0.7
                ),
                ScoringCriteria(
                    name="基本错误",
                    description="低相似度",
                    score_percentage=0.2,
                    conditions=["low_similarity"],
                    min_similarity=0.3
                )
            ],
            similarity_threshold=0.7,
            keyword_weight=0.4,
            partial_credit=True
        )
        
        # 简答题规则
        short_answer_rule = QuestionTypeRule(
            question_type="short_answer",
            name="简答题综合规则",
            description="简答题综合评分规则",
            scoring_criteria=[
                ScoringCriteria(
                    name="优秀",
                    description="答案完整准确，包含所有要点",
                    score_percentage=1.0,
                    conditions=["high_similarity", "all_keywords"],
                    min_similarity=0.8
                ),
                ScoringCriteria(
                    name="良好",
                    description="答案基本正确，包含主要要点",
                    score_percentage=0.8,
                    conditions=["medium_similarity", "most_keywords"],
                    min_similarity=0.6
                ),
                ScoringCriteria(
                    name="及格",
                    description="答案部分正确，包含部分要点",
                    score_percentage=0.6,
                    conditions=["low_similarity", "some_keywords"],
                    min_similarity=0.4
                ),
                ScoringCriteria(
                    name="不及格",
                    description="答案基本错误或空白",
                    score_percentage=0.2,
                    conditions=["very_low_similarity", "few_keywords"],
                    min_similarity=0.2
                )
            ],
            similarity_threshold=0.6,
            keyword_weight=0.5,
            partial_credit=True
        )
        
        # 论述题规则
        essay_rule = QuestionTypeRule(
            question_type="essay",
            name="论述题综合规则",
            description="论述题综合评分规则，需要人工复核",
            scoring_criteria=[
                ScoringCriteria(
                    name="自动初评-优秀",
                    description="包含丰富关键词和高相似度",
                    score_percentage=0.9,
                    conditions=["high_similarity", "rich_keywords"],
                    min_similarity=0.7
                ),
                ScoringCriteria(
                    name="自动初评-良好",
                    description="包含主要关键词",
                    score_percentage=0.7,
                    conditions=["medium_similarity", "main_keywords"],
                    min_similarity=0.5
                ),
                ScoringCriteria(
                    name="自动初评-及格",
                    description="包含基本关键词",
                    score_percentage=0.5,
                    conditions=["basic_keywords"],
                    min_similarity=0.3
                ),
                ScoringCriteria(
                    name="需要人工阅卷",
                    description="自动评分置信度低，需要人工阅卷",
                    score_percentage=0.3,
                    conditions=["low_confidence"]
                )
            ],
            similarity_threshold=0.5,
            keyword_weight=0.6,
            partial_credit=True
        )
        
        # 存储默认规则
        self.rules = {
            "single_choice": single_choice_rule,
            "multiple_choice": multiple_choice_rule,
            "fill_blank": fill_blank_rule,
            "short_answer": short_answer_rule,
            "essay": essay_rule
        }
    
    def load_custom_rules(self):
        """加载自定义规则"""
        try:
            for rule_file in self.rules_dir.glob("*.json"):
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)
                
                # 重建评分标准对象
                criteria = []
                for criteria_data in rule_data.get("scoring_criteria", []):
                    criteria.append(ScoringCriteria(**criteria_data))
                
                rule_data["scoring_criteria"] = criteria
                rule = QuestionTypeRule(**rule_data)
                
                self.rules[rule.question_type] = rule
                self.logger.info(f"加载自定义规则: {rule.name}")
                
        except Exception as e:
            self.logger.error(f"加载自定义规则失败: {e}")
    
    def save_rule(self, rule: QuestionTypeRule):
        """保存规则到文件"""
        try:
            rule.updated_at = datetime.now().isoformat()
            rule_file = self.rules_dir / f"{rule.question_type}.json"
            
            # 转换为可序列化的字典
            rule_dict = asdict(rule)
            
            with open(rule_file, 'w', encoding='utf-8') as f:
                json.dump(rule_dict, f, indent=2, ensure_ascii=False)
            
            self.rules[rule.question_type] = rule
            self.logger.info(f"保存规则: {rule.name}")
            
        except Exception as e:
            self.logger.error(f"保存规则失败: {e}")
            raise
    
    def get_rule(self, question_type: str) -> Optional[QuestionTypeRule]:
        """获取指定题型的规则"""
        return self.rules.get(question_type)
    
    def list_rules(self) -> List[QuestionTypeRule]:
        """列出所有规则"""
        return list(self.rules.values())
    
    def create_custom_rule(self, question_type: str, name: str, description: str,
                          scoring_criteria: List[ScoringCriteria],
                          **kwargs) -> QuestionTypeRule:
        """创建自定义规则"""
        rule = QuestionTypeRule(
            question_type=question_type,
            name=name,
            description=description,
            scoring_criteria=scoring_criteria,
            **kwargs
        )
        
        self.save_rule(rule)
        return rule
    
    def update_rule(self, question_type: str, **updates):
        """更新规则"""
        if question_type not in self.rules:
            raise ValueError(f"规则不存在: {question_type}")
        
        rule = self.rules[question_type]
        
        # 更新属性
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self.save_rule(rule)
    
    def delete_rule(self, question_type: str):
        """删除规则"""
        if question_type in self.rules:
            rule_file = self.rules_dir / f"{question_type}.json"
            if rule_file.exists():
                rule_file.unlink()
            
            del self.rules[question_type]
            self.logger.info(f"删除规则: {question_type}")
    
    def export_rules(self, export_path: str):
        """导出所有规则"""
        try:
            export_data = {}
            for question_type, rule in self.rules.items():
                export_data[question_type] = asdict(rule)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"导出规则到: {export_path}")
            
        except Exception as e:
            self.logger.error(f"导出规则失败: {e}")
            raise
    
    def import_rules(self, import_path: str):
        """导入规则"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            for question_type, rule_data in import_data.items():
                # 重建评分标准对象
                criteria = []
                for criteria_data in rule_data.get("scoring_criteria", []):
                    criteria.append(ScoringCriteria(**criteria_data))
                
                rule_data["scoring_criteria"] = criteria
                rule = QuestionTypeRule(**rule_data)
                
                self.save_rule(rule)
            
            self.logger.info(f"从 {import_path} 导入规则成功")
            
        except Exception as e:
            self.logger.error(f"导入规则失败: {e}")
            raise
    
    def validate_rule(self, rule: QuestionTypeRule) -> List[str]:
        """验证规则有效性"""
        errors = []
        
        # 检查基本字段
        if not rule.question_type:
            errors.append("题型不能为空")
        
        if not rule.name:
            errors.append("规则名称不能为空")
        
        if not rule.scoring_criteria:
            errors.append("评分标准不能为空")
        
        # 检查评分标准
        total_percentage = 0
        for criteria in rule.scoring_criteria:
            if criteria.score_percentage < 0 or criteria.score_percentage > 1:
                errors.append(f"评分百分比必须在0-1之间: {criteria.name}")
            
            if not criteria.conditions:
                errors.append(f"评分条件不能为空: {criteria.name}")
        
        # 检查阈值
        if rule.similarity_threshold < 0 or rule.similarity_threshold > 1:
            errors.append("相似度阈值必须在0-1之间")
        
        if rule.keyword_weight < 0 or rule.keyword_weight > 1:
            errors.append("关键词权重必须在0-1之间")
        
        return errors
    
    def test_rule(self, question_type: str, test_cases: List[Dict]) -> Dict:
        """测试规则"""
        rule = self.get_rule(question_type)
        if not rule:
            return {"error": f"规则不存在: {question_type}"}
        
        results = []
        for test_case in test_cases:
            student_answer = test_case.get("student_answer", "")
            correct_answer = test_case.get("correct_answer", "")
            expected_score = test_case.get("expected_score", 0)
            
            # 这里需要调用实际的评分逻辑
            # 简化示例
            result = {
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "expected_score": expected_score,
                "actual_score": 0,  # 需要实际计算
                "passed": False
            }
            results.append(result)
        
        return {
            "rule_name": rule.name,
            "test_results": results,
            "pass_rate": sum(1 for r in results if r["passed"]) / len(results) if results else 0
        }


def main():
    """主函数 - 测试规则管理器"""
    manager = GradingRulesManager()
    
    print("📋 评分规则管理器测试")
    
    # 列出所有规则
    rules = manager.list_rules()
    print(f"\n当前规则数量: {len(rules)}")
    
    for rule in rules:
        print(f"- {rule.question_type}: {rule.name}")
        print(f"  评分标准数量: {len(rule.scoring_criteria)}")
        print(f"  支持部分分数: {rule.partial_credit}")
    
    # 创建自定义规则示例
    custom_criteria = [
        ScoringCriteria(
            name="完全正确",
            description="答案完全正确",
            score_percentage=1.0,
            conditions=["exact_match"]
        ),
        ScoringCriteria(
            name="部分正确",
            description="答案部分正确",
            score_percentage=0.5,
            conditions=["partial_match"]
        )
    ]
    
    try:
        custom_rule = manager.create_custom_rule(
            question_type="custom_type",
            name="自定义规则测试",
            description="这是一个测试用的自定义规则",
            scoring_criteria=custom_criteria
        )
        print(f"\n✅ 创建自定义规则成功: {custom_rule.name}")
        
        # 验证规则
        errors = manager.validate_rule(custom_rule)
        if errors:
            print(f"❌ 规则验证失败: {errors}")
        else:
            print("✅ 规则验证通过")
        
    except Exception as e:
        print(f"❌ 创建自定义规则失败: {e}")


if __name__ == "__main__":
    main()
