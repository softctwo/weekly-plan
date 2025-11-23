<template>
  <div class="roles-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>岗位职责库管理</span>
          <el-button
            type="primary"
            @click="showRoleDialog = true"
          >
            <el-icon><Plus /></el-icon>
            新建岗位
          </el-button>
        </div>
      </template>

      <!-- 岗位列表（折叠面板） -->
      <el-collapse
        v-model="activeRoles"
        v-loading="loading"
      >
        <el-collapse-item
          v-for="role in roles"
          :key="role.id"
          :name="role.id"
        >
          <template #title>
            <div class="role-title">
              <span>
                <el-tag :type="role.is_active ? 'success' : 'info'">
                  {{ role.is_active ? '启用' : '停用' }}
                </el-tag>
                <strong style="margin-left: 10px">{{ role.name }}</strong>
                <el-tag
                  type="info"
                  size="small"
                  style="margin-left: 10px"
                >
                  {{ role.name_en }}
                </el-tag>
              </span>
              <div
                class="role-actions"
                @click.stop
              >
                <el-button
                  size="small"
                  type="primary"
                  @click="showAddRespDialog(role)"
                >
                  添加职责
                </el-button>
                <el-button
                  size="small"
                  :type="role.is_active ? 'warning' : 'success'"
                  @click="toggleRoleStatus(role)"
                >
                  {{ role.is_active ? '停用' : '启用' }}
                </el-button>
              </div>
            </div>
          </template>

          <!-- 职责列表 -->
          <div class="responsibilities-section">
            <el-empty
              v-if="!role.responsibilities || role.responsibilities.length === 0"
              description="暂无职责"
              :image-size="60"
            />

            <div
              v-for="resp in role.responsibilities"
              :key="resp.id"
              class="responsibility-item"
            >
              <div class="resp-header">
                <el-tag
                  :type="resp.is_active ? '' : 'info'"
                  size="large"
                >
                  {{ resp.name }}
                </el-tag>
                <div>
                  <el-button
                    size="small"
                    type="primary"
                    @click="showAddTaskTypeDialog(resp)"
                  >
                    添加任务类型
                  </el-button>
                  <el-button
                    size="small"
                    :type="resp.is_active ? 'warning' : 'success'"
                    @click="toggleRespStatus(resp)"
                  >
                    {{ resp.is_active ? '停用' : '启用' }}
                  </el-button>
                </div>
              </div>

              <!-- 任务类型列表 -->
              <div class="task-types">
                <el-tag
                  v-for="taskType in resp.task_types"
                  :key="taskType.id"
                  :type="taskType.is_active ? 'success' : 'info'"
                  size="small"
                  class="task-type-tag"
                  closable
                  @close="toggleTaskTypeStatus(taskType)"
                >
                  {{ taskType.name }}
                </el-tag>

                <el-empty
                  v-if="!resp.task_types || resp.task_types.length === 0"
                  description="暂无任务类型"
                  :image-size="40"
                />
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>

      <el-empty
        v-if="roles.length === 0"
        description="暂无岗位数据"
        style="margin-top: 40px"
      />
    </el-card>

    <!-- 新建岗位对话框 -->
    <el-dialog
      v-model="showRoleDialog"
      title="新建岗位"
      width="500px"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleRules"
        label-width="100px"
      >
        <el-form-item
          label="岗位名称"
          prop="name"
        >
          <el-input
            v-model="roleForm.name"
            placeholder="如：研发工程师"
          />
        </el-form-item>

        <el-form-item
          label="英文名称"
          prop="name_en"
        >
          <el-input
            v-model="roleForm.name_en"
            placeholder="如：R&D"
          />
        </el-form-item>

        <el-form-item label="岗位描述">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入岗位描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRoleDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleCreateRole"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加职责对话框 -->
    <el-dialog
      v-model="showRespDialog"
      title="添加职责"
      width="500px"
    >
      <el-form
        ref="respFormRef"
        :model="respForm"
        :rules="respRules"
        label-width="100px"
      >
        <el-form-item
          label="职责名称"
          prop="name"
        >
          <el-input
            v-model="respForm.name"
            placeholder="如：产品功能开发"
          />
        </el-form-item>

        <el-form-item label="职责描述">
          <el-input
            v-model="respForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入职责描述"
          />
        </el-form-item>

        <el-form-item label="排序序号">
          <el-input-number
            v-model="respForm.sort_order"
            :min="0"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRespDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleCreateResp"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加任务类型对话框 -->
    <el-dialog
      v-model="showTaskTypeDialog"
      title="添加任务类型"
      width="500px"
    >
      <el-form
        ref="taskTypeFormRef"
        :model="taskTypeForm"
        :rules="taskTypeRules"
        label-width="100px"
      >
        <el-form-item
          label="任务类型"
          prop="name"
        >
          <el-input
            v-model="taskTypeForm.name"
            placeholder="如：需求分析与评审"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="taskTypeForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入任务类型描述"
          />
        </el-form-item>

        <el-form-item label="排序序号">
          <el-input-number
            v-model="taskTypeForm.sort_order"
            :min="0"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showTaskTypeDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleCreateTaskType"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoles, createRole, createResponsibility, createTaskType } from '@/api/roles'
