<template>
  <div class="memory-example">
    <el-card>
      <template #header>
        <div class="example-header">
          <h3>全局记忆功能演示</h3>
          <p>展示如何在组件中使用全局记忆系统</p>
        </div>
      </template>
      
      <!-- 操作按钮区域 -->
      <div class="action-section">
        <h4>操作演示</h4>
        <div class="action-buttons">
          <el-button @click="recordTaskCreation" type="primary">
            <el-icon><Plus /></el-icon>
            记录任务创建
          </el-button>
          
          <el-button @click="recordTaskUpdate">
            <el-icon><Edit /></el-icon>
            记录任务更新
          </el-button>
          
          <el-button @click="recordPageView">
            <el-icon><View /></el-icon>
            记录页面访问
          </el-button>
          
          <el-button @click="addRecommendation">
            <el-icon><Star /></el-icon>
            添加智能推荐
          </el-button>
          
          <el-button @click="updatePreferences">
            <el-icon><Setting /></el-icon>
            更新偏好设置
          </el-button>
        </div>
      </div>
      
      <!-- 当前状态显示 -->
      <div class="status-section">
        <h4>当前记忆状态</h4>
        <div class="status-grid">
          <div class="status-item">
            <label>当前页面:</label>
            <span>{{ currentMemory.currentPage || '无' }}</span>
          </div>
          
          <div class="status-item">
            <label>当前任务:</label>
            <span>{{ currentMemory.currentTask || '无' }}</span>
          </div>
          
          <div class="status-item">
            <label>最后操作:</label>
            <span>{{ currentMemory.lastAction || '无' }}</span>
          </div>
          
          <div class="status-item">
            <label>会话次数:</label>
            <span>{{ memoryStore.systemMemory.sessionCount }}</span>
          </div>
        </div>
      </div>
      
      <!-- 历史记录显示 -->
      <div class="history-section">
        <h4>最近操作历史</h4>
        <div class="history-table">
          <el-table :data="recentHistory" style="width: 100%">
            <el-table-column prop="action" label="操作" width="150">
              <template #default="{ row }">
                <el-tag size="small">{{ getActionLabel(row.action) }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="page" label="页面" width="120">
              <template #default="{ row }">
                <span v-if="row.page">{{ row.page }}</span>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="timestamp" label="时间">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
            
            <el-table-column label="数据">
              <template #default="{ row }">
                <el-tooltip 
                  v-if="row.data" 
                  :content="JSON.stringify(row.data, null, 2)"
                  placement="top"
                >
                  <el-button size="small" text>查看详情</el-button>
                </el-tooltip>
                <span v-else class="text-gray">无</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <!-- 行为模式分析 -->
      <div class="patterns-section">
        <h4>行为模式分析</h4>
        <div class="patterns-grid">
          <div class="pattern-card">
            <h5>活跃时间分布</h5>
            <div class="time-distribution">
              <div 
                v-for="pattern in topActiveHours" 
                :key="pattern.hour"
                class="time-bar-item"
              >
                <span class="time-label">{{ pattern.hour }}:00</span>
                <div class="bar-container">
                  <div 
                    class="bar-fill" 
                    :style="{ width: `${(pattern.count / maxPatternCount) * 100}%` }"
                  ></div>
                </div>
                <span class="count">{{ pattern.count }}</span>
              </div>
            </div>
          </div>
          
          <div class="pattern-card">
            <h5>常用任务类型</h5>
            <div class="task-types">
              <div 
                v-for="(stats, type) in topTaskTypes" 
                :key="type"
                class="task-type-item"
              >
                <span class="type-name">{{ type }}</span>
                <span class="type-count">{{ stats.count }} 次</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 智能推荐展示 -->
      <div class="recommendations-section">
        <h4>当前智能推荐</h4>
        <div class="recommendations-grid">
          <div 
            v-for="rec in currentRecommendations" 
            :key="rec.id"
            class="recommendation-card"
          >
            <div class="rec-header">
              <h5>{{ rec.title || rec.type }}</h5>
              <el-progress 
                :percentage="rec.score" 
                :stroke-width="6"
                :show-text="false"
                class="rec-score"
              />
            </div>
            <p class="rec-description">{{ rec.description || '基于您的使用习惯智能推荐' }}</p>
            <div class="rec-footer">
              <el-tag size="small">{{ rec.type }}</el-tag>
              <span class="rec-time">{{ formatTime(rec.createdAt) }}</span>
            </div>
          </div>
        </div>
        <div v-if="currentRecommendations.length === 0" class="empty-recommendations">
          <el-icon><Lightbulb /></el-icon>
          <p>继续使用系统，智能推荐将根据您的操作习惯生成</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMemoryStore } from '../store/memory'
import { 
  Plus, 
  Edit, 
  View, 
  Star, 
  Setting,
  Lightbulb
} from '@element-plus/icons-vue'

const memoryStore = useMemoryStore()

// 响应式数据
const demoTaskId = ref('demo-task-001')
const demoTaskTitle = ref('演示任务')

// 计算属性
const currentMemory = computed(() => memoryStore.tempMemory)
const
currentMemory = computed(() => memoryStore.tempMemory)
const recentHistory = computed(() => memoryStore.getHistoryRecords(5))

const topActiveHours = computed(() => {
  return memoryStore.behaviorPatterns.mostActiveHours
    .slice()
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)
})

