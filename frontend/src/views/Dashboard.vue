<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon :size="32"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_tasks }}</div>
              <div class="stat-label">总任务数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.completed_tasks }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon progress">
              <el-icon :size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.in_progress_tasks }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon key">
              <el-icon :size="32"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.key_tasks_count }}</div>
              <div class="stat-label">重点任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 完成率 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <span>本周完成率</span>
          </template>
          <el-progress
            :percentage="statistics.completion_rate"
            :color="getProgressColor(statistics.completion_rate)"
            :stroke-width="20"
          >
            <span class="progress-text">
              {{ statistics.completion_rate.toFixed(1) }}%
            </span>
          </el-progress>
        </el-card>
      </el-col>
    </el-row>

    <!-- 重点任务列表 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>★ 重点任务</span>
              <el-button type="primary" size="small" @click="goToTasks">
                查看全部
              </el-button>
            </div>
          </template>

          <el-table :data="keyTasks" stripe>
            <el-table-column prop="title" label="任务标题" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="keyTasks.length === 0" description="暂无重点任务" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  List,
  CircleCheck,
  Clock,
  Star
} from '@element-plus/icons-vue'
import { getEmployeeDashboard } from '@/api/dashboard'
import dayjs from 'dayjs'

const router = useRouter()

const statistics = ref({
  total_tasks: 0,
  completed_tasks: 0,
  in_progress_tasks: 0,
  completion_rate: 0,
  key_tasks_count: 0
})

const keyTasks = ref([])

const getCurrentWeek = () => {
  const now = new Date()
  const year = now.getFullYear()
  const weekNumber = dayjs(now).week()
  return { year, week_number: weekNumber }
}

const loadDashboard = async () => {
  try {
    const params = getCurrentWeek()
    const data = await getEmployeeDashboard(params)
    statistics.value = data.statistics
    keyTasks.value = data.key_tasks || []
  } catch (error) {
    ElMessage.error('加载仪表盘数据失败')
  }
}

const getProgressColor = (percentage) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const getStatusType = (status) => {
  const typeMap = {
    todo: 'info',
    in_progress: 'warning',
    completed: 'success',
    delayed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    todo: '待办',
    in_progress: '进行中',
    completed: '已完成',
    delayed: '已延期'
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const goToTasks = () => {
  router.push('/tasks')
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.progress {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.key {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.progress-text {
  font-size: 16px;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
