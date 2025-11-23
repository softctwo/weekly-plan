#!/usr/bin/env python3
"""
检查LLM配置详情
"""
import requests
import json

def check_llm_configs():
    """检查LLM配置详情"""
    
    base_url = "http://localhost:8000/api"
    
    print("=== LLM配置详情检查 ===")
    
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
    
    # 2. 获取详细的LLM配置
    print("\n2. 获取详细的LLM配置...")
    try:
        configs_response = requests.get(f"{base_url}/ai/llm-configs", headers=headers)
        print(f"LLM配置状态码: {configs_response.status_code}")
        
        if configs_response.status_code == 200:
            configs = configs_response.json()
            print(f"配置数量: {len(configs)}")
            
            print("\n详细配置信息:")
            for i, config in enumerate(configs, 1):
                print(f"\n配置 {i}:")
                print(f"  ID: {config.get('id', 'N/A')}")
                print(f"  名称: {config.get('name', 'N/A')}")
                print(f"  提供商: {config.get('provider', 'N/A')}")
                print(f"  模型: {config.get('model', 'N/A')}")
                print(f"  启用状态: {config.get('is_enabled', False)}")
                print(f"  API密钥: {'已设置' if config.get('api_key') else '未设置'}")
                print(f"  API地址: {config.get('api_base', '默认')}")
                print(f"  创建时间: {config.get('created_at', 'N/A')}")
                
                # 检查是否有额外的错误信息
                if 'error' in config:
                    print(f"  错误信息: {config['error']}")
                
                # 显示配置状态
                if not config.get('is_enabled', False):
                    print(f"  ⚠️  该配置未启用")
                if not config.get('api_key'):
                    print(f"  ⚠️  缺少API密钥")
            
            # 3. 尝试启用一个配置（如果没有启用的）
            enabled_configs = [c for c in configs if c.get('is_enabled', False)]
            if not enabled_configs and configs:
                print("\n3. 尝试启用配置...")
                first_config = configs[0]
                config_id = first_config['id']
                
                # 更新配置为启用状态
                update_data = {
                    "is_enabled": True,
                    "name": first_config['name'],
                    "provider": first_config['provider'],
                    "model": first_config['model'],
                    "api_key": first_config.get('api_key', ''),  # 保持现有密钥
                    "api_base": first_config.get('api_base', '')
                }
                
                print(f"尝试启用配置: {first_config['name']} (ID: {config_id})")
                update_response = requests.put(
                    f"{base_url}/ai/llm-configs/{config_id}",
                    json=update_data,
                    headers=headers
                )
                
                print(f"更新配置状态码: {update_response.status_code}")
                if update_response.status_code == 200:
                    print("✅ 配置启用成功")
                    return True
                else:
                    print(f"❌ 配置启用失败: {update_response.text}")
                    return False
            
            return len(enabled_configs) > 0
        else:
            print(f"❌ 获取LLM配置失败: {configs_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 检查LLM配置错误: {e}")
        return False

def main():
    """主函数"""
    success = check_llm_configs()
    
    print("\n" + "="*60)
    if success:
        print("✅ LLM配置检查完成，有可用配置")
    else:
        print("❌ LLM配置检查失败，需要手动配置")
        print("\n📋 解决方案:")
        print("1. 登录系统管理界面")
        print("2. 进入AI分析配置页面")
        print("3. 添加或启用LLM配置")
        print("4. 确保填写正确的API密钥")

if __name__ == "__main__":
    main()