const maxPatternCount = computed(() => {
  const patterns = memoryStore.behaviorPatterns.mostActiveHours
  return patterns.length > 0 ? Math.max(...patterns.map(p => p.count)) : 1
})

const topTaskTypes = computed(() => {
  const taskDurations = memoryStore.behaviorPatterns.commonTaskDurations
  return Object.fromEntries(
    Object.entries(taskDurations)
      .sort(([,a], [,b]) => b.count - a.count)
      .slice(0, 5)
  )
})

const currentRecommendations = computed(() => {
  const allRecs = []
  Object.entries(memoryStore.recommendations).forEach(([type, recs]) => {
    if (Array.isArray(recs) && recs.length > 0) {
      allRecs.push(...recs.map(rec => ({ ...rec, type })))
    }
  })
  return allRecs.sort((a, b) => b.score - a.score).slice(0, 3)
})

// 方法
const recordTaskCreation = () => {
  memoryStore.recordHistory('create_task', {
    taskId: demoTaskId.value,
    title: demoTaskTitle.value,
    type: 'meeting',
    priority: 'high'
  }, 'Tasks')
  
  // 添加到常用任务推荐
  memoryStore.addRecommendation('frequentlyUsedTasks', {
    title: '创建会议任务',
    description: '您经常创建会议相关的任务',
    type: 'meeting',
    taskId: demoTaskId.value
  })
  
  ElMessage.success('已记录任务创建操作')
}

const recordTaskUpdate = () => {
  memoryStore.recordHistory('update_task', {
    taskId: demoTaskId.value,
    title: demoTaskTitle.value,
    changes: {
      status: 'in_progress',
      assignee: '张三'
    }
  }, 'Tasks')
  
  ElMessage.success('已记录任务更新操作')
}

const recordPageView = () => {
  memoryStore.recordHistory('page_dashboard', {
    pageName: 'Dashboard',
    visitTime: Date.now()
  }, 'Dashboard')
  
  memoryStore.updateSystemMemory('page_view', {
    pageName: 'Dashboard'
  })
  
  ElMessage.success('已记录页面访问')
}

const addRecommendation = () => {
  const recommendations = [
    {
      title: '建议设置周目标',
      description: '基于您的工作习惯，建议设置周目标来提高效率',
      type: 'goal_setting'
    },
    {
      title: '任务时间优化',
      description: '您的会议任务平均耗时2小时，建议合理安排时间',
      type: 'time_optimization'
    }
  ]
  
  recommendations.forEach(rec => {
    memoryStore.addRecommendation('personalizedReminders', rec)
  })
  
  ElMessage.success('已添加智能推荐')
}

const updatePreferences = () => {
  memoryStore.updatePreferences({
    theme: 'dark',
    notifications: {
      email: true,
      push: false,
      sound: true
    },
    autoSave: false
  })
  
  ElMessage.success('已更新偏好设置')
}

const getActionLabel = (action) => {
  const labelMap = {
    'create_task': '创建任务',
    'update_task': '更新任务',
    'view_task': '查看任务',
    'complete_task': '完成任务',
    'page_dashboard': '访问仪表盘',
    'page_tasks': '访问任务页面',
    'update_preferences': '更新偏好'
  }
  return labelMap[action] || action
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 生命周期
onMounted(() => {
  // 组件挂载时记录页面访问
  memoryStore.recordHistory('page_memory_example', {}, 'MemoryExample')
  memoryStore.updateSystemMemory('page_view', {
    pageName: 'MemoryExample'
  })
})
</script>

<style scoped>
.memory-example {
  padding: 20px;
}

.example-header h3 {
  margin: 0;
  color: #303133;
}

.example-header p {
  margin: 8px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.action-section,
.status-section,
.history-section,
.patterns-section,
.recommendations-section {
  margin-bottom: 24px;
}

.action-section h4,
.status-section h4,
.history-section h4,
.patterns-section h4,
.recommendations-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.status-item label {
  font-weight: 500;
  color: #606266;
}

.status-item span {
  color: #303133;
}

.patterns-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.pattern-card {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.pattern-card h5 {
  margin: 0 0 16px 0;
  color: #303133;
}

.time-distribution {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-label {
  width: 45px;
  font-size: 12px;
  color: #606266;
}

.bar-container {
  flex: 1;
  height: 6px;
  background-color: #f0f2f5;
  border-radius
: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%);
  transition: width 0.3s ease;
}

.count {
  width: 30px;
  text-align: right;
  font-size: 12px;
  color: #909399;
}

.task-types {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-type-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.task-type-item:last-child {
  border-bottom: none;
}

.type-name {
  color: #606266;
  font-size: 14px;
}

.type-count {
  color: #409eff;
  font-weight: 500;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.recommendation-card {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  transition: box-shadow 0.2s;
}

.recommendation-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.rec-header h5 {
  margin: 0;
  color: #303133;
  font-size: 14px;
}

.rec-score {
  width: 60px;
}

.rec-description {
  margin: 8px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

.rec-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rec-time {
  font-size: 11px;
  color: #c0c4cc;
}

.empty-recommendations {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-recommendations .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-recommendations p {
  margin: 0;
  font-size: 14px;
}

.text-gray {
  color: #c0c4cc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .memory-example {
    padding: 16px;
  }
  
  .patterns-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    justify-content: center;
  }
}
</style>
