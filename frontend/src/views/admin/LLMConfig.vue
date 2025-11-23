<template>
  <div class="llm-config-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>大模型配置管理</span>
          <el-button
            type="primary"
            :icon="Plus"
            @click="showCreateDialog = true"
          >
            新建配置
          </el-button>
        </div>
      </template>

      <!-- 配置列表 -->
      <el-table
        v-loading="loading"
        :data="configs"
        stripe
      >
        <el-table-column
          prop="name"
          label="配置名称"
          width="200"
        />
        <el-table-column
          prop="provider"
          label="提供商"
          width="120"
        >
          <template #default="{ row }">
            <el-tag
              v-if="row.provider === 'deepseek'"
              type="primary"
            >
              Deepseek
            </el-tag>
            <el-tag
              v-else-if="row.provider === 'openai'"
              type="success"
            >
              OpenAI
            </el-tag>
            <el-tag v-else>
              {{ row.provider }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="model_name"
          label="模型名称"
          width="150"
        />
        <el-table-column
          prop="api_key"
          label="API Key"
          width="200"
        >
          <template #default="{ row }">
            <span>{{ maskApiKey(row.api_key) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="max_tokens"
          label="Max Tokens"
          width="120"
          align="center"
        />
        <el-table-column
          prop="temperature"
          label="Temperature"
          width="120"
          align="center"
        />
        <el-table-column
          label="状态"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              v-if="row.is_active"
              type="success"
            >
              已激活
            </el-tag>
            <el-tag
              v-else
              type="info"
            >
              未激活
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="250"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button-group>
              <el-button
                v-if="!row.is_active"
                size="small"
                type="success"
                @click="activateConfig(row.id)"
              >
                激活
              </el-button>
              <el-button
                size="small"
                type="primary"
                @click="showEditDialog(row)"
              >
                编辑
              </el-button>
              <el-popconfirm
                title="确定要删除这个配置吗？"
                @confirm="deleteConfig(row.id)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 测试连接 -->
      <div style="margin-top: 20px">
        <el-button
          type="warning"
          :icon="Connection"
          :loading="testing"
          @click="testConnection"
        >
          测试当前激活配置的连接
        </el-button>
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingConfig ? '编辑配置' : '新建配置'"
      width="600px"
    >
      <el-form
        ref="configFormRef"
        :model="configForm"
        :rules="configRules"
        label-width="120px"
      >
        <el-form-item
          label="配置名称"
          prop="name"
        >
          <el-input
            v-model="configForm.name"
            placeholder="例如：Deepseek默认配置"
          />
        </el-form-item>

        <el-form-item
          label="提供商"
          prop="provider"
        >
          <el-select
            v-model="configForm.provider"
            placeholder="选择提供商"
          >
            <el-option
              label="Deepseek"
              value="deepseek"
            />
            <el-option
              label="OpenAI"
              value="openai"
            />
          </el-select>
        </el-form-item>

        <el-form-item
          label="API Key"
          prop="api_key"
        >
          <el-input
            v-model="configForm.api_key"
            type="password"
            show-password
            placeholder="sk-..."
          />
        </el-form-item>

        <el-form-item label="API Base URL">
          <el-input
            v-model="configForm.api_base"
            placeholder="留空使用默认URL"
          />
          <div class="form-tip">
            Deepseek默认: https://api.deepseek.com/v1/chat/completions
          </div>
        </el-form-item>

        <el-form-item
          label="模型名称"
          prop="model_name"
        >
          <el-input
            v-model="configForm.model_name"
            placeholder="例如：deepseek-chat"
          />
        </el-form-item>

        <el-form-item
          label="Max Tokens"
          prop="max_tokens"
        >
          <el-input-number
            v-model="configForm.max_tokens"
            :min="100"
            :max="32000"
            :step="100"
          />
        </el-form-item>

        <el-form-item
          label="Temperature"
          prop="temperature"
        >
          <el-input
            v-model="configForm.temperature"
            placeholder="0.0-1.0，推荐0.7"
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="configForm.description"
            type="textarea"
            :rows="3"
            placeholder="配置说明"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Connection } from '@element-plus/icons-vue'
import request from '@/api/request'

const loading = ref(false)
const testing = ref(false)
const submitting = ref(false)
const showDialog = ref(false)
const showCreateDialog = ref(false)
const editingConfig = ref(null)
const configFormRef = ref(null)

const configs = ref([])

const configForm = ref({
  name: '',
  provider: 'deepseek',
  api_key: '',
  api_base: '',
  model_name: 'deepseek-chat',
  max_tokens: 4000,
  temperature: '0.7',
  description: ''
})

const configRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  max_tokens: [{ required: true, message: '请输入Max Tokens', trigger: 'blur' }],
  temperature: [{ required: true, message: '请输入Temperature', trigger: 'blur' }]
}

// 加载配置列表
const loadConfigs = async() => {
  loading.value = true
  try {
    const response = await request({
      url: '/ai/llm-configs',
      method: 'get'
    })
    configs.value = response.data || response
  } catch (error) {
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

// 遮掩API Key显示
const maskApiKey = (key) => {
  if (!key || key.length < 10) {return '******'}
  return key.substring(0, 7) + '****' + key.substring(key.length - 4)
}

// 显示编辑对话框
const showEditDialog = (config) => {
  editingConfig.value = config
  configForm.value = { ...config }
  showDialog.value = true
}

// 提交表单
const handleSubmit = async() => {
  if (!configFormRef.value) {return}

  await configFormRef.value.validate(async(valid) => {
    if (!valid) {return}

    submitting.value = true
    try {
      if (editingConfig.value) {
        // 更新
        await request({
          url: `/ai/llm-configs/${editingConfig.value.id}`,
          method: 'put',
          data: configForm.value
        })
        ElMessage.success('配置更新成功')
      } else {
        // 创建
        await request({
          url: '/ai/llm-configs',
          method: 'post',
          data: configForm.value
        })
        ElMessage.success('配置创建成功')
      }

      showDialog.value = false
      loadConfigs()
    } catch (error) {
      ElMessage.error(editingConfig.value ? '更新配置失败' : '创建配置失败')
    } finally {
      submitting.value = false
    }
  })
}

// 激活配置
const activateConfig = async(configId) => {
  try {
    await request({
      url: `/ai/llm-configs/${configId}/activate`,
      method: 'post'
    })
    ElMessage.success('配置已激活')
    loadConfigs()
  } catch (error) {
    ElMessage.error('激活配置失败')
  }
}

// 删除配置
const deleteConfig = async(configId) => {
  try {
    await request({
      url: `/ai/llm-configs/${configId}`,
      method: 'delete'
    })
    ElMessage.success('配置已删除')
    loadConfigs()
  } catch (error) {
    ElMessage.error('删除配置失败')
  }
}

// 测试连接
const testConnection = async() => {
  testing.value = true
  try {
    const response = await request({
      url: '/ai/analyze/test',
      method: 'get'
    })

    const result = response.data || response

    if (result.status === 'success') {
      ElMessageBox.alert(
        `连接成功！\n\n配置: ${result.config_name}\n提供商: ${result.provider}\n模型: ${result.model}\n\nAI响应: ${result.response}`,
        '测试成功',
        { type: 'success' }
      )
    } else {
      ElMessageBox.alert(
        `连接失败：${result.error}`,
        '测试失败',
        { type: 'error' }
      )
    }
  } catch (error) {
    ElMessage.error('测试连接失败')
  } finally {
    testing.value = false
  }
}

// 监听新建对话框
const watchCreateDialog = () => {
  if (showCreateDialog.value) {
    editingConfig.value = null
    configForm.value = {
      name: '',
      provider: 'deepseek',
      api_key: '',
      api_base: '',
      model_name: 'deepseek-chat',
      max_tokens: 4000,
      temperature: '0.7',
      description: ''
    }
    showDialog.value = true
    showCreateDialog.value = false
  }
}

onMounted(() => {
  loadConfigs()
})

// 使用watch监听showCreateDialog
import { watch } from 'vue'
watch(showCreateDialog, watchCreateDialog)
</script>

<style scoped>
.llm-config-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
