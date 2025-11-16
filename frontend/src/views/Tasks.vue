<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的任务列表</span>
          <div class="header-actions">
            <el-button type="success" @click="exportToExcel" :icon="Download">
              导出Excel
            </el-button>
            <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
              新建任务
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选器和批量操作工具栏 -->
      <el-row :gutter="10" style="margin-bottom: 20px">
        <el-col :span="12">
          <el-space wrap>
            <el-checkbox v-model="filterKeyTasks" @change="loadTasks">
              只看重点任务
            </el-checkbox>
            <el-select
              v-model="filterStatus"
              placeholder="筛选状态"
              clearable
              @change="loadTasks"
              style="width: 150px"
            >
              <el-option label="待办" value="todo" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已延期" value="delayed" />
            </el-select>
          </el-space>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-space v-if="selectedTasks.length > 0">
            <el-tag type="info">已选择 {{ selectedTasks.length }} 项</el-tag>
            <el-button size="small" type="primary" @click="showBatchStatusDialog = true">
              批量更新状态
            </el-button>
            <el-button size="small" type="warning" @click="batchMarkAsKey">
              批量标记重点
            </el-button>
            <el-button size="small" type="danger" @click="batchDelete">
              批量删除
            </el-button>
            <el-button size="small" @click="clearSelection">
              清除选择
            </el-button>
          </el-space>
        </el-col>
      </el-row>

      <!-- 拖拽排序提示 -->
      <el-alert
        v-if="!filterKeyTasks && !filterStatus"
        title="提示：可以拖拽任务卡片进行排序"
        type="info"
        :closable="false"
        style="margin-bottom: 15px"
      />

      <!-- 任务列表（拖拽模式） -->
      <div v-loading="loading">
        <draggable
          v-model="paginatedTasks"
          item-key="id"
          handle=".drag-handle"
          @end="handleDragEnd"
          :disabled="filterKeyTasks || !!filterStatus"
          class="task-list"
        >
          <template #item="{ element }">
            <div class="task-card" :class="{ 'selected': isSelected(element.id) }">
              <div class="task-card-header">
                <el-checkbox
                  :model-value="isSelected(element.id)"
                  @change="toggleSelection(element.id)"
                  class="task-checkbox"
                />
                <el-icon
                  class="drag-handle"
                  :class="{ 'disabled': filterKeyTasks || !!filterStatus }"
                  :size="20"
                >
                  <Rank />
                </el-icon>
                <div class="task-title-section">
                  <el-icon v-if="element.is_key_task" color="#f56c6c" :size="20">
                    <StarFilled />
                  </el-icon>
                  <span class="task-title">{{ element.title }}</span>
                  <el-tag :type="getStatusType(element.status)" size="small">
                    {{ getStatusText(element.status) }}
                  </el-tag>
                </div>
                <div class="task-actions">
                  <el-button
                    size="small"
                    type="primary"
                    @click="showUpdateStatusDialog(element)"
                  >
                    更新状态
                  </el-button>
                  <el-button
                    size="small"
                    type="warning"
                    @click="toggleKeyTask(element)"
                  >
                    {{ element.is_key_task ? '取消重点' : '标记重点' }}
                  </el-button>
                  <el-popconfirm
                    title="确定要删除这个任务吗？"
                    @confirm="deleteTask(element.id)"
                  >
                    <template #reference>
                      <el-button size="small" type="danger">删除</el-button>
                    </template>
                  </el-popconfirm>
                </div>
              </div>
              <div v-if="element.description" class="task-description">
                {{ element.description }}
              </div>
              <div class="task-meta">
                <el-tag v-if="element.linked_task_type" size="small" type="info">
                  {{ element.linked_task_type.name }}
                </el-tag>
                <span class="task-date">
                  创建时间: {{ formatDate(element.created_at) }}
                </span>
              </div>
            </div>
          </template>
        </draggable>

        <el-empty
          v-if="paginatedTasks.length === 0 && !loading"
          description="暂无任务数据"
          :image-size="100"
        />
      </div>

      <!-- 分页 -->
      <el-pagination
        v-if="allTasks.length > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="allTasks.length"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建任务" width="600px">
      <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="100px">
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item label="是否重点">
          <el-switch v-model="taskForm.is_key_task" />
        </el-form-item>
        <el-form-item label="关联职责">
          <el-cascader
            v-model="taskForm.linked_task_type_id"
            :options="responsibilityOptions"
            :props="{
              value: 'id',
              label: 'name',
              children: 'task_types',
              emitPath: false
            }"
            placeholder="选择职责和任务类型（可选）"
            clearable
            filterable
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTask" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 更新状态对话框 -->
    <el-dialog v-model="showStatusDialog" title="更新任务状态" width="400px">
      <el-form label-width="80px">
        <el-form-item label="任务状态">
          <el-select v-model="statusForm.status" placeholder="选择状态">
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已延期" value="delayed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateStatus" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量更新状态对话框 -->
    <el-dialog v-model="showBatchStatusDialog" title="批量更新状态" width="400px">
      <el-form label-width="80px">
        <el-form-item label="新状态">
          <el-select v-model="batchStatusForm.status" placeholder="选择状态">
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已延期" value="delayed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatchStatusDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchUpdateStatus" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, StarFilled, Download, Rank } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import * as XLSX from 'xlsx'
import { getMyTasks, createTask, updateTask, deleteTask as deleteTaskApi } from '@/api/tasks'
import { useUserStore } from '@/store/user'
import { useCacheStore } from '@/store/cache'
import dayjs from 'dayjs'
import request from '@/api/request'

