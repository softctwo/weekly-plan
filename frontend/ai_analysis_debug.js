// AI分析功能错误诊断脚本
// 在浏览器控制台中运行此脚本进行诊断

class AIAnalysisDebugger {
    constructor() {
        this.logs = [];
        this.errors = [];
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toISOString();
        const logEntry = { timestamp, message, type };
        this.logs.push(logEntry);
        
        const color = type === 'error' ? 'red' : type === 'warning' ? 'orange' : 'green';
        console.log(`%c[AI分析诊断] ${message}`, `color: ${color}`);
    }
    
    // 检查Vue组件状态
    checkVueComponent() {
        this.log('检查Vue组件状态...');
        
        try {
            // 查找AIAnalysisDialog组件实例
            const app = document.querySelector('#app').__vue_app__;
            if (!app) {
                this.log('无法找到Vue应用实例', 'error');
                return false;
            }
            
            this.log('Vue应用实例找到', 'success');
            return true;
        } catch (error) {
            this.log(`Vue组件检查失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 检查Element Plus组件
    checkElementPlus() {
        this.log('检查Element Plus组件...');
        
        try {
            // 检查Element Plus是否加载
            if (typeof ElementPlus !== 'undefined') {
                this.log('Element Plus已加载', 'success');
                return true;
            } else {
                this.log('Element Plus未加载', 'error');
                return false;
            }
        } catch (error) {
            this.log(`Element Plus检查失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 检查网络请求
    async checkNetworkRequest() {
        this.log('检查网络请求配置...');
        
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                this.log('警告: 未找到认证token', 'warning');
            } else {
                this.log('认证token已找到', 'success');
            }
            
            // 尝试一个简单的请求
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': token ? `Bearer ${token}` : ''
                }
            });
            
