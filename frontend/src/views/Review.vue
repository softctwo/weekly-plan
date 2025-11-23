<template>
  <div class="review-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>周复盘</span>
          <div>
            <el-select
              v-model="selectedWeek"
              placeholder="选择周次"
              @change="loadTasks"
            >
              <el-option
                v-for="week in recentWeeks"
                :key="week.value"
                :label="week.label"
                :value="week.value"
              />
            </el-select>
          </div>
        </div>
      </template>

      <el-alert
        v-if="!hasTasksToReview"
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        本周暂无需要复盘的任务，或所有任务已完成复盘
      </el-alert>

      <!-- 任务复盘列表 -->
      <div v-loading="loading">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-review-item"
        >
          <div class="task-header">
            <div>
              <el-icon
                v-if="task.is_key_task"
                color="#f56c6c"
                :size="20"
              >
                <StarFilled />
              </el-icon>
              <span class="task-title">{{ task.title }}</span>
              <el-tag
                :type="getStatusType(task.status)"
                size="small"
                style="margin-left: 10px"
              >
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
            <div v-if="task.review">
              <el-tag type="success">
                已复盘
              </el-tag>
            </div>
          </div>

          <div
            v-if="task.description"
            class="task-desc"
          >
            {{ task.description }}
          </div>

          <!-- 复盘表单 -->
          <div
            v-if="!task.review"
            class="review-form"
          >
            <el-form
              :model="getReviewForm(task.id)"
              label-width="120px"
            >
              <el-form-item label="任务状态">
                <el-radio-group
                  v-model="getReviewForm(task.id).is_completed"
                  @change="handleStatusChange(task.id)"
                >
                  <el-radio :label="true">
                    已完成
                  </el-radio>
                  <el-radio :label="false">
                    未完成
                  </el-radio>
                </el-radio-group>
              </el-form-item>

              <!-- 未完成时的必填项 -->
              <template v-if="!getReviewForm(task.id).is_completed">
                <el-form-item
                  label="未完成原因"
                  required
                >
                  <el-select
                    v-model="getReviewForm(task.id).incomplete_reason"
                    placeholder="请选择未完成原因"
                    style="width: 100%"
                  >
                    <el-option
                      label="客户原因"
                      value="客户原因"
                    />
                    <el-option
                      label="内部资源不足"
                      value="内部资源不足"
                    />
                    <el-option
                      label="优先级变更"
                      value="优先级变更"
                    />
                    <el-option
                      label="技术难度超预期"
                      value="技术难度超预期"
                    />
                    <el-option
                      label="需求变更"
                      value="需求变更"
                    />
                    <el-option
                      label="其他原因"
                      value="其他原因"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item
                  label="后续动作"
                  required
                >
                  <el-radio-group v-model="getReviewForm(task.id).follow_up_action">
                    <el-radio label="delay_to_next_week">
                      延期至下周
                    </el-radio>
                    <el-radio label="cancel">
                      取消任务
                    </el-radio>
                  </el-radio-group>
                </el-form-item>
              </template>

              <el-form-item label="复盘备注">
                <el-input
                  v-model="getReviewForm(task.id).notes"
                  type="textarea"
                  :rows="3"
                  placeholder="可以写一些心得、反思或下周计划..."
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  :loading="submitting"
                  @click="submitReview(task)"
                >
                  提交复盘
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 已复盘信息展示 -->
          <div
            v-else
            class="review-info"
          >
            <el-descriptions
              :column="2"
              border
            >
              <el-descriptions-item label="完成状态">
                <el-tag :type="task.review.is_completed ? 'success' : 'danger'">
                  {{ task.review.is_completed ? '已完成' : '未完成' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="复盘时间">
                {{ formatDate(task.review.reviewed_at) }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="!task.review.is_completed"
                label="未完成原因"
              >
                {{ task.review.incomplete_reason }}
              </el-descriptions-item>
              <el-descriptions-item
                v-if="!task.review.is_completed"
                label="后续动作"
              >
                <el-tag :type="task.review.follow_up_action === 'delay_to_next_week' ? 'warning' : 'info'">
                  {{ getFollowUpText(task.review.follow_up_action) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item
                v-if="task.review.notes"
                label="复盘备注"
                :span="2"
              >
                {{ task.review.notes }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </div>

      <!-- 生成周报按钮 -->
      <div
        v-if="allTasksReviewed && tasks.length > 0"
        class="generate-report"
      >
        <el-divider />
        <el-button
          type="success"
          size="large"
          @click="generateReport"
        >
          <el-icon><Document /></el-icon>
          生成周报
        </el-button>
      </div>
    </el-card>

    <!-- 周报对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="本周工作周报"
      width="800px"
      top="5vh"
    >
      <div
        v-if="weeklyReport"
        class="weekly-report"
      >
        <div class="report-header">
          <h3>{{ weeklyReport.user.name }} - 第{{ weeklyReport.week_number }}周工作周报</h3>
          <p>{{ weeklyReport.year }}年</p>
        </div>

        <el-divider />

        <!-- 统计摘要 -->
        <div class="report-summary">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">
                  任务总数
                </div>
                <div class="summary-value">
                  {{ weeklyReport.summary.total_tasks }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">
                  已完成
                </div>
                <div class="summary-value success">
                  {{ weeklyReport.summary.completed_count }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">
                  未完成
                </div>
                <div class="summary-value danger">
                  {{ weeklyReport.summary.incomplete_count }}
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-label">
                  完成率
                </div>
                <div class="summary-value">
                  {{ weeklyReport.summary.completion_rate.toFixed(1) }}%
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 重点工作 -->
        <div class="report-section">
          <h4>★ 重点工作</h4>
          <el-table
            :data="weeklyReport.key_tasks"
            stripe
          >
            <el-table-column
              prop="title"
              label="任务"
            />
            <el-table-column
              prop="status"
              label="状态"
              width="100"
            >
              <template #default="{ row }">
                <el-tag :type="row.is_completed ? 'success' : 'danger'">
                  {{ row.is_completed ? '已完成' : '未完成' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              label="未完成原因"
              width="150"
            >
              <template #default="{ row }">
                {{ row.review?.incomplete_reason || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 已完成任务 -->
        <div class="report-section">
          <h4>✓ 已完成任务 ({{ weeklyReport.summary.completed_count }}项)</h4>
          <ul>
            <li
              v-for="task in weeklyReport.completed_tasks"
              :key="task.id"
            >
              {{ task.title }}
            </li>
          </ul>
        </div>

        <!-- 未完成任务 -->
        <div
          v-if="weeklyReport.incomplete_tasks.length > 0"
          class="report-section"
        >
          <h4>✗ 未完成任务 ({{ weeklyReport.summary.incomplete_count }}项)</h4>
          <ul>
            <li
              v-for="task in weeklyReport.incomplete_tasks"
              :key="task.id"
            >
              {{ task.title }}
              <el-tag
                size="small"
                style="margin-left: 10px"
              >
                {{ task.review?.incomplete_reason }}
              </el-tag>
              <el-tag
                type="warning"
                size="small"
                style="margin-left: 5px"
              >
                {{ getFollowUpText(task.review?.follow_up_action) }}
              </el-tag>
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <el-button @click="showReportDialog = false">
          关闭
        </el-button>
        <el-button
          type="primary"
          @click="exportReport"
        >
          导出周报
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { StarFilled, Document } from '@element-plus/icons-vue'
import { getMyTasks, createTaskReview, getWeeklyReport } from '@/api/tasks'
import dayjs from 'dayjs'
import weekOfYear from 'dayjs/plugin/weekOfYear'

dayjs.extend(weekOfYear)

const loading = ref(false)
const submitting = ref(false)
const tasks = ref([])
const reviewForms = ref({})
const selectedWeek = ref(null)
const showReportDialog = ref(false)
const weeklyReport = ref(null)

// 生成最近4周的选项
const recentWeeks = computed(() => {
  const weeks = []
  for (let i = 0; i < 4; i++) {
    const date = dayjs().subtract(i, 'week')
    const weekNum = date.week()
    const year = date.year()
    weeks.push({
      value: `${year}-${weekNum}`,
      label: `${year}年第${weekNum}周 (${date.startOf('week').format('MM-DD')} ~ ${date.endOf('week').format('MM-DD')})`
    })
  }
  return weeks
})

// 是否有任务需要复盘
const hasTasksToReview = computed(() => {
  return tasks.value.length > 0
})

// 是否所有任务都已复盘
const allTasksReviewed = computed(() => {
  return tasks.value.length > 0 && tasks.value.every(t => t.review)
})

// 加载任务列表
const loadTasks = async() => {
  if (!selectedWeek.value) {return}

  const [year, week_number] = selectedWeek.value.split('-')

  loading.value = true
  try {
    const data = await getMyTasks({
      year: parseInt(year),
      week_number: parseInt(week_number)
    })
    tasks.value = data

    // 初始化复盘表单
    data.forEach(task => {
      if (!task.review) {
        reviewForms.value[task.id] = {
          task_id: task.id,
          is_completed: task.status === 'completed',
          incomplete_reason: '',
          follow_up_action: 'delay_to_next_week',
          notes: ''
        }
      }
    })
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取复盘表单
const getReviewForm = (taskId) => {
  if (!reviewForms.value[taskId]) {
    reviewForms.value[taskId] = {
      task_id: taskId,
      is_completed: false,
      incomplete_reason: '',
      follow_up_action: 'delay_to_next_week',
      notes: ''
    }
  }
  return reviewForms.value[taskId]
}

// 处理状态变更
const handleStatusChange = (taskId) => {
  const form = getReviewForm(taskId)
  if (form.is_completed) {
    // 已完成时清空未完成原因和后续动作
    form.incomplete_reason = ''
    form.follow_up_action = null
  } else {
    // 未完成时设置默认值
    form.follow_up_action = 'delay_to_next_week'
  }
}

// 提交复盘
const submitReview = async(task) => {
  const form = getReviewForm(task.id)

  // 验证
  if (!form.is_completed) {
    if (!form.incomplete_reason) {
      ElMessage.warning('请选择未完成原因')
      return
    }
    if (!form.follow_up_action) {
      ElMessage.warning('请选择后续动作')
      return
    }
  }

  submitting.value = true
  try {
    await createTaskReview(form)
    ElMessage.success('复盘提交成功')
    loadTasks()
  } catch (error) {
    ElMessage.error('提交复盘失败')
  } finally {
    submitting.value = false
  }
}

// 生成周报
const generateReport = async() => {
  if (!selectedWeek.value) {return}

  const [year, week_number] = selectedWeek.value.split('-')

  loading.value = true
  try {
    const data = await getWeeklyReport({
      year: parseInt(year),
      week_number: parseInt(week_number)
    })
    weeklyReport.value = data
    showReportDialog.value = true
  } catch (error) {
    ElMessage.error('生成周报失败')
  } finally {
    loading.value = false
  }
}

// 导出周报
const exportReport = () => {
  ElMessage.info('导出功能开发中')
}

// 辅助函数
const getStatusType = (status) => {
  const map = { todo: 'info', in_progress: 'warning', completed: 'success', delayed: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { todo: '待办', in_progress: '进行中', completed: '已完成', delayed: '已延期' }
  return map[status] || status
}

const getFollowUpText = (action) => {
  const map = { delay_to_next_week: '延期至下周', cancel: '取消任务' }
  return map[action] || action
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  // 默认选择本周
  selectedWeek.value = recentWeeks.value[0].value
  loadTasks()
})
</script>

<style scoped>
.review-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-review-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fff;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  margin-left: 8px;
}

.task-desc {
  color: #606266;
  margin: 10px 0;
  padding-left: 28px;
}

.review-form {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.review-info {
  margin-top: 15px;
}

.generate-report {
  text-align: center;
  margin-top: 20px;
}

.weekly-report {
  max-height: 70vh;
  overflow-y: auto;
}

.report-header {
  text-align: center;
}

.report-header h3 {
  margin: 0;
  color: #303133;
}

.report-header p {
  margin: 5px 0 0;
  color: #909399;
}

.report-summary {
  margin: 20px 0;
}

.summary-item {
  text-align: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.summary-value.success {
  color: #67c23a;
}

.summary-value.danger {
  color: #f56c6c;
}

.report-section {
  margin: 20px 0;
}

.report-section h4 {
  margin: 15px 0 10px;
  color: #303133;
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.report-section ul {
  list-style: none;
  padding: 0;
}

.report-section ul li {
  padding: 8px 0;
  border-bottom: 1px dashed #ebeef5;
}
</style>
