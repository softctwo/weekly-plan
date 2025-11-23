<template>
  <div class="memory-center">
    <!-- 记忆中心头部 -->
    <div class="memory-header">
      <div class="header-content">
        <h2>
          <el-icon><MemoryStick /></el-icon>
          全局记忆中心
        </h2>
        <p class="header-description">
          智能记忆您的操作习惯，提供个性化体验
        </p>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          size="small" 
          @click="refreshMemory"
          :loading="loading"
        >
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button 
          size="small" 
          @click="exportMemory"
        >
          <el-icon><Download /></el-icon>
          导出记忆
        </el-button>
        <el-popconfirm
          title="确认清除所有记忆数据？此操作不可恢复。"
          @confirm="clearAllMemory"
        >
          <template #reference>
            <el-button type="danger" size="small">
              <el-icon><Delete /></el-icon>
              清除记忆
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ memoryStats.historyCount }}</div>
            <div class="stat-label">历史记录</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ memoryStats.recommendationsCount }}</div>
            <div class="stat-label">智能推荐</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ memoryStats.patternsAnalyzed }}</div>
            <div class="stat-label">行为模式</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ memoryStats.sessionInfo?.sessionCount || 0 }}</div>
            <div class="stat-label">使用会话</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-grid">
      <!-- 活跃时间模式 -->
      <el-card class="pattern-card">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><Timer /></el-icon>
              活跃时间模式
            </span>
          </div>
        </template>
        <div class="time-patterns">
          <div 
            v-for="pattern in activeTimePattern.slice(0, 6)" 
            :key="pattern.hour"
            class="time-pattern-item"
          >
            <div class="time-label">{{ pattern.hour }}:00</div>
            <div class="time-bar">
              <div 
                class="time-bar-fill" 
                :style="{ width: `${(pattern.count / maxActivityCount) * 100}%` }"
              ></div>
            </div>
            <div class="time-count">{{ pattern.count }}</div>
          </div>
        </div>
      </el-card>

      <!-- 最近操作历史 -->
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><List /></el-icon>
              最近操作历史
            </span>
            <el-button size="small" text @click="showAllHistory">
              查看全部
            </el-button>
          </div>
        </template>
        <div class="history-list">
          <div 
            v-for="item in recentHistory" 
            :key="item.id"
            class="history-item"
          >
            <div class="history-icon">
              <el-icon>
                <component :is="getActionIcon(item.action)" />
              </el-icon>
            </div>
            <div class="history-content">
              <div class="history-action">{{ getActionLabel(item.action) }}</div>
              <div class="history-meta">
                <span class="history-time">{{ formatTime(item.timestamp) }}</span>
                <span v-if="item.page" class="history-page">{{ item.page }}</span>
              </div>
            </div>
          </div>
          <div v-if="recentHistory.length === 0" class="empty-state">
            <el-icon><DocumentDelete /></el-icon>
            <p>暂无操作历史</p>
          </div>
        </div>
      </el-card>

      <!-- 智能推荐 -->
      <el-card class="recommendations-card">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><MagicStick /></el-icon>
              智能推荐
            </span>
            <el-tag size="small" type="success">{{ totalRecommendations }} 条推荐</el-tag>
          </div>
        </template>
        <div class="recommendations-list">
          <div 
            v-for="recommendation in topRecommendations" 
            :key="`${recommendation.type}-${recommendation.id}`"
            class="recommendation-item"
          >
            <div class="recommendation-score">
              <el-progress 
                type="circle" 
                :percentage="recommendation.score" 
                :width="40"
                :stroke-width="4"
              />
            </div>
            <div class="recommendation-content">
              <div class="recommendation-title">{{ recommendation.title || recommendation.type }}</div>
              <div class="recommendation-desc">{{ recommendation.description || '基于您的使用习惯推荐' }}</div>
              <div class="recommendation-meta">
                <el-tag size="small">{{ recommendation.type }}</el-tag>
                <span class="recommendation-time">{{ formatTime(recommendation.createdAt) }}</span>
              </div>
            </div>
          </div>
          <div v-if="topRecommendations.length === 0" class="empty-state">
            <el-icon><Lightbulb /></el-icon>
            <p>暂无智能推荐</p>
          </div>
        </div>
     
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMemoryStore } from '../store/memory'
import { 
  MemoryStick, 
  Refresh, 
  Download, 
  Delete, 
  Clock, 
  Star, 
  TrendCharts, 
  User, 
  Timer, 
  List, 
  DocumentDelete,
  MagicStick,
  Lightbulb,
  Edit,
  View,
  Plus,
  Check
} from '@element-plus/icons-vue'

