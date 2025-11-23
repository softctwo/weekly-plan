# AI分析功能故障排查指南

## 问题症状
1. AI分析报错
2. 无法选择分析对象
3. 点击开始分析按钮时报错

## 已确认的后端状态
- ✅ 后端LLM配置正常（Deepseek配置已启用）
- ✅ 数据库连接正常
- ✅ 用户权限正常
- ✅ API端点存在且可访问

## 前端错误排查步骤

### 第一步：浏览器控制台检查
1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签页
3. 尝试使用AI分析功能，观察错误信息
4. 同时检查 Network 标签页中的请求状态

### 第二步：快速诊断
在浏览器控制台中运行以下代码进行快速诊断：

```javascript
// 运行完整诊断
aiAnalysisDebugger.runFullDiagnostics();

// 或者逐步检查
aiAnalysisDebugger.checkAIEndpoint();
aiAnalysisDebugger.checkTeamMembers();
```

### 第三步：常见问题及解决方案

#### 1. API请求失败 (404/500/503错误)

**症状:** Network标签页显示红色请求，状态码非200

**排查步骤:**
```bash
# 检查后端AI服务状态
curl -X POST "http://localhost:8000/api/ai/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "analysis_type": "comprehensive",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

**可能原因:**
- AI服务未启动
- LLM配置错误
- 网络连接问题

**解决方案:**
- 检查后端AI服务日志
- 确认Deepseek API密钥配置正确
- 重启后端服务

#### 2. 团队成员数据为空

**症状:** 分析对象下拉列表为空

**排查代码:**
```javascript
// 在控制台中检查团队数据
fetch('/api/dashboard/team?year=2024&week_number=1', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(response => response.json())
.then(data => {
  console.log('团队数据:', data);
  console.log('团队成员:', data.team_members);
});
```

**可能原因:**
- 没有团队成员数据
- 数据格式不正确
- 权限不足

**解决方案:**
- 检查数据库中是否有用户数据
- 确认用户有权限访问团队数据
- 检查团队数据API返回格式

#### 3. 前端JavaScript错误

**症状:** 控制台出现红色错误信息

**常见错误及解决:**

**错误: `Cannot read property 'team_members' of undefined`**
```javascript
// 问题代码
const teamMembers = data.team_members;

// 修复代码
const teamMembers = data?.team_members || [];
```

**错误: `marked is not defined`**
```javascript
// 确保marked库已正确导入
import { marked } from 'marked';
```

**错误: `Cannot read property 'analysis_result' of null`**
```javascript
// 问题代码
const result = response.data.analysis_result;

// 修复代码
const result = response.data?.analysis_result;
```

#### 4. Element Plus组件错误

**症状:** 组件无法正常工作或样式异常

**检查项目:**
- Element Plus是否正确安装
- 组件是否正确导入
- 版本是否兼容

**验证代码:**
```javascript
// 检查Element Plus
console.log('Element Plus:', typeof ElementPlus);
console.log('ElMessage:', typeof ElMessage);
console.log('ElLoading:', typeof ElLoading);
```

#### 5. 日期范围选择器问题

**症状:** 日期选择后无效或报错

**检查项目:**
- dayjs库是否正确加载
- 日期格式是否正确

**验证代码:**
```javascript
// 检查日期格式
const startDate = dayjs().subtract(30, 'day').format('YYYY-MM-DD');
const endDate = dayjs().format('YYYY-MM-DD');
console.log('日期范围:', startDate, '至', endDate);
```

### 第四步：详细诊断

使用诊断页面进行详细测试：
1. 打开 `frontend/test_ai_analysis.html`
2. 点击各个测试按钮
3. 查看测试结果和错误信息

### 第五步：网络请求分析

在Network标签页中检查：
1. 请求URL是否正确: `/api/ai/analyze`
2. 请求方法是否为POST
3. 请求头是否包含正确的Authorization
4. 请求体参数是否正确
5. 响应状态码和错误信息

**正确的请求格式:**
```json
{
  "user_id": null,  // 或具体用户ID
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "analysis_type": "comprehensive"
}
```

### 第六步：权限验证

**检查token有效性:**
```javascript
// 检查token
const token = localStorage.getItem('token');
console.log('Token存在:', !!token);

// 验证token
fetch('/api/auth/me', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
.then(response => {
  console.log('Token验证:', response.ok ? '有效' : '无效');
});
```

## 修复建议

### 1. 组件数据传递修复
在 `Team.vue` 中确保正确传递团队数据：

```vue
<AIAnalysisDialog
  v-model="showAIAnalysisDialog"
  :team-members="teamMembers"
/>
```

### 2. 错误处理增强
在 `AIAnalysisDialog.vue` 中增强错误处理：

```javascript
const startAnalysis = async() => {
  try {
    // 添加参数验证
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请选择分析周期');
      return;
    }
    
    // 添加更详细的错误信息
    const response = await request({
      url: '/ai/analyze',
      method: 'post',
      data: {
        user_id: analysisForm.value.user_id || null,
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        analysis_type: analysisForm.value.analysis_type
      }
    });
    
    result.value = response.data || response;
    ElMessage.success('分析完成');
    
  } catch (error) {
    console.error('AI分析错误详情:', error);
    
    // 更详细的错误处理
    let errorMessage = '分析失败';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.status === 422) {
      errorMessage = '请求参数错误，请检查输入';
    } else if (error.response?.status === 500) {
      errorMessage = 'AI服务内部错误，请联系管理员';
    } else if (error.response?.status === 503) {
      errorMessage = 'AI服务暂不可用，请稍后重试';
    }
    
    ElMessage.error(errorMessage);
  }
};
```

### 3. 数据验证增强
添加对团队数据的验证：

```javascript
// 在组件挂载时验证数据
watch(() => props.teamMembers, (newMembers) => {
  if (!newMembers || newMembers.length === 0) {
    console.warn('团队数据为空');
    ElMessage.warning('暂无团队成员数据');
  }
}, { immediate: true });
```

## 测试验证

修复后请进行以下测试：
1. ✅ 能够正常打开AI分析对话框
2. ✅ 分析对象下拉列表显示团队成员
3. ✅ 日期范围选择器正常工作
4. ✅ 点击"开始分析"按钮无错误
5. ✅ 能够看到分析结果
6. ✅ 错误提示信息清晰明确

## 联系支持

如果以上步骤仍无法解决问题，请提供：
1. 浏览器控制台的完整错误日志
2. Network标签页的请求详情
3. 后端服务的错误日志
4. 运行诊断脚本的结果