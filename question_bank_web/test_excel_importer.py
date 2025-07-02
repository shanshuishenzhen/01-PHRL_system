import unittest
import os
import pandas as pd
import tempfile
import unittest.mock as mock
from excel_importer import parse_question_id, import_questions_from_excel, save_questions_to_db
from sqlalchemy.exc import OperationalError

class TestExcelImporter(unittest.TestCase):
    def setUp(self):
        self.test_excel = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        self.test_excel.close()
        
        self.valid_data = {
            'ID': ['A-B-C-001-001', 'A-B-C-001-002'],
            '题型代码': ['B', 'G'],
            '难度代码': ['1', '3'],
            '一致性代码': ['5', '4'],
            '试题（题干）': ['题干1', '题干2'],
            '正确答案': ['A', 'A,B']
        }
        
        expected_columns = [
            '序号', '认定点代码', '题号', '试题（选项A）', '试题（选项B）', 
            '试题（选项C）', '试题（选项D）', '试题（选项E）', '【图】及位置', '解析'
        ]
        for col in expected_columns:
            self.valid_data[col] = [''] * len(self.valid_data['ID'])
    
    def tearDown(self):
        os.unlink(self.test_excel.name)
    
    def test_parse_question_id_valid(self):
        result = parse_question_id('A-B-C-D-001')
        self.assertEqual(result, {
            "full_id": "A-B-C-D-001",
            "level1_code": "A",
            "level2_code": "B",
            "level3_code": "C",
            "knowledge_point": "D",
            "sequence": "001"
        })
    
    def test_parse_question_id_invalid(self):
        with self.assertRaises(ValueError):
            parse_question_id('A-B-C')
    
    def test_import_valid_excel(self):
        df = pd.DataFrame(self.valid_data)
        df.to_excel(self.test_excel.name, index=False)
        
        questions, errors = import_questions_from_excel(self.test_excel.name)
        self.assertEqual(len(questions), 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(questions[0]['id'], 'A-B-C-001-001')
        
    def test_export_error_report(self):
        from excel_importer import export_error_report
        
        errors = [
            {"row": 2, "id": "ID001", "message": "错误1"},
            {"row": 3, "id": "ID002", "message": "错误2"}
        ]
        
        report_path = export_error_report(errors)
        self.assertTrue(os.path.exists(report_path))
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("总错误数: 2", content)
            self.assertIn("第 2 行 (ID: ID001): 错误1", content)
            self.assertIn("第 3 行 (ID: ID002): 错误2", content)
        
        os.unlink(report_path)
    
    def test_missing_columns(self):
        invalid_data = {k: v for k, v in self.valid_data.items() if k != '题型代码'}
        df = pd.DataFrame(invalid_data)
        df.to_excel(self.test_excel.name, index=False)
        
        questions, errors = import_questions_from_excel(self.test_excel.name)
        self.assertEqual(len(questions), 0)
        self.assertGreater(len(errors), 0)
        self.assertIn("Excel文件缺少预期的列", errors[0]['message'])
    
    def test_invalid_question_type(self):
        invalid_data = self.valid_data.copy()
        invalid_data['题型代码'] = ['B', 'X']
        df = pd.DataFrame(invalid_data)
        df.to_excel(self.test_excel.name, index=False)
        
        questions, errors = import_questions_from_excel(self.test_excel.name)
        self.assertEqual(len(questions), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("无效的题型代码", errors[0]['message'])
    
    def test_missing_stem(self):
        invalid_data = self.valid_data.copy()
        invalid_data['试题（题干）'] = ['题干1', '']
        df = pd.DataFrame(invalid_data)
        df.to_excel(self.test_excel.name, index=False)
        
        questions, errors = import_questions_from_excel(self.test_excel.name)
        self.assertEqual(len(questions), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("题干不能为空", errors[0]['message'])
    
    @mock.patch('excel_importer.create_engine')
    @mock.patch('excel_importer.sessionmaker')
    def test_save_to_db_success(self, mock_sessionmaker, mock_create_engine):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock.MagicMock(return_value=mock_session)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with mock.patch.dict(os.environ, {'DATABASE_URL': 'test_db_url'}):
            questions = [{'id': 'test-id', 'stem': 'test stem'}]
            errors = save_questions_to_db(questions)
            
            self.assertEqual(len(errors), 0)
            mock_session.commit.assert_called_once()
    
    def test_save_to_db_missing_url(self):
        with mock.patch.dict(os.environ, clear=True):
            errors = save_questions_to_db([{'id': 'test'}])
            self.assertEqual(len(errors), 1)
            self.assertIn("数据库连接字符串未设置", errors[0]['message'])
            
    @mock.patch('excel_importer.create_engine')
    @mock.patch('excel_importer.sessionmaker')
    @mock.patch('time.sleep', return_value=None)
    def test_save_to_db_retry_success(self, mock_sleep, mock_sessionmaker, mock_create_engine):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock.MagicMock(return_value=mock_session)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        mock_session.commit.side_effect = [
            OperationalError("模拟数据库错误", {}, None),
            None
        ]
        
        with mock.patch.dict(os.environ, {'DATABASE_URL': 'test_db_url'}):
            questions = [{'id': 'test-id', 'stem': 'test stem'}]
            errors = save_questions_to_db(questions, max_retries=2)
            
            self.assertEqual(len(errors), 0)
            self.assertEqual(mock_session.commit.call_count, 2)
            mock_sleep.assert_called_once()
            
    @mock.patch('excel_importer.create_engine')
    @mock.patch('excel_importer.sessionmaker')
    @mock.patch('time.sleep', return_value=None)
    def test_save_to_db_retry_failure(self, mock_sleep, mock_sessionmaker, mock_create_engine):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock.MagicMock(return_value=mock_session)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        mock_session.commit.side_effect = OperationalError("模拟数据库错误", {}, None)
        
        with mock.patch.dict(os.environ, {'DATABASE_URL': 'test_db_url'}):
            questions = [{'id': 'test-id', 'stem': 'test stem'}]
            errors = save_questions_to_db(questions, max_retries=3)
            
            self.assertEqual(len(errors), 4)
            self.assertEqual(mock_session.commit.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)
            self.assertIn("达到最大重试次数 (3)", errors[-1]['message'])
            
    @mock.patch('excel_importer.export_error_report')
    def test_error_report_in_main(self, mock_export):
        from excel_importer import main
        
        invalid_data = self.valid_data.copy()
        invalid_data['题型代码'] = ['B', 'X']
        df = pd.DataFrame(invalid_data)
        df.to_excel(self.test_excel.name, index=False)
        
        with mock.patch('excel_importer.import_questions_from_excel') as mock_import:
            mock_import.return_value = ([], [{"message": "测试错误"}])
            main()
        
        mock_export.assert_called_once()

if __name__ == '__main__':
    unittest.main()
