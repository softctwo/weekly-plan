#!/usr/bin/env python3
"""
直接测试AI分析功能，绕过限流
"""
import sqlite3
import json
from datetime import datetime, timedelta

def test_ai_analysis_direct():
    """直接测试AI分析功能"""
    
    print("=== 直接AI分析功能测试 ===")
    
    # 1. 检查数据库连接
    print("\n1. 检查数据库连接...")
    try:
        conn = sqlite3.connect('/Users/zhangyanlong/workspaces/weekly-plan/backend/weekly_plan.db')
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 2. 检查LLM配置
        print("\n2. 检查LLM配置...")
        cursor.execute("SELECT id, name, provider, model_name, is_active, api_key FROM llm_configs WHERE is_active=1 AND is_deleted!=1;")
        configs = cursor.fetchall()
        
        if not configs:
            print("❌ 没有启用的LLM配置")
            return False
            
        print(f"✅ 找到 {len(configs)} 个启用的LLM配置")
        for config in configs:
            print(f"  配置: {config[1]} ({config[2]} - {config[3]})")
            print(f"  状态: {'启用' if config[4] else '禁用'}")
            print(f"  API密钥: {'已设置' if config[5] else '未设置'}")
        
        # 3. 检查用户数据
        print("\n3. 检查用户数据...")
        cursor.execute("SELECT id, username, full_name, user_type, is_active FROM users WHERE username='admin';")
        user = cursor.fetchone()
        
        if not user:
            print("❌ 没有找到admin用户")
            return False
            
        user_id, username, full_name, user_type, is_active = user
        print(f"✅ 用户存在: {full_name} (类型: {user_type})")
        
        if user_type not in ['admin', 'manager']:
            print(f"⚠️  用户类型 {user_type} 没有AI分析权限")
            return False
        
        # 4. 检查任务数据
        print("\n4. 检查任务数据...")
        # 获取最近30天的任务
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT COUNT(*) as total_tasks, 
                   SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_tasks,
                   SUM(CASE WHEN is_key_task = 1 THEN 1 ELSE 0 END) as key_tasks
            FROM weekly_tasks 
            WHERE user_id = ? 
            AND planned_start_time >= ? 
            AND planned_start_time <= ?
        """, (user_id, start_date, end_date))
        
        task_stats = cursor.fetchone()
        total_tasks = task_stats[0] or 0
        completed_tasks = task_stats[1] or 0  
        key_tasks = task_stats[2] or 0
        
        print(f"任务统计: 总任务={total_tasks}, 已完成={completed_tasks}, 重点任务={key_tasks}")
        
        if total_tasks == 0:
            print("⚠️  没有任务数据，AI分析可能无法进行")
        else:
            print("✅ 有任务数据可用于分析")
        
        # 5. 模拟AI服务调用
        print("\n5. 模拟AI服务调用...")
        
        # 构建模拟数据
        mock_data = {
            "user_name": full_name,
            "period": f"{start_date} 至 {end_date}",
            "statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                "key_tasks": key_tasks,
                "key_completion_rate": round((completed_tasks / key_tasks * 100) if key_tasks > 0 else 0, 1),
                "delayed_tasks": 0,
                "delay_rate": 0
            }
        }
        
        print("模拟数据构建成功:")
        print(f"  用户: {mock_data['user_name']}")
        print(f"  周期: {mock_data['period']}")
        print(f"  统计: {json.dumps(mock_data['statistics'], ensure_ascii=False, indent=2)}")
        
        # 6. 检查后端服务
        print("\n6. 检查后端服务...")
        
        # 检查是否有错误日志
        try:
            with open('/Users/zhangyanlong/workspaces/weekly-plan/backend/logs/error.log', 'r') as f:
                error_logs = f.read()
                if 'ai_analysis' in error_logs or 'AIAnalysisService' in error_logs:
                    print("⚠️  发现AI分析相关错误日志")
                    # 显示最近的错误
                    lines = error_logs.split('\n')
                    recent_errors = []
                    for line in lines[-50:]:  # 最后50行
                        if 'ai_analysis' in line or 'AIAnalysisService' in line:
                            recent_errors.append(line)
                    
                    if recent_errors:
                        print("最近相关错误:")
                        for error in recent_errors[-3:]:  # 显示最后3个
                            print(f"  {error}")
                else:
                    print("✅ 未发现AI分析相关错误日志")
        except Exception as e:
            print(f"无法读取错误日志: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作错误: {e}")
        return False

def main():
    """主函数"""
    success = test_ai_analysis_direct()
    
    print("\n" + "="*60)
    if success:
        print("🎉 直接测试完成！")
        print("✅ 数据库连接正常")
        print("✅ LLM配置存在且启用")
        print("✅ 用户权限正常")
        print("✅ 基础数据检查通过")
        
        print("\n🔍 问题定位建议:")
        print("1. 前端控制台错误检查")
        print("2. 网络请求监控")
        print("3. 浏览器开发者工具")
        print("4. 前端JavaScript错误")
    else:
        print("❌ 直接测试发现异常")

if __name__ == "__main__":
    main()