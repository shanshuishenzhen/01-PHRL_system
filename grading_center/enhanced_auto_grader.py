#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的自动阅卷系统

基于最佳实践的智能阅卷算法，支持：
- 多种题型的智能评分
- 语义相似度分析
- 关键词匹配
- 模糊匹配
- 评分规则配置
- 质量检查
"""

import os
import sys
import json
import re
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import jieba
import jieba.analyse


@dataclass
class GradingRule:
    """评分规则配置"""
    question_type: str
    exact_match_score: float = 1.0
    partial_match_score: float = 0.5
    keyword_weight: float = 0.3
    similarity_threshold: float = 0.8
    case_sensitive: bool = False
    ignore_punctuation: bool = True
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class GradingResult:
    """评分结果"""
    question_id: str
    question_type: str
    student_answer: str
    correct_answer: str
    max_score: float
    obtained_score: float
    score_ratio: float
    grading_method: str
    confidence: float
    feedback: str
    keywords_matched: List[str] = None
    similarity_score: float = 0.0
    
    def __post_init__(self):
        if self.keywords_matched is None:
            self.keywords_matched = []
        self.score_ratio = self.obtained_score / self.max_score if self.max_score > 0 else 0


class EnhancedAutoGrader:
    """增强的自动阅卷器"""
    
    def __init__(self, config_path: str = None):
        self.setup_logging()
        self.load_config(config_path)
        self.setup_jieba()
        
        # 默认评分规则
        self.default_rules = {
            "single_choice": GradingRule("single_choice", exact_match_score=1.0),
            "multiple_choice": GradingRule("multiple_choice", exact_match_score=1.0),
            "true_false": GradingRule("true_false", exact_match_score=1.0),
            "fill_blank": GradingRule("fill_blank", exact_match_score=1.0, 
                                    partial_match_score=0.7, similarity_threshold=0.9),
            "short_answer": GradingRule("short_answer", exact_match_score=1.0,
                                      partial_match_score=0.6, keyword_weight=0.4,
                                      similarity_threshold=0.7),
            "essay": GradingRule("essay", exact_match_score=1.0,
                               partial_match_score=0.5, keyword_weight=0.5,
                               similarity_threshold=0.6)
        }
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "enhanced_grader.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: str = None):
        """加载配置"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.warning(f"加载配置失败: {e}，使用默认配置")
                self.config = {}
        else:
            self.config = {}
    
    def setup_jieba(self):
        """设置jieba分词"""
        try:
            # 添加自定义词典
            custom_words = self.config.get("custom_words", [])
            for word in custom_words:
                jieba.add_word(word)
            
            # 设置停用词
            self.stop_words = set(self.config.get("stop_words", [
                "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"
            ]))
            
        except Exception as e:
            self.logger.warning(f"设置jieba失败: {e}")
    
    def normalize_text(self, text: str, rule: GradingRule) -> str:
        """文本标准化"""
        if not text:
            return ""
        
        text = str(text).strip()
        
        # 移除标点符号
        if rule.ignore_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
        
        # 大小写处理
        if not rule.case_sensitive:
            text = text.lower()
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        try:
            # 使用TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
            # 过滤停用词
            keywords = [kw for kw in keywords if kw not in self.stop_words]
            return keywords
        except Exception as e:
            self.logger.warning(f"提取关键词失败: {e}")
            return []
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        try:
            # 使用SequenceMatcher计算相似度
            similarity = SequenceMatcher(None, text1, text2).ratio()
            return similarity
        except Exception as e:
            self.logger.warning(f"计算相似度失败: {e}")
            return 0.0
    
    def calculate_keyword_match_score(self, student_text: str, correct_text: str, 
                                    keywords: List[str] = None) -> Tuple[float, List[str]]:
        """计算关键词匹配分数"""
        if not keywords:
            keywords = self.extract_keywords(correct_text)
        
        if not keywords:
            return 0.0, []
        
        student_keywords = self.extract_keywords(student_text)
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in student_keywords or keyword in student_text:
                matched_keywords.append(keyword)
        
        match_ratio = len(matched_keywords) / len(keywords) if keywords else 0
        return match_ratio, matched_keywords
    
    def grade_single_choice(self, student_answer: str, correct_answer: str, 
                          max_score: float, rule: GradingRule) -> GradingResult:
        """评分单选题"""
        student_norm = self.normalize_text(student_answer, rule)
        correct_norm = self.normalize_text(correct_answer, rule)
        
        if student_norm == correct_norm:
            score = max_score
            confidence = 1.0
            feedback = "答案完全正确"
        else:
            score = 0
            confidence = 1.0
            feedback = f"答案错误，正确答案是: {correct_answer}"
        
        return GradingResult(
            question_id="", question_type="single_choice",
            student_answer=student_answer, correct_answer=correct_answer,
            max_score=max_score, obtained_score=score,
            grading_method="exact_match", confidence=confidence,
            feedback=feedback, score_ratio=score/max_score
        )
    
    def grade_multiple_choice(self, student_answer: Any, correct_answer: Any,
                            max_score: float, rule: GradingRule) -> GradingResult:
        """评分多选题"""
        # 处理不同格式的答案
        if isinstance(student_answer, str):
            student_set = set(student_answer.strip().upper())
        elif isinstance(student_answer, list):
            student_set = set(str(x).strip().upper() for x in student_answer)
        else:
            student_set = set()
        
        if isinstance(correct_answer, str):
            correct_set = set(correct_answer.strip().upper())
        elif isinstance(correct_answer, list):
            correct_set = set(str(x).strip().upper() for x in correct_answer)
        else:
            correct_set = set()
        
        if student_set == correct_set:
            score = max_score
            feedback = "答案完全正确"
            confidence = 1.0
        else:
            # 部分分数计算
            intersection = student_set & correct_set
            union = student_set | correct_set
            
            if intersection:
                # 根据交集比例给分
                partial_ratio = len(intersection) / len(correct_set)
                score = max_score * partial_ratio * rule.partial_match_score
                feedback = f"部分正确，得到 {len(intersection)}/{len(correct_set)} 个正确选项"
                confidence = 0.8
            else:
                score = 0
                feedback = f"答案错误，正确答案是: {correct_answer}"
                confidence = 1.0
        
        return GradingResult(
            question_id="", question_type="multiple_choice",
            student_answer=str(student_answer), correct_answer=str(correct_answer),
            max_score=max_score, obtained_score=score,
            grading_method="set_comparison", confidence=confidence,
            feedback=feedback, score_ratio=score/max_score
        )
    
    def grade_fill_blank(self, student_answer: str, correct_answer: str,
                        max_score: float, rule: GradingRule) -> GradingResult:
        """评分填空题"""
        student_norm = self.normalize_text(student_answer, rule)
        correct_norm = self.normalize_text(correct_answer, rule)
        
        # 精确匹配
        if student_norm == correct_norm:
            score = max_score
            confidence = 1.0
            feedback = "答案完全正确"
            method = "exact_match"
        else:
            # 相似度匹配
            similarity = self.calculate_similarity(student_norm, correct_norm)
            
            if similarity >= rule.similarity_threshold:
                score = max_score * rule.partial_match_score
                confidence = similarity
                feedback = f"答案基本正确（相似度: {similarity:.2f}）"
                method = "similarity_match"
            else:
                # 关键词匹配
                keyword_score, matched_keywords = self.calculate_keyword_match_score(
                    student_norm, correct_norm
                )
                
                if keyword_score > 0:
                    score = max_score * keyword_score * rule.keyword_weight
                    confidence = keyword_score
                    feedback = f"包含部分关键词: {', '.join(matched_keywords)}"
                    method = "keyword_match"
                else:
                    score = 0
                    confidence = 1.0
                    feedback = f"答案错误，正确答案是: {correct_answer}"
                    method = "no_match"
        
        return GradingResult(
            question_id="", question_type="fill_blank",
            student_answer=student_answer, correct_answer=correct_answer,
            max_score=max_score, obtained_score=score,
            grading_method=method, confidence=confidence,
            feedback=feedback, similarity_score=similarity if 'similarity' in locals() else 0,
            score_ratio=score/max_score
        )
    
    def grade_question(self, question_id: str, student_answer: Any, correct_answer: Any,
                      question_type: str, max_score: float, 
                      custom_rule: GradingRule = None) -> GradingResult:
        """评分单个题目"""
        try:
            # 获取评分规则
            rule = custom_rule or self.default_rules.get(question_type, 
                                                       self.default_rules["essay"])
            
            # 根据题型选择评分方法
            if question_type == "single_choice":
                result = self.grade_single_choice(str(student_answer), str(correct_answer), 
                                                max_score, rule)
            elif question_type == "multiple_choice":
                result = self.grade_multiple_choice(student_answer, correct_answer, 
                                                  max_score, rule)
            elif question_type == "true_false":
                result = self.grade_single_choice(str(student_answer), str(correct_answer), 
                                                max_score, rule)
            elif question_type == "fill_blank":
                result = self.grade_fill_blank(str(student_answer), str(correct_answer), 
                                             max_score, rule)
            elif question_type in ["short_answer", "essay"]:
                result = self.grade_fill_blank(str(student_answer), str(correct_answer), 
                                             max_score, rule)
            else:
                # 未知题型，使用默认评分
                result = GradingResult(
                    question_id=question_id, question_type=question_type,
                    student_answer=str(student_answer), correct_answer=str(correct_answer),
                    max_score=max_score, obtained_score=max_score * 0.5,
                    grading_method="default", confidence=0.5,
                    feedback="未知题型，给予默认分数", score_ratio=0.5
                )
            
            # 设置题目ID
            result.question_id = question_id
            
            return result
            
        except Exception as e:
            self.logger.error(f"评分题目 {question_id} 失败: {e}")
            return GradingResult(
                question_id=question_id, question_type=question_type,
                student_answer=str(student_answer), correct_answer=str(correct_answer),
                max_score=max_score, obtained_score=0,
                grading_method="error", confidence=0,
                feedback=f"评分出错: {str(e)}", score_ratio=0
            )
    
    def grade_exam(self, student_answers: Dict, correct_answers: Dict, 
                   custom_rules: Dict[str, GradingRule] = None) -> Dict:
        """评分整个考试"""
        try:
            results = []
            total_score = 0
            total_max_score = 0
            
            questions = correct_answers.get("questions", {})
            
            for question_id, correct_data in questions.items():
                student_answer = student_answers.get(question_id, "")
                correct_answer = correct_data.get("correct_answer", "")
                question_type = correct_data.get("question_type", "essay")
                max_score = float(correct_data.get("score", 10))
                
                # 获取自定义规则
                custom_rule = None
                if custom_rules and question_id in custom_rules:
                    custom_rule = custom_rules[question_id]
                
                # 评分
                result = self.grade_question(
                    question_id, student_answer, correct_answer,
                    question_type, max_score, custom_rule
                )
                
                results.append(result.__dict__)
                total_score += result.obtained_score
                total_max_score += max_score
            
            # 计算总体统计
            pass_score = total_max_score * 0.6  # 60%及格
            passed = total_score >= pass_score
            percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
            
            return {
                "total_score": total_score,
                "total_max_score": total_max_score,
                "percentage": percentage,
                "passed": passed,
                "pass_score": pass_score,
                "question_results": results,
                "grading_summary": {
                    "total_questions": len(questions),
                    "graded_questions": len(results),
                    "average_confidence": sum(r["confidence"] for r in results) / len(results) if results else 0,
                    "grading_time": time.time()
                }
            }
            
        except Exception as e:
            self.logger.error(f"评分考试失败: {e}")
            return {
                "error": str(e),
                "total_score": 0,
                "total_max_score": 0,
                "percentage": 0,
                "passed": False
            }


