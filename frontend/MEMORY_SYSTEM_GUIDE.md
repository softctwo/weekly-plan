# 全局记忆系统使用指南

## 概述

全局记忆系统是为周工作计划管理系统设计的智能记忆功能，能够：

- 📝 **记录用户操作历史** - 自动追踪用户在系统中的所有操作
- 🧠 **学习用户行为模式** - 分析用户的使用习惯和偏好
- 💡 **提供智能推荐** - 基于历史数据生成个性化建议
- ⚙️ **持久化用户偏好** - 保存用户的设置和配置
- 📊 **生成行为分析报告** - 提供用户使用统计和洞察

## 核心功能

### 1. 历史记录系统
- 自动记录用户的所有重要操作
- 支持操作分类和标签
- 提供操作历史的查询和分析

### 2. 智能推荐引擎
- 基于用户行为生成个性化推荐
- 支持多种推荐类型（任务、角色、时间等）
- 动态调整推荐分数和优先级

### 3. 行为模式分析
- 活跃时间分布统计
- 任务类型使用频率分析
- 页面访问模式分析
- 生产力评分计算

### 4. 偏好设置管理
- 用户界面偏好持久化
- 通知设置记忆
- 个性化配置保存

## 快速开始

### 1. 导入记忆系统

```javascript
import { useMemoryStore } from '@/store/memory'
```

### 2. 在组件中使用

```javascript
<script setup>
import { useMemoryStore } from '@/store/memory'

const memoryStore = useMemoryStore()

// 记录用户操作
const handleTaskCreate = (taskData) => {
  // 创建任务的业务逻辑...
  
  // 记录到记忆系统
  memoryStore.recordHistory('create_task', {
    taskId: taskData.id,
    title: taskData.title,
    type: taskData.type,
    priority: taskData.priority
  }, 'Tasks')
}
</script>
```

### 3. 初始化系统

记忆系统会在应用启动时自动初始化，但您也可以手动控制：

```javascript
// 手动初始化
memoryStore.initializeMemory()

// 检查初始化状态
console.log(memoryStore.memoryStats)
```

## API 参考

### 核心方法

#### `recordHistory(action, data, page)`
记录用户操作到历史记录

**参数:**
- `action` (string): 操作类型，如 'create_task', 'update_task', 'page_dashboard'
- `data` (any): 操作相关的数据
- `page` (string): 页面来源

**示例:**
```javascript
// 记录任务创建
memoryStore.recordHistory('create_task', {
  taskId: 'task-001',
  title: '完成项目报告',
  type: 'report',
  priority: 'high'
}, 'Tasks')

// 记录页面访问
memoryStore.recordHistory('page_tasks', {
  pageName: 'Tasks',
  visitTime: Date.now()
}, 'Tasks')
```

#### `addRecommendation(type, data)`
添加智能推荐

**参数:**
- `type` (string): 推荐类型，如 'frequentlyUsedTasks', 'recentRoles'
- `data` (any): 推荐数据

**示例:**
```javascript
// 添加常用任务推荐
memoryStore.addRecommendation('frequentlyUsedTasks', {
  title: '周会准备',
  description: '您经常在周一创建周会相关的任务',
  type: 'meeting',
  score: 85
})

// 添加角色推荐
memoryStore.addRecommendation('recentRoles', {
  title: '产品经理',
  description: '您最近频繁使用产品经理角色的职责',
  roleId: 'pm-role-001'
})
```

#### `updatePreferences(preferences)`
更新用户偏好设置

**参数:**
- `preferences` (object): 偏好设置对象

**示例:**
```javascript
memoryStore.updatePreferences({
  theme: 'dark',
  language: 'zh-cn',
  notifications: {
    email: true,
    push: false,
    sound: true
  },
  weekStart: 1
})
```

#### `updateTempMemory(tempData)`
更新临时记忆（会话级数据）

**参数:**
- `tempData` (object): 临时数据

**示例:**
```javascript
memoryStore.updateTempMemory({
  currentPage: 'Tasks',
  currentTask: 'task-001',
  breadcrumbs: ['Dashboard', 'Tasks', 'Create Task']
})
```

### 查询方法

#### `getHistoryRecords(limit, filterAction)`
获取历史操作记录

```javascript
// 获取最近10条记录
const recentHistory = memoryStore.getHistoryRecords(10)

// 获取特定操作类型的历史记录
const taskHistory = memoryStore.getHistoryRecords(20, 'create_task')
```

#### `getPersonalizedRecommendations(context)`
获取个性化推荐

```javascript
// 获取任务相关的推荐
const taskRecommendations = memoryStore.getPersonalizedRecommendations('task')

// 获取角色相关的推荐
const roleRecommendations = memoryStore.getPersonalizedRecommendations('role')
```

#### 计算属性

```javascript
// 记忆统计信息
console.log(memoryStore.memoryStats)

// 活跃时间模式
console.log(memoryStore.activeTimePattern)

// 用户偏好
console.log(memoryStore.userPreferences)
```

## 高级功能

### 1. 行为模式分析

系统会自动分析用户的行为模式：

```javascript
// 获取分析报告
const report = memoryStore.getIntelligenceReport()
console.log(report)
```

### 2. 数据导入导出

```javascript
// 导出记忆数据
const backupData = memoryStore.exportMemoryData()

// 导入记忆数据
memoryStore.importMemoryData(backupData)
```

### 3. 数据持久化

记忆数据会自动保存到 localStorage，您也可以手动触发：

```javascript
// 手动保存
memoryStore.saveMemoryToStorage()

// 重新加载
memoryStore.loadMemoryFromStorage()
```

## 最佳实践

### 1. 操作类型命名规范

