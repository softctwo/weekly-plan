#!/usr/bin/env python3
"""
测试AI分析功能修复
"""
import requests
import json

def test_ai_analysis_fix():
    """测试AI分析功能"""
    
    base_url = "http://localhost:8000/api"
    
    print("=== AI分析功能测试 ===")
    
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
    
    # 2. 检查LLM配置
    print("\n2. 检查LLM配置...")
    try:
        configs_response = requests.get(f"{base_url}/ai/llm-configs", headers=headers)
        print(f"LLM配置状态码: {configs_response.status_code}")
        
        if configs_response.status_code == 200:
            configs = configs_response.json()
            print(f"配置数量: {len(configs)}")
            
            enabled_configs = [c for c in configs if c.get('is_enabled', False)]
            print(f"启用配置数量: {len(enabled_configs)}")
            
            if enabled_configs:
                print("启用的配置:")
                for config in enabled_configs:
                    print(f"  - {config['name']} ({config['model']}) - 提供商: {config['provider']}")
            else:
                print("⚠️  没有启用的LLM配置")
                return False
        else:
            print(f"❌ 获取LLM配置失败: {configs_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 检查LLM配置错误: {e}")
        return False
    
    # 3. 测试AI分析
    print("\n3. 测试AI分析...")
    try:
        # 获取当前用户信息
        user_response = requests.get(f"{base_url}/users/me", headers=headers)
        if user_response.status_code == 200:
            current_user = user_response.json()
            print(f"当前用户: {current_user['full_name']} (类型: {current_user['user_type']})")
            
            # 检查权限
            if current_user['user_type'] not in ['admin', 'manager']:
                print("⚠️  当前用户没有AI分析权限")
                return False
        
        # 准备分析数据
        analysis_data = {
            "user_id": None,  # 分析整个团队
            "start_date": "2025-11-01",
            "end_date": "2025-11-30",
            "analysis_type": "comprehensive"
        }
        
        print(f"分析参数: {json.dumps(analysis_data, ensure_ascii=False, indent=2)}")
        
        # 发送分析请求
        print("正在发送AI分析请求...")
        analysis_response = requests.post(
            f"{base_url}/ai/analyze", 
            json=analysis_data, 
            headers=headers
        )
        
        print(f"AI分析状态码: {analysis_response.status_code}")
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            print("✅ AI分析成功！")
            print(f"分析对象: {result.get('user_name', '未知')}")
            print(f"分析周期: {result.get('analysis_period', '未知')}")
            print(f"统计信息: {json.dumps(result.get('statistics', {}), ensure_ascii=False, indent=2)}")
            
            # 显示分析结果摘要
            analysis_result = result.get('analysis_result', '')
            if analysis_result:
                print(f"分析结果摘要: {analysis_result[:200]}...")
            
            return True
        else:
            error_detail = analysis_response.json().get('detail', '未知错误')
            print(f"❌ AI分析失败: {error_detail}")
            
            # 尝试获取更详细的错误信息
            if analysis_response.status_code == 500:
                print("💡 500错误通常表示后端服务问题，可能是：")
                print("   - LLM配置不正确")
                print("   - LLM服务不可用")
                print("   - 数据库查询错误")
                print("   - 其他内部错误")
            
            return False
            
    except Exception as e:
        print(f"❌ AI分析错误: {e}")
        return False

def main():
    """主测试函数"""
    success = test_ai_analysis_fix()
    
    print("\n" + "="*60)
    if success:
        print("🎉 AI分析功能测试成功！")
        print("✅ 用户登录正常")
        print("✅ LLM配置获取正常")
        print("✅ AI分析功能正常")
        print("\n📋 结论: AI分析功能基本正常，如果前端有问题，可能是其他原因")
    else:
        print("❌ AI分析功能测试失败")
        print("需要进一步检查LLM配置和服务状态")

if __name__ == "__main__":
    main()