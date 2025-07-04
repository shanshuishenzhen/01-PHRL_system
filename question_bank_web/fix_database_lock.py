#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库锁定问题
"""

import sqlite3
import os
import time
import psutil
from contextlib import contextmanager

def check_database_locks():
    """检查数据库锁定状态"""
    print("=== 检查数据库锁定状态 ===")
    
    db_file = 'questions.db'
    if not os.path.exists(db_file):
        print(f"❌ 数据库文件不存在: {db_file}")
        return False
    
    try:
        # 尝试连接数据库
        conn = sqlite3.connect(db_file, timeout=5.0)
        cursor = conn.cursor()
        
        # 检查数据库是否可写
        cursor.execute("BEGIN IMMEDIATE;")
        cursor.execute("ROLLBACK;")
        
        print("✅ 数据库连接正常，无锁定")
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("❌ 数据库被锁定")
            return False
        else:
            print(f"❌ 数据库错误: {e}")
            return False
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")
        return False

def find_processes_using_database():
    """查找正在使用数据库的进程"""
    print("\n=== 查找使用数据库的进程 ===")
    
    db_file = os.path.abspath('questions.db')
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 检查进程是否在使用数据库文件
            for f in proc.open_files():
                if f.path == db_file:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    })
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if processes:
        print("找到以下进程正在使用数据库:")
        for proc in processes:
            print(f"  PID: {proc['pid']}, 名称: {proc['name']}")
            print(f"  命令行: {proc['cmdline']}")
    else:
        print("未找到正在使用数据库的进程")
    
    return processes

def kill_database_processes():
    """终止使用数据库的进程"""
    processes = find_processes_using_database()
    
    if not processes:
        return True
    
    print("\n=== 终止数据库进程 ===")
    for proc in processes:
        try:
            p = psutil.Process(proc['pid'])
            if 'python' in proc['name'].lower():
                print(f"终止Python进程 PID: {proc['pid']}")
                p.terminate()
                time.sleep(2)
                if p.is_running():
                    p.kill()
                    print(f"强制终止进程 PID: {proc['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"无法终止进程 PID: {proc['pid']}, 错误: {e}")
    
    time.sleep(3)
    return True

def backup_database():
    """备份数据库"""
    print("\n=== 备份数据库 ===")
    
    source = 'questions.db'
    backup = f'questions_backup_{int(time.time())}.db'
    
    try:
        import shutil
        shutil.copy2(source, backup)
        print(f"✅ 数据库已备份到: {backup}")
        return backup
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def fix_database_lock():
    """修复数据库锁定问题"""
    print("\n=== 修复数据库锁定 ===")
    
    # 方法1: 使用WAL模式
    try:
        conn = sqlite3.connect('questions.db', timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=10000;")
        conn.execute("PRAGMA temp_store=memory;")
        conn.commit()
        conn.close()
        print("✅ 已设置WAL模式和优化参数")
        return True
    except Exception as e:
        print(f"❌ 设置WAL模式失败: {e}")
    
    # 方法2: 重建数据库连接
    try:
        # 删除可能存在的锁文件
        lock_files = ['questions.db-shm', 'questions.db-wal', 'questions.db-journal']
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"✅ 删除锁文件: {lock_file}")
        
        # 测试数据库连接
        conn = sqlite3.connect('questions.db', timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions;")
        count = cursor.fetchone()[0]
        print(f"✅ 数据库连接正常，题目数量: {count}")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 重建连接失败: {e}")
        return False

@contextmanager
def safe_db_connection(db_path='questions.db', timeout=30.0):
    """安全的数据库连接上下文管理器"""
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=timeout)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def test_database_operations():
    """测试数据库操作"""
    print("\n=== 测试数据库操作 ===")
    
    try:
        with safe_db_connection() as conn:
            cursor = conn.cursor()
            
            # 测试读操作
            cursor.execute("SELECT COUNT(*) FROM questions;")
            count = cursor.fetchone()[0]
            print(f"✅ 读操作正常，题目数量: {count}")
            
            # 测试写操作（创建临时表）
            cursor.execute("""
                CREATE TEMPORARY TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    test_data TEXT
                );
            """)
            cursor.execute("INSERT INTO test_table (test_data) VALUES (?);", ("test",))
            conn.commit()
            print("✅ 写操作正常")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        return False

def main():
    """主修复流程"""
    print("数据库锁定问题修复工具")
    print("=" * 50)
    
    # 1. 检查当前状态
    if check_database_locks():
        print("✅ 数据库状态正常，无需修复")
        return True
    
    # 2. 备份数据库
    backup_file = backup_database()
    if not backup_file:
        print("⚠️ 备份失败，但继续修复")
    
    # 3. 查找并终止相关进程
    kill_database_processes()
    
    # 4. 修复数据库锁定
    if fix_database_lock():
        print("✅ 数据库锁定修复成功")
    else:
        print("❌ 数据库锁定修复失败")
        return False
    
    # 5. 测试数据库操作
    if test_database_operations():
        print("✅ 数据库功能测试通过")
        return True
    else:
        print("❌ 数据库功能测试失败")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 数据库锁定问题修复完成！")
            print("建议:")
            print("1. 重启Web服务器")
            print("2. 避免同时运行多个数据库操作")
            print("3. 使用提供的safe_db_connection()进行数据库操作")
        else:
            print("\n❌ 修复失败，请手动检查数据库文件")
    except KeyboardInterrupt:
        print("\n用户中断修复过程")
    except Exception as e:
        print(f"\n修复过程出错: {e}")
        import traceback
        traceback.print_exc()