使用清晰的操作类型命名：

```javascript
// 推荐
memoryStore.recordHistory('create_task', data, 'Tasks')
memoryStore.recordHistory('update_user_profile', data, 'Profile')
memoryStore.recordHistory('page_dashboard', data, 'Dashboard')

// 不推荐
memoryStore.recordHistory('do_something', data, 'Page')
memoryStore.recordHistory('click', data, 'UI')
```

### 2. 数据结构建议

为推荐数据使用一致的字段：

```javascript
{
  title: '推荐标题',
  description: '推荐描述',
  type: '推荐类型',
  score: 85, // 0-100分数
  createdAt: '2024-01-01T00:00:00Z',
  // 其他业务相关字段
}
```

### 3. 性能优化

- 避免频繁调用记录方法
- 对于大量数据，考虑批量处理
- 定期清理过期的推荐数据

```javascript
// 批量记录操作
const batchHistory = [
  { action: 'create_task', data: task1, page: 'Tasks' },
  { action: 'create_task', data: task2, page: 'Tasks' },
  { action:
  'create_task', data: task3, page: 'Tasks' }
]

batchHistory.forEach(item => {
  memoryStore.recordHistory(item.action, item.data, item.page)
})
```

### 4. 错误处理

```javascript
try {
  memoryStore.recordHistory('create_task', taskData, 'Tasks')
} catch (error) {
  console.error('记录操作失败:', error)
  // 错误恢复逻辑
}
```

## 组件集成示例

### 1. 在页面组件中使用

```vue
<template>
  <div>
    <h2>任务列表</h2>
    <el-button @click="createTask">创建任务</el-button>
  </div>
</template>

<script setup>
import { useMemoryStore } from '@/store/memory'

const memoryStore = useMemoryStore()

const createTask = async () => {
  try {
    // 创建任务的业务逻辑
    const newTask = await createTaskAPI()
    
    // 记录到记忆系统
    memoryStore.recordHistory('create_task', {
      taskId: newTask.id,
      title: newTask.title,
      type: newTask.type
    }, 'Tasks')
    
    // 添加智能推荐
    memoryStore.addRecommendation('frequentlyUsedTasks', {
      title: `创建${newTask.type}类型任务`,
      description: '您刚刚创建了一个新任务',
      type: newTask.type,
      score: 90
    })
    
    ElMessage.success('任务创建成功')
  } catch (error) {
    ElMessage.error('创建任务失败')
  }
}
</script>
```

### 2. 在路由守卫中使用

```javascript
// router/index.js
import { useMemoryStore } from '@/store/memory'

router.beforeEach((to, from, next) => {
  const memoryStore = useMemoryStore()
  
  // 记录页面访问
  memoryStore.recordHistory('page_view', {
    from: from.name,
    to: to.name,
    timestamp: Date.now()
  }, to.name)
  
  // 更新当前页面状态
  memoryStore.updateTempMemory({
    currentPage: to.name,
    lastPage: from.name
  })
  
  next()
})
```

### 3. 在业务组件中使用

```vue
<script setup>
import { useMemoryStore } from '@/store/memory'

const memoryStore = useMemoryStore()

// 在组件挂载时记录
onMounted(() => {
  memoryStore.recordHistory('component_mounted', {
    component: 'TaskList',
    props: props
  }, 'Tasks')
})

// 在用户交互时记录
const handleTaskClick = (task) => {
  memoryStore.recordHistory('task_click', {
    taskId: task.id,
    taskTitle: task.title
  }, 'Tasks')
  
  memoryStore.updateSystemMemory('task_view', {
    taskId: task.id
  })
}
</script>
```

## 故障排除

### 1. 数据丢失问题

如果发现记忆数据丢失，检查以下几点：

- localStorage 是否被清除
- 存储空间是否充足
- 是否有 JavaScript 错误

```javascript
// 检查存储状态
console.log(localStorage.getItem('weekly_plan_memory'))

// 检查错误
window.addEventListener('error', (e) => {
  console.error('JavaScript错误:', e.error)
})
```

### 2. 性能问题

如果记忆系统影响性能，考虑：

- 减少记录频率
- 增加缓存机制
- 优化数据结构

```javascript
// 节流记录操作
const throttledRecord = useThrottle((action, data) => {
  memoryStore.recordHistory(action, data)
}, 1000)
```

### 3. 内存溢出

长期使用可能导致内存占用过高：

```javascript
// 定期清理历史记录
if (memoryStore.userHistory.length > 100) {
  // 保留最新的50条记录
  const recentHistory = memoryStore.userHistory.slice(0, 50)
  memoryStore.userHistory = recentHistory
  memoryStore.saveMemoryToStorage()
}
```

## 版本更新日志

### v1.0.0 (当前版本)
- ✅ 基础记忆功能
- ✅ 历史记录系统
- ✅ 智能推荐引擎
- ✅ 行为模式分析
- ✅ 数据持久化
- ✅ Vue 3 + Pinia 集成

### 计划功能
- 🔄 机器学习推荐算法
- 🔄 更多数据分析维度
- 🔄 云端数据同步
- 🔄 团队协作记忆
- 🔄 高级报表功能

## 技术支持

如果您在使用过程中遇到问题，可以：

1. 查看控制台日志：`[Memory]` 前缀的日志信息
2. 使用浏览器开发者工具检查 localStorage
3. 运行内存统计：`console.log(memoryStore.memoryStats)`
4. 导出数据进行调试：`memoryStore.exportMemoryData()`

---

**注意：** 全局记忆系统目前仅在客户端运行，数据存储在浏览器的 localStorage 中。后续版本将考虑添加服务端存储选项。
