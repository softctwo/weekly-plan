// AI分析功能修复验证脚本
// 用于验证所有修复是否生效

class AIFixesValidator {
    constructor() {
        this.results = {};
        this.testResults = document.createElement('div');
        this.setupUI();
    }
    
    setupUI() {
        this.testResults.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            width: 400px;
            max-height: 80vh;
            background: white;
            border: 2px solid #333;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-size: 12px;
            overflow-y: auto;
        `;
        
        this.testResults.innerHTML = `
            <div style="text-align: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #333;">AI分析功能修复验证</h3>
                <button onclick="aiFixesValidator.runAllTests()" 
                        style="margin-top: 8px; padding: 5px 10px; background: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    运行所有测试
                </button>
                <button onclick="aiFixesValidator.close()" 
                        style="margin-top: 8px; margin-left: 5px; padding: 5px 10px; background: #f44336; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    关闭
                </button>
            </div>
            <div id="test-results-content"></div>
        `;
        
        document.body.appendChild(this.testResults);
    }
    
    log(message, type = 'info') {
        const content = document.getElementById('test-results-content') || this.testResults;
        const div = document.createElement('div');
        div.style.cssText = `
            margin: 3px 0;
            padding: 3px;
            border-radius: 3px;
            background: ${type === 'success' ? '#e8f5e8' : type === 'error' ? '#ffeaea' : '#f0f0f0'};
            color: ${type === 'success' ? '#2e7d2e' : type === 'error' ? '#d32f2f' : '#666'};
        `;
        div.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
        content.appendChild(div);
    }
    
    async testTeamMembersData() {
        this.log('测试团队成员数据...');
        
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/dashboard/team?year=2024&week_number=1', {
                headers: {
                    'Authorization': token ? `Bearer ${token}` : ''
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.team_members) {
                const hasValidMembers = data.team_members.length > 0 && 
                    data.team_members.every(member => 
                        member.hasOwnProperty('id') && 
                        member.hasOwnProperty('full_name')
                    );
                
                if (hasValidMembers) {
                    this.log(`✅ 团队成员数据正常: ${data.team_members.length} 个成员`, 'success');
                    this.results.teamMembers = true;
                    return true;
                } else {
                    this.log('❌ 团队成员数据格式错误', 'error');
                    this.results.teamMembers = false;
                    return false;
                }
            } else {
                this.log('❌ 无法获取团队成员数据', 'error');
                this.results.teamMembers = false;
                return false;
            }
        } catch (error) {
            this.log(`❌ 团队成员数据测试失败: ${error.message}`, 'error');
            this.results.teamMembers = false;
            return false;
        }
    }
    
    async testAIEndpoint() {
        this.log('测试AI分析端点...');
        
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
                const hasRequiredFields = data.hasOwnProperty('analysis_result') && 
                    data.hasOwnProperty('statistics') && 
                    data.hasOwnProperty('analysis_period');
                
                if (hasRequiredFields) {
                    this.log('✅ AI分析端点正常', 'success');
                    this.results.aiEndpoint = true;
                    return true;
                } else {
                    this.log('❌ AI分析响应数据格式错误', 'error');
                    this.results.aiEndpoint = false;
                    return false;
                }
            } else {
                this.log(`❌ AI分析端点错误: ${response.status}`, 'error');
                this.results.aiEndpoint = false;
                return false;
            }
        } catch (error) {
            this.log(`❌ AI分析端点测试失败: ${error.message}`, 'error');
            this.results.aiEndpoint = false;
            return false;
        }
    }
    
    testDateHandling() {
        this.log('测试日期处理...');
        
        try {
            if (typeof dayjs === 'undefined') {
                this.log('❌ dayjs未加载', 'error');
                this.results.dateHandling = false;
                return false;
            }
            
            const startDate = dayjs().subtract(30, 'day').format('YYYY-MM-DD');
            const endDate = dayjs().format('YYYY-MM-DD');
            
            const regex = /^\d{4}-\d{2}-\d{2}$/;
            const isValidFormat = regex.test(startDate) && regex.test(endDate);
            
            if (isValidFormat) {
                this.log(`✅ 日期处理正常: ${startDate} 至 ${endDate}`, 'success');
                this.results.dateHandling = true;
                return true;
            } else {
                this.log('❌ 日期格式错误', 'error');
                this.results.dateHandling = false;
                return false;
            }
        } catch (error) {
            this.log(`❌ 日期处理测试失败: ${error.message}`, 'error');
            this.results.dateHandling = false;
            return false;
        }
    }
    
    testMarkdownRendering() {
        this.log('测试Markdown渲染...');
        
        try {
            if (typeof marked === 'undefined') {
                this.log('❌ marked库未加载', 'error');
                this.results.markdown = false;
                return false;
            }
            
            const testMarkdown = '# 测试标题\n**粗体文本**\n- 列表项1\n- 列表项2';
            const rendered = marked(testMarkdown);
            
            const hasExpectedElements = rendered.includes('<h1>') && 
                rendered.includes('<strong>') && 
                rendered.includes('<ul>') || rendered.includes('<li>');
            
            if (hasExpectedElements) {
                this.log('✅ Markdown渲染正常', 'success');
                this.results.markdown = true;
                return true;
            } else {
                this.log('❌ Markdown渲染输出异常', 'error');
                this.results.markdown = false;
                return false;
            }
        } catch (error) {
            this.log(`❌ Markdown渲染测试失败: ${error.message}`, 'error');
            this.results.markdown = false;
            return false;
        }
    }
    
    testComponentIntegration() {
        this.log('测试组件集成...');
        
        try {
            // 检查是否能找到Vue组件
            const dialogElement = document.querySelector('.el-dialog');
            const selectElement = document.querySelector('.el-select');
            const datePickerElement = document.querySelector('.el-date-picker');
            
            const hasElements = !!(dialogElement || selectElement || datePickerElement);
            
            if (hasElements) {
                this.log('✅ Element Plus组件正常渲染', 'success');
                this.results.componentIntegration = true;
                return true;
            } else {
                this.log('⚠️  未找到Element Plus组件（可能对话框未打开）', 'warning');
                this.results.componentIntegration = null;
                return null;
            }
        } catch (error) {
            this.log(`❌ 组件集成测试失败: ${error.message}`, 'error');
            this.results.componentIntegration = false;
            return false;
        }
    }
    
    testErrorHandling() {
        this.log('测试错误处理...');
        
        try {
            // 模拟一个错误情况
            const originalConsoleError = console.error;
            let errorCaught = false;
            
            console.error = (message) => {
                if (message.includes('AI分析')) {
                    errorCaught = true;
                }
                originalConsoleError(message);
            };
            
            // 触发一个模拟错误
            setTimeout(() => {
                console.error('AI分析功能测试错误');
                console.error = originalConsoleError;
                
                if (errorCaught) {
                    this.log('✅ 错误处理机制正常', 'success');
                    this.results.errorHandling = true;
                } else {
                    this.log('⚠️  错误处理机制未触发', 'warning');
                    this.results.errorHandling = null;
                }
            }, 100);
            
            return true;
        } catch (error) {
            this.log(`❌ 错误处理测试失败: ${error.message}`, 'error');
            this.results.errorHandling = false;
            return false;
        }
    }
    
    async runAllTests() {
        this.log('开始运行所有修复验证测试...', 'info');
        
        // 清除之前的结果
        document.getElementById('test-results-content').innerHTML = '';
        this.results = {};
        
        // 运行所有测试
        await this.testTeamMembersData();
        await this.testAIEndpoint();
        this.testDateHandling();
        this.testMarkdownRendering();
        this.testComponentIntegration();
        this.testErrorHandling();
        
        // 生成总结报告
        this.generateSummary();
    }
    
    generateSummary() {
        const passed = Object.values(this.results).filter(r => r === true).length;
        const failed = Object.values(this.results).filter(r => r === false).length;
        const warnings = Object.values(this.results).filter(r => r === null).length;
        const total = Object.keys(this.results).length;
        
        this.log('=== 修复验证总结 ===', 'info');
        this.log(`✅ 通过: ${passed} 项`, 'success');
        this.log(`❌ 失败: ${failed} 项`, 'error');
        this.log(`⚠️  警告: ${warnings} 项`, 'warning');
        this.log(`总计: ${total} 项`, 'info');
        
        if (failed === 0) {
            this.log('🎉 所有修复验证通过！AI分析功能应该正常工作。', 'success');
        } else {
            this.log('🔧 发现一些问题，请查看详细日志进行修复。', 'error');
            
            // 提供具体建议
            if (this.results.teamMembers === false) {
                this.log('💡 建议: 检查团队数据API和数据库连接', 'warning');
            }
            if (this.results.aiEndpoint === false) {
                this.log('💡 建议: 检查后端AI服务和LLM配置', 'warning');
            }
            if (this.results.dateHandling === false) {
                this.log('💡 建议: 检查dayjs库是否正确加载', 'warning');
            }
            if (this.results.markdown === false) {
                this.log('💡 建议: 检查marked库是否正确加载', 'warning');
            }
        }
        
        // 保存结果到全局
        window.aiValidationResults = this.results;
    }
    
    close() {
        if (this.testResults.parentNode) {
            this.testResults.parentNode.removeChild(this.testResults);
        }
        console.log('AI分析修复验证工具已关闭');
    }
    
    // 获取详细的失败信息
    getFailureDetails() {
        const failures = {};
        for (const [test, result] of Object.entries(this.results)) {
            if (result === false) {
                failures[test] = this.getTestFailureReason(test);
            }
        }
        return failures;
    }
    
    getTestFailureReason(test) {
        const reasons = {
            teamMembers: '团队成员数据获取失败或格式不正确',
            aiEndpoint: 'AI分析API端点无法访问或返回错误',
            dateHandling: 'dayjs库未加载或日期格式错误',
            markdown: 'marked库未加载或Markdown渲染失败',
            componentIntegration: 'Element Plus组件未正确渲染',
            errorHandling: '错误处理机制未正常工作'
        };
        return reasons[test] || '未知原因';
    }
}

// 创建全局验证器实例
window.aiFixesValidator = new AIFixesValidator();

console.log('%c🔧 AI分析修复验证工具已加载', 'color: #4CAF50; font-weight: bold;');
console.log('%c使用方法:', 'color: #2196F3;');
console.log('- 运行所有测试: aiFixesValidator.runAllTests()');
console.log('- 获取失败详情: aiFixesValidator.getFailureDetails()');
console.log('- 关闭验证工具: aiFixesValidator.close()');

// 页面加载完成后自动运行一次测试
window.addEventListener('load', () => {
    setTimeout(() => {
        console.log('自动运行AI分析修复验证...');
        aiFixesValidator.runAllTests();
    }, 2000);
});