const userStore = useUserStore()
const cacheStore = useCacheStore()

const loading = ref(false)
const submitting = ref(false)
const allTasks = ref([])
const filterKeyTasks = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const showStatusDialog = ref(false)
const showBatchStatusDialog = ref(false)
const selectedTasks = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

const taskFormRef = ref(null)
const currentTask = ref(null)
const responsibilityOptions = ref([])

const taskForm = ref({
  title: '',
  description: '',
  is_key_task: false,
  linked_task_type_id: null,
  week_number: dayjs().week(),
  year: dayjs().year()
})

const taskRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }]
}

const statusForm = ref({
  status: 'todo'
})

const batchStatusForm = ref({
  status: 'todo'
})

// 分页后的任务列表
const paginatedTasks = computed({
  get: () => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return allTasks.value.slice(start, end)
  },
  set: (value) => {
    // 当拖拽排序时，更新allTasks
    const start = (currentPage.value - 1) * pageSize.value
    allTasks.value.splice(start, pageSize.value, ...value)
  }
})

// 加载职责选项（用于级联选择器）
const loadResponsibilities = async () => {
  try {
    const userInfo = await request({ url: '/users/me', method: 'get' })
    const roles = userInfo.roles || []

    // 构建级联选项
    const options = []
    for (const role of roles) {
      for (const resp of role.responsibilities || []) {
        if (resp.is_active && resp.task_types?.length > 0) {
          options.push({
            id: resp.id,
            name: `${role.name} - ${resp.name}`,
            task_types: resp.task_types
              .filter(tt => tt.is_active)
              .map(tt => ({
                id: tt.id,
                name: tt.name
              }))
          })
        }
      }
    }
    responsibilityOptions.value = options
  } catch (error) {
    console.error('加载职责选项失败:', error)
  }
}

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      week_number: dayjs().week(),
      year: dayjs().year()
    }
    if (filterKeyTasks.value) {
      params.is_key_task = true
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }

    // 生成缓存键（包含所有筛选条件）
    const cacheKey = `tasks_${params.year}_w${params.week_number}_key${params.is_key_task || 'all'}_status${params.status || 'all'}`

    // 使用缓存策略获取任务数据
    const data = await cacheStore.getTasksCache(cacheKey, async () => {
      return await getMyTasks(params)
    })

    allTasks.value = data

    // 重置到第一页
    currentPage.value = 1
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 创建任务
const handleCreateTask = async () => {
  if (!taskFormRef.value) return

  await taskFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await createTask(taskForm.value)
      ElMessage.success('任务创建成功')
      showCreateDialog.value = false
      taskForm.value = {
        title: '',
        description: '',
        is_key_task: false,
        linked_task_type_id: null,
        week_number: dayjs().week(),
        year: dayjs().year()
      }

      // 清除任务和仪表盘缓存
      cacheStore.invalidateTasks()
      cacheStore.invalidateDashboard()

      loadTasks()
    } catch (error) {
      ElMessage.error('创建任务失败')
    } finally {
      submitting.value = false
    }
  })
}

// 显示更新状态对话框
const showUpdateStatusDialog = (task) => {
  currentTask.value = task
  statusForm.value.status = task.status
  showStatusDialog.value = true
}

// 更新任务状态
const handleUpdateStatus = async () => {
  if (!currentTask.value) return

  submitting.value = true
  try {
    await updateTask(currentTask.value.id, { status: statusForm.value.status })
    ElMessage.success('状态更新成功')
    showStatusDialog.value = false

    // 清除缓存
    cacheStore.invalidateTasks()
    cacheStore.invalidateDashboard()

    loadTasks()
  } catch (error) {
    ElMessage.error('更新状态失败')
  } finally {
    submitting.value = false
  }
}

