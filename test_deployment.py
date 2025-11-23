#!/usr/bin/env python3
"""
部署测试脚本 - 验证岗责驱动的周工作计划管理系统
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_deployment():
    """测试系统部署状态"""
    print("=" * 60)
    print("岗责驱动的周工作计划管理系统 - 部署测试")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    frontend_url = "http://localhost:3000"
    
    test_results = []
    
    # 1. 测试后端服务
    print("\n1. 测试后端服务...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✓ 后端服务正常运行")
            test_results.append(("后端服务", "通过"))
        else:
            print(f"✗ 后端服务异常: {response.status_code}")
            test_results.append(("后端服务", "失败"))
    except Exception as e:
        print(f"✗ 后端服务连接失败: {e}")
        test_results.append(("后端服务", "失败"))
    
    # 2. 测试前端服务
    print("\n2. 测试前端服务...")
    try:
        response = requests.get(frontend_url)
        if response.status_code == 200 and "岗责驱动的周工作计划管理系统" in response.text:
            print("✓ 前端服务正常运行")
            test_results.append(("前端服务", "通过"))
        else:
            print(f"✗ 前端服务异常: {response.status_code}")
            print(f"  页面内容预览: {response.text[:100]}...")
            test_results.append(("前端服务", "失败"))
    except Exception as e:
        print(f"✗ 前端服务连接失败: {e}")
        test_results.append(("前端服务", "失败"))
    
    # 3. 测试用户登录 (等待限流结束)
    print("\n3. 测试用户登录...")
    time.sleep(5)  # 等待限流结束
    
    try:
        # 测试管理员登录
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(
            f"{base_url}/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✓ 管理员登录成功")
            test_results.append(("管理员登录", "通过"))
            
            # 4. 测试获取用户信息
            print("\n4. 测试获取用户信息...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/api/users/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✓ 获取用户信息成功: {user_data.get('full_name')}")
                test_results.append(("获取用户信息", "通过"))
            else:
                print(f"✗ 获取用户信息失败: {response.status_code}")
                test_results.append(("获取用户信息", "失败"))
            
            # 5. 测试获取岗位列表
            print("\n5. 测试获取岗位列表...")
            response = requests.get(f"{base_url}/api/roles/", headers=headers)
            
            if response.status_code == 200:
                roles_data = response.json()
                print(f"✓ 获取岗位列表成功: {len(roles_data)} 个岗位")
                test_results.append(("获取岗位列表", "通过"))
            else:
                print(f"✗ 获取岗位列表失败: {response.status_code}")
                test_results.append(("获取岗位列表", "失败"))
                
        else:
            print(f"✗ 管理员登录失败: {response.status_code} - {response.text}")
            test_results.append(("管理员登录", "失败"))
            
    except Exception as e:
        print(f"✗ 登录测试失败: {e}")
        test_results.append(("管理员登录", "失败"))
    
    # 6. 测试普通用户登录
    print("\n6. 测试普通用户登录...")
    time.sleep(2)  # 等待限流
    
    try:
        login_data = {
            "username": "zhangsan",
            "password": "123456"
        }
        response = requests.post(
            f"{base_url}/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✓ 普通用户登录成功")
            test_results.append(("普通用户登录", "通过"))
        else:
            print(f"✗ 普通用户登录失败: {response.status_code}")
            test_results.append(("普通用户登录", "失败"))
            
    except Exception as e:
        print(f"✗ 普通用户登录测试失败: {e}")
        test_results.append(("普通用户登录", "失败"))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通过" if result == "通过" else "✗ 失败"
        print(f"{test_name}: {status}")
        if result == "通过":
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统部署成功！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    success = test_deployment()
    sys.exit(0 if success else 1)