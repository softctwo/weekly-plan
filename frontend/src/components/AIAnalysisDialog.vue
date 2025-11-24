<template>
  <el-dialog
    v-model="visible"
    title="AI工作分析"
    width="900px"
    :close-on-click-modal="false"
  >
    <!-- 分析参数 -->
    <el-form
      v-if="!analyzing && !result"
      :model="analysisForm"
      label-width="100px"
    >
      <el-form-item label="分析对象">
        <el-select
          v-model="analysisForm.user_id"
          placeholder="选择员工（不选择则分析团队）"
          clearable
          filterable
        >
          <el-option
            v-for="user in teamMembers"
            :key="user.user_id || user.id"
            :label="user.user_name || user.full_name"
            :value="user.user_id || user.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="分析周期">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="分析类型">
        <el-radio-group v-model="analysisForm.analysis_type">
          <el-radio label="comprehensive">
            全面分析
          </el-radio>
          <el-radio label="performance">
            绩效分析
          </el-radio>
          <el-radio label="improvement">
            改进建议
          </el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <!-- 分析中 -->
    <div
      v-if="analyzing"
      class="analyzing-container"
    >
      <el-icon
        class="is-loading"
        :size="50"
      >
        <Loading />
      </el-icon>
      <p class="analyzing-text">
        AI正在分析中，请稍候...
      </p>
      <p class="analyzing-tip">
        这可能需要10-30秒
      </p>
    </div>

    <!-- 分析结果 -->
    <div
      v-if="result && !analyzing"
      class="result-container"
    >
      <el-alert
        :title="`分析对象：${result.user_name || '团队全体'}`"
        type="success"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <div style="margin-top: 10px">
            <strong>分析周期：</strong>{{ result.analysis_period }}
          </div>
        </template>
      </el-alert>

      <!-- 统计数据 -->
      <el-card
        v-if="result.statistics"
        shadow="never"
        style="margin-bottom: 20px"
      >
        <template #header>
          <span style="font-weight: 600">数据统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic
              title="总任务数"
              :value="result.statistics.total_tasks"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="已完成"
              :value="result.statistics.completed_tasks"
            >
              <template #suffix>
                <span style="font-size: 14px; color: #67c23a">
                  ({{ result.statistics.completion_rate }}%)
                </span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="重点任务"
              :value="result.statistics.key_tasks"
            >
              <template #suffix>
                <span style="font-size: 14px; color: #e6a23c">
                  ({{ result.statistics.key_completion_rate }}%)
                </span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic
              title="延期任务"
              :value="result.statistics.delayed_tasks"
            >
              <template #suffix>
                <span style="font-size: 14px; color: #f56c6c">
                  ({{ result.statistics.delay_rate }}%)
                </span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </el-card>

      <!-- AI分析结果 -->
      <el-card shadow="never">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center">
            <span style="font-weight: 600">AI分析报告</span>
            <el-button
              size="small"
              :icon="CopyDocument"
              @click="copyResult"
            >
              复制报告
            </el-button>
          </div>
        </template>
        <div
          class="markdown-body"
          v-html="renderedMarkdown"
        />
      </el-card>
    </div>

    <template #footer>
      <el-button @click="handleClose">
        {{ result ? '关闭' : '取消' }}
      </el-button>
      <el-button
        v-if="!analyzing && !result"
        type="primary"
        :loading="analyzing"
        @click="startAnalysis"
      >
        开始分析
      </el-button>
      <el-button
        v-if="result"
        type="warning"
        @click="resetAnalysis"
      >
        重新分析
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, CopyDocument } from '@element-plus/icons-vue'
import { analyzeWork } from '@/api/ai'
import dayjs from 'dayjs'
import { marked } from 'marked'