// 切换重点任务标记
const toggleKeyTask = async (task) => {
  try {
    await updateTask(task.id, { is_key_task: !task.is_key_task })
    ElMessage.success(task.is_key_task ? '已取消重点标记' : '已标记为重点任务')

    // 清除缓存
    cacheStore.invalidateTasks()
    cacheStore.invalidateDashboard()

    loadTasks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除任务
const deleteTask = async (taskId) => {
  try {
    await deleteTaskApi(taskId)
    ElMessage.success('任务已删除')

    // 清除缓存
    cacheStore.invalidateTasks()
    cacheStore.invalidateDashboard()

    loadTasks()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 拖拽结束处理
const handleDragEnd = async () => {
  // 这里可以调用API保存新的排序
  // 目前只在前端更新顺序
  ElMessage.success('排序已更新')
}

// 批量选择相关
const isSelected = (taskId) => {
  return selectedTasks.value.includes(taskId)
}

const toggleSelection = (taskId) => {
  const index = selectedTasks.value.indexOf(taskId)
  if (index > -1) {
    selectedTasks.value.splice(index, 1)
  } else {
    selectedTasks.value.push(taskId)
  }
}

const clearSelection = () => {
  selectedTasks.value = []
}

// 批量更新状态
const handleBatchUpdateStatus = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择任务')
    return
  }

  submitting.value = true
  try {
    for (const taskId of selectedTasks.value) {
      await updateTask(taskId, { status: batchStatusForm.value.status })
    }
    ElMessage.success(`已更新 ${selectedTasks.value.length} 个任务的状态`)
    showBatchStatusDialog.value = false
    clearSelection()

    // 清除缓存
    cacheStore.invalidateTasks()
    cacheStore.invalidateDashboard()

    loadTasks()
  } catch (error) {
    ElMessage.error('批量更新失败')
  } finally {
    submitting.value = false
  }
}

// 批量标记重点
const batchMarkAsKey = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择任务')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedTasks.value.length} 个任务标记为重点吗？`,
      '批量标记重点',
      { type: 'warning' }
    )

    for (const taskId of selectedTasks.value) {
      await updateTask(taskId, { is_key_task: true })
    }
    ElMessage.success(`已标记 ${selectedTasks.value.length} 个重点任务`)
    clearSelection()

    // 清除缓存
    cacheStore.invalidateTasks()
    cacheStore.invalidateDashboard()

    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量标记失败')
    }
  }
}

// 批量删除
const batchDelete = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择任务')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？此操作不可恢复！`,
      '批量删除',
      { type: 'warning' }
    )

    for (const taskId of selectedTasks.value) {
      await deleteTaskApi(taskId)
    }
    ElMessage.success(`已删除 ${selectedTasks.value.length} 个任务`)
    clearSelection()

    // 清除缓存
    cacheStore.invalidateTasks()
    cacheStore.invalidateDashboard()

    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 导出Excel
const exportToExcel = () => {
  if (allTasks.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  try {
    // 准备导出数据
    const exportData = allTasks.value.map((task, index) => ({
      '序号': index + 1,
      '任务标题': task.title,
      '任务描述': task.description || '-',
      '是否重点': task.is_key_task ? '是' : '否',
      '状态': getStatusText(task.status),
      '关联任务类型': task.linked_task_type?.name || '-',
      '创建时间': formatDate(task.created_at),
      '更新时间': formatDate(task.updated_at)
    }))

    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '我的任务')

    // 设置列宽
    ws['!cols'] = [
      { wch: 6 },  // 序号
      { wch: 30 }, // 任务标题
      { wch: 50 }, // 任务描述
      { wch: 10 }, // 是否重点
      { wch: 10 }, // 状态
      { wch: 20 }, // 关联任务类型
      { wch: 20 }, // 创建时间
      { wch: 20 }  // 更新时间
    ]

    // 导出文件
    const fileName = `我的任务_第${dayjs().week()}周_${dayjs().format('YYYY-MM-DD')}.xlsx`
    XLSX.writeFile(wb, fileName)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 辅助函数
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

const formatDate = (dateStr) => {
  return dateStr ? dayjs(dateStr).format('YYYY-MM-DD HH:mm') : '-'
}

onMounted(() => {
  loadTasks()
  loadResponsibilities()
})
</script>

<style scoped>
.tasks-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.task-list {
  min-height: 200px;
}

.task-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  transition: all 0.3s;
  cursor: move;
}

.task-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.task-card.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.task-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.task-checkbox {
  flex-shrink: 0;
}

.drag-handle {
  flex-shrink: 0;
  cursor: grab;
  color: #909399;
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-handle.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.task-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.task-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.task-description {
  margin-left: 56px;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
}

.task-meta {
  margin-left: 56px;
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.task-date {
  font-size: 12px;
}
</style>
