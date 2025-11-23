<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button
            type="primary"
            @click="showCreateDialog = true"
          >
            <el-icon><Plus /></el-icon>
            新建用户
          </el-button>
        </div>
      </template>

      <!-- 用户列表 -->
      <el-table
        v-loading="loading"
        :data="users"
        stripe
      >
        <el-table-column
          prop="username"
          label="用户名"
          width="120"
        />
        <el-table-column
          prop="full_name"
          label="姓名"
          width="120"
        />
        <el-table-column
          prop="email"
          label="邮箱"
          width="200"
        />
        <el-table-column
          prop="user_type"
          label="用户类型"
          width="100"
        >
          <template #default="{ row }">
            <el-tag :type="getUserTypeTag(row.user_type)">
              {{ getUserTypeText(row.user_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="关联岗位"
          min-width="200"
        >
          <template #default="{ row }">
            <el-tag
              v-for="role in getUserRoles(row.id)"
              :key="role.id"
              size="small"
              style="margin-right: 5px"
            >
              {{ role.name }}
            </el-tag>
            <el-button
              size="small"
              text
              type="primary"
              @click="showRoleLinkDialog(row)"
            >
              管理岗位
            </el-button>
          </template>
        </el-table-column>
        <el-table-column
          prop="is_active"
          label="状态"
          width="80"
        >
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="180"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              :type="row.is_active ? 'danger' : 'success'"
              @click="toggleUserStatus(row)"
            >
              {{ row.is_active ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="600px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item
          label="用户名"
          prop="username"
        >
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            :disabled="!!editingUser"
          />
        </el-form-item>

        <el-form-item
          label="姓名"
          prop="full_name"
        >
          <el-input
            v-model="userForm.full_name"
            placeholder="请输入姓名"
          />
        </el-form-item>

        <el-form-item
          label="邮箱"
          prop="email"
        >
          <el-input
            v-model="userForm.email"
            placeholder="请输入邮箱"
          />
        </el-form-item>

        <el-form-item
          v-if="!editingUser"
          label="密码"
          prop="password"
        >
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            show-password
          />
        </el-form-item>

        <el-form-item
          label="用户类型"
          prop="user_type"
        >
          <el-select
            v-model="userForm.user_type"
            placeholder="请选择用户类型"
          >
            <el-option
              label="员工"
              value="employee"
            />
            <el-option
              label="管理者"
              value="manager"
            />
            <el-option
              label="管理员"
              value="admin"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="部门">
          <el-select
            v-model="userForm.department_id"
            placeholder="请选择部门"
            clearable
          >
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="直属上级">
          <el-select
            v-model="userForm.manager_id"
            placeholder="请选择直属上级"
            clearable
          >
            <el-option
              v-for="user in managers"
              :key="user.id"
              :label="`${user.full_name} (${user.username})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 岗位关联对话框 -->
    <el-dialog
      v-model="showRoleDialog"
      title="管理用户岗位"
      width="500px"
    >
      <div v-if="currentUser">
        <p style="margin-bottom: 15px">
          用户: <strong>{{ currentUser.full_name }}</strong>
        </p>

        <el-transfer
          v-model="selectedRoles"
          :data="availableRoles"
          :titles="['可用岗位', '已关联岗位']"
          :props="{ key: 'id', label: 'name' }"
        />
      </div>

      <template #footer>
        <el-button @click="showRoleDialog = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSaveRoles"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/api/request'

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const departments = ref([])
const roles = ref([])
const userRoles = ref({}) // 用户ID -> 岗位列表映射

const showCreateDialog = ref(false)
const showRoleDialog = ref(false)
const editingUser = ref(null)
const currentUser = ref(null)
const selectedRoles = ref([])

const userFormRef = ref(null)
const userForm = ref({
  username: '',
  full_name: '',
  email: '',
  password: '',
  user_type: 'employee',
  department_id: null,
  manager_id: null
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  user_type: [{ required: true, message: '请选择用户类型', trigger: 'change' }]
}

// 管理者列表（用于选择直属上级）
const managers = computed(() => {
  return users.value.filter(u => ['manager', 'admin'].includes(u.user_type))
})

// 可用岗位（用于transfer组件）
const availableRoles = computed(() => {
  return roles.value.filter(r => r.is_active).map(r => ({
    id: r.id,
    name: r.name
  }))
})

// 加载用户列表
const loadUsers = async() => {
  loading.value = true
  try {
    const data = await request({ url: '/users/', method: 'get' })
    users.value = data

    // 加载每个用户的岗位
    for (const user of data) {
      await loadUserRoles(user.id)
    }
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 加载部门列表
const loadDepartments = async() => {
  try {
    const data = await request({ url: '/users/departments/', method: 'get' })
    departments.value = data
  } catch (error) {
    console.error('加载部门列表失败:', error)
  }
}

// 加载岗位列表
const loadRoles = async() => {
  try {
    const data = await request({ url: '/roles/', method: 'get' })
    roles.value = data
  } catch (error) {
    console.error('加载岗位列表失败:', error)
  }
}

// 加载用户的岗位
const loadUserRoles = async(userId) => {
  try {
    const user = await request({ url: `/users/${userId}`, method: 'get' })
    userRoles.value[userId] = user.roles || []
  } catch (error) {
    console.error(`加载用户${userId}的岗位失败:`, error)
  }
}

// 获取用户岗位
const getUserRoles = (userId) => {
  return userRoles.value[userId] || []
}

// 用户类型标签
const getUserTypeTag = (type) => {
  const map = { admin: 'danger', manager: 'warning', employee: '' }
  return map[type] || ''
}

const getUserTypeText = (type) => {
  const map = { admin: '管理员', manager: '管理者', employee: '员工' }
  return map[type] || type
}

// 编辑用户
const handleEdit = (row) => {
  editingUser.value = row
  userForm.value = {
    username: row.username,
    full_name: row.full_name,
    email: row.email,
    user_type: row.user_type,
    department_id: row.department_id,
    manager_id: row.manager_id
  }
  showCreateDialog.value = true
}

// 提交用户表单
const handleSubmit = async() => {
  if (!userFormRef.value) {return}

  await userFormRef.value.validate(async(valid) => {
    if (!valid) {return}

    submitting.value = true
    try {
      if (editingUser.value) {
        // 编辑用户
        const updateData = { ...userForm.value }
        delete updateData.username
        delete updateData.password

        await request({
          url: `/users/${editingUser.value.id}`,
          method: 'put',
          data: updateData
        })
        ElMessage.success('用户更新成功')
      } else {
        // 创建用户
        await request({
          url: '/users/',
          method: 'post',
          data: userForm.value
        })
        ElMessage.success('用户创建成功')
      }

      showCreateDialog.value = false
      editingUser.value = null
      resetForm()
      loadUsers()
    } catch (error) {
      ElMessage.error(editingUser.value ? '更新用户失败' : '创建用户失败')
    } finally {
      submitting.value = false
    }
  })
}

// 切换用户状态
const toggleUserStatus = async(row) => {
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? '停用' : '启用'}用户 ${row.full_name} 吗？`,
      '提示',
      { type: 'warning' }
    )

    await request({
      url: `/users/${row.id}`,
      method: 'put',
      data: { is_active: !row.is_active }
    })

    ElMessage.success(`用户已${row.is_active ? '停用' : '启用'}`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 显示岗位关联对话框
const showRoleLinkDialog = async(row) => {
  currentUser.value = row
  const userRoleList = getUserRoles(row.id)
  selectedRoles.value = userRoleList.map(r => r.id)
  showRoleDialog.value = true
}

// 保存岗位关联
const handleSaveRoles = async() => {
  if (!currentUser.value) {return}

  submitting.value = true
  try {
    const currentRoleIds = getUserRoles(currentUser.value.id).map(r => r.id)

    // 找出需要添加和删除的岗位
    const toAdd = selectedRoles.value.filter(id => !currentRoleIds.includes(id))
    const toRemove = currentRoleIds.filter(id => !selectedRoles.value.includes(id))

    // 删除岗位
    for (const roleId of toRemove) {
      await request({
        url: `/users/${currentUser.value.id}/roles/${roleId}`,
        method: 'delete'
      })
    }

    // 添加岗位
    for (const roleId of toAdd) {
      await request({
        url: `/users/${currentUser.value.id}/roles/${roleId}`,
        method: 'post'
      })
    }

    ElMessage.success('岗位关联更新成功')
    showRoleDialog.value = false
    await loadUserRoles(currentUser.value.id)
  } catch (error) {
    ElMessage.error('更新岗位关联失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  userForm.value = {
    username: '',
    full_name: '',
    email: '',
    password: '',
    user_type: 'employee',
    department_id: null,
    manager_id: null
  }
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

onMounted(() => {
  loadUsers()
  loadDepartments()
  loadRoles()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
