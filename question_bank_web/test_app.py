#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, get_question_type_info

def test_index():
    with app.test_client() as client:
        try:
            response = client.get('/')
            print(f'Status: {response.status_code}')
            if response.status_code == 200:
                print('Success! Page loaded correctly.')
                print(f'Data length: {len(response.data)}')

                # 检查题型显示
                content = response.data.decode('utf-8')
                if '单选题' in content:
                    print('✓ 题型显示正常：找到"单选题"')
                else:
                    print('✗ 题型显示异常：未找到"单选题"')

                if 'type-single' in content:
                    print('✓ 题型样式正常：找到"type-single"')
                else:
                    print('✗ 题型样式异常：未找到"type-single"')

            else:
                print(f'Error: {response.status_code}')
                print(response.data.decode('utf-8')[:500])
        except Exception as e:
            print(f'Exception: {e}')
            import traceback
            traceback.print_exc()

def test_question_type_mapping():
    print('\n题型映射测试:')
    test_codes = ['B', 'G', 'C', 'D', 'E', 'T', 'U', 'W', 'F', 'X']
    for code in test_codes:
        info = get_question_type_info(code)
        print(f'{code}: {info["name"]} ({info["class"]})')

if __name__ == '__main__':
    test_index()
    test_question_type_mapping()
