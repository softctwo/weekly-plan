# AI分析功能错误快速排查清单

## 🔍 5分钟快速诊断

### 1. 控制台检查 (30秒)
```javascript
// 在浏览器控制台运行这些命令

// 检查基础环境
console.log('✅ Token:', !!localStorage.getItem('token'));
console.log('✅ dayjs:', typeof dayjs !== 'undefined');
console.log('✅ marked:', typeof marked !== 'undefined');
console.log('✅ ElementPlus:', typeof ElementPlus !== 'undefined');

// 检查团队数据
fetch('/api/dashboard/team?year=2024&week_number=1', {
  headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
}).then(r => r.json()).then(d => console.log('✅ 团队数据:', d.team_members?.length || 0));

// 检查AI端点
fetch('/api/ai/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem('token')},
  body: JSON.stringify({analysis_type: 'comprehensive', start_date: '2024-01-01', end_date: '2024-01-31'})
}).then(r => console.log('✅ AI端点状态:', r.status));
```

### 2. 一键诊断 (10秒)
```javascript
// 运行完整诊断
aiAnalysisDebugger.runFullDiagnostics();
```

### 3. 修复验证 (30秒)
```javascript
// 验证修复效果
aiFixesValidator.runAllTests();
```

---

## 🚨 常见错误症状与解决

### 症状1: 点击"开始分析"无反应
**可能原因:**
1. ❌ 团队数据为空
2. ❌ 日期范围未选择
3. ❌ API请求失败

**快速解决:**
```javascript
// 检查团队数据
if (!props.teamMembers || props.teamMembers.length === 0) {
  console.error('❌ 团队数据为空');
}

// 检查日期
if (!dateRange.value || dateRange.value.length !== 2) {
  console.error('❌ 日期范围无效');
}
```

### 症状2: 分析对象下拉列表为空
**可能原因:**
1. ❌ teamMembers数据未传入
2. ❌ 数据格式错误
3. ❌ API返回错误

**快速解决:**
```javascript
// 检查数据传递
console.log('团队数据:', props.teamMembers);
console.log('第一个成员:', props.teamMembers?.[0]);
```

### 症状3: 报错"分析失败"
**可能原因:**
1. ❌ 后端AI服务未启动
2. ❌ LLM配置错误
3. ❌ 网络超时

**快速解决:**
```bash
# 检查后端日志
tail -f backend/logs/app.log | grep -i "ai\|analyze\|error"
```

### 症状4: 报告无法显示
**可能原因:**
1. ❌ marked库未加载
2. ❌ 数据格式错误
3. ❌ 渲染错误

**快速解决:**
```javascript
// 测试marked
const test = marked('# 测试');
console.log('✅ marked正常:', test.includes('<h1>'));
```

---

## 🔧 快速修复代码

### 修复1: 增强错误处理
```javascript
// 在AIAnalysisDialog.vue的startAnalysis方法中
const startAnalysis = async() => {
  // 添加参数验证
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择分析周期');
    return;
  }
  
  // 添加日期验证
  const startDate = dayjs(dateRange.value[0]);
  const endDate = dayjs(dateRange.value[1]);
  if (!startDate.isValid() || !endDate.isValid()) {
    ElMessage.warning('日期格式无效');
    return;
  }
  
  // 详细错误处理
  try {
    // ... 现有代码
  } catch (error) {
    console.error('AI分析错误:', error);
    let message = '分析失败';
    if (error.response?.status === 500) message = 'AI服务内部错误';
    else if (error.response?.status === 503) message = 'AI服务不可用';
    else if (error.response?.status === 422) message = '请求参数错误';
    else if (error.message) message = error.message;
    ElMessage.error(message);
  }
};
```

### 修复2: 数据验证
```javascript
// 验证团队数据
const validateTeamMembers = () => {
  if (!props.teamMembers || props.teamMembers.length === 0) {
    console.warn('⚠️ 团队数据为空');
    return false;
  }
  
  const required = ['id', 'full_name'];
  const first = props.teamMembers[0];
  for (const field of required) {
    if (!first.hasOwnProperty(field)) {
      console.error(`❌ 缺少字段: ${field}`);
      return false;
    }
  }
  return true;
};
```

### 修复3: 空数据保护
```javascript
// 在模板中添加空数据保护
<el-option
  v-for="user in (teamMembers || [])"
  :key="user.id || user.full_name"
  :label="user.full_name || '未知用户'"
  :value="user.id"
/>
```

---

## 📊 测试验证

### 快速测试 (1分钟)
```javascript
// 1. 打开AI分析对话框
// 2. 检查下拉列表是否有数据
// 3. 选择日期范围
// 4. 点击开始分析
// 5. 观察控制台和网络请求
```

### 完整测试 (5分钟)
```javascript
// 运行完整验证
aiFixesValidator.runAllTests();

// 检查错误监控
console.log('AI错误:', aiErrorMonitor.getAIAnalysisErrors());
```

---

## 🆘 紧急联系信息

如果以上步骤无法解决问题，请收集以下信息：

1. **浏览器控制台截图**
2. **Network标签页的请求详情**
3. **运行诊断脚本的结果**
4. **后端错误日志**

**快速收集命令:**
```javascript
// 收集诊断信息
const diagnosticInfo = {
  timestamp: new Date().toISOString(),
  userAgent: navigator.userAgent,
  token: !!localStorage.getItem('token'),
  errors: aiErrorMonitor.getAIAnalysisErrors(),
  validation: window.aiValidationResults || '未运行'
};

console.log('诊断信息:', JSON.stringify(diagnosticInfo, null, 2));
```

---

## ✅ 修复确认清单

修复完成后，请确认：
- [ ] 控制台无红色错误
- [ ] 团队数据正常显示
- [ ] 日期选择器正常工作
- [ ] AI分析能够启动
- [ ] 错误提示清晰明了
- [ ] 网络请求状态200
- [ ] 最终报告能够显示

**最终验证:**
```javascript
// 确认修复成功
aiFixesValidator.runAllTests();
// 应该显示: ✅ 通过: 6/6 项
```