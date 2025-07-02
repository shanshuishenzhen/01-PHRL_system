# -*- coding: utf-8 -*-
"""
Numpy导入冲突修复工具

解决模块化开发中pandas无法导入numpy的问题。

更新日志：
- 2025-01-07：创建numpy导入冲突修复工具
"""

import os
import sys
import importlib
from pathlib import Path
from typing import Optional


class NumpyImportFixer:
    """Numpy导入冲突修复器"""
    
    def __init__(self):
        self.original_path = sys.path.copy()
        self.numpy_installed = False
        self.pandas_installed = False
        
    def check_numpy_installation(self) -> bool:
        """检查numpy是否正确安装"""
        try:
            import numpy
            self.numpy_installed = True
            print(f"✅ numpy 版本: {numpy.__version__}")
            return True
        except ImportError as e:
            print(f"❌ numpy 导入失败: {e}")
            self.numpy_installed = False
            return False
    
    def check_pandas_installation(self) -> bool:
        """检查pandas是否正确安装"""
        try:
            import pandas
            self.pandas_installed = True
            print(f"✅ pandas 版本: {pandas.__version__}")
            return True
        except ImportError as e:
            print(f"❌ pandas 导入失败: {e}")
            self.pandas_installed = False
            return False
    
    def clean_sys_path(self):
        """清理sys.path中可能导致冲突的路径"""
        current_dir = os.getcwd()
        project_root = Path(__file__).parent.parent
        
        # 移除当前目录和项目根目录，避免导入冲突
        paths_to_remove = [
            current_dir,
            str(project_root),
            '.',
            ''
        ]
        
        cleaned_path = []
        for path in sys.path:
            if path not in paths_to_remove:
                cleaned_path.append(path)
        
        sys.path = cleaned_path
        print(f"🔧 清理sys.path，移除了 {len(sys.path) - len(cleaned_path)} 个可能冲突的路径")
    
    def fix_numpy_import(self) -> bool:
        """修复numpy导入问题"""
        print("🔧 正在修复numpy导入问题...")
        
        # 1. 清理sys.path
        self.clean_sys_path()
        
        # 2. 重新导入numpy
        if 'numpy' in sys.modules:
            del sys.modules['numpy']
        
        # 3. 尝试导入numpy
        try:
            import numpy
            print(f"✅ numpy 修复成功，版本: {numpy.__version__}")
            return True
        except ImportError as e:
            print(f"❌ numpy 修复失败: {e}")
            return False
    
    def fix_pandas_import(self) -> bool:
        """修复pandas导入问题"""
        print("🔧 正在修复pandas导入问题...")
        
        # 1. 确保numpy可用
        if not self.fix_numpy_import():
            return False
        
        # 2. 重新导入pandas
        if 'pandas' in sys.modules:
            del sys.modules['pandas']
        
        # 3. 尝试导入pandas
        try:
            import pandas
            print(f"✅ pandas 修复成功，版本: {pandas.__version__}")
            return True
        except ImportError as e:
            print(f"❌ pandas 修复失败: {e}")
            return False
    
    def restore_sys_path(self):
        """恢复原始的sys.path"""
        sys.path = self.original_path.copy()
        print("🔄 已恢复原始sys.path")
    
    def safe_import_numpy(self):
        """安全导入numpy"""
        try:
            # 临时清理路径
            original_path = sys.path.copy()
            self.clean_sys_path()
            
            # 导入numpy
            import numpy
            
            # 恢复路径
            sys.path = original_path
            
            return numpy
        except ImportError:
            # 恢复路径
            sys.path = original_path
            raise
    
    def safe_import_pandas(self):
        """安全导入pandas"""
        try:
            # 临时清理路径
            original_path = sys.path.copy()
            self.clean_sys_path()
            
            # 先导入numpy
            import numpy
            # 再导入pandas
            import pandas
            
            # 恢复路径
            sys.path = original_path
            
            return pandas
        except ImportError:
            # 恢复路径
            sys.path = original_path
            raise


def fix_numpy_import_globally():
    """全局修复numpy导入问题"""
    fixer = NumpyImportFixer()
    
    print("🚀 开始修复numpy导入问题")
    print("=" * 40)
    
    # 检查当前状态
    print("📋 检查当前安装状态:")
    numpy_ok = fixer.check_numpy_installation()
    pandas_ok = fixer.check_pandas_installation()
    
    if numpy_ok and pandas_ok:
        print("✅ numpy和pandas都正常，无需修复")
        return True
    
    # 尝试修复
    if not numpy_ok:
        if not fixer.fix_numpy_import():
            print("❌ numpy修复失败")
            return False
    
    if not pandas_ok:
        if not fixer.fix_pandas_import():
            print("❌ pandas修复失败")
            return False
    
    print("✅ 修复完成")
    return True


def create_import_wrapper():
    """创建导入包装器"""
    wrapper_code = '''
# -*- coding: utf-8 -*-
"""
安全导入包装器
避免numpy导入冲突
"""

def safe_import_numpy():
    """安全导入numpy"""
    import sys
    import os
    
    # 临时移除当前目录
    original_path = sys.path.copy()
    if '.' in sys.path:
        sys.path.remove('.')
    if '' in sys.path:
        sys.path.remove('')
    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())
    
    try:
        import numpy
        sys.path = original_path
        return numpy
    except ImportError:
        sys.path = original_path
        raise


def safe_import_pandas():
    """安全导入pandas"""
    import sys
    import os
    
    # 临时移除当前目录
    original_path = sys.path.copy()
    if '.' in sys.path:
        sys.path.remove('.')
    if '' in sys.path:
        sys.path.remove('')
    if os.getcwd() in sys.path:
        sys.path.remove(os.getcwd())
    
    try:
        import numpy  # 先导入numpy
        import pandas
        sys.path = original_path
        return pandas
    except ImportError:
        sys.path = original_path
        raise


# 使用示例:
# from common.numpy_fix import safe_import_numpy, safe_import_pandas
# np = safe_import_numpy()
# pd = safe_import_pandas()
'''
    
    wrapper_file = Path(__file__).parent / "safe_imports.py"
    with open(wrapper_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_code)
    
    print(f"✅ 创建导入包装器: {wrapper_file}")


if __name__ == "__main__":
    # 修复numpy导入问题
    fix_numpy_import_globally()
    
    # 创建导入包装器
    create_import_wrapper()
    
    print("\n📋 使用说明:")
    print("1. 在需要使用numpy/pandas的模块中:")
    print("   from common.safe_imports import safe_import_numpy, safe_import_pandas")
    print("   np = safe_import_numpy()")
    print("   pd = safe_import_pandas()")
    print("2. 或者直接调用修复函数:")
    print("   from common.numpy_fix import fix_numpy_import_globally")
    print("   fix_numpy_import_globally()")