const memoryStore = useMemoryStore()

// 响应式数据
const loading = ref(false)

// 计算属性
const memoryStats = computed(() => memoryStore.memoryStats)
const activeTimePattern = computed(() => memoryStore.activeTimePattern)
const recentHistory = computed(() => memoryStore.getHistoryRecords(8))
const totalRecommendations = computed(() => memoryStats.value.recommendationsCount)

const maxActivityCount = computed(() => {
  const patterns = activeTimePattern.value
  return patterns.length > 0 ? Math.max(...patterns.map(p => p.count)) : 1
})

const topRecommendations = computed(() => {
  const allRecs = []
  Object.entries(memoryStore.recommendations).forEach(([type, recs]) => {
    if (Array.isArray(recs)) {
      allRecs.push(...recs.map(rec => ({ ...rec, type })))
    }
  })
  return allRecs.sort((a, b) => b.score - a.score).slice(0, 5)
})

// 方法
const refreshMemory = async () => {
  loading.value = true
  try {
    // 重新加载记忆数据
    memoryStore.loadMemoryFromStorage()
  } finally {
    loading.value = false
  }
}

const exportMemory = () => {
  const data = memoryStore.exportMemoryData()
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `weekly-plan-memory-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const clearAllMemory = () => {
  memoryStore.clearAllMemory()
}

const showAllHistory = () => {
  // 可以打开历史记录的详细对话框
  console.log('显示完整历史记录')
}

const getActionIcon = (action) => {
  const iconMap = {
    'create_task': Plus,
    'update_task': Edit,
    'view_task': View,
    'complete_task': Check,
    'page_dashboard': TrendCharts,
    'page_tasks': List,
    'update_preferences': User
  }
  return iconMap[action] || DocumentDelete
}

const getActionLabel = (action) => {
  const labelMap = {
    'create_task': '创建任务',
    'update_task': '更新任务',
    'view_task': '查看任务',
    'complete_task': '完成任务',
    'page_dashboard': '访问仪表盘',
    'page_tasks': '访问任务页面',
    'update_preferences': '更新偏好设置'
  }
  return labelMap[action] || action
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 1天内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 生命周期
onMounted(() => {
  // 组件挂载时的初始化逻辑
})
</script>

<style scoped>
.memory-center {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.memory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-description {
  margin: 8px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-patterns {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.time-pattern-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-label {
  width: 50px;
  font-size: 
  14px;
  color: #606266;
}

.time-bar {
  flex: 1;
  height: 8px;
  background-color: #f0f2f5;
  border-radius: 4px;
  overflow: hidden;
}

.time-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.time-count {
  width: 30px;
  text-align: right;
  font-size: 12px;
  color: #909399;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.history-item:last-child {
  border-bottom: none;
}

.history-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.history-content {
  flex: 1;
}

.history-action {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.history-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.recommendations-list {
  max-height: 300px;
  overflow-y: auto;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-score {
  flex-shrink: 0;
}

.recommendation-content {
  flex: 1;
}

.recommendation-title {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.recommendation-desc {
  font-size: 12px;
  color: #909399;
  margin: 4px 0;
}

.recommendation-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recommendation-time {
  font-size: 11px;
  color: #c0c4cc;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .memory-center {
    padding: 16px;
  }
  
  .memory-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
}
</style>
