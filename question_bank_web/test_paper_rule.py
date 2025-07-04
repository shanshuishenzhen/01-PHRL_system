#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试组题规则Excel文件
"""

import pandas as pd
import os

def create_test_paper_rule():
    """创建测试组题规则文件"""
    
    # 创建题型分布数据
    sheet1_data = {
        '题库名称': ['保卫管理员（三级）理论题库', '保卫管理员（三级）理论题库', '保卫管理员（三级）理论题库'],
        '题型': ['B（单选题）', 'G（多选题）', 'C（判断题）'],
        '题量': [5, 3, 2],
        '每题分数': [4.0, 6.0, 2.0]
    }
    
    # 创建知识点分布数据
    sheet2_data = {
        '1级代码': ['A', 'A', 'B'],
        '1级比重(%)': [50.0, 50.0, 50.0],
        '2级代码': ['A', 'B', 'A'],
        '2级比重(%)': [30.0, 20.0, 50.0],
        '3级代码': ['A', 'A', 'A'],
        '3级比重(%)': [100.0, 100.0, 100.0]
    }
    
    # 创建Excel文件
    filename = 'test_paper_rule.xlsx'
    filepath = os.path.join('uploads', filename)
    
    # 确保uploads目录存在
    os.makedirs('uploads', exist_ok=True)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 写入题型分布
        df1 = pd.DataFrame(sheet1_data)
        df1.to_excel(writer, sheet_name='题型分布', index=False)
        
        # 写入知识点分布
        df2 = pd.DataFrame(sheet2_data)
        df2.to_excel(writer, sheet_name='知识点分布', index=False)
    
    print(f"✅ 测试组题规则文件已创建: {filepath}")
    
    # 显示文件内容
    print("\n题型分布:")
    print(df1.to_string(index=False))
    
    print("\n知识点分布:")
    print(df2.to_string(index=False))
    
    return filepath

def test_upload_paper_rule():
    """测试上传组题规则功能"""
    import requests
    
    # 创建测试文件
    filepath = create_test_paper_rule()
    
    try:
        # 准备上传数据
        files = {'file': open(filepath, 'rb')}
        data = {
            'paper_name': '测试试卷',
            'num_sets': 1
        }
        
        # 发送POST请求
        response = requests.post('http://localhost:5000/upload-paper-rule', 
                               files=files, data=data, timeout=30)
        
        files['file'].close()
        
        if response.status_code == 200:
            print("✅ 上传组题规则测试成功")
            print(f"响应状态码: {response.status_code}")
        else:
            print(f"❌ 上传组题规则测试失败")
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
    finally:
        # 清理测试文件
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🧹 已清理测试文件: {filepath}")

if __name__ == "__main__":
    print("组题规则测试工具")
    print("=" * 50)
    
    # 只创建测试文件，不自动上传
    create_test_paper_rule()
    
    print("\n📝 测试文件已创建，您可以:")
    print("1. 手动在浏览器中上传测试")
    print("2. 运行 test_upload_paper_rule() 函数进行自动测试")
    
    # 如果需要自动测试，取消下面的注释
    # test_upload_paper_rule()
