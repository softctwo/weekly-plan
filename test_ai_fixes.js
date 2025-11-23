/**
 * AI分析功能修复验证工具
 * 在浏览器控制台中运行此脚本来验证修复效果
 */

window.aiFixesValidator = {
  // 运行所有测试
  runAllTests: function() {
    console.log('🧪 AI分析功能修复验证开始...');
    
    const results = {
      componentIntegration: this.testComponentIntegration(),
      dataFlow: this.testDataFlow(),
      userInteraction: this.testUserInteraction(),
      apiCommunication: this.testApiCommunication(),
      errorHandling: this.testErrorHandling(),
      uiRendering: this.testUIRendering()
    };
    
    this.generateTestReport(results);
    return results;
  },
  
  // 测试组件集成
  testComponentIntegration: function() {
    console.log('🔧 测试组件集成...');
    
    try {
      // 检查AI分析对话框是否正确集成
      const teamPage = document.querySelector('[class*="team"]');
      if (!teamPage) {
        return { status: 'error', message: '未找到团队页面' };
      }
      
      const vueInstance = teamPage.__vue_parent_component?.proxy;
      if (!vueInstance) {
        return { status: 'error', message: '无法获取Vue实例' };
      }
      
      // 检查AI分析对话框状态
      const hasAIAnalysisDialog = vueInstance.showAIAnalysisDialog !== undefined;
      const hasTeamMembers = vueInstance.teamMembers !== undefined;
      
      console.log('组件状态:', {
        hasAIAnalysisDialog,
        hasTeamMembers,
        dialogVisible: vueInstance.showAIAnalysisDialog,
        teamMembersCount: vueInstance.teamMembers?.length
      });
      
      return {
        status: hasAIAnalysisDialog && hasTeamMembers ? 'success' : 'error',
        hasAIAnalysisDialog,
        hasTeamMembers,
        teamMembersCount: vueInstance.teamMembers?.length || 0
      };
      
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  },
  
  // 测试数据流
  testDataFlow: function() {
    console.log('📊 测试数据流...');
    
    try {
      // 获取AI分析对话框
      const dialog = document.querySelector('.el-dialog') || 
                    document.querySelector('[title*="AI"]');
      
      if (!dialog) {
        return { status: 'warning', message: 'AI分析对话框未显示' };
      }
      
      const dialogInstance = dialog.__vue_parent_component?.proxy;
      if (!dialogInstance) {
        return { status: 'error', message: '无法获取对话框实例' };
      }
      
      // 检查数据流动
      const teamMembers = dialogInstance.teamMembers;
      const analysisForm = dialogInstance.analysisForm;
      const dateRange = dialogInstance.dateRange;
      
      const dataFlowOk = teamMembers && analysisForm && dateRange;
      
      console.log('数据流状态:', {
        teamMembersCount: teamMembers?.length,
        analysisForm: analysisForm,
        dateRange: dateRange,
        dataFlowOk
      });
      
      return {
        status: dataFlowOk ? 'success' : 'error',
        teamMembersCount: teamMembers?.length || 0,
        hasAnalysisForm: !!analysisForm,
        hasDateRange: !!dateRange
      };
      
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  },
  
  // 测试用户交互
  testUserInteraction: function() {
    console.log('🎯 测试用户交互...');
    
    try {
      // 检查选择器
      const userSelector = document.querySelector('.el-select');
      const datePicker = document.querySelector('.el-date-editor--daterange');
      const analyzeButton = document.querySelector('.el-button--primary');
      
      const hasUserSelector = !!userSelector;
      const hasDatePicker = !!datePicker;
      const hasAnalyzeButton = !!analyzeButton;
      
      console.log('交互元素:', {
        hasUserSelector,
        hasDatePicker,
        hasAnalyzeButton
      });
      
      // 检查选择器状态
      if (userSelector) {
        const selectorInstance = userSelector.__vue_parent_component?.proxy;
        if (selectorInstance) {
          console.log('用户选择器详情:', {
            optionsCount: selectorInstance.options?.length || 0,
            currentValue: selectorInstance.modelValue || selectorInstance.value,
            visible: selectorInstance.visible
          });
        }
      }
      
      return {
        status: hasUserSelector && hasDatePicker && hasAnalyzeButton ? 'success' : 'error',
        hasUserSelector,
        hasDatePicker,
        hasAnalyzeButton
      };
      
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  },
  
  // 测试API通信
  testApiCommunication: function() {
    console.log('🌐 测试API通信...');
    
    return new Promise((resolve) => {
      // 测试AI服务状态
      this.testAIServiceStatus()
        .then(status => {
          console.log('AI服务状态:', status);
          resolve({
            status: status.available ? 'success' : 'error',
            serviceStatus: status,
            endpoints: ['/ai/analyze', '/ai/llm-configs', '/ai/status']
          });
        })
        .catch(error => {
          console.error('API通信测试失败:', error);
          resolve({
            status: 'error',
            message: error.message
          });
        });
    });
  },
  
  // 测试AI服务状态
  testAIServiceStatus: async function() {
    try {
      // 获取token
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      if (!token) {
        return { available: false, reason: '未登录' };
      }
      
      // 测试AI状态端点
      const response = await fetch('/api/ai/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const llmResponse = await fetch('/api/ai/llm-configs', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      return {
        available: response.ok,
        statusEndpoint: response.status,
        llmEndpoint: llmResponse.status,
        hasValidConfig: llmResponse.ok
      };
      
    } catch (error) {
      return {
        available: false,
        reason: '网络错误',
        error: error.message
      };
    }
  },
  
  // 测试错误处理
  testErrorHandling: function() {
    console.log('🛡️ 测试错误处理...');
    
    try {
      // 模拟各种错误情况
      const testCases = [
        { name: '空日期范围', data: { user_id: null, start_date: '', end_date: '' } },
        { name: '无效日期', data: { user_id: null, start_date: 'invalid-date', end_date: '2025-01-01' } },
        { name: '开始日期晚于结束日期', data: { user_id: null, start_date: '2025-01-02', end_date: '2025-01-01' } },
        { name: '无效用户ID', data: { user_id: 99999, start_date: '2025-01-01', end_date: '2025-01-31' } }
      ];
      
      const results = testCases.map(testCase => {
        try {
          // 验证数据格式
          const isValid = this.validateAnalysisData(testCase.data);
          return {
            name: testCase.name,
            isValid: isValid,
            data: testCase.data
          };
        } catch (error) {
          return {
            name: testCase.name,
            isValid: false,
            error: error.message
          };
        }
      });
      
      console.log('错误处理测试结果:', results);
      
      const allPassed = results.every(r => !r.isValid); // 所有无效数据都应该被正确识别
      
      return {
        status: allPassed ? 'success' : 'error',
        testResults: results,
        allPassed: allPassed
      };
      
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  },
  
  // 验证分析数据
  validateAnalysisData: function(data) {
    if (!data.start_date || !data.end_date) {
      throw new Error('日期范围不完整');
    }
    
    const start = new Date(data.start_date);
    const end = new Date(data.end_date);
    
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      throw new Error('日期格式无效');
    }
    
    if (start > end) {
      throw new Error('开始日期不能晚于结束日期');
    }
    
    return true;
  },
  
  // 测试UI渲染
  testUIRendering: function() {
    console.log('🎨 测试UI渲染...');
    
    try {
      // 检查Element Plus组件渲染
      const selectElements = document.querySelectorAll('.el-select')
      const buttonElements = document.querySelectorAll('.el-button')
      const datePickerElements = document.querySelectorAll('.el-date-editor')
      
      const hasSelect = selectElements.length > 0
      const hasButtons = buttonElements.length > 0  
      const hasDatePicker = datePickerElements.length > 0
      
      console.log('UI元素统计:', {
        selectElements: selectElements.length,
        buttonElements: buttonElements.length,
        datePickerElements: datePickerElements.length
      });
      
      // 检查是否有渲染错误
      const hasRenderErrors = document.querySelector('.el-alert--error') !== null;
      
      return {
        status: hasSelect && hasButtons && !hasRenderErrors ? 'success' : 'error',
        hasSelect,
        hasButtons,
        hasDatePicker,
        hasRenderErrors
      };
      
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  },
  
  // 生成测试报告
  generateTestReport: function(results) {
    console.log('\n📊 ===== AI分析功能修复验证报告 =====');
    
    const passed = Object.values(results).filter(r => r.status === 'success').length;
    const failed = Object.values(results).filter(r => r.status === 'error').length;
    const warnings = Object.values(results).filter(r => r.status === 'warning').length;
    
    console.log(`测试通过: ${passed}`);
    console.log(`测试失败: ${failed}`);
    console.log(`测试警告: ${warnings}`);
    
    if (failed === 0) {
      console.log('🎉 所有测试通过！AI分析功能修复成功');
    } else {
      console.log('❌ 发现失败的测试，需要进一步修复');
    }
    
    console.log('\n详细结果:');
    Object.entries(results).forEach(([key, result]) => {
      const icon = result.status === 'success' ? '✅' : 
                  result.status === 'error' ? '❌' : '⚠️';
      console.log(`${icon} ${key}: ${result.status}`);
      if (result.message) {
        console.log(`   ${result.message}`);
      }
    });
    
    // 具体建议
    console.log('\n📋 修复建议:');
    if (results.componentIntegration.status !== 'success') {
      console.log('1. 检查AI分析对话框组件集成');
    }
    if (results.dataFlow.status !== 'success') {
      console.log('2. 检查数据流和props传递');
    }
    if (results.userInteraction.status !== 'success') {
      console.log('3. 检查用户交互元素');
    }
    if (results.apiCommunication.status !== 'success') {
      console.log('4. 检查API通信和服务状态');
    }
    if (results.errorHandling.status !== 'success') {
      console.log('5. 检查错误处理逻辑');
    }
    if (results.uiRendering.status !== 'success') {
      console.log('6. 检查UI渲染问题');
    }
    
    return { passed, failed, warnings, total: passed + failed + warnings };
  },
  
  // 快速测试关键功能
  runQuickTest: function() {
    console.log('⚡ 快速测试AI分析关键功能...');
    
    const tests = [
      this.testComponentIntegration(),
      this.testDataFlow(),
      this.testUserInteraction()
    ];
    
    const passed = tests.filter(t => t.status === 'success').length;
    const total = tests.length;
    
    console.log(`快速测试结果: ${passed}/${total} 通过`);
    
    if (passed === total) {
      console.log('✅ 关键功能正常，可以进行完整测试');
    } else {
      console.log('❌ 关键功能有问题，需要修复');
    }
    
    return { passed, total };
  }
};

// 添加验证器到全局窗口对象
window.aiFixesValidator = aiFixesValidator;

console.log('🧪 AI分析功能修复验证工具已加载');
console.log('使用方法:');
console.log('  aiFixesValidator.runQuickTest()     - 快速测试');
console.log('  aiFixesValidator.runAllTests()      - 完整测试');
console.log('  aiFixesValidator.testApiCommunication() - 测试API通信');

// 自动运行快速测试（延迟执行，等待页面完全加载）
setTimeout(() => {
  console.log('🚀 自动运行快速测试...');
  aiFixesValidator.runQuickTest();
}, 3000);