const props = defineProps({
  modelValue: Boolean,
  teamMembers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const analyzing = ref(false)
const result = ref(null)

const analysisForm = ref({
  user_id: null,
  analysis_type: 'comprehensive'
})

const dateRange = ref([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])

// 验证团队数据
const validateTeamMembers = () => {
  if (!props.teamMembers || props.teamMembers.length === 0) {
    console.warn('团队数据为空或格式不正确')
    return false
  }

  // 验证数据结构 - 支持两种格式：团队仪表盘格式和用户列表格式
  const requiredFields = ['user_id', 'user_name']
  const alternativeFields = ['id', 'full_name']
  const firstMember = props.teamMembers[0]

  // 检查是否有至少一种必要的数据结构
  const hasPrimaryFields = requiredFields.every(field => firstMember.hasOwnProperty(field))
  const hasAlternativeFields = alternativeFields.every(field => firstMember.hasOwnProperty(field))

  if (!hasPrimaryFields && !hasAlternativeFields) {
    console.error('团队成员数据缺少必要字段')
    console.error('可用字段:', Object.keys(firstMember))
    return false
  }

  console.log('✅ 团队成员数据验证通过')
  return true
}

// Markdown渲染
const renderedMarkdown = computed(() => {
  if (!result.value?.analysis_result) {return ''}
  return marked(result.value.analysis_result)
})

// 开始分析
const startAnalysis = async() => {
  // 增强的参数验证
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择分析周期')
    return
  }

  // 验证日期格式
  const startDate = dayjs(dateRange.value[0])
  const endDate = dayjs(dateRange.value[1])
  
  if (!startDate.isValid() || !endDate.isValid()) {
    ElMessage.warning('日期格式无效')
    return
  }
  
  if (startDate.isAfter(endDate)) {
    ElMessage.warning('开始日期不能晚于结束日期')
    return
  }

  analyzing.value = true
  try {
    console.log('开始AI分析，请求参数:', {
      user_id: analysisForm.value.user_id,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      analysis_type: analysisForm.value.analysis_type
    })

    const response = await analyzeWork({
      user_id: analysisForm.value.user_id || null,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      analysis_type: analysisForm.value.analysis_type
    })

    console.log('AI分析响应:', response)
    
    // 增强的数据验证
    if (!response) {
      throw new Error('响应数据为空')
    }
    
    result.value = response.data || response
    ElMessage.success('分析完成')
  } catch (error) {
    console.error('AI分析错误详情:', error)
    
    // 增强的错误处理
    let errorMessage = '分析失败'
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.response?.status === 422) {
      errorMessage = '请求参数错误，请检查输入'
    } else if (error.response?.status === 500) {
      errorMessage = 'AI服务内部错误，请联系管理员'
    } else if (error.response?.status === 503) {
      errorMessage = 'AI服务暂不可用，请稍后重试'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  } finally {
    analyzing.value = false
  }
}

// 重置分析
const resetAnalysis = () => {
  result.value = null
  analysisForm.value = {
    user_id: null,
    analysis_type: 'comprehensive'
  }
}

// 关闭对话框
const handleClose = () => {
  if (!analyzing.value) {
    resetAnalysis()
    visible.value = false
  }
}

// 复制结果
const copyResult = () => {
  if (!result.value?.analysis_result) {return}

  const text = `# AI工作分析报告

**分析对象：**${result.value.user_name || '团队全体'}
**分析周期：**${result.value.analysis_period}

## 数据统计
- 总任务数：${result.value.statistics.total_tasks}
- 已完成：${result.value.statistics.completed_tasks} (${result.value.statistics.completion_rate}%)
- 重点任务：${result.value.statistics.key_tasks} (${result.value.statistics.key_completion_rate}%)
- 延期任务：${result.value.statistics.delayed_tasks} (${result.value.statistics.delay_rate}%)

---

${result.value.analysis_result}
`

  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('报告已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 监听对话框打开/关闭
watch(visible, (val) => {
  if (val) {
    // 对话框打开时验证数据
    console.log('AI分析对话框打开，团队数据:', props.teamMembers)
    validateTeamMembers()
  } else {
    resetAnalysis()
  }
})

// 监听团队数据变化
watch(() => props.teamMembers, (newMembers) => {
  console.log('团队数据更新:', newMembers)
  if (newMembers && newMembers.length > 0) {
    validateTeamMembers()
  }
}, { immediate: true })
</script>

<style scoped>
.analyzing-container {
  text-align: center;
  padding: 60px 0;
}

.analyzing-text {
  font-size: 18px;
  font-weight: 500;
  color: #409eff;
  margin-top: 20px;
}

.analyzing-tip {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.result-container {
  max-height: 600px;
  overflow-y: auto;
}

.markdown-body {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body :deep(h3) {
  font-size: 1.25em;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body :deep(li) {
  margin-top: 0.25em;
}

.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #e6a23c;
}

.markdown-body :deep(code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-body :deep(blockquote) {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin-left: 0;
  margin-right: 0;
}
</style>
