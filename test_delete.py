import json
import os

def check_users():
    f = 'user_management/users.json'
    print(f"文件存在: {os.path.exists(f)}")
    if os.path.exists(f):
        print(f"文件大小: {os.path.getsize(f)} bytes")
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"用户数量: {len(data.get('users', []))}")
        for i, user in enumerate(data.get('users', [])):
            print(f"用户{i+1}: ID={user.get('id')}, 用户名={user.get('username')}")

def test_delete():
    """测试删除功能"""
    f = 'user_management/users.json'
    
    # 读取原始数据
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    original_count = len(data.get('users', []))
    print(f"删除前用户数量: {original_count}")
    
    # 要删除的用户ID（选择一些非超级用户）
    users_to_delete = [2, 3, 4, 5]  # 删除ID为2,3,4,5的用户
    print(f"要删除的用户ID: {users_to_delete}")
    
    # 执行删除
    filtered_users = []
    deleted_count = 0
    
    for user in data.get('users', []):
        if user.get('id') in users_to_delete:
            if user.get('role') == 'super_admin':
                print(f"跳过超级用户: {user.get('username')}")
                filtered_users.append(user)
            else:
                print(f"删除用户: {user.get('username')} (ID: {user.get('id')})")
                deleted_count += 1
        else:
            filtered_users.append(user)
    
    # 更新数据
    data['users'] = filtered_users
    
    # 保存数据
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    
    print(f"删除后用户数量: {len(filtered_users)}")
    print(f"实际删除数量: {deleted_count}")
    print("删除操作完成！")

if __name__ == "__main__":
    print("=== 删除前状态 ===")
    check_users()
    print("\n=== 执行删除测试 ===")
    test_delete()
    print("\n=== 删除后状态 ===")
    check_users() 