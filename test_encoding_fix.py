#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编码问题修复脚本
"""

import os
import sys
import pandas as pd
import traceback

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_excel_reading():
    """测试Excel文件读取"""
    print("🔍 测试Excel文件读取")
    print("-" * 40)
    
    template_path = os.path.join('developer_tools', '样例题组题规则模板.xlsx')
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    try:
        # 测试不同的读取方式
        print("1. 使用默认引擎读取...")
        df1 = pd.read_excel(template_path)
        print(f"✅ 默认引擎读取成功，行数: {len(df1)}")
        
        print("2. 使用openpyxl引擎读取...")
        df2 = pd.read_excel(template_path, engine='openpyxl')
        print(f"✅ openpyxl引擎读取成功，行数: {len(df2)}")
        
        print("3. 检查列名...")
        print(f"列名: {list(df2.columns)}")
        
        print("4. 检查数据类型...")
        for col in df2.columns:
            print(f"  {col}: {df2[col].dtype}")
        
        print("5. 检查是否有特殊字符...")
        for col in df2.columns:
            if df2[col].dtype == 'object':
                for idx, val in df2[col].items():
                    if pd.notna(val):
                        val_str = str(val)
                        # 检查是否包含特殊Unicode字符
                        for char in val_str:
                            if ord(char) > 127:
                                print(f"  发现非ASCII字符: '{char}' (U+{ord(char):04X}) 在列 '{col}' 行 {idx}")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel读取失败: {e}")
        traceback.print_exc()
        return False

def test_sample_generation():
    """测试样例题库生成"""
    print("\n🔍 测试样例题库生成")
    print("-" * 40)
    
    try:
        from developer_tools.question_bank_generator import generate_from_excel
        
        template_path = os.path.join('developer_tools', '样例题组题规则模板.xlsx')
        output_path = os.path.join('test_output.xlsx')
        
        if not os.path.exists(template_path):
            print(f"❌ 模板文件不存在: {template_path}")
            return False
        
        print("1. 开始生成样例题库...")
        result = generate_from_excel(template_path, output_path, append_mode=False)
        
        if len(result) == 3:
            total_generated, bank_name, db_success = result
            print(f"✅ 生成成功!")
            print(f"  题库名称: {bank_name}")
            print(f"  题目数量: {total_generated}")
            print(f"  数据库保存: {'成功' if db_success else '失败'}")
        else:
            total_generated, bank_name = result
            print(f"✅ 生成成功!")
            print(f"  题库名称: {bank_name}")
            print(f"  题目数量: {total_generated}")
        
        # 检查输出文件
        if os.path.exists(output_path):
            print(f"✅ 输出文件已创建: {output_path}")
            
            # 读取输出文件验证
            df_output = pd.read_excel(output_path)
            print(f"✅ 输出文件验证成功，包含 {len(df_output)} 行数据")
            
            # 清理测试文件
            os.remove(output_path)
            print("✅ 测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 样例题库生成失败: {e}")
        traceback.print_exc()
        return False

def test_encoding_handling():
    """测试编码处理"""
    print("\n🔍 测试编码处理")
    print("-" * 40)
    
    try:
        # 测试包含特殊字符的数据
        test_data = {
            '题库名称': ['测试题库♀', '测试题库♂'],
            'ID': ['TEST-001', 'TEST-002'],
            '题型代码': ['B（单选题）', 'G（多选题）'],
            '试题（题干）': ['这是一道测试题目♀', '这是另一道测试题目♂']
        }
        
        df = pd.DataFrame(test_data)
        print("1. 创建包含特殊字符的测试数据...")
        print(f"  数据形状: {df.shape}")
        
        # 测试保存
        test_file = 'test_encoding.xlsx'
        print("2. 测试保存到Excel...")
        
        try:
            df.to_excel(test_file, index=False, engine='openpyxl')
            print("✅ 使用openpyxl引擎保存成功")
        except UnicodeEncodeError as e:
            print(f"⚠️ 检测到编码错误: {e}")
            print("3. 尝试清理特殊字符...")
            
            # 清理特殊字符
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).apply(
                        lambda x: x.encode('utf-8', errors='ignore').decode('utf-8') if isinstance(x, str) else x
                    )
            
            df.to_excel(test_file, index=False, engine='openpyxl')
            print("✅ 清理特殊字符后保存成功")
        
        # 验证读取
        df_read = pd.read_excel(test_file, engine='openpyxl')
        print(f"✅ 读取验证成功，行数: {len(df_read)}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✅ 测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 编码处理测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 开发工具编码问题修复测试")
    print("=" * 50)
    
    tests = [
        ("Excel文件读取", test_excel_reading),
        ("编码处理", test_encoding_handling),
        ("样例题库生成", test_sample_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 发生异常: {e}")
            results.append((test_name, False))
    
    print("\n📊 测试结果汇总")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过！编码问题已修复。")
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")

if __name__ == '__main__':
    main()
