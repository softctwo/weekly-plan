# AI分析功能错误排查清单

## 问题现象

用户报告：
1. AI分析报错
2. 无法选择分析对象（员工选择器空白）
3. 点击开始分析按钮时报错

## 已确认的系统状态

✅ **后端状态正常：**
- LLM配置存在且启用（Deepseek配置已验证）
- 数据库连接正常
- 用户权限正常（admin用户为管理员权限）
- API端点存在且可访问

## 快速诊断步骤

### Step 1: 运行自动诊断工具

在浏览器控制台中执行：

```javascript
// 运行完整诊断
aiAnalysisDebugger.runFullDiagnostics()

// 运行快速测试
aiFixesValidator.runQuickTest()

// 启动错误监控
aiErrorMonitor.start()
```

### Step 2: 检查关键组件状态

```javascript
// 检查团队数据
console.log('团队数据:', props.teamMembers)

// 检查AI对话框状态
console.log('AI对话框:', {
  visible: dialog.visible,
  teamMembers: dialog.teamMembers,
  analysisForm: dialog.analysisForm,
  dateRange: dialog.dateRange
})

// 检查选择器状态
console.log('用户选择器:', {
  options: selector.options,
  value: selector.modelValue
})
```

### Step 3: 检查网络请求

```javascript
// 检查最近的网络请求
performance.getEntriesByType('resource')
  .filter(entry => entry.name.includes('/ai/'))
  .slice(-5)
  .forEach(entry => {
    console.log(`${entry.name}: ${entry.responseStatus}`)
  })
```

## 详细排查清单

### 🔍 1. 团队数据检查

- [ ] 团队数据是否成功加载？
- [ ] teamMembers数组是否有数据？
- [ ] 团队成员数据结构是否正确（包含id, full_name字段）？
- [ ] 数据是否正确传递到AI分析对话框？

**验证代码：**
```javascript
const teamPage = document.querySelector('[class*="team"]')
const vueInstance = teamPage?.__vue_parent_component?.proxy
console.log('团队数据:', vueInstance?.teamMembers)
```

### 🔍 2. AI对话框组件检查

- [ ] AI对话框是否正确导入？
- [ ] 组件是否正确接收teamMembers prop？
- [ ] 组件内部状态是否正确初始化？
- [ ] Element Plus组件是否正常渲染？

**验证代码：**
```javascript
const dialog = document.querySelector('.el-dialog')
const dialogInstance = dialog?.__vue_parent_component?.proxy
console.log('对话框状态:', dialogInstance)
```

### 🔍 3. 选择器功能检查

- [ ] 用户选择器是否有选项数据？
- [ ] 日期选择器是否能正常选择？
- [ ] 选择器是否能正确绑定值？
- [ ] 选择器是否有任何JavaScript错误？

**验证代码：**
```javascript
const userSelector = document.querySelector('.el-select')
const selectorInstance = userSelector?.__vue_parent_component?.proxy
console.log('选择器状态:', {
  options: selectorInstance?.options,
  value: selectorInstance?.modelValue
})
```

### 🔍 4. API通信检查

- [ ] /api/ai/analyze 请求是否发送成功？
- [ ] 请求参数是否正确？
- [ ] 响应状态码是什么？
- [ ] 是否有跨域或认证问题？

**验证代码：**
```javascript
// 监控网络请求
aiErrorMonitor.setupNetworkMonitoring()

// 检查AI服务状态
fetch('/api/ai/status', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(res => console.log('AI状态:', res.status))
```

### 🔍 5. 错误处理检查

- [ ] 是否有JavaScript运行时错误？
- [ ] Promise拒绝是否被正确处理？
- [ ] 错误信息是否对用户友好？
- [ ] 错误是否被正确记录？

**验证代码：**
```javascript
// 检查错误历史
console.log('错误历史:', aiErrorMonitor.getErrorHistory())

// 检查控制台错误
console.log('JavaScript错误:', window.__jsErrors__)
```

### 🔍 6. 依赖库检查

- [ ] dayjs库是否正确加载？
- [ ] marked库是否正确加载？
- [ ] Element Plus组件是否正常？
- [ ] 是否有依赖冲突？

**验证代码：**
```javascript
console.log('依赖检查:', {
  dayjs: typeof dayjs,
  marked: typeof marked,
  ElementPlus: typeof ElementPlus,
  ElMessage: typeof ElMessage
})
```

## 常见问题解决方案

### ❌ 问题1: 团队数据为空

**症状：** teamMembers数组为空
**原因：** 数据未加载或加载失败
**解决：**
```javascript
// 确保在Team.vue中正确加载团队数据
const loadTeamData = async () => {
  try {
    const data = await getTeamDashboard({ year, week_number })
    teamMembers.value = data.team_members || []
  } catch (error) {
    ElMessage.error('加载团队数据失败')
  }
}
```

### ❌ 问题2: 选择器无选项

**症状：** 用户选择器下拉为空
**原因：** teamMembers未正确传入或格式错误
**解决：**
```javascript
// 确保数据结构正确
const teamMembers = [
  { id: 1, full_name: '张三' },
  { id: 2, full_name: '李四' }
]

// 验证数据传递
<AIAnalysisDialog :team-members="teamMembers" />
```

### ❌ 问题3: 点击分析按钮无反应

**症状：** 点击开始分析按钮没有任何反应
**原因：** 事件处理函数错误或验证失败
**解决：**
```javascript
// 增强错误处理和日志
const startAnalysis = async () => {
  console.log('开始分析，参数:', { user_id, start_date, end_date })
  
  try {
    // 详细的参数验证
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请选择分析周期')
      return
    }
    
    const response = await analyzeWork(params)
    console.log('分析成功:', response)
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error(error.message || '分析失败')
  }
}
```

### ❌ 问题4: API请求失败

**症状：** 网络请求返回4xx或5xx错误
**原因：** 认证、权限或服务端问题
**解决：**
1. 检查用户权限（需要admin或manager）
2. 检查登录状态（token是否有效）
3. 检查LLM配置是否正确
4. 查看服务端错误日志

### ❌ 问题5: 日期选择器异常

**症状：** 日期选择器无法选择或格式错误
**原因：** dayjs库问题或格式配置错误
**解决：**
```javascript
// 确保日期格式正确
const dateRange = ref([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])

// 验证日期格式
const startDate = dayjs(dateRange.value[0])
const endDate = dayjs(dateRange.value[1])

if (!startDate.isValid() || !endDate.isValid()) {
  ElMessage.warning('日期格式无效')
  return
}
```

## 修复验证

修复完成后，运行以下验证：

```javascript
// 完整验证
aiFixesValidator.runAllTests()

// 功能测试
aiAnalysisDebugger.runFullDiagnostics()

// 错误监控
aiErrorMonitor.generateReport()
```

## 联系支持

如果按照以上步骤仍无法解决问题，请提供以下信息：

1. 浏览器控制台错误截图
2. 网络请求截图（特别是失败的请求）
3. 运行诊断工具的完整输出
4. 复现问题的具体步骤
5. 用户角色和权限信息

**诊断信息收集：**
```javascript
// 收集完整的诊断信息
const diagnostics = {
  userAgent: navigator.userAgent,
  url: window.location.href,
  teamData: aiAnalysisDebugger.checkTeamData(),
  componentState: aiAnalysisDebugger.checkComponentState(),
  errors: aiErrorMonitor.getErrorHistory(),
  logs: aiErrorMonitor.getLogHistory()
}

console.log('诊断信息:', JSON.stringify(diagnostics, null, 2))
```