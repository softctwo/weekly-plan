<template>
  <el-dialog
    v-model="visible"
    title="AI工作分析"
    width="900px"
    :close-on-click-modal="false"
  >
    <!-- 分析参数 -->
    <el-form :model="analysisForm" label-width="100px" v-if="!analyzing && !result">
      <el-form-item label="分析对象">
        <el-select
          v-model="analysisForm.user_id"
          placeholder="选择员工（不选择则分析团队）"
          clearable
          filterable
        >
          <el-option
            v-for="user in teamMembers"
            :key="user.id"
            :label="user.full_name"
            :value="user.id"
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
          <el-radio label="comprehensive">全面分析</el-radio>
          <el-radio label="performance">绩效分析</el-radio>
          <el-radio label="improvement">改进建议</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <!-- 分析中 -->
    <div v-if="analyzing" class="analyzing-container">
      <el-icon class="is-loading" :size="50"><Loading /></el-icon>
      <p class="analyzing-text">AI正在分析中，请稍候...</p>
      <p class="analyzing-tip">这可能需要10-30秒</p>
    </div>

    <!-- 分析结果 -->
    <div v-if="result && !analyzing" class="result-container">
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
      <el-card shadow="never" style="margin-bottom: 20px" v-if="result.statistics">
        <template #header>
          <span style="font-weight: 600">数据统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总任务数" :value="result.statistics.total_tasks" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="已完成" :value="result.statistics.completed_tasks">
              <template #suffix>
                <span style="font-size: 14px; color: #67c23a">
                  ({{ result.statistics.completion_rate }}%)
                </span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="重点任务" :value="result.statistics.key_tasks">
              <template #suffix>
                <span style="font-size: 14px; color: #e6a23c">
                  ({{ result.statistics.key_completion_rate }}%)
                </span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="延期任务" :value="result.statistics.delayed_tasks">
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
            <el-button size="small" :icon="CopyDocument" @click="copyResult">
              复制报告
            </el-button>
          </div>
        </template>
        <div class="markdown-body" v-html="renderedMarkdown"></div>
      </el-card>
    </div>

    <template #footer>
      <el-button @click="handleClose">{{ result ? '关闭' : '取消' }}</el-button>
      <el-button
        v-if="!analyzing && !result"
        type="primary"
        @click="startAnalysis"
        :loading="analyzing"
      >
        开始分析
      </el-button>
      <el-button v-if="result" type="warning" @click="resetAnalysis">
        重新分析
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, CopyDocument } from '@element-plus/icons-vue'
import request from '@/api/request'
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

// Markdown渲染
const renderedMarkdown = computed(() => {
  if (!result.value?.analysis_result) return ''
  return marked(result.value.analysis_result)
})

// 开始分析
const startAnalysis = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择分析周期')
    return
  }

  analyzing.value = true
  try {
    const response = await request({
      url: '/ai/analyze',
      method: 'post',
      data: {
        user_id: analysisForm.value.user_id || null,
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        analysis_type: analysisForm.value.analysis_type
      }
    })

    result.value = response.data || response
    ElMessage.success('分析完成')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '分析失败')
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
  if (!result.value?.analysis_result) return

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
  if (!val) {
    resetAnalysis()
  }
})
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
