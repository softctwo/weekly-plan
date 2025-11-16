<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的任务列表</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>

      <!-- 筛选器 -->
      <el-row :gutter="10" style="margin-bottom: 20px">
        <el-col :span="6">
          <el-checkbox v-model="filterKeyTasks" @change="loadTasks">
            只看重点任务
          </el-checkbox>
        </el-col>
      </el-row>

      <!-- 任务表格 -->
      <el-table :data="tasks" stripe>
        <el-table-column label="重点" width="60" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_key_task" color="#f56c6c" :size="20">
              <StarFilled />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="任务标题" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="updateTaskStatus(row)">
              更新状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建任务" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务标题">
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
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, StarFilled } from '@element-plus/icons-vue'
import { getMyTasks, createTask } from '@/api/tasks'
import dayjs from 'dayjs'

const tasks = ref([])
const filterKeyTasks = ref(false)
const showCreateDialog = ref(false)

const taskForm = ref({
  title: '',
  description: '',
  is_key_task: false,
  week_number: dayjs().week(),
  year: dayjs().year()
})

const loadTasks = async () => {
  try {
    const params = {
      week_number: dayjs().week(),
      year: dayjs().year()
    }
    if (filterKeyTasks.value) {
      params.is_key_task = true
    }
    const data = await getMyTasks(params)
    tasks.value = data
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  }
}

const handleCreateTask = async () => {
  if (!taskForm.value.title) {
    ElMessage.warning('请输入任务标题')
    return
  }

  try {
    await createTask(taskForm.value)
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    taskForm.value = {
      title: '',
      description: '',
      is_key_task: false,
      week_number: dayjs().week(),
      year: dayjs().year()
    }
    loadTasks()
  } catch (error) {
    ElMessage.error('创建任务失败')
  }
}

const updateTaskStatus = (row) => {
  ElMessage.info('状态更新功能待实现')
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

onMounted(() => {
  loadTasks()
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
</style>
