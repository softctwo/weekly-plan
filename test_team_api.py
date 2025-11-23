#!/usr/bin/env python3
"""
测试团队仪表盘API，检查团队数据是否能正常加载
"""
import requests
import json
import time

def test_team_dashboard():
    """测试团队仪表盘API"""
    
    base_url = "http://localhost:8000/api"
    
    print("=== 团队仪表盘API测试 ===")
    
    # 等待限流重置
    print("等待限流重置...")
    time.sleep(5)
    
    # 1. 用户登录
    print("\n1. 用户登录...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.text}")
            return False
            
        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("✅ 登录成功")
        
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return False
    
    # 2. 检查当前用户权限
    print("\n2. 检查当前用户权限...")
    try:
        user_response = requests.get(f"{base_url}/users/me", headers=headers)
        if user_response.status_code == 200:
            current_user = user_response.json()
            print(f"当前用户: {current_user['full_name']} (类型: {current_user['user_type']})")
            
            # 检查权限
            if current_user['user_type'] not in ['admin', 'manager']:
                print("⚠️  当前用户没有团队管理权限")
                return False
        else:
            print(f"❌ 获取用户信息失败: {user_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 检查用户权限错误: {e}")
        return False
    
    # 3. 测试团队仪表盘API
    print("\n3. 测试团队仪表盘API...")
    try:
        # 获取当前年份和周数
        from datetime import datetime
        now = datetime.now()
        year = now.year
        week_number = now.isocalendar()[1]
        
        print(f"请求参数: year={year}, week_number={week_number}")
        
        dashboard_response = requests.get(
            f"{base_url}/dashboard/team", 
            headers=headers,
            params={
                "year": year,
                "week_number": week_number
            }
        )
        
        print(f"团队仪表盘状态码: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ 团队仪表盘API调用成功")
            
            # 检查团队数据
            team_members = dashboard_data.get('team_members', [])
            print(f"团队成员数量: {len(team_members)}")
            
            if team_members:
                print("\n团队成员列表:")
                for i, member in enumerate(team_members[:5]):  # 显示前5个
                    print(f"  {i+1}. {member.get('full_name', '未知')} (ID: {member.get('id', 'N/A')})")
                    print(f"     总任务: {member.get('total_tasks', 0)}")
                    print(f"     完成任务: {member.get('completed_tasks', 0)}")
                    print(f"     完成率: {member.get('completion_rate', 0)}%")
                
                if len(team_members) > 5:
                    print(f"  ... 还有 {len(team_members) - 5} 个成员")
                
                return True
            else:
                print("⚠️  没有团队成员数据")
                return False
                
        elif dashboard_response.status_code == 403:
            print("❌ 权限不足，无法访问团队数据")
            print("需要管理员或管理者权限")
            return False
        elif dashboard_response.status_code == 404:
            print("❌ 团队数据未找到")
            return False
        else:
            print(f"❌ 团队仪表盘API调用失败: {dashboard_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 团队仪表盘API错误: {e}")
        return False
    
    # 4. 测试AI分析准备
    print("\n4. 测试AI分析准备...")
    try:
        # 检查是否有任务数据可用于分析
        if team_members:
            # 选择第一个成员进行测试
            test_member = team_members[0]
            user_id = test_member.get('id')
            
            print(f"选择测试成员: {test_member.get('full_name', '未知')} (ID: {user_id})")
            
            # 获取成员详细信息
            member_detail_response = requests.get(
                f"{base_url}/dashboard/team/member/{user_id}",
                headers=headers,
                params={
                    "year": year,
                    "week_number": week_number
                }
            )
            
            print(f"成员详情状态码: {member_detail_response.status_code}")
            
            if member_detail_response.status_code == 200:
                member_data = member_detail_response.json()
                tasks = member_data.get('tasks', [])
                print(f"成员任务数量: {len(tasks)}")
                
                if tasks:
                    print("✅ 有任务数据可用于AI分析")
                    return True
                else:
                    print("⚠️  成员没有任务数据")
                    return True  # 这不算失败
            else:
                print(f"⚠️  获取成员详情失败: {member_detail_response.text}")
                return True  # 这不算失败
        else:
            print("⚠️  没有团队成员可用于测试")
            return False
            
    except Exception as e:
        print(f"❌ AI分析准备错误: {e}")
        return False

def main():
    """主测试函数"""
    success = test_team_dashboard()
    
    print("\n" + "="*60)
    if success:
        print("🎉 团队仪表盘API测试成功！")
        print("✅ 用户登录正常")
        print("✅ 团队数据加载正常")
        print("✅ 团队成员列表正常返回")
        print("\n📋 结论: 后端API正常，AI分析对象选择器应该有数据")
        print("\n🔍 建议检查前端:")
        print("1. 检查AI分析对话框是否正确传入teamMembers")
        print("2. 检查团队数据是否在页面加载时获取")
        print("3. 检查控制台是否有JavaScript错误")
    else:
        print("❌ 团队仪表盘API测试失败")
        print("需要进一步检查后端API和用户权限")

if __name__ == "__main__":
    main()