<template>
  <div class="team-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>团队视图</span>
          <div style="display: flex; gap: 10px">
            <el-button
              type="warning"
              :icon="MagicStick"
              @click="showAIAnalysisDialog = true"
            >
              AI分析
            </el-button>
            <el-select
              v-model="selectedWeek"
              placeholder="选择周次"
              @change="loadTeamData"
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

      <!-- 团队统计概览 -->
      <div
        v-if="teamData"
        class="team-stats"
      >
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon team">
                <el-icon :size="32">
                  <User />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">
                  {{ teamData.team_size }}
                </div>
                <div class="stat-label">
                  团队成员
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon total">
                <el-icon :size="32">
                  <List />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">
                  {{ totalTasks }}
                </div>
                <div class="stat-label">
                  总任务数
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon completed">
                <el-icon :size="32">
                  <CircleCheck />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">
                  {{ totalCompleted }}
                </div>
                <div class="stat-label">
                  已完成
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon rate">
                <el-icon :size="32">
                  <TrendCharts />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">
                  {{ averageRate }}%
                </div>
                <div class="stat-label">
                  平均完成率
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 团队成员列表 -->
      <div
        v-loading="loading"
        class="team-members"
      >
        <el-table
          :data="paginatedMembers"
          stripe
          style="cursor: pointer"
          @row-click="showMemberDetail"
        >
          <el-table-column
            prop="user_name"
            label="成员"
            width="120"
          >
            <template #default="{ row }">
              <strong>{{ row.user_name }}</strong>
            </template>
          </el-table-column>

          <el-table-column
            label="任务概况"
            width="150"
          >
            <template #default="{ row }">
              <el-tag
                type="info"
                size="small"
              >
                总数: {{ row.total_tasks }}
              </el-tag>
              <el-tag
                type="success"
                size="small"
                style="margin-left: 5px"
              >
                完成: {{ row.completed_tasks }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="completion_rate"
            label="完成率"
            width="150"
          >
            <template #default="{ row }">
              <el-progress
                :percentage="row.completion_rate"
                :color="getProgressColor(row.completion_rate)"
                :stroke-width="16"
              />
            </template>
          </el-table-column>

          <el-table-column
            label="重点任务"
            width="120"
          >
            <template #default="{ row }">
              <el-tag
                type="warning"
                size="small"
              >
                {{ row.key_tasks_summary.completed }} / {{ row.key_tasks_summary.total }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            label="延期任务"
            width="80"
          >
            <template #default="{ row }">
              <el-tag
                v-if="row.delayed_tasks > 0"
                type="danger"
                size="small"
              >
                {{ row.delayed_tasks }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="review_status"
            label="复盘状态"
            width="100"
          >
            <template #default="{ row }">
              <el-tag
                :type="getReviewStatusType(row.review_status)"
                size="small"
              >
                {{ row.review_status }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="220"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                @click.stop="showMemberDetail(row)"
              >
                查看详情
              </el-button>
              <el-button
                size="small"
                type="warning"
                @click.stop="openAssignDialog(row)"
              >
                指派任务
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="teamMembers.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </el-card>

    <!-- 成员详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`${currentMember?.user_name} - 周计划详情`"
      width="90%"
      top="5vh"
      destroy-on-close
    >
      <div
        v-if="currentMember && memberDetail"
        v-loading="detailLoading"
      >
        <!-- 成员信息 -->
        <el-descriptions
          :column="3"
          border
        >
          <el-descriptions-item label="姓名">
            {{ memberDetail.member.name }}
          </el-descriptions-item>
          <el-descriptions-item label="岗位">
            <el-tag
              v-for="role in memberDetail.member.roles"
              :key="role.id"
              size="small"
              style="margin-right: 5px"
            >
              {{ role.name }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="周次">
            {{ memberDetail.year }}年 第{{ memberDetail.week_number }}周
          </el-descriptions-item>
        </el-descriptions>

        <!-- 筛选器 -->
        <div class="detail-filters">
          <el-checkbox
            v-model="filterKeyTasks"
            @change="applyFilters"
          >
            只看重点任务
          </el-checkbox>
          <el-select
            v-model="filterRole"
            placeholder="按岗位筛选"
            clearable
            style="width: 200px; margin-left: 10px"
            @change="applyFilters"
          >
            <el-option
              v-for="role in memberDetail.member.roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
          <el-select
            v-model="filterSource"
            placeholder="按来源筛选"
            clearable
            style="width: 200px; margin-left: 10px"
            @change="applyFilters"
          >
            <el-option
              v-for="option in sourceOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <el-button
            type="primary"
            :icon="Plus"
            @click="openAssignDialog()"
          >
            指派任务
          </el-button>
        </div>

        <!-- 任务列表 -->
        <el-table
          :data="filteredTasks"
          stripe
          style="margin-top: 20px"
        >
          <el-table-column
            label="重点"
            width="60"
            align="center"
          >
            <template #default="{ row }">
              <el-icon
                v-if="row.is_key_task"
                color="#f56c6c"
                :size="20"
              >
                <StarFilled />
              </el-icon>
            </template>
          </el-table-column>

          <el-table-column
            prop="title"
            label="任务标题"
            min-width="200"
          />

          <el-table-column
            label="来源"
            width="120"
          >
            <template #default="{ row }">
              <el-tag
                v-if="row.source_type === 'manager_assigned'"
                type="warning"
                size="small"
              >
                领导安排
              </el-tag>
              <el-tag
                v-else-if="row.source_type === 'responsibility'"
                size="small"
              >
                职责任务
              </el-tag>
              <el-tag
                v-else
                type="info"
                size="small"
              >
                个人临时
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            prop="status"
            label="状态"
            width="100"
          >
            <template #default="{ row }">
              <el-tag
                :type="getStatusType(row.status)"
                size="small"
              >
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            label="复盘信息"
            width="200"
          >
            <template #default="{ row }">
              <div v-if="row.review">
                <el-tag
                  :type="row.review.is_completed ? 'success' : 'danger'"
                  size="small"
                >
                  {{ row.review.is_completed ? '已完成' : '未完成' }}
                </el-tag>
                <div
                  v-if="!row.review.is_completed"
                  style="margin-top: 5px"
                >
                  <el-text
                    size="small"
                    type="info"
                  >
                    原因: {{ row.review.incomplete_reason }}
                  </el-text>
                </div>
              </div>
              <el-tag
                v-else
                type="info"
                size="small"
              >
                未复盘
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <!-- 评论区 -->
        <el-divider>管理者审阅与反馈</el-divider>

        <!-- 已有评论 -->
        <div
          v-if="memberComments.length > 0"
          class="comments-section"
        >
          <div
            v-for="comment in memberComments"
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-header">
              <el-tag size="small">
                管理者评论
              </el-tag>
              <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
          </div>
        </div>

        <!-- 添加评论 -->
        <el-form
          :model="commentForm"
          style="margin-top: 20px"
        >
          <el-form-item label="评论/辅导建议">
            <el-input
              v-model="commentForm.content"
              type="textarea"
              :rows="4"
              placeholder="请输入您的评论或辅导建议..."
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="submitting"
              @click="submitComment"
            >
              提交评论
            </el-button>
            <el-button
              type="success"
              :loading="submitting"
              @click="markAsReviewed"
            >
              标记为已审阅
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">
          关闭
        </el-button>
      </template>
    </el-dialog>

    <!-- 指派任务 -->
    <el-dialog
      v-model="showAssignDialog"
      :title="`指派任务给 ${currentMember?.user_name || ''}`"
      width="600px"
    >
      <el-form
        :model="assignForm"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="任务标题">
          <el-input
            v-model="assignForm.title"
            placeholder="请输入任务标题"
          />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select
            v-model="assignForm.linked_task_type_id"
            filterable
            placeholder="选择任务类型（岗位/职责/类型）"
            style="width: 100%"
          >
            <el-option
              v-for="item in taskTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="是否重点">
          <el-switch v-model="assignForm.is_key_task" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="assignForm.planned_start_time"
            type="datetime"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="assignForm.planned_end_time"
            type="datetime"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="assignForm.description"
            type="textarea"
            :rows="3"
            placeholder="可选：补充说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="assignLoading"
          @click="submitAssign"
        >
          确认指派
        </el-button>
      </template>
    </el-dialog>

    <!-- AI分析对话框 -->
    <AIAnalysisDialog
      v-model="showAIAnalysisDialog"
      :team-members="teamMembers"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  List,
  CircleCheck,
  TrendCharts,
  StarFilled,
  MagicStick,
  Plus
} from '@element-plus/icons-vue'
import { getTeamDashboard, getMemberDetail, addComment, markAsReviewed as markReviewedAPI } from '@/api/dashboard'
import { assignTask } from '@/api/tasks'
import { getRoles } from '@/api/roles'
import { useNotificationStore } from '@/store/notification'
import AIAnalysisDialog from '@/components/AIAnalysisDialog.vue'
import dayjs from 'dayjs'
import weekOfYear from 'dayjs/plugin/weekOfYear'

const notificationStore = useNotificationStore()

dayjs.extend(weekOfYear)

const loading = ref(false)
const detailLoading = ref(false)
const submitting = ref(false)
const teamData = ref(null)
const teamMembers = ref([])
const selectedWeek = ref(null)
const showDetailDialog = ref(false)
const showAIAnalysisDialog = ref(false)
const currentMember = ref(null)
const memberDetail = ref(null)
const memberComments = ref([])
const showAssignDialog = ref(false)
const assignLoading = ref(false)
const taskTypeOptions = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选
const filterKeyTasks = ref(false)
const filterRole = ref(null)
const filterSource = ref(null)

// 评论表单
const commentForm = ref({
  content: ''
})

// 指派表单
const assignForm = ref({
  title: '',
  linked_task_type_id: null,
  is_key_task: false,
  planned_start_time: dayjs().hour(9).minute(0).second(0).toDate(),
  planned_end_time: dayjs().hour(10).minute(0).second(0).toDate(),
  description: ''
})

const sourceOptions = [
  { label: '职责建议', value: 'responsibility' },
  { label: '领导安排', value: 'manager_assigned' },
  { label: '个人临时', value: 'personal' }
]

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

// 团队统计
const totalTasks = computed(() => {
  return teamMembers.value.reduce((sum, m) => sum + m.total_tasks, 0)
})

const totalCompleted = computed(() => {
  return teamMembers.value.reduce((sum, m) => sum + m.completed_tasks, 0)
})

const averageRate = computed(() => {
  if (teamMembers.value.length === 0) {return 0}
  const sum = teamMembers.value.reduce((sum, m) => sum + m.completion_rate, 0)
  return (sum / teamMembers.value.length).toFixed(1)
})

// 分页数据
const paginatedMembers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return teamMembers.value.slice(start, end)
})

// 筛选后的任务
const filteredTasks = computed(() => {
  if (!memberDetail.value) {return []}

  let tasks = memberDetail.value.tasks || []
  if (filterKeyTasks.value) {
    tasks = tasks.filter(t => t.is_key_task)
  }
  if (filterSource.value) {
    tasks = tasks.filter(t => t.source_type === filterSource.value)
  }
  return tasks
})

// 加载团队数据
const loadTeamData = async() => {
  if (!selectedWeek.value) {return}

  const [year, week_number] = selectedWeek.value.split('-')

  loading.value = true
  try {
    const data = await getTeamDashboard({
      year: parseInt(year),
      week_number: parseInt(week_number)
    })
    teamData.value = data
    teamMembers.value = data.team_members || []

    // 检查待审阅的成员并生成通知
    checkPendingReviews()
  } catch (error) {
    ElMessage.error('加载团队数据失败')
  } finally {
    loading.value = false
  }
}

// 检查待审阅的成员
const checkPendingReviews = () => {
  const pendingCount = teamMembers.value.filter(m => !m.is_reviewed).length
  if (pendingCount > 0) {
    notificationStore.addTeamReviewReminder(pendingCount)
  }
}

// 显示成员详情
const showMemberDetail = async(row) => {
  currentMember.value = row
  // 重置筛选
  filterKeyTasks.value = false
  filterRole.value = null
  filterSource.value = null

  showDetailDialog.value = true
  await loadMemberDetail()
}

const loadMemberDetail = async() => {
  if (!currentMember.value || !selectedWeek.value) {return}
  const [year, week_number] = selectedWeek.value.split('-')

  detailLoading.value = true
  try {
    const params = {
      year: parseInt(year),
      week_number: parseInt(week_number)
    }
    if (filterKeyTasks.value) {
      params.is_key_task = true
    }
    if (filterRole.value) {
      params.role_id = filterRole.value
    }
    if (filterSource.value) {
      params.source_type = filterSource.value
    }

    const detail = await getMemberDetail(currentMember.value.user_id, params)
    memberDetail.value = detail
    memberComments.value = detail.comments || []
  } catch (error) {
    ElMessage.error('加载成员详情失败')
  } finally {
    detailLoading.value = false
  }
}

// 提交评论
const submitComment = async() => {
  if (!commentForm.value.content) {
    ElMessage.warning('请输入评论内容')
    return
  }

  if (!currentMember.value) {return}

  const [year, week_number] = selectedWeek.value.split('-')

  submitting.value = true
  try {
    await addComment({
      user_id: currentMember.value.user_id,
      week_number: parseInt(week_number),
      year: parseInt(year),
      content: commentForm.value.content
    })

    ElMessage.success('评论提交成功')
    commentForm.value.content = ''

    // 重新加载详情
    showMemberDetail(currentMember.value)
  } catch (error) {
    ElMessage.error('提交评论失败')
  } finally {
    submitting.value = false
  }
}

// 标记为已审阅
const markAsReviewed = async() => {
  if (memberComments.value.length === 0) {
    ElMessage.warning('请先添加评论后再标记为已审阅')
    return
  }

  submitting.value = true
  try {
    const lastComment = memberComments.value[memberComments.value.length - 1]
    await markReviewedAPI(lastComment.id)

    ElMessage.success('已标记为已审阅')
    loadTeamData()
    showDetailDialog.value = false
  } catch (error) {
    ElMessage.error('标记失败')
  } finally {
    submitting.value = false
  }
}

// 应用筛选
const applyFilters = () => {
  if (currentMember.value) {
    loadMemberDetail()
  }
}

// 分页处理
const handlePageChange = (page) => {
  currentPage.value = page
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

// 辅助函数
const getProgressColor = (percentage) => {
  if (percentage < 30) {return '#f56c6c'}
  if (percentage < 70) {return '#e6a23c'}
  return '#67c23a'
}

const getReviewStatusType = (status) => {
  const map = {
    '未提交': 'info',
    '已提交': 'warning',
    '已审阅': 'success'
  }
  return map[status] || 'info'
}

const getStatusType = (status) => {
  const map = {
    todo: 'info',
    in_progress: 'warning',
    completed: 'success',
    delayed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    todo: '待办',
    in_progress: '进行中',
    completed: '已完成',
    delayed: '已延期'
  }
  return map[status] || status
}

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const openAssignDialog = (row) => {
  if (row) {
    currentMember.value = row
  }
  if (!currentMember.value) {
    ElMessage.warning('请先选择团队成员')
    return
  }
  assignForm.value = {
    title: '',
    linked_task_type_id: null,
    is_key_task: false,
    planned_start_time: dayjs().hour(9).minute(0).second(0).toDate(),
    planned_end_time: dayjs().hour(10).minute(0).second(0).toDate(),
    description: ''
  }
  showAssignDialog.value = true
}

const submitAssign = async() => {
  if (!currentMember.value) {
    ElMessage.warning('未选择成员')
    return
  }
  if (!assignForm.value.title || !assignForm.value.linked_task_type_id) {
    ElMessage.warning('请填写标题并选择任务类型')
    return
  }
  if (!selectedWeek.value) {
    ElMessage.warning('请先选择周次')
    return
  }

  const [year, week_number] = selectedWeek.value.split('-')
  assignLoading.value = true
  try {
    await assignTask(currentMember.value.user_id, {
      title: assignForm.value.title,
      description: assignForm.value.description,
      year: parseInt(year),
      week_number: parseInt(week_number),
      source_type: 'manager_assigned',
      linked_task_type_id: assignForm.value.linked_task_type_id,
      is_key_task: assignForm.value.is_key_task,
      planned_start_time: dayjs(assignForm.value.planned_start_time).toISOString(),
      planned_end_time: dayjs(assignForm.value.planned_end_time).toISOString()
    })
    ElMessage.success('指派成功')
    showAssignDialog.value = false
    loadMemberDetail()
    loadTeamData()
  } catch (error) {
    ElMessage.error('指派失败')
  } finally {
    assignLoading.value = false
  }
}

const loadTaskTypes = async() => {
  try {
    const roles = await getRoles(false)
    const list = []
    roles.forEach(role => {
      (role.responsibilities || []).forEach(resp => {
        (resp.task_types || []).forEach(tt => {
          list.push({
            value: tt.id,
            label: `${role.name} / ${resp.name} / ${tt.name}`
          })
        })
      })
    })
    taskTypeOptions.value = list
  } catch (error) {
    ElMessage.error('加载任务类型失败')
  }
}

onMounted(() => {
  selectedWeek.value = recentWeeks.value[0].value
  loadTeamData()
   loadTaskTypes()
})
</script>

<style scoped>
.team-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-stats {
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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

.stat-icon.team {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.total {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.rate {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-filters {
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.comments-section {
  margin: 20px 0;
}

.comment-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-content {
  color: #303133;
  line-height: 1.6;
}
</style>
