import os

# 创建模板目录
templates_dir = 'templates'
try:
    os.makedirs(templates_dir, exist_ok=True)
    print(f"目录 '{templates_dir}' 创建成功")
except Exception as e:
    print(f"创建目录错误: {e}")

# 创建index.html文件
index_path = os.path.join(templates_dir, 'index.html')
try:
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>题库管理系统</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        .flashes { list-style-type: none; padding: 0; }
        .flashes li { margin-bottom: 10px; padding: 10px; border-radius: 4px; }
        .flashes .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .flashes .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .flashes .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>题库管理系统</h1>
    <p><a href="{{ url_for('handle_import_excel') }}">导入Excel题库</a></p>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul class=flashes>
        {% for category, message in messages %}
          <li class="{{ category }}">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <h2>题目列表 (最多显示10条)</h2>
    {% if questions %}
    <table>
        <thead>
            <tr><th>ID</th><th>题干</th><th>题型</th><th>难度</th></tr>
        </thead>
        <tbody>
        {% for q in questions %}
            <tr>
                <td>{{ q.id }}</td>
                <td>{{ q.stem | truncate(100) }}</td>
                <td>{{ q.question_type_code }}</td>
                <td>{{ q.difficulty_code }}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>题库为空或加载失败。</p>
    {% endif %}
</body>
</html>""")
    print(f"文件 '{index_path}' 创建成功")
except Exception as e:
    print(f"创建文件错误: {e}")

# 创建import_form.html文件
import_form_path = os.path.join(templates_dir, 'import_form.html')
try:
    with open(import_form_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>导入Excel题库</title>
</head>
<body>
    <h1>导入Excel题库</h1>
    <form method="post" enctype="multipart/form-data">
      <p>
        <label for="excel_file">选择Excel文件 (.xlsx):</label><br>
        <input type="file" id="excel_file" name="excel_file" accept=".xlsx" required>
      </p>
      <p><input type="submit" value="上传并导入"></p>
    </form>
    <p><a href="{{ url_for('index') }}">返回首页</a></p>
</body>
</html>""")
    print(f"文件 '{import_form_path}' 创建成功")
except Exception as e:
    print(f"创建文件错误: {e}")
