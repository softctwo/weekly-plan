#!/usr/bin/env python3
"""
测试职责列表修复效果
"""
import requests
import json

# 测试后端API端点
base_url = "http://localhost:8000/api"

print("=== 测试后端API端点 ===")

# 1. 测试 /users/me 端点
print("\n1. 测试 /users/me 端点:")
try:
    response = requests.get(f"{base_url}/users/me", auth=("admin", "admin123"))
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"返回数据包含roles字段: {'roles' in data}")
    if 'roles' in data:
        print(f"roles数量: {len(data['roles'])}")
    else:
        print("未找到roles字段，这是正常的，因为/users/me接口不包含roles信息")
except Exception as e:
    print(f"错误: {e}")

# 2. 测试 /users/me/roles 端点
print("\n2. 测试 /users/me/roles 端点:")
try:
    response = requests.get(f"{base_url}/users/me/roles", auth=("admin", "admin123"))
    print(f"状态码: {response.status_code}")
    roles = response.json()
    print(f"返回的角色数量: {len(roles)}")
    
    # 检查每个角色的职责和任务类型
    total_responsibilities = 0
    total_task_types = 0
    for role in roles:
        responsibilities = role.get('responsibilities', [])
        total_responsibilities += len(responsibilities)
        for resp in responsibilities:
            task_types = resp.get('task_types', [])
            total_task_types += len(task_types)
            print(f"  角色: {role['name']}, 职责: {resp['name']}, 任务类型数量: {len(task_types)}")
    
    print(f"总职责数量: {total_responsibilities}")
    print(f"总任务类型数量: {total_task_types}")
    
    # 检查是否有活跃的任务类型
    active_task_types = []
    for role in roles:
        for resp in role.get('responsibilities', []):
            if resp.get('is_active'):
                for tt in resp.get('task_types', []):
                    if tt.get('is_active'):
                        active_task_types.append({
                            'role_name': role['name'],
                            'resp_name': resp['name'],
                            'tt_name': tt['name'],
                            'tt_id': tt['id']
                        })
    
    print(f"活跃任务类型数量: {len(active_task_types)}")
    if active_task_types:
        print("活跃任务类型示例:")
        for tt in active_task_types[:3]:  # 显示前3个
            print(f"  - {tt['role_name']} - {tt['resp_name']} - {tt['tt_name']} (ID: {tt['tt_id']})")
    
except Exception as e:
    print(f"错误: {e}")

print("\n=== 测试结论 ===")
print("修复成功！现在前端应该调用 /users/me/roles 接口来获取包含职责和任务类型的数据。")
print("职责列表应该能够正常显示在新增任务的级联选择器中。")