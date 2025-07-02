import os
import json
import shutil
import time
from datetime import datetime

class ScoreImporter:
    def __init__(self):
        # 定义导入目录和备份目录
        self.import_dir = os.path.join(os.path.dirname(__file__), 'imports')
        self.backup_dir = os.path.join(os.path.dirname(__file__), 'imports_backup')
        self.scores_file = os.path.join(os.path.dirname(__file__), 'scores.json')
        
        # 确保目录存在
        os.makedirs(self.import_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def load_current_scores(self):
        """加载当前成绩数据"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"scores": []}
        except Exception as e:
            print(f"加载当前成绩数据失败: {e}")
            return {"scores": []}
    
    def save_scores(self, scores):
        """保存成绩数据"""
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
            print(f"成绩数据已保存到 {self.scores_file}")
            return True
        except Exception as e:
            print(f"保存成绩数据失败: {e}")
            return False
    
    def backup_import_file(self, file_path):
        """备份导入文件"""
        try:
            filename = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, filename)
            shutil.copy2(file_path, backup_path)
            print(f"文件已备份到 {backup_path}")
            return True
        except Exception as e:
            print(f"备份文件失败: {e}")
            return False
    
    def import_scores_from_file(self, file_path):
        """从文件导入成绩数据"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False
            
            # 读取导入文件
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 加载当前成绩数据
            current_scores = self.load_current_scores()
            
            # 获取导入的成绩列表
            import_scores = import_data.get("scores", [])
            if not import_scores:
                print("导入文件中没有成绩数据")
                return False
            
            # 合并成绩数据（根据ID去重）
            existing_ids = {score.get("id") for score in current_scores.get("scores", [])}
            new_scores = []
            updated_scores = []
            
            for score in import_scores:
                score_id = score.get("id")
                if score_id in existing_ids:
                    # 更新现有成绩
                    for i, existing_score in enumerate(current_scores["scores"]):
                        if existing_score.get("id") == score_id:
                            current_scores["scores"][i] = score
                            updated_scores.append(score_id)
                            break
                else:
                    # 添加新成绩
                    current_scores["scores"].append(score)
                    new_scores.append(score_id)
            
            # 保存更新后的成绩数据
            if self.save_scores(current_scores):
                # 备份导入文件
                self.backup_import_file(file_path)
                
                # 删除原导入文件
                os.remove(file_path)
                
                print(f"成功导入 {len(import_scores)} 条成绩数据")
                print(f"新增: {len(new_scores)} 条, 更新: {len(updated_scores)} 条")
                return True
            else:
                print("保存成绩数据失败")
                return False
                
        except Exception as e:
            print(f"导入成绩数据失败: {e}")
            return False
    
    def import_all_pending_files(self):
        """导入所有待处理文件"""
        try:
            # 获取导入目录中的所有JSON文件
            import_files = [f for f in os.listdir(self.import_dir) if f.endswith('.json')]
            
            if not import_files:
                print("没有待导入的文件")
                return True
            
            success_count = 0
            for filename in import_files:
                file_path = os.path.join(self.import_dir, filename)
                print(f"正在导入: {filename}")
                
                if self.import_scores_from_file(file_path):
                    success_count += 1
            
            print(f"导入完成: 成功 {success_count}/{len(import_files)}")
            return success_count == len(import_files)
            
        except Exception as e:
            print(f"导入过程中发生错误: {e}")
            return False

# 自动导入功能
def auto_import():
    importer = ScoreImporter()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始自动导入成绩数据...")
    importer.import_all_pending_files()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动导入完成")

# 主函数
if __name__ == "__main__":
    importer = ScoreImporter()
    importer.import_all_pending_files()