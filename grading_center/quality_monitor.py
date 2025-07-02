#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阅卷质量监控系统

监控和分析阅卷质量，包括：
- 评分一致性分析
- 异常评分检测
- 评分员表现分析
- 质量报告生成
- 实时监控预警
"""

import json
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np


@dataclass
class GradingRecord:
    """评分记录"""
    record_id: str
    exam_id: str
    question_id: str
    student_id: str
    grader_id: str
    score: float
    max_score: float
    grading_time: str
    confidence: float = 1.0
    comments: str = ""
    grading_method: str = "manual"
    
    @property
    def score_ratio(self) -> float:
        return self.score / self.max_score if self.max_score > 0 else 0


@dataclass
class QualityMetrics:
    """质量指标"""
    consistency_score: float  # 一致性分数 (0-1)
    reliability_score: float  # 可靠性分数 (0-1)
    efficiency_score: float   # 效率分数 (0-1)
    accuracy_score: float     # 准确性分数 (0-1)
    overall_score: float      # 总体质量分数 (0-1)
    
    anomaly_count: int = 0
    total_records: int = 0
    average_grading_time: float = 0.0
    score_variance: float = 0.0


@dataclass
class GraderPerformance:
    """评分员表现"""
    grader_id: str
    grader_name: str
    total_graded: int
    average_score: float
    score_variance: float
    average_time: float
    consistency_with_others: float
    accuracy_rate: float
    quality_metrics: QualityMetrics
    last_active: str


class QualityMonitor:
    """阅卷质量监控器"""
    
    def __init__(self, data_dir: str = "quality_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.setup_logging()
        self.grading_records: List[GradingRecord] = []
        self.quality_thresholds = self.load_quality_thresholds()
        
        # 加载历史数据
        self.load_grading_records()
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "quality_monitor.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_quality_thresholds(self) -> Dict:
        """加载质量阈值配置"""
        default_thresholds = {
            "consistency_threshold": 0.8,      # 一致性阈值
            "reliability_threshold": 0.85,     # 可靠性阈值
            "efficiency_threshold": 0.7,       # 效率阈值
            "accuracy_threshold": 0.9,         # 准确性阈值
            "score_variance_threshold": 0.15,  # 分数方差阈值
            "time_variance_threshold": 0.3,    # 时间方差阈值
            "anomaly_threshold": 0.05,         # 异常比例阈值
            "min_grading_time": 30,            # 最小评分时间(秒)
            "max_grading_time": 1800,          # 最大评分时间(秒)
        }
        
        threshold_file = self.data_dir / "quality_thresholds.json"
        if threshold_file.exists():
            try:
                with open(threshold_file, 'r', encoding='utf-8') as f:
                    custom_thresholds = json.load(f)
                default_thresholds.update(custom_thresholds)
            except Exception as e:
                self.logger.warning(f"加载质量阈值失败: {e}")
        
        return default_thresholds
    
    def load_grading_records(self):
        """加载评分记录"""
        try:
            records_file = self.data_dir / "grading_records.json"
            if records_file.exists():
                with open(records_file, 'r', encoding='utf-8') as f:
                    records_data = json.load(f)
                
                self.grading_records = [
                    GradingRecord(**record) for record in records_data
                ]
                
                self.logger.info(f"加载评分记录: {len(self.grading_records)} 条")
        except Exception as e:
            self.logger.error(f"加载评分记录失败: {e}")
    
    def save_grading_records(self):
        """保存评分记录"""
        try:
            records_file = self.data_dir / "grading_records.json"
            records_data = [asdict(record) for record in self.grading_records]
            
            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump(records_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"保存评分记录失败: {e}")
    
    def add_grading_record(self, record: GradingRecord):
        """添加评分记录"""
        self.grading_records.append(record)
        
        # 实时质量检查
        self.check_real_time_quality(record)
        
        # 定期保存
        if len(self.grading_records) % 100 == 0:
            self.save_grading_records()
    
    def check_real_time_quality(self, record: GradingRecord):
        """实时质量检查"""
        warnings = []
        
        # 检查评分时间异常
        try:
            grading_time = self.parse_grading_time(record.grading_time)
            if grading_time < self.quality_thresholds["min_grading_time"]:
                warnings.append(f"评分时间过短: {grading_time}秒")
            elif grading_time > self.quality_thresholds["max_grading_time"]:
                warnings.append(f"评分时间过长: {grading_time}秒")
        except:
            pass
        
        # 检查分数异常
        if record.score > record.max_score:
            warnings.append(f"分数超出最大值: {record.score}/{record.max_score}")
        
        if record.score < 0:
            warnings.append(f"分数为负值: {record.score}")
        
        # 检查置信度异常
        if record.confidence < 0.5:
            warnings.append(f"置信度过低: {record.confidence}")
        
        # 发出警告
        if warnings:
            self.logger.warning(f"评分质量警告 - 记录ID: {record.record_id}, "
                              f"评分员: {record.grader_id}, 警告: {'; '.join(warnings)}")
    
    def parse_grading_time(self, grading_time_str: str) -> float:
        """解析评分时间"""
        # 简化实现，假设grading_time是ISO格式的时间戳
        # 实际应该根据具体格式解析
        return 60.0  # 默认60秒
    
    def calculate_consistency_score(self, question_records: List[GradingRecord]) -> float:
        """计算一致性分数"""
        if len(question_records) < 2:
            return 1.0
        
        # 计算分数比例的标准差
        score_ratios = [record.score_ratio for record in question_records]
        variance = statistics.variance(score_ratios) if len(score_ratios) > 1 else 0
        
        # 转换为一致性分数 (方差越小，一致性越高)
        consistency = max(0, 1 - variance / self.quality_thresholds["score_variance_threshold"])
        return min(1.0, consistency)
    
    def detect_anomalies(self, records: List[GradingRecord]) -> List[GradingRecord]:
        """检测异常评分"""
        if len(records) < 3:
            return []
        
        anomalies = []
        score_ratios = [record.score_ratio for record in records]
        
        # 使用IQR方法检测异常值
        q1 = np.percentile(score_ratios, 25)
        q3 = np.percentile(score_ratios, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        for record in records:
            if record.score_ratio < lower_bound or record.score_ratio > upper_bound:
                anomalies.append(record)
        
        return anomalies
    
    def analyze_grader_performance(self, grader_id: str, 
                                 time_period: int = 30) -> GraderPerformance:
        """分析评分员表现"""
        # 获取指定时间段内的评分记录
        cutoff_date = datetime.now() - timedelta(days=time_period)
        
        grader_records = [
            record for record in self.grading_records
            if record.grader_id == grader_id
        ]
        
        if not grader_records:
            return GraderPerformance(
                grader_id=grader_id,
                grader_name=f"评分员_{grader_id}",
                total_graded=0,
                average_score=0,
                score_variance=0,
                average_time=0,
                consistency_with_others=0,
                accuracy_rate=0,
                quality_metrics=QualityMetrics(0, 0, 0, 0, 0),
                last_active=""
            )
        
        # 计算基本统计
        scores = [record.score_ratio for record in grader_records]
        average_score = statistics.mean(scores)
        score_variance = statistics.variance(scores) if len(scores) > 1 else 0
        
        # 计算一致性
        consistency_scores = []
        for record in grader_records:
            same_question_records = [
                r for r in self.grading_records
                if r.question_id == record.question_id and r.student_id == record.student_id
            ]
            if len(same_question_records) > 1:
                consistency = self.calculate_consistency_score(same_question_records)
                consistency_scores.append(consistency)
        
        consistency_with_others = statistics.mean(consistency_scores) if consistency_scores else 1.0
        
        # 计算质量指标
        quality_metrics = QualityMetrics(
            consistency_score=consistency_with_others,
            reliability_score=min(1.0, 1 - score_variance),
            efficiency_score=0.8,  # 简化计算
            accuracy_score=0.9,    # 需要与标准答案比较
            overall_score=0.0,
            total_records=len(grader_records),
            score_variance=score_variance
        )
        
        quality_metrics.overall_score = (
            quality_metrics.consistency_score * 0.3 +
            quality_metrics.reliability_score * 0.3 +
            quality_metrics.efficiency_score * 0.2 +
            quality_metrics.accuracy_score * 0.2
        )
        
        return GraderPerformance(
            grader_id=grader_id,
            grader_name=f"评分员_{grader_id}",
            total_graded=len(grader_records),
            average_score=average_score,
            score_variance=score_variance,
            average_time=0,  # 需要计算实际时间
            consistency_with_others=consistency_with_others,
            accuracy_rate=0.9,  # 简化
            quality_metrics=quality_metrics,
            last_active=grader_records[-1].grading_time if grader_records else ""
        )
    
    def generate_quality_report(self, exam_id: str = None) -> Dict:
        """生成质量报告"""
        # 筛选记录
        if exam_id:
            records = [r for r in self.grading_records if r.exam_id == exam_id]
        else:
            records = self.grading_records
        
        if not records:
            return {"error": "没有找到评分记录"}
        
        # 总体统计
        total_records = len(records)
        unique_graders = len(set(record.grader_id for record in records))
        unique_questions = len(set(record.question_id for record in records))
        
        # 检测异常
        anomalies = self.detect_anomalies(records)
        anomaly_rate = len(anomalies) / total_records if total_records > 0 else 0
        
        # 计算总体质量指标
        all_scores = [record.score_ratio for record in records]
        overall_variance = statistics.variance(all_scores) if len(all_scores) > 1 else 0
        
        # 按题目分析一致性
        question_consistency = {}
        for question_id in set(record.question_id for record in records):
            question_records = [r for r in records if r.question_id == question_id]
            if len(question_records) > 1:
                consistency = self.calculate_consistency_score(question_records)
                question_consistency[question_id] = consistency
        
        average_consistency = statistics.mean(question_consistency.values()) if question_consistency else 1.0
        
        # 评分员表现分析
        grader_performances = {}
        for grader_id in set(record.grader_id for record in records):
            performance = self.analyze_grader_performance(grader_id)
            grader_performances[grader_id] = asdict(performance)
        
        # 生成报告
        report = {
            "report_id": f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "exam_id": exam_id,
            "summary": {
                "total_records": total_records,
                "unique_graders": unique_graders,
                "unique_questions": unique_questions,
                "anomaly_count": len(anomalies),
                "anomaly_rate": anomaly_rate,
                "overall_variance": overall_variance,
                "average_consistency": average_consistency
            },
            "quality_metrics": {
                "consistency_score": average_consistency,
                "reliability_score": max(0, 1 - overall_variance),
                "anomaly_score": max(0, 1 - anomaly_rate),
                "overall_quality": (average_consistency + max(0, 1 - overall_variance) + max(0, 1 - anomaly_rate)) / 3
            },
            "question_analysis": question_consistency,
            "grader_performances": grader_performances,
            "anomalies": [asdict(anomaly) for anomaly in anomalies[:10]],  # 只显示前10个异常
            "recommendations": self.generate_recommendations(
                average_consistency, overall_variance, anomaly_rate
            )
        }
        
        # 保存报告
        report_file = self.data_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def generate_recommendations(self, consistency: float, variance: float, 
                               anomaly_rate: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if consistency < self.quality_thresholds["consistency_threshold"]:
            recommendations.append("评分一致性较低，建议加强评分员培训和标准化")
        
        if variance > self.quality_thresholds["score_variance_threshold"]:
            recommendations.append("评分方差较大，建议制定更详细的评分标准")
        
        if anomaly_rate > self.quality_thresholds["anomaly_threshold"]:
            recommendations.append("异常评分较多，建议增加质量检查和复核机制")
        
        if not recommendations:
            recommendations.append("评分质量良好，继续保持当前标准")
        
        return recommendations


def main():
    """主函数 - 测试质量监控系统"""
    monitor = QualityMonitor()
    
    # 添加测试数据
    test_records = [
        GradingRecord("r1", "exam1", "q1", "s1", "grader1", 8.5, 10, "2024-01-01T10:00:00Z", 0.9),
        GradingRecord("r2", "exam1", "q1", "s1", "grader2", 8.0, 10, "2024-01-01T10:05:00Z", 0.8),
        GradingRecord("r3", "exam1", "q1", "s1", "grader3", 9.0, 10, "2024-01-01T10:10:00Z", 0.95),
        GradingRecord("r4", "exam1", "q2", "s1", "grader1", 7.0, 10, "2024-01-01T10:15:00Z", 0.7),
        GradingRecord("r5", "exam1", "q2", "s1", "grader2", 6.5, 10, "2024-01-01T10:20:00Z", 0.6),
    ]
    
    for record in test_records:
        monitor.add_grading_record(record)
    
    print("📊 阅卷质量监控系统测试")
    
    # 生成质量报告
    report = monitor.generate_quality_report("exam1")
    
    print(f"\n质量报告摘要:")
    print(f"总记录数: {report['summary']['total_records']}")
    print(f"评分员数: {report['summary']['unique_graders']}")
    print(f"题目数: {report['summary']['unique_questions']}")
    print(f"异常率: {report['summary']['anomaly_rate']:.2%}")
    print(f"平均一致性: {report['summary']['average_consistency']:.3f}")
    print(f"总体质量: {report['quality_metrics']['overall_quality']:.3f}")
    
    print(f"\n改进建议:")
    for rec in report['recommendations']:
        print(f"- {rec}")


if __name__ == "__main__":
    main()
