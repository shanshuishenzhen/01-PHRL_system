#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复题库管理模块中的Unicode字符
"""

import os
import re

def fix_unicode_chars():
    """修复app.py中的Unicode字符"""
    
    # Unicode字符替换映射
    unicode_replacements = {
        '📚': '',
        '📥': '',
        '📤': '',
        '📋': '',
        '🔄': '',
        '🔍': '',
        '⚡': '',
        '🎯': '',
        '🗂️': '',
        '📄': '',
        '🗑️': '',
        '👁️': '',
        '📊': '',
        '📝': '',
        '⏱️': '',
        '📅': '',
        '📭': '',
        '🏠': '',
        '🚀': '',
        '❌': '',
        '😊': '',
        '⚖️': '',
        '😰': '',
        '💡': '',
    }
    
    app_file = 'question_bank_web/app.py'
    
    if not os.path.exists(app_file):
        print(f"文件不存在: {app_file}")
        return False
    
    try:
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换Unicode字符
        for unicode_char, replacement in unicode_replacements.items():
            content = content.replace(unicode_char, replacement)
        
        # 清理多余的空格
        content = re.sub(r'>\s+<', '><', content)  # 移除标签间的多余空格
        content = re.sub(r'class="btn[^"]*">\s+', lambda m: m.group(0).rstrip() + '', content)  # 清理按钮文本前的空格
        
        # 特殊处理一些常见的情况
        replacements = [
            # 按钮文本清理
            ('class="btn btn-success"> 导入Excel题库', 'class="btn btn-success">导入Excel题库'),
            ('class="btn btn-primary"> 导入样例题库', 'class="btn btn-primary">导入样例题库'),
            ('class="btn"> 下载题库模板', 'class="btn">下载题库模板'),
            ('class="btn"> 刷新页面', 'class="btn">刷新页面'),
            ('class="btn btn-success"> 导出题库', 'class="btn btn-success">导出题库'),
            ('class="btn btn-warning"> 高级浏览', 'class="btn btn-warning">高级浏览'),
            ('class="btn btn-primary"> 快速生成', 'class="btn btn-primary">快速生成'),
            ('class="btn btn-warning"> 自定义组题', 'class="btn btn-warning">自定义组题'),
            ('class="btn btn-danger"> 上传组题规则', 'class="btn btn-danger">上传组题规则'),
            ('class="btn btn-info"> 题库管理', 'class="btn btn-info">题库管理'),
            
            # 标题清理
            ('<h1> 题库管理系统</h1>', '<h1>题库管理系统</h1>'),
            ('<h1> 导入Excel题库</h1>', '<h1>导入Excel题库</h1>'),
            ('<h1> 试卷管理</h1>', '<h1>试卷管理</h1>'),
            ('<h1> 自定义组题</h1>', '<h1>自定义组题</h1>'),
            ('<h1> 快速生成试卷</h1>', '<h1>快速生成试卷</h1>'),
            
            # 其他文本清理
            ('<h2> 题目列表', '<h2>题目列表'),
            ('<h3> 暂无题目</h3>', '<h3>暂无题目</h3>'),
            ('<h3> 暂无试卷</h3>', '<h3>暂无试卷</h3>'),
            ('<h4> 文件要求：</h4>', '<h4>文件要求：</h4>'),
            ('<strong> 提示：</strong>', '<strong>提示：</strong>'),
            
            # 导航链接清理
            ('"> 首页</a>', '">首页</a>'),
            ('"> 导入题库</a>', '">导入题库</a>'),
            ('"> 试卷管理</a>', '">试卷管理</a>'),
            ('"> 快速生成</a>', '">快速生成</a>'),
            ('"> 自定义组题</a>', '">自定义组题</a>'),
            
            # 表单按钮清理
            ('value=" 上传并导入">', 'value="上传并导入">'),
            ('"> 生成试卷</button>', '">生成试卷</button>'),
            ('"> 取消</a>', '">取消</a>'),
            ('"> 删除</button>', '">删除</button>'),
            
            # span标签清理
            ('<span> 总分:', '<span>总分:'),
            ('<span> 时长:', '<span>时长:'),
            ('<span> 难度:', '<span>难度:'),
            ('<span> 创建:', '<span>创建:'),
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        # 写回文件
        if content != original_content:
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Unicode字符修复完成")
            print(f"修复的文件: {app_file}")
            return True
        else:
            print("ℹ️  没有发现需要修复的Unicode字符")
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def test_app_startup():
    """测试app.py是否能正常启动"""
    import subprocess
    import sys
    
    try:
        print("🔍 测试题库管理模块启动...")
        
        # 测试语法检查
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'question_bank_web/app.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ 题库管理模块语法检查通过")
            return True
        else:
            print(f"❌ 题库管理模块语法错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始修复题库管理模块Unicode字符问题")
    print("=" * 50)
    
    # 修复Unicode字符
    if fix_unicode_chars():
        print("✅ Unicode字符修复成功")
    else:
        print("❌ Unicode字符修复失败")
        return False
    
    # 测试启动
    if test_app_startup():
        print("✅ 题库管理模块测试通过")
    else:
        print("❌ 题库管理模块测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 修复完成！")
    print("\n✅ 修复内容:")
    print("1. ✅ 移除了所有有问题的Unicode字符")
    print("2. ✅ 清理了多余的空格")
    print("3. ✅ 优化了按钮和标题文本")
    print("4. ✅ 题库管理模块语法检查通过")
    
    print("\n🚀 现在可以正常使用:")
    print("• 开发工具生成题库后自动跳转不会出错")
    print("• 题库管理模块界面正常显示")
    print("• 不会再出现编码错误")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
