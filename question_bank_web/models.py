from sqlalchemy import create_engine, Column, String, Text, CHAR, DateTime, Enum as SAEnum, Integer, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.mysql import INTEGER # For MySQL specific integer types if needed
import datetime
import uuid

Base = declarative_base()

# Define ENUMs for codes if you prefer them over CHARs for better readability
# class QuestionType(SAEnum):
#     SINGLE_CHOICE = 'B'
#     MULTIPLE_CHOICE = 'G'
#     TRUE_FALSE = 'C'
#     FILL_IN_BLANK = 'T'
#     SHORT_ANSWER = 'D'
#     CALCULATION = 'U'
#     ESSAY = 'W'
#     CASE_ANALYSIS = 'E'
#     COMPOSITE = 'F'

# class DifficultyLevel(SAEnum):
#     VERY_EASY = '1'
#     EASY = '2'
#     MEDIUM = '3'
#     HARD = '4'
#     VERY_HARD = '5'

class Question(Base):
    __tablename__ = 'questions'

    id = Column(String(255), primary_key=True, comment="主键，格式：三级代码-考核点代码-序号，例如：A-B-C-001-002")
    # If you decide to keep serial_number_excel and knowledge_point_code as separate fields:
    # serial_number_excel = Column(String(50), comment="对应Excel中的序号")
    # knowledge_point_code = Column(String(100), comment="认定点代码/考核点代码")
    
    question_type_code = Column(CHAR(1), nullable=False, comment="题型代码: B, G, C, T, D, U, W, E, F")
    # Alternatively, using the Enum defined above:
    # question_type_code = Column(QuestionType, nullable=False, comment="题型代码")
    
    question_number = Column(String(50), comment="题号")
    stem = Column(Text, nullable=False, comment="试题题干")
    option_a = Column(Text)
    option_b = Column(Text)
    option_c = Column(Text)
    option_d = Column(Text)
    option_e = Column(Text)
    image_info = Column(String(255), comment="【图】及位置，可存储图片路径或描述")
    correct_answer = Column(Text, nullable=False, comment="正确答案")
    
    difficulty_code = Column(CHAR(1), nullable=False, comment="难度代码: 1, 2, 3, 4, 5")
    # Alternatively, using the Enum defined above:
    # difficulty_code = Column(DifficultyLevel, nullable=False, comment="难度代码")
    
    consistency_code = Column(CHAR(1), comment="一致性代码: 1, 2, 3, 4, 5")
    analysis = Column(Text, comment="解析")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # 新增外键，关联到题库表
    question_bank_id = Column(String(36), ForeignKey('question_banks.id'), nullable=False, index=True)
    
    # 建立关系
    question_bank = relationship("QuestionBank", back_populates="questions")

    def __repr__(self):
        return f"<Question(id='{self.id}', stem='{self.stem[:30]}...')>"
        
    def to_dict(self):
        """将Question对象转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'question_type_code': self.question_type_code,
            'type': self.get_question_type(),
            'question_number': self.question_number,
            'stem': self.stem,
            'options': self.get_options(),
            'image_info': self.image_info,
            'correct_answer': self.correct_answer,
            'difficulty_code': self.difficulty_code,
            'consistency_code': self.consistency_code,
            'analysis': self.analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_bank_id': self.question_bank_id
        }
    
    def get_options(self):
        """获取题目选项，返回非空选项的列表"""
        options = []
        if self.option_a:
            options.append(self.option_a)
        if self.option_b:
            options.append(self.option_b)
        if self.option_c:
            options.append(self.option_c)
        if self.option_d:
            options.append(self.option_d)
        if self.option_e:
            options.append(self.option_e)
        return options
    
    def get_question_type(self):
        """根据题型代码返回题型名称"""
        type_map = {
            'B': 'single_choice',  # 单选题
            'G': 'multiple_choice',  # 多选题
            'C': 'true_false',  # 判断题
            'T': 'fill_blank',  # 填空题
            'D': 'short_answer',  # 简答题
            'U': 'calculation',  # 计算题
            'W': 'essay',  # 论述题
            'E': 'case_analysis',  # 案例分析
            'F': 'composite'  # 综合题
        }
        return type_map.get(self.question_type_code, 'unknown')

class Paper(Base):
    """试卷模型"""
    __tablename__ = 'papers'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="试卷ID")
    name = Column(String(255), nullable=False, comment="试卷名称")
    description = Column(Text, comment="试卷描述")
    total_score = Column(Float, default=100.0, comment="试卷总分")
    duration = Column(Integer, default=120, comment="考试时长（分钟）")
    difficulty_level = Column(String(50), comment="试卷难度等级")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # 关联试卷题目
    paper_questions = relationship("PaperQuestion", back_populates="paper", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Paper(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        """将Paper对象转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'total_score': self.total_score,
            'duration': self.duration,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'questions': [pq.to_dict() for pq in self.paper_questions]
        }

