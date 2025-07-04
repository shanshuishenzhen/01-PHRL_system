#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试组卷复核功能
"""

from paper_validator import PaperValidator
from models import Paper, PaperQuestion, Question
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_paper_validation():
    """测试组卷复核功能"""
    print("测试组卷复核功能")
    print("=" * 50)
    
    # 连接数据库
    engine = create_engine('sqlite:///questions.db')
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 查找试卷
        papers = db.query(Paper).order_by(Paper.created_at.desc()).limit(3).all()
        print(f"找到 {len(papers)} 套试卷")
        
        for paper in papers:
            print(f"\n试卷: {paper.name}")
            print(f"ID: {paper.id}")
            
            # 查看试卷题目
            paper_questions = db.query(PaperQuestion).filter(
                PaperQuestion.paper_id == paper.id
            ).all()
            print(f"题目数量: {len(paper_questions)}")
            
            if paper_questions:
                # 测试验证功能
                try:
                    validator = PaperValidator()
                    result = validator.validate_paper_composition(
                        paper.id,
                        output_dir="paper_validation_test_reports"
                    )
                    print(f"验证状态: {result.get('status', '未知')}")
                    print(f"报告路径: {result.get('report_path', '无')}")
                    
                    if result.get('status') == 'success':
                        print("✅ 验证成功！")
                        if result.get('l3_code_distribution'):
                            print("三级代码分布:")
                            for code, count in list(result['l3_code_distribution'].items())[:5]:
                                print(f"  {code}: {count}题")
                        break
                    else:
                        print("❌ 验证失败")
                        
                except Exception as e:
                    print(f"验证失败: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("无题目数据")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_paper_validation()
