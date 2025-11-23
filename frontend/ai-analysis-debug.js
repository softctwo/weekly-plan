/**
 * AI分析功能调试工具
 * 在浏览器控制台中运行这些函数来诊断问题
 */

// AI分析调试器
window.aiAnalysisDebugger = {
  // 运行完整的诊断
  runFullDiagnostics: function() {
    console.log('🔍 AI分析功能完整诊断开始...');
    
    const results = {
      teamData: this.checkTeamData(),
      componentState: this.checkComponentState(),
      dateRange: this.checkDateRange(),
      apiEndpoints: this.checkApiEndpoints(),
      elementPlus: this.checkElementPlus(),
      errors: this.checkErrors(),
      network: this.checkNetworkRequests()
    };
    
    console.log('📊 诊断结果汇总:', results);
    this.generateReport(results);
    
    return results;
  },
  
  // 检查团队数据
  checkTeamData: function() {
    console.log('📋 检查团队数据...');
    try {
      // 获取团队页面实例
      const teamPage = document.querySelector('[class*="team"]') || document.querySelector('.el-main');
      const vueInstance = teamPage?.__vue_parent_component?.proxy;
      
      if (!vueInstance) {
        console.warn('⚠️  无法获取Vue实例');
        return { status: 'warning', details: '无法获取Vue实例' };
      }
      
      const teamMembers = vueInstance.teamMembers || vueInstance.$data?.teamMembers;
      console.log('团队数据:', teamMembers);
      
      if (!teamMembers || !Array.isArray(teamMembers)) {
        console.error('❌ 团队数据格式错误');
        return { status: 'error', details: '团队数据不是数组或不存在' };
      }
      
      if (teamMembers.length === 0) {
        console.warn('⚠️  团队数据为空');
        return { status: 'warning', details: '团队数据为空数组' };
      }
      
      console.log(`✅ 团队数据正常: ${teamMembers.length} 个成员`);
      return { 
        status: 'success', 
        count: teamMembers.length,
        sample: teamMembers[0]
      };
      
    } catch (error) {
      console.error('❌ 检查团队数据时出错:', error);
      return { status: 'error', details: error.message };
    }
  },
  
  // 检查组件状态
  checkComponentState: function() {
    console.log('🔧 检查AI分析组件状态...');
    try {
      // 查找AI分析对话框
      const dialog = document.querySelector('.el-dialog') || 
                    document.querySelector('[class*="analysis"]') ||
                    document.querySelector('[title*="AI"]');
      
      if (!dialog) {
        console.warn('⚠️  未找到AI分析对话框');
        return { status: 'warning', details: 'AI分析对话框未显示' };
      }
      
      // 获取Vue组件实例
      const vueInstance = dialog.__vue_parent_component?.proxy;
      if (!vueInstance) {
        console.warn('⚠️  无法获取对话框Vue实例');
        return { status: 'warning', details: '无法获取组件实例' };
      }
      
      console.log('对话框组件:', vueInstance);
      
      // 检查关键数据
      const formData = vueInstance.analysisForm || vueInstance.$data?.analysisForm;
      const teamMembers = vueInstance.teamMembers || vueInstance.$props?.teamMembers;
      const dateRange = vueInstance.dateRange || vueInstance.$data?.dateRange;
      
      console.log('分析表单:', formData);
      console.log('团队成员:', teamMembers);
      console.log('日期范围:', dateRange);
      
      return {
        status: 'success',
        formData: formData,
        teamMembersCount: teamMembers?.length || 0,
        dateRange: dateRange,
        componentLoaded: true
      };
      
    } catch (error) {
      console.error('❌ 检查组件状态时出错:', error);
      return { status: 'error', details: error.message };
    }
  },
  
  // 检查日期范围
  checkDateRange: function() {
    console.log('📅 检查日期范围...');
    try {
      if (typeof dayjs === 'undefined') {
        console.error('❌ dayjs未加载');
        return { status: 'error', details: 'dayjs库未加载' };
      }
      
      // 测试日期功能
      const today = dayjs();
      const thirtyDaysAgo = today.subtract(30, 'day');
      
      console.log('当前日期:', today.format('YYYY-MM-DD'));
      console.log('30天前:', thirtyDaysAgo.format('YYYY-MM-DD'));
      
      // 检查日期格式
      const formattedToday = today.format('YYYY-MM-DD');
      const formattedThirtyDaysAgo = thirtyDaysAgo.format('YYYY-MM-DD');
      
      console.log('格式化日期:', formattedToday, '至', formattedThirtyDaysAgo);
      
      return {
        status: 'success',
        today: formattedToday,
        thirtyDaysAgo: formattedThirtyDaysAgo,
        dayjsLoaded: true
      };
      
    } catch (error) {
      console.error('❌ 检查日期范围时出错:', error);
      return { status: 'error', details: error.message };
    }
  },
  
  // 检查API端点
  checkApiEndpoints: function() {
    console.log('🔌 检查API端点...');
    
    const endpoints = [
      '/api/ai/analyze',
      '/api/ai/llm-configs',
      '/api/dashboard/team'
    ];
    
    const results = {};
    
    endpoints.forEach(endpoint => {
      try {
        // 检查是否在网络请求日志中
        const networkEntries = performance.getEntriesByType('navigation');
        const hasRecentAccess = networkEntries.some(entry => 
          entry.name && entry.name.includes(endpoint.replace('/api', ''))
        );
        
        results[endpoint] = {
          status: hasRecentAccess ? 'accessed' : 'unknown',
          hasAccess: hasRecentAccess
        };
        
        console.log(`${endpoint}: ${hasRecentAccess ? '✅ 最近访问过' : '❓ 未检测到访问'}`);
        
      } catch (error) {
        console.error(`检查 ${endpoint} 失败:`, error);
        results[endpoint] = { status: 'error', details: error.message };
      }
    });
    
    return results;
  },
  
  // 检查Element Plus组件
  checkElementPlus: function() {
    console.log('🎯 检查Element Plus组件...');
    
    try {
      // 检查Element Plus是否加载
      if (typeof ElementPlus === 'undefined') {
        console.error('❌ Element Plus未加载');
        return { status: 'error', details: 'Element Plus库未加载' };
      }
      
      console.log('✅ Element Plus已加载');
      
      // 检查关键组件
      const components = ['ElSelect', 'ElOption', 'ElDatePicker', 'ElButton', 'ElMessage'];
      const missingComponents = [];
      
      components.forEach(comp => {
        if (!window[comp] && !ElementPlus[comp]) {
          missingComponents.push(comp);
        }
      });
      
      if (missingComponents.length > 0) {
        console.warn('⚠️  缺少组件:', missingComponents);
        return { status: 'warning', missing: missingComponents };
      }
      
      console.log('✅ 所有关键组件都已加载');
      return { status: 'success', components: components };
      
    } catch (error) {
      console.error('❌ 检查Element Plus时出错:', error);
      return { status: 'error', details: error.message };
    }
  },
  
  // 检查错误
  checkErrors: function() {
    console.log('🔍 检查JavaScript错误...');
    
    // 收集控制台错误
    const errors = window.__jsErrors__ || [];
    const recentErrors = errors.slice(-10); // 最近10个错误
    
    if (recentErrors.length > 0) {
      console.error('发现JavaScript错误:', recentErrors);
      return { 
        status: 'error', 
        count: recentErrors.length,
        recent: recentErrors
      };
    }
    
    console.log('✅ 未检测到JavaScript错误');
    return { status: 'success', count: 0 };
  },
  
  // 检查网络请求
  checkNetworkRequests: function() {
    console.log('🌐 检查网络请求...');
    
    // 获取最近的网络请求
    const entries = performance.getEntriesByType('resource');
    const apiRequests = entries.filter(entry => 
      entry.name && entry.name.includes('/api/')
    );
    
    const recentRequests = apiRequests.slice(-10);
    
    console.log(`发现 ${recentRequests.length} 个最近的API请求`);
    
    // 检查失败的请求
    const failedRequests = recentRequests.filter(entry => 
      entry.responseStatus >= 400
    );
    
    if (failedRequests.length > 0) {
      console.error('发现失败的请求:', failedRequests);
      return { 
        status: 'error', 
        total: recentRequests.length,
        failed: failedRequests.length,
        failedRequests: failedRequests
      };
    }
    
    console.log('✅ 网络请求正常');
    return { 
      status: 'success', 
      total: recentRequests.length,
      failed: 0
    };
  },
  
  // 生成报告
  generateReport: function(results) {
    console.log('\n📊 ===== AI分析功能诊断报告 =====');
    
    const hasErrors = Object.values(results).some(r => r.status === 'error');
    const hasWarnings = Object.values(results).some(r => r.status === 'warning');
    
    if (hasErrors) {
      console.error('❌ 发现错误，需要修复');
    } else if (hasWarnings) {
      console.warn('⚠️  发现警告，建议优化');
    } else {
      console.log('✅ 所有检查通过，功能正常');
    }
    
    console.log('\n详细结果:');
    Object.entries(results).forEach(([key, result]) => {
      const icon = result.status === 'error' ? '❌' : 
                  result.status === 'warning' ? '⚠️' : '✅';
      console.log(`${icon} ${key}: ${result.status}`);
      if (result.details) {
        console.log(`   ${result.details}`);
      }
    });
    
    console.log('\n📋 推荐操作:');
    if (hasErrors) {
      console.log('1. 修复标记为错误的项目');
      console.log('2. 重新运行诊断工具');
      console.log('3. 测试AI分析功能');
    } else if (hasWarnings) {
      console.log('1. 优化标记为警告的项目');
      console.log('2. 检查用户体验');
    } else {
      console.log('1. 功能正常，可以正常使用');
    }
  }
};

// 全局错误收集器
window.__jsErrors__ = window.__jsErrors__ || [];

// 重写console.error来捕获错误
const originalError = console.error;
console.error = function(...args) {
  window.__jsErrors__.push({
    message: args.join(' '),
    timestamp: new Date().toISOString(),
    stack: new Error().stack
  });
  originalError.apply(console, args);
};

// 监听未处理的Promise拒绝
window.addEventListener('unhandledrejection', function(event) {
  window.__jsErrors__.push({
    message: `Unhandled Promise Rejection: ${event.reason}`,
    timestamp: new Date().toISOString(),
    type: 'promise_rejection'
  });
});

// 监听JavaScript错误
window.addEventListener('error', function(event) {
  window.__jsErrors__.push({
    message: `${event.message} at ${event.filename}:${event.lineno}:${event.colno}`,
    timestamp: new Date().toISOString(),
    type: 'javascript_error',
    error: event.error
  });
});

console.log('🔧 AI分析调试工具已加载');
console.log('使用方法: aiAnalysisDebugger.runFullDiagnostics()');