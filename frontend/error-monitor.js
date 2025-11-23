/**
 * AI分析功能错误监控器
 * 在浏览器控制台中运行此脚本来实时监控错误
 */

window.aiErrorMonitor = {
  // 开始监控
  start: function() {
    console.log('🔍 AI分析错误监控器启动...');
    
    this.setupErrorCapture();
    this.setupNetworkMonitoring();
    this.setupComponentMonitoring();
    this.setupConsoleLogging();
    
    console.log('✅ 监控器已启动，正在捕获AI相关错误...');
  },
  
  // 设置错误捕获
  setupErrorCapture: function() {
    const self = this;
    
    // 捕获未处理的Promise错误
    window.addEventListener('unhandledrejection', function(event) {
      if (self.isAIAnalysisRelated(event.reason)) {
        console.error('🚨 AI分析Promise错误:', event.reason);
        self.logError('promise_rejection', event.reason);
      }
    });
    
    // 捕获JavaScript运行时错误
    window.addEventListener('error', function(event) {
      if (self.isAIAnalysisRelated(event.error) || self.isAIAnalysisRelated(event.filename)) {
        console.error('🚨 AI分析JavaScript错误:', event);
        self.logError('javascript_error', {
          message: event.message,
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
          error: event.error
        });
      }
    });
  },
  
  // 设置网络监控
  setupNetworkMonitoring: function() {
    const self = this;
    const originalFetch = window.fetch;
    
    // 重写fetch来监控AI相关请求
    window.fetch = function(...args) {
      const [url, options] = args;
      const isAIRequest = typeof url === 'string' && url.includes('/ai/');
      
      if (isAIRequest) {
        console.log(`📡 AI请求开始: ${url}`, options);
        
        return originalFetch.apply(this, args)
          .then(response => {
            console.log(`📡 AI请求完成: ${url} - 状态: ${response.status}`);
            
            if (!response.ok) {
              console.error(`🚨 AI请求失败: ${url} - 状态: ${response.status}`);
              self.logError('network_error', {
                url: url,
                status: response.status,
                statusText: response.statusText
              });
            }
            
            return response;
          })
          .catch(error => {
            console.error(`🚨 AI请求异常: ${url}`, error);
            self.logError('network_exception', {
              url: url,
              error: error.message
            });
            throw error;
          });
      }
      
      return originalFetch.apply(this, args);
    };
    
    // 监控XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
      const xhr = new originalXHR();
      const originalOpen = xhr.open;
      const originalSend = xhr.send;
      
      let method = '';
      let url = '';
      
      xhr.open = function(m, u) {
        method = m;
        url = u;
        return originalOpen.apply(this, arguments);
      };
      
      xhr.send = function() {
        const isAIRequest = url.includes('/ai/');
        
        if (isAIRequest) {
          console.log(`📡 AI XHR请求开始: ${method} ${url}`);
          
          const startTime = Date.now();
          
          const checkComplete = function() {
            if (xhr.readyState === 4) {
              const duration = Date.now() - startTime;
              console.log(`📡 AI XHR请求完成: ${method} ${url} - 状态: ${xhr.status} - 耗时: ${duration}ms`);
              
              if (xhr.status >= 400) {
                console.error(`🚨 AI XHR请求失败: ${method} ${url} - 状态: ${xhr.status}`);
                self.logError('xhr_error', {
                  method: method,
                  url: url,
                  status: xhr.status,
                  statusText: xhr.statusText,
                  duration: duration
                });
              }
            }
          };
          
          xhr.addEventListener('readystatechange', checkComplete);
          xhr.addEventListener('error', function() {
            console.error(`🚨 AI XHR请求异常: ${method} ${url}`);
            self.logError('xhr_exception', {
              method: method,
              url: url
            });
          });
        }
        
        return originalSend.apply(this, arguments);
      };
      
      return xhr;
    };
  },
  
  // 设置组件监控
  setupComponentMonitoring: function() {
    const self = this;
    
    // 监控AI分析对话框
    this.monitorAIAnalysisDialog();
    
    // 监控团队数据变化
    this.monitorTeamData();
    
    // 监控选择器状态
    this.monitorSelectorState();
  },
  
  // 监控AI分析对话框
  monitorAIAnalysisDialog: function() {
    const checkDialog = () => {
      const dialog = document.querySelector('.el-dialog') || 
                    document.querySelector('[title*="AI"]') ||
                    document.querySelector('[class*="analysis"]');
      
      if (dialog) {
        const vueInstance = dialog.__vue_parent_component?.proxy;
        if (vueInstance) {
          console.log('🎯 AI分析对话框状态:', {
            visible: vueInstance.visible,
            analyzing: vueInstance.analyzing,
            result: vueInstance.result,
            teamMembers: vueInstance.teamMembers,
            analysisForm: vueInstance.analysisForm,
            dateRange: vueInstance.dateRange
          });
        }
      }
    };
    
    // 定期检查对话框状态
    setInterval(checkDialog, 3000);
    checkDialog(); // 立即检查一次
  },
  
  // 监控团队数据
  monitorTeamData: function() {
    // 监听团队数据变化
    const checkTeamData = () => {
      const teamPage = document.querySelector('[class*="team"]');
      if (teamPage) {
        const vueInstance = teamPage.__vue_parent_component?.proxy;
        if (vueInstance && vueInstance.teamMembers) {
          console.log('👥 团队数据状态:', {
            count: vueInstance.teamMembers.length,
            firstMember: vueInstance.teamMembers[0],
            loading: vueInstance.loading
          });
        }
      }
    };
    
    setInterval(checkTeamData, 5000);
    checkTeamData();
  },
  
  // 监控选择器状态
  monitorSelectorState: function() {
    const checkSelectors = () => {
      const userSelector = document.querySelector('.el-select');
      const datePicker = document.querySelector('.el-date-picker') || 
                        document.querySelector('.el-date-editor--daterange');
      
      if (userSelector) {
        const vueInstance = userSelector.__vue_parent_component?.proxy;
        if (vueInstance) {
          console.log('🎯 用户选择器状态:', {
            value: vueInstance.modelValue || vueInstance.value,
            options: vueInstance.options?.length || 0,
            visible: vueInstance.visible
          });
        }
      }
      
      if (datePicker) {
        const vueInstance = datePicker.__vue_parent_component?.proxy;
        if (vueInstance) {
          console.log('📅 日期选择器状态:', {
            value: vueInstance.modelValue || vueInstance.value,
            type: vueInstance.type
          });
        }
      }
    };
    
    setInterval(checkSelectors, 2000);
    checkSelectors();
  },
  
  // 设置控制台日志
  setupConsoleLogging: function() {
    console.log('📝 AI分析功能控制台日志已启用');
    
    // 增强的日志输出
    const originalLog = console.log;
    console.log = function(...args) {
      const message = args.join(' ');
      if (message.includes('AI') || message.includes('分析') || message.includes('team')) {
        window.aiErrorMonitor.logMessage('log', message, args);
      }
      originalLog.apply(this, args);
    };
  },
  
  // 判断是否与AI分析相关
  isAIAnalysisRelated: function(error) {
    if (!error) return false;
    
    const errorStr = error.toString().toLowerCase();
    const relatedKeywords = [
      'ai', 'analyze', 'analysis', 'team', 'member',
      'el-select', 'el-option', 'el-date-picker',
      'dayjs', 'marked', 'request', 'api'
    ];
    
    return relatedKeywords.some(keyword => errorStr.includes(keyword));
  },
  
  // 记录错误
  logError: function(type, details) {
    const errorInfo = {
      timestamp: new Date().toISOString(),
      type: type,
      details: details,
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    console.error('🚨 AI分析错误记录:', errorInfo);
    
    // 存储到本地以便后续分析
    const errors = JSON.parse(localStorage.getItem('aiErrors') || '[]');
    errors.push(errorInfo);
    localStorage.setItem('aiErrors', JSON.stringify(errors));
  },
  
  // 记录消息
  logMessage: function(type, message, originalArgs) {
    const logInfo = {
      timestamp: new Date().toISOString(),
      type: type,
      message: message,
      originalArgs: originalArgs
    };
    
    // 存储到本地
    const logs = JSON.parse(localStorage.getItem('aiLogs') || '[]');
    logs.push(logInfo);
    localStorage.setItem('aiLogs', JSON.stringify(logs));
  },
  
  // 获取错误历史
  getErrorHistory: function() {
    return JSON.parse(localStorage.getItem('aiErrors') || '[]');
  },
  
  // 获取日志历史
  getLogHistory: function() {
    return JSON.parse(localStorage.getItem('aiLogs') || '[]');
  },
  
  // 清除历史记录
  clearHistory: function() {
    localStorage.removeItem('aiErrors');
    localStorage.removeItem('aiLogs');
    console.log('🗑️ 历史记录已清除');
  },
  
  // 生成错误报告
  generateReport: function() {
    const errors = this.getErrorHistory();
    const logs = this.getLogHistory();
    
    console.log('\n📊 ===== AI分析错误报告 =====');
    console.log(`错误数量: ${errors.length}`);
    console.log(`日志数量: ${logs.length}`);
    
    if (errors.length > 0) {
      console.log('\n最近的错误:');
      errors.slice(-5).forEach((error, index) => {
        console.log(`${index + 1}. [${error.timestamp}] ${error.type}`);
        console.log(`   ${JSON.stringify(error.details)}`);
      });
    }
    
    console.log('\n📋 建议:');
    if (errors.length > 0) {
      console.log('1. 查看上面的错误详情');
      console.log('2. 根据错误类型进行修复');
      console.log('3. 重新测试AI分析功能');
    } else {
      console.log('✅ 未发现错误，功能正常');
    }
  }
};

// 自动启动监控
setTimeout(() => {
  console.log('🚀 AI分析错误监控器准备就绪');
  console.log('使用方法: aiErrorMonitor.start()');
  console.log('查看报告: aiErrorMonitor.generateReport()');
  console.log('清除历史: aiErrorMonitor.clearHistory()');
}, 1000);