import request from '@/api/request'

const loading = ref(false)
const submitting = ref(false)
const roles = ref([])
const activeRoles = ref([])

const showRoleDialog = ref(false)
const showRespDialog = ref(false)
const showTaskTypeDialog = ref(false)

const currentRole = ref(null)
const currentResp = ref(null)

const roleFormRef = ref(null)
const respFormRef = ref(null)
const taskTypeFormRef = ref(null)

const roleForm = ref({
  name: '',
  name_en: '',
  description: ''
})

const respForm = ref({
  name: '',
  description: '',
  sort_order: 0
})

const taskTypeForm = ref({
  name: '',
  description: '',
  sort_order: 0
})

const roleRules = {
  name: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }],
  name_en: [{ required: true, message: '请输入英文名称', trigger: 'blur' }]
}

const respRules = {
  name: [{ required: true, message: '请输入职责名称', trigger: 'blur' }]
}

const taskTypeRules = {
  name: [{ required: true, message: '请输入任务类型', trigger: 'blur' }]
}

// 加载岗位列表
const loadRoles = async() => {
  loading.value = true
  try {
    const data = await getRoles(true) // 包含停用的岗位
    roles.value = data
    // 默认展开前3个岗位
    activeRoles.value = data.slice(0, 3).map(r => r.id)
  } catch (error) {
    ElMessage.error('加载岗位列表失败')
  } finally {
    loading.value = false
  }
}

// 创建岗位
const handleCreateRole = async() => {
  if (!roleFormRef.value) {return}

  await roleFormRef.value.validate(async(valid) => {
    if (!valid) {return}

    submitting.value = true
    try {
      await createRole(roleForm.value)
      ElMessage.success('岗位创建成功')
      showRoleDialog.value = false
      roleForm.value = { name: '', name_en: '', description: '' }
      loadRoles()
    } catch (error) {
      ElMessage.error('创建岗位失败')
    } finally {
      submitting.value = false
    }
  })
}

// 显示添加职责对话框
const showAddRespDialog = (role) => {
  currentRole.value = role
  respForm.value = { name: '', description: '', sort_order: 0 }
  showRespDialog.value = true
}

// 创建职责
const handleCreateResp = async() => {
  if (!respFormRef.value || !currentRole.value) {return}

  await respFormRef.value.validate(async(valid) => {
    if (!valid) {return}

    submitting.value = true
    try {
      await createResponsibility({
        ...respForm.value,
        role_id: currentRole.value.id
      })
      ElMessage.success('职责创建成功')
      showRespDialog.value = false
      loadRoles()
    } catch (error) {
      ElMessage.error('创建职责失败')
    } finally {
      submitting.value = false
    }
  })
}

// 显示添加任务类型对话框
const showAddTaskTypeDialog = (resp) => {
  currentResp.value = resp
  taskTypeForm.value = { name: '', description: '', sort_order: 0 }
  showTaskTypeDialog.value = true
}

// 创建任务类型
const handleCreateTaskType = async() => {
  if (!taskTypeFormRef.value || !currentResp.value) {return}

  await taskTypeFormRef.value.validate(async(valid) => {
    if (!valid) {return}

    submitting.value = true
    try {
      await createTaskType({
        ...taskTypeForm.value,
        responsibility_id: currentResp.value.id
      })
      ElMessage.success('任务类型创建成功')
      showTaskTypeDialog.value = false
      loadRoles()
    } catch (error) {
      ElMessage.error('创建任务类型失败')
    } finally {
      submitting.value = false
    }
  })
}

// 切换岗位状态
const toggleRoleStatus = async(role) => {
  try {
    await ElMessageBox.confirm(
      `确定要${role.is_active ? '停用' : '启用'}岗位 ${role.name} 吗？`,
      '提示',
      { type: 'warning' }
    )

    await request({
      url: `/roles/${role.id}/deactivate`,
      method: 'put'
    })

    ElMessage.success(`岗位已${role.is_active ? '停用' : '启用'}`)
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 切换职责状态
const toggleRespStatus = async(resp) => {
  try {
    await ElMessageBox.confirm(
      `确定要${resp.is_active ? '停用' : '启用'}职责 ${resp.name} 吗？`,
      '提示',
      { type: 'warning' }
    )

    await request({
      url: `/roles/responsibilities/${resp.id}/deactivate`,
      method: 'put'
    })

    ElMessage.success(`职责已${resp.is_active ? '停用' : '启用'}`)
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 切换任务类型状态
const toggleTaskTypeStatus = async(taskType) => {
  try {
    await ElMessageBox.confirm(
      `确定要${taskType.is_active ? '停用' : '启用'}任务类型 ${taskType.name} 吗？`,
      '提示',
      { type: 'warning' }
    )

    await request({
      url: `/roles/task-types/${taskType.id}/deactivate`,
      method: 'put'
    })

    ElMessage.success(`任务类型已${taskType.is_active ? '停用' : '启用'}`)
    loadRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.roles-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.role-actions {
  display: flex;
  gap: 10px;
}

.responsibilities-section {
  padding: 10px 20px;
}

.responsibility-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.resp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-types {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.task-type-tag {
  cursor: pointer;
}
</style>
