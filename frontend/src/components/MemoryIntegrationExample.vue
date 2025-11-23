<template>
  <div class="memory-integration">
    <!-- 在侧边栏添加记忆中心入口 -->
    <el-menu-item 
      index="memory-center" 
      @click="$router.push('/memory-center')"
      class="memory-menu-item"
    >
      <el-icon><MemoryStick /></el-icon>
      <span>记忆中心</span>
      <el-badge 
        v-if="unreadRecommendations > 0" 
        :value="unreadRecommendations" 
        class="memory-badge"
      />
    </el-menu-item>

    <!-- 在顶部栏添加记忆快捷按钮 -->
    <el-tooltip content="记忆统计" placement="bottom">
      <el-button 
        circle 
        size="small"
        @click="showMemoryStats = !showMemoryStats"
        class="memory-stats-btn"
      >
        <el-icon><TrendCharts /></el-icon>
      </el-button>
    </el-tooltip>

    <!-- 记忆统计抽屉 -->
    <el-drawer
      v-model="showMemoryStats"
      title="记忆统计"
      direction="rtl"
      size="400px"
      :with-header="true"
    >
      <div class="memory-stats-content">
        <!-- 快速统计 -->
        <div class="quick-stats">
          <el-statistic title="今日操作" :value="todayOperations" />
          <el-statistic title="历史记录" :value="memoryStats.historyCount" />
          <el-statistic title="智能推荐" :value="memoryStats.recommendationsCount" />
        </div>

        <!-- 最近活动 -->
        <div class="recent-activities">
          <h4>最近活动</h4>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="formatTime(activity.timestamp)"
              placement="top"
            >
              <p>{{ getActionLabel(activity.action) }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>

        <!-- 快捷操作 -->
        <div class="quick-actions">
          <h4>快捷操作</h4>
          <el-button-group>
            <el-button size="small" @click="openMemoryCenter">
              <el-icon><Setting /></el-icon>
              记忆中心
            </el-button>
            <el-button size="small" @click="exportMemory">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
            <el-button size="small" @click="clearTempMemory">
              <el-icon><RefreshLeft /></el-icon>
              清理缓存
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-drawer>

    <!-- 在内容区域添加智能提醒 -->
    <div v-if="showSmartReminder" class="smart-reminder">
      <el-alert
        :title="smartReminder.title"
        :description="smartReminder.description"
        type="info"
        show-icon
        :closable="true"
        @close="dismissReminder"
      >
        <template #default>
          <div class="reminder-content">
            <div class="reminder-text">
              <strong>{{ smartReminder.title }}</strong>
              <p>{{ smartReminder.description }}</p>
            </div>
            <div class="reminder-actions">
              <el-button size="small" type="primary" @click="handleReminderAction">
                {{ smartReminder.actionText }}
              </el-button>
              <el-button size="small" @click="dismissReminder">
                忽略
              </el-button>
            </div>
          </div>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMemoryStore } from '@/store/memory'
import { 
  MemoryStick, 
  TrendCharts, 
  Setting, 
  Download, 
  RefreshLeft 
} from '@element-plus/icons-vue'

const router = useRouter()
const memoryStore = useMemoryStore()

// 响应式数据
const showMemoryStats = ref(false)
const showSmartReminder = ref(false)
const smartReminder = ref({
  title: '',
  description: '',
  actionText: '',
  action: null
})

// 计算属性
const memoryStats = computed(() => memoryStore.memoryStats)
const unreadRecommendations = computed(() => {
  return memoryStore.recommendations.personalizedReminders?.length || 0
})

const todayOperations = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return memoryStore.userHistory.filter(item => item.date === today).length
})

const recentActivities = computed(() => {
  return memoryStore.getHistoryRecords(5)
})

// 方法
const openMemoryCenter = () => {
  showMemoryStats.value = false
  router.push('/memory-center')
}

const exportMemory = () => {
  const data = memoryStore.exportMemoryData()
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `memory-backup-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('记忆数据导出成功')
}

const clearTempMemory = () => {
  memoryStore.clearTempMemory()
  ElMessage.success('临时记忆已清理')
}

const dismissReminder = () => {
  showSmartReminder.value = false
}

const handleReminderAction = () => {
  if (smartReminder.value.action) {
    smartReminder.value.action()
  }
  dismissReminder()
}

const getActionLabel = (action) => {
  const labelMap = {
    'create_task': '创建了新任务',
    'update_task': '更新了任务',
    'page_dashboard': '访问了仪表盘',
    'page_tasks': '访问了任务页面',
    'update_preferences': '更新了偏好设置'
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

const checkForSmartReminders = () => {
  // 检查是否有需要显示的智能提醒
  const reminders = memoryStore.recommendations.personalizedReminders || []
  
  if (reminders.length > 0) {
    // 显示最新的推荐作为智能提醒
    const latestReminder = reminders[0]
    
    smartReminder.value = {
      title: latestReminder.title || '智能建议',
      description: latestReminder.description || '根据您的使用习惯，我们有一些建议',
      actionText: '查看详情',
      action: () => {
        router.push('/memory-center')
      }
    }
    
    showSmartReminder.value = true
  }
}

const initializeMemoryIntegration = () => {
  // 记录页面加载
  memoryStore.recordHistory('page_memory_integration', {}, 'MemoryIntegration')
  
  // 检查智能提醒
  setTimeout(() => {
    checkForSmartReminders()
  }, 2000) // 2秒后显示提醒
}

// 生命周期
onMounted(() => {
  initializeMemoryIntegration()
})

onUnmounted(() => {
  // 清理资源
  showMemoryStats.value = false
  showSmartReminder.value = false
})
</script>

<style scoped>
.memory-menu-item {
  position: relative;
}

.memory-badge {
  position: absolute;
  top: 8px;
  right: 20px;
}

.memory-stats-btn {
  margin: 0 4px;
}

.memory-stats-content {
  padding: 16px;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.recent-activities {
  margin-bottom: 24px;
}

.recent-activities h4,
.quick-actions h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 14px;
}

.smart-reminder {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  width: 400px;
  max-width: calc(100vw - 40px);
}

.reminder-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.reminder-text {
  flex: 1;
}

.reminder-text strong {
  color: #303133;
  font-size: 14px;
}

.reminder-text p {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
}

.reminder-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .memory-stats-content {
    padding: 12px;
  }
  
  .quick-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .smart-reminder {
    width: calc(100vw - 20px);
    left: 10px;
    transform: none;
  }
  
  .reminder-content {
    flex-direction: column;
  }
  
  .reminder-actions {
    flex-direction: row;
    width: 100%;
  }
}
</style>