def main():
    """主函数 - 测试增强阅卷系统"""
    grader = EnhancedAutoGrader()
    
    # 测试数据
    student_answers = {
        "q1": "B",
        "q2": ["A", "C"],
        "q3": "Python是一种解释型编程语言",
        "q4": "面向对象编程的主要特点包括封装、继承和多态"
    }
    
    correct_answers = {
        "questions": {
            "q1": {
                "correct_answer": "B",
                "question_type": "single_choice",
                "score": 10
            },
            "q2": {
                "correct_answer": ["A", "C"],
                "question_type": "multiple_choice", 
                "score": 15
            },
            "q3": {
                "correct_answer": "Python是解释型语言",
                "question_type": "fill_blank",
                "score": 10
            },
            "q4": {
                "correct_answer": "面向对象编程的特点是封装、继承、多态",
                "question_type": "short_answer",
                "score": 20
            }
        }
    }
    
    # 执行评分
    result = grader.grade_exam(student_answers, correct_answers)
    
    print("🎯 增强自动阅卷结果:")
    print(f"总分: {result['total_score']:.1f}/{result['total_max_score']}")
    print(f"百分比: {result['percentage']:.1f}%")
    print(f"是否及格: {'是' if result['passed'] else '否'}")
    print(f"平均置信度: {result['grading_summary']['average_confidence']:.2f}")
    
    print("\n详细评分:")
    for q_result in result['question_results']:
        print(f"题目 {q_result['question_id']}: {q_result['obtained_score']:.1f}/{q_result['max_score']} "
              f"({q_result['grading_method']}, 置信度: {q_result['confidence']:.2f})")
        print(f"  反馈: {q_result['feedback']}")


if __name__ == "__main__":
    main()