            if (response.ok) {
                this.log('网络请求正常', 'success');
                return true;
            } else {
                this.log(`网络请求失败: ${response.status}`, 'error');
                return false;
            }
        } catch (error) {
            this.log(`网络请求检查失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 检查AI分析API端点
    async checkAIEndpoint() {
        this.log('检查AI分析API端点...');
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/ai/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : ''
                },
                body: JSON.stringify({
                    analysis_type: 'comprehensive',
                    start_date: '2024-01-01',
                    end_date: '2024-01-31'
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.log('AI分析API端点正常', 'success');
                return true;
            } else {
                this.log(`AI分析API错误: ${response.status} - ${data.detail || '未知错误'}`, 'error');
                this.log(`错误详情: ${JSON.stringify(data)}`, 'error');
                return false;
            }
        } catch (error) {
            this.log(`AI分析API连接失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 检查团队成员数据
    async checkTeamMembers() {
        this.log('检查团队成员数据...');
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/dashboard/team?year=2024&week_number=1', {
                headers: {
                    'Authorization': token ? `Bearer ${token}` : ''
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (data.team_members && data.team_members.length > 0) {
                    this.log(`找到 ${data.team_members.length} 个团队成员`, 'success');
                    
                    // 检查数据结构
                    const firstMember = data.team_members[0];
                    const requiredFields = ['id', 'full_name'];
                    const missingFields = requiredFields.filter(field => !firstMember.hasOwnProperty(field));
                    
                    if (missingFields.length > 0) {
                        this.log(`团队成员数据缺少字段: ${missingFields.join(', ')}`, 'error');
                        return false;
                    } else {
                        this.log('团队成员数据结构正确', 'success');
                        return true;
                    }
                } else {
                    this.log('团队成员数据为空', 'warning');
                    return false;
                }
            } else {
                this.log(`团队数据获取失败: ${response.status}`, 'error');
                return false;
            }
        } catch (error) {
            this.log(`团队数据检查失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 检查日期范围选择器
    checkDateRange() {
        this.log('检查日期范围选择器...');
        
        try {
            // 检查dayjs是否可用
            if (typeof dayjs !== 'undefined') {
                this.log('dayjs已加载', 'success');
                
                // 测试日期格式
                const startDate = dayjs().subtract(30, 'day').format('YYYY-MM-DD');
                const endDate = dayjs().format('YYYY-MM-DD');
                
                this.log(`日期范围: ${startDate} 至 ${endDate}`, 'success');
                return true;
            } else {
                this.log('dayjs未加载', 'error');
                return false;
            }
        } catch (error) {
            this.log(`日期范围检查失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 检查marked库
    checkMarkdownRenderer() {
        this.log('检查Markdown渲染器...');
        
        try {
            if (typeof marked !== 'undefined') {
                this.log('marked库已加载', 'success');
                
                // 测试markdown渲染
                const testMarkdown = '# 测试标题\n**粗体文本**';
                const rendered = marked(testMarkdown);
                
                if (rendered.includes('<h1>') && rendered.includes('<strong>')) {
                    this.log('Markdown渲染正常', 'success');
                    return true;
                } else {
                    this.log('Markdown渲染异常', 'error');
                    return false;
                }
            } else {
                this.log('marked库未加载', 'error');
                return false;
            }
        } catch (error) {
            this.log(`Markdown渲染器检查失败: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 模拟AI分析请求
    async simulateAnalysis() {
        this.log('模拟AI分析请求...');
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/ai/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : ''
                },
                body: JSON.stringify({
                    user_id: null,
                    analysis_type: 'comprehensive',
                    start_date: '2024-01-01',
                    end_date: '2024-01-31'
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.log('AI分析请求成功', 'success');
                
                // 检查返回的数据结构
                const requiredFields = ['analysis_result', 'statistics', 'analysis_period'];
                const missingFields = requiredFields.filter(field => !data.hasOwnProperty(field));
                
                if (missingFields.length > 0) {
                    this.log(`AI分析结果缺少字段: ${missingFields.join(', ')}`, 'error');
                } else {
                    this.log('AI分析结果数据结构正确', 'success');
                }
                
                return true;
            } else {
                this.log(`AI分析请求失败: ${response.status}`, 'error');
                
                // 详细错误分析
                if (response.status === 422) {
                    this.log('请求参数验证失败', 'error');
                    if (data.detail) {
                        data.detail.forEach(err => {
                            this.log(`字段错误: ${err.loc.join('.')} - ${err.msg}`, 'error');
                        });
                    }
                } else if (response.status === 500) {
                    this.log('服务器内部错误，可能是LLM配置问题', 'error');
                } else if (response.status === 503) {
                    this.log('AI服务不可用', 'error');
                }
                
                return false;
            }
        } catch (error) {
            this.log(`AI分析请求异常: ${error.message}`, 'error');
            return false;
        }
    }
    
    // 运行完整诊断
    async runFullDiagnostics() {
        console.log('%c=== AI分析功能完整诊断 ===', 'color: blue; font-size: 16px; font-weight: bold;');
        
        this.log('开始完整诊断...');
        
        const results = {
            vue: this.checkVueComponent(),
            elementPlus: this.checkElementPlus(),
            network: await this.checkNetworkRequest(),
            aiEndpoint: await this.checkAIEndpoint(),
            teamMembers: await this.checkTeamMembers(),
            dateRange: this.checkDateRange(),
            markdown: this.checkMarkdownRenderer(),
            simulation: await this.simulateAnalysis()
        };
        
        // 总结报告
        console.log('%c=== 诊断结果总结 ===', 'color: blue; font-size: 14px; font-weight: bold;');
        
        const passed = Object.values(results).filter(r => r === true).length;
        const total = Object.keys(results).length;
        
        this.log(`诊断完成: ${passed}/${total} 项通过`);
        
        if (passed === total) {
            console.log('%c✅ 所有检查通过！AI分析功能应该正常工作。', 'color: green; font-size: 14px; font-weight: bold;');
        } else {
            console.log('%c❌ 发现一些问题，请查看上面的详细日志。', 'color: red; font-size: 14px; font-weight: bold;');
            
            // 提供具体建议
            if (!results.aiEndpoint) {
                console.log('%c💡 建议: 检查后端AI服务配置和LLM设置', 'color: orange;');
            }
            if (!results.teamMembers) {
                console.log('%c💡 建议: 检查团队数据是否正确加载', 'color: orange;');
            }
            if (!results.network) {
                console.log('%c💡 建议: 检查网络连接和API配置', 'color: orange;');
            }
        }
        
        return results;
    }
    
    // 获取诊断日志
    getLogs() {
        return this.logs;
    }
}

// 创建全局调试器实例
window.aiAnalysisDebugger = new AIAnalysisDebugger();

console.log('%cAI分析调试器已加载', 'color: green; font-weight: bold;');
console.log('%c使用方法: aiAnalysisDebugger.runFullDiagnostics()', 'color: blue;');
console.log('%c或者查看详细日志: aiAnalysisDebugger.getLogs()', 'color: blue;');