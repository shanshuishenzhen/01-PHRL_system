#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库生成器修复测试脚本

测试修复后的题库生成功能，包括：
1. df变量定义问题修复
2. 题库名称逻辑改进
3. 增量生成功能
4. 样例题库生成
"""

import sys
import os
import unittest
import pandas as pd
import tempfile
import json
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入题库生成器模块
try:
    from developer_tools.question_bank_generator import generate_from_excel, generate_question
    GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入题库生成器模块: {e}")
    GENERATOR_AVAILABLE = False

class TestQuestionBankGeneratorFix(unittest.TestCase):
    """题库生成器修复测试类"""
    
    def setUp(self):
        """测试前准备"""
        if not GENERATOR_AVAILABLE:
            self.skipTest("题库生成器模块不可用")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试用的Excel模板
        self.test_excel_path = os.path.join(self.temp_dir, "test_template.xlsx")
        self.create_test_excel_template()
        
        # 输出文件路径
        self.output_path = os.path.join(self.temp_dir, "test_output.xlsx")
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_excel_template(self):
        """创建测试用的Excel模板"""
        # 创建测试数据
        test_data = {
            '题库名称': ['保卫管理员（三级）理论', '保卫管理员（三级）理论', '消防安全管理'],
            '1级代码': ['A', 'A', 'B'],
            '2级代码': ['A-01', 'A-01', 'B-01'],
            '3级代码': ['A-01-001', 'A-01-002', 'B-01-001'],
            '知识点数量': [2, 1, 3],
            'B(单选题)': [5, 3, 4],
            'C(判断题)': [2, 1, 2],
            'G(多选题)': [1, 0, 1]
        }
        
        df = pd.DataFrame(test_data)
        df.to_excel(self.test_excel_path, index=False)
        print(f"✅ 创建测试Excel模板: {self.test_excel_path}")
    
    def test_generate_question_function(self):
        """测试单个题目生成函数"""
        try:
            question = generate_question('B', 'A-01-001', 1, 1, '单选题')
            
            # 检查必要字段
            self.assertIn('id', question)
            self.assertIn('type', question)
            self.assertIn('stem', question)
            self.assertIn('options', question)
            self.assertIn('answer', question)
            
            # 检查ID格式
            expected_id = 'B-A-01-001-001-001'
            self.assertEqual(question['id'], expected_id)
            
            print("✅ 单个题目生成测试通过")
            
        except Exception as e:
            self.fail(f"单个题目生成测试失败: {e}")
    
    def test_excel_reading(self):
        """测试Excel文件读取"""
        try:
            df = pd.read_excel(self.test_excel_path)
            
            # 检查必要列是否存在
            required_columns = ['题库名称', '1级代码', '2级代码', '3级代码', '知识点数量']
            for col in required_columns:
                self.assertIn(col, df.columns, f"缺少必要列: {col}")
            
            # 检查数据行数
            self.assertGreater(len(df), 0, "Excel文件应包含数据行")
            
            print("✅ Excel文件读取测试通过")
            
        except Exception as e:
            self.fail(f"Excel文件读取测试失败: {e}")
    
    def test_basic_generation(self):
        """测试基本生成功能"""
        try:
            total_generated, bank_name = generate_from_excel(self.test_excel_path, self.output_path)
            
            # 检查返回值
            self.assertIsInstance(total_generated, int)
            self.assertGreater(total_generated, 0)
            self.assertIsInstance(bank_name, str)
            self.assertTrue(bank_name.endswith('样例题库'))
            
            # 检查输出文件是否存在
            self.assertTrue(os.path.exists(self.output_path))
            
            # 检查Excel文件内容
            output_df = pd.read_excel(self.output_path)
            self.assertGreater(len(output_df), 0)
            self.assertIn('题库名称', output_df.columns)
            
            print(f"✅ 基本生成测试通过 - 题库: {bank_name}, 题目数: {total_generated}")
            
        except Exception as e:
            self.fail(f"基本生成测试失败: {e}")
    
    def test_bank_name_logic(self):
        """测试题库名称逻辑"""
        try:
            total_generated, bank_name = generate_from_excel(self.test_excel_path, self.output_path)
            
            # 检查题库名称是否正确添加了"样例题库"后缀
            self.assertTrue(bank_name.endswith('样例题库'))
            
            # 读取输出文件检查题库名称
            output_df = pd.read_excel(self.output_path)
            unique_bank_names = output_df['题库名称'].unique()
            
            # 应该只有一个题库名称（第一个非空的）
            self.assertEqual(len(unique_bank_names), 1)
            self.assertEqual(unique_bank_names[0], bank_name)
            
            print(f"✅ 题库名称逻辑测试通过 - 名称: {bank_name}")
            
        except Exception as e:
            self.fail(f"题库名称逻辑测试失败: {e}")
    
    def test_append_mode(self):
        """测试增量模式"""
        try:
            # 第一次生成
            total_1, bank_name_1 = generate_from_excel(self.test_excel_path, self.output_path, append_mode=False)
            
            # 创建另一个模板（不同题库名称）
            test_data_2 = {
                '题库名称': ['新题库测试'],
                '1级代码': ['C'],
                '2级代码': ['C-01'],
                '3级代码': ['C-01-001'],
                '知识点数量': [1],
                'B(单选题)': [2],
                'C(判断题)': [1]
            }
            
            test_excel_2 = os.path.join(self.temp_dir, "test_template_2.xlsx")
            df_2 = pd.DataFrame(test_data_2)
            df_2.to_excel(test_excel_2, index=False)
            
            # 第二次生成（增量模式）
            total_2, bank_name_2 = generate_from_excel(test_excel_2, self.output_path, append_mode=True)
            
            # 检查结果
            output_df = pd.read_excel(self.output_path)
            unique_bank_names = output_df['题库名称'].unique()
            
            # 应该有两个不同的题库名称
            self.assertEqual(len(unique_bank_names), 2)
            self.assertIn(bank_name_1, unique_bank_names)
            self.assertIn(bank_name_2, unique_bank_names)
            
            # 总题目数应该是两次生成的总和
            total_questions = len(output_df)
            self.assertGreater(total_questions, total_1)
            
            print(f"✅ 增量模式测试通过 - 题库1: {bank_name_1}, 题库2: {bank_name_2}")
            
        except Exception as e:
            self.fail(f"增量模式测试失败: {e}")
    
    def test_json_backup(self):
        """测试JSON备份功能"""
        try:
            total_generated, bank_name = generate_from_excel(self.test_excel_path, self.output_path)
            
            # 检查JSON备份文件
            json_path = self.output_path.replace('.xlsx', '.json')
            self.assertTrue(os.path.exists(json_path))
            
            # 读取JSON文件
            with open(json_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # 检查JSON结构
            self.assertIn('bank_name', backup_data)
            self.assertIn('questions', backup_data)
            self.assertIn('generation_time', backup_data)
            self.assertIn('append_mode', backup_data)
            
            # 检查数据一致性
            self.assertEqual(backup_data['bank_name'], bank_name)
            self.assertEqual(len(backup_data['questions']), total_generated)
            
            print(f"✅ JSON备份测试通过 - 备份文件: {json_path}")
            
        except Exception as e:
            self.fail(f"JSON备份测试失败: {e}")

def run_manual_test():
    """运行手动测试"""
    print("\n🧪 开始手动测试...")
    
    try:
        # 检查是否有样例模板文件
        template_path = os.path.join('developer_tools', '样例题组题规则模板.xlsx')
        if not os.path.exists(template_path):
            print(f"❌ 样例模板文件不存在: {template_path}")
            return
        
        # 测试输出路径
        output_path = os.path.join('question_bank_web', 'questions_sample_test.xlsx')
        
        print(f"📁 使用模板: {template_path}")
        print(f"📁 输出路径: {output_path}")
        
        # 测试基本生成
        print("\n1. 测试基本生成...")
        total_generated, bank_name = generate_from_excel(template_path, output_path)
        print(f"✅ 生成成功 - 题库: {bank_name}, 题目数: {total_generated}")
        
        # 测试增量生成
        print("\n2. 测试增量生成...")
        total_generated_2, bank_name_2 = generate_from_excel(template_path, output_path, append_mode=True)
        print(f"✅ 增量生成成功 - 题库: {bank_name_2}, 题目数: {total_generated_2}")
        
        # 检查最终结果
        if os.path.exists(output_path):
            df = pd.read_excel(output_path)
            print(f"📊 最终文件包含 {len(df)} 道题目")
            print(f"📚 题库名称: {df['题库名称'].unique()}")
        
        print("\n✅ 手动测试完成")
        
    except Exception as e:
        print(f"❌ 手动测试失败: {e}")

def main():
    """主函数"""
    print("🔧 题库生成器修复测试")
    print("=" * 50)
    
    if not GENERATOR_AVAILABLE:
        print("❌ 题库生成器模块不可用，无法进行测试")
        return
    
    # 运行单元测试
    print("\n🧪 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 询问是否运行手动测试
    print("\n" + "=" * 50)
    response = input("是否运行手动测试？(y/n): ").lower().strip()
    
    if response in ['y', 'yes', '是']:
        run_manual_test()
    else:
        print("跳过手动测试")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
