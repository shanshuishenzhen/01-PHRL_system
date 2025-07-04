# 题库数据库架构解决方案

## 问题描述
- 当前：所有题库存储在同一数据库中，导致ID冲突
- 需求：不同题库项目完全独立，题库内ID唯一，跨题库ID可重复

## 解决方案对比

### 方案一：多数据库架构（推荐）

#### 优点
- ✅ 完全隔离，符合业务逻辑
- ✅ 性能最优，每个项目数据量小
- ✅ 维护简单，项目独立
- ✅ 扩展性好，可独立备份/迁移
- ✅ 安全性高，项目间完全隔离

#### 实现方式
```python
# 动态数据库连接
def get_database_for_project(project_name):
    db_path = f"question_banks/{project_name}.db"
    return create_engine(f'sqlite:///{db_path}')

# 使用示例
project_db = get_database_for_project("视频创推1")
session = sessionmaker(bind=project_db)()
```

#### 目录结构
```
question_bank_web/
├── question_banks/
│   ├── 视频创推1.db
│   ├── 保卫管理1.db
│   ├── 项目A.db
│   └── 项目B.db
├── app.py
└── models.py
```

### 方案二：单数据库+项目字段

#### 优点
- ✅ 实现简单，改动最小
- ✅ 统一管理，便于全局查询

#### 缺点
- ❌ 性能随项目增多下降
- ❌ 数据耦合，安全性较低
- ❌ 备份恢复复杂

#### 实现方式
```python
# 在Question模型中添加project_name字段
class Question(Base):
    __tablename__ = 'questions'
    id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)  # 新增
    # ... 其他字段
    
    __table_args__ = (
        UniqueConstraint('id', 'project_name', name='uq_question_id_project'),
    )
```

### 方案三：复合主键方案

#### 实现方式
```python
class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(String, primary_key=True)  # 原ID
    project_name = Column(String, primary_key=True)  # 项目名
    # ... 其他字段
```

## 推荐实施方案：多数据库架构

### 实施步骤

#### 1. 数据库管理器
```python
class DatabaseManager:
    def __init__(self, base_dir="question_banks"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self._engines = {}
    
    def get_engine(self, project_name):
        if project_name not in self._engines:
            db_path = os.path.join(self.base_dir, f"{project_name}.db")
            self._engines[project_name] = create_engine(f'sqlite:///{db_path}')
            # 创建表结构
            Base.metadata.create_all(self._engines[project_name])
        return self._engines[project_name]
    
    def get_session(self, project_name):
        engine = self.get_engine(project_name)
        Session = sessionmaker(bind=engine)
        return Session()
    
    def list_projects(self):
        if not os.path.exists(self.base_dir):
            return []
        return [f[:-3] for f in os.listdir(self.base_dir) if f.endswith('.db')]
```

#### 2. Flask应用修改
```python
# 全局数据库管理器
db_manager = DatabaseManager()

@app.route('/select-project')
def select_project():
    projects = db_manager.list_projects()
    return render_template('select_project.html', projects=projects)

@app.route('/set-project/<project_name>')
def set_project(project_name):
    session['current_project'] = project_name
    return redirect(url_for('index'))

def get_current_db():
    project_name = session.get('current_project', 'default')
    return db_manager.get_session(project_name)
```

#### 3. 导入功能修改
```python
@app.route('/import-sample', methods=['GET'])
def handle_import_sample():
    project_name = session.get('current_project', 'default')
    db = db_manager.get_session(project_name)
    
    # 使用项目专用数据库进行导入
    excel_file_path = os.path.join(os.path.dirname(__file__), 'questions_sample.xlsx')
    questions_added, errors = import_questions_from_excel(excel_file_path, db)
    
    # ... 处理结果
```

### 迁移现有数据

#### 数据分离脚本
```python
def migrate_existing_data():
    # 连接现有数据库
    old_engine = create_engine('sqlite:///questions.db')
    OldSession = sessionmaker(bind=old_engine)
    old_session = OldSession()
    
    # 按题库名称分组
    questions = old_session.query(Question).all()
    banks = old_session.query(QuestionBank).all()
    
    # 按题库分组数据
    data_by_bank = {}
    for bank in banks:
        bank_questions = [q for q in questions if q.bank_id == bank.id]
        data_by_bank[bank.name] = {
            'bank': bank,
            'questions': bank_questions
        }
    
    # 创建新的项目数据库
    for project_name, data in data_by_bank.items():
        new_session = db_manager.get_session(project_name)
        
        # 创建新题库记录
        new_bank = QuestionBank(
            id=data['bank'].id,
            name=data['bank'].name,
            description=data['bank'].description
        )
        new_session.add(new_bank)
        
        # 迁移题目
        for question in data['questions']:
            new_question = Question(
                id=question.id,
                bank_id=new_bank.id,
                content=question.content,
                # ... 其他字段
            )
            new_session.add(new_question)
        
        new_session.commit()
        new_session.close()
    
    old_session.close()
```

## 实施建议

### 立即行动
1. **备份现有数据库**
2. **实施多数据库架构**
3. **迁移现有数据**
4. **更新前端界面**（添加项目选择）

### 长期优化
1. **项目管理界面**
2. **数据导入/导出工具**
3. **项目间数据复制功能**
4. **统一的项目配置管理**

## 总结

多数据库架构最符合您的业务需求：
- 🎯 **业务逻辑清晰**：每个项目独立
- 🚀 **性能最优**：数据量小，查询快
- 🔒 **安全隔离**：项目间完全独立
- 📈 **易于扩展**：新项目直接创建新数据库
- 🛠️ **维护简单**：可独立备份、迁移、删除项目