class PaperQuestion(Base):
    """试卷题目关联模型"""
    __tablename__ = 'paper_questions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="关联ID")
    paper_id = Column(String(36), ForeignKey('papers.id'), nullable=False, comment="试卷ID")
    question_id = Column(String(255), ForeignKey('questions.id'), nullable=False, comment="题目ID")
    question_order = Column(Integer, nullable=False, comment="题目在试卷中的顺序")
    score = Column(Float, nullable=False, comment="题目分值")
    section_name = Column(String(100), comment="题目所属章节/部分")
    
    # 关联关系
    paper = relationship("Paper", back_populates="paper_questions")
    question = relationship("Question")
    
    def __repr__(self):
        return f"<PaperQuestion(paper_id='{self.paper_id}', question_id='{self.question_id}', order={self.question_order})>"
    
    def to_dict(self):
        """将PaperQuestion对象转换为字典，用于JSON序列化"""
        result = {
            'id': self.id,
            'paper_id': self.paper_id,
            'question_id': self.question_id,
            'question_order': self.question_order,
            'score': self.score,
            'section_name': self.section_name
        }
        
        # 如果需要包含题目详情
        if self.question:
            result['question'] = self.question.to_dict()
            
        return result

class QuestionGroup(Base):
    """题目分组模型（用于组题规则）"""
    __tablename__ = 'question_groups'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="分组ID")
    name = Column(String(255), nullable=False, comment="分组名称")
    description = Column(Text, comment="分组描述")
    question_type_code = Column(CHAR(1), comment="题型代码")
    difficulty_code = Column(CHAR(1), comment="难度代码")
    min_count = Column(Integer, default=1, comment="最少题目数量")
    max_count = Column(Integer, default=10, comment="最多题目数量")
    score_per_question = Column(Float, default=5.0, comment="每题分值")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<QuestionGroup(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        """将QuestionGroup对象转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'question_type_code': self.question_type_code,
            'difficulty_code': self.difficulty_code,
            'min_count': self.min_count,
            'max_count': self.max_count,
            'score_per_question': self.score_per_question,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class QuestionBank(Base):
    """题库模型"""
    __tablename__ = 'question_banks'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="题库ID")
    name = Column(String(255), unique=True, nullable=False, comment="题库名称")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, comment="创建时间")

    # 新增反向关系
    questions = relationship("Question", back_populates="question_bank", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuestionBank(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        """将QuestionBank对象转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'question_count': len(self.questions) if self.questions else 0
        }

# 示例：如何连接到MySQL数据库并创建表
# Replace with your actual database connection string
# DB_URL = "mysql+mysqlconnector://user:password@host/dbname"
# engine = create_engine(DB_URL, echo=True)

# To create tables in the database (run this once):
# Base.metadata.create_all(engine)

# --- You would also define other tables like Papers, PaperQuestions, Users here ---