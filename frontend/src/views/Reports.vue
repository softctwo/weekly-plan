<template>
  <div class="reports-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据统计报表</span>
          <el-space>
            <el-dropdown @command="handleExportCommand">
              <el-button type="success" :icon="Download">
                导出报表<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="excel">
                    <el-icon><Document /></el-icon>
                    导出为 Excel
                  </el-dropdown-item>
                  <el-dropdown-item command="pdf">
                    <el-icon><Document /></el-icon>
                    导出为 PDF
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="primary" :icon="Refresh" @click="loadReportData">
              刷新数据
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 时间范围选择 -->
      <el-row :gutter="20" style="margin-bottom: 20px">
        <el-col :span="8">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-col>
        <el-col :span="4">
          <el-button @click="setLastWeek">最近一周</el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="setLastMonth">最近一月</el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="setLastQuarter">最近一季</el-button>
        </el-col>
      </el-row>

      <!-- 核心指标卡片 -->
      <el-row :gutter="20" style="margin-bottom: 30px">
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon tasks">
              <el-icon :size="40"><List /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ reportData.total_tasks }}</div>
              <div class="metric-label">总任务数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon completed">
              <el-icon :size="40"><CircleCheck /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ reportData.completed_tasks }}</div>
              <div class="metric-label">已完成</div>
              <div class="metric-trend">
                {{ reportData.completion_rate }}% 完成率
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon key">
              <el-icon :size="40"><StarFilled /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ reportData.key_tasks }}</div>
              <div class="metric-label">重点任务</div>
              <div class="metric-trend">
                {{ reportData.key_completion_rate }}% 完成率
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-icon delayed">
              <el-icon :size="40"><Warning /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ reportData.delayed_tasks }}</div>
              <div class="metric-label">延期任务</div>
              <div class="metric-trend">
                {{ reportData.delay_rate }}% 延期率
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 状态分布和趋势图表 (ECharts) -->
      <el-row :gutter="20" style="margin-bottom: 30px">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>任务状态分布</span>
            </template>
            <div class="echarts-container">
              <v-chart :option="statusChartOption" autoresize />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>周任务完成趋势</span>
            </template>
            <div class="echarts-container">
              <v-chart :option="trendChartOption" autoresize />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 岗位职责分析 -->
      <el-row :gutter="20" style="margin-bottom: 30px" v-if="userStore.isManager">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <span>团队成员绩效统计</span>
            </template>
            <el-table :data="memberPerformance" stripe>
              <el-table-column prop="member_name" label="成员姓名" width="150" />
              <el-table-column prop="total_tasks" label="总任务" width="100" align="center" />
              <el-table-column prop="completed_tasks" label="已完成" width="100" align="center" />
              <el-table-column prop="key_tasks" label="重点任务" width="100" align="center" />
              <el-table-column label="完成率" width="150" align="center">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.completion_rate"
                    :color="getProgressColor(row.completion_rate)"
                    :stroke-width="12"
                  />
                </template>
              </el-table-column>
              <el-table-column label="平均任务周期" width="150" align="center">
                <template #default="{ row }">
                  {{ row.avg_completion_days }} 天
                </template>
              </el-table-column>
              <el-table-column prop="reviewed_weeks" label="已复盘周数" width="120" align="center" />
              <el-table-column label="绩效评分" width="120" align="center">
                <template #default="{ row }">
                  <el-rate
                    :model-value="row.performance_score"
                    disabled
                    show-score
                    score-template="{value}"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 职责类型统计 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <span>任务类型分布统计</span>
            </template>
            <el-table :data="taskTypeStats" stripe max-height="400">
              <el-table-column prop="task_type" label="任务类型" width="200" />
              <el-table-column prop="responsibility" label="所属职责" width="200" />
              <el-table-column prop="count" label="任务数量" width="120" align="center" />
              <el-table-column label="完成情况" min-width="300">
                <template #default="{ row }">
                  <el-space direction="vertical" :size="0" style="width: 100%">
                    <div style="display: flex; justify-content: space-between">
                      <span>已完成: {{ row.completed }}</span>
                      <span>进行中: {{ row.in_progress }}</span>
                      <span>待办: {{ row.todo }}</span>
                    </div>
                    <el-progress
                      :percentage="row.completion_rate"
                      :stroke-width="10"
                      :color="getProgressColor(row.completion_rate)"
                    />
                  </el-space>
                </template>
              </el-table-column>
              <el-table-column label="平均用时" width="120" align="center">
                <template #default="{ row }">
                  {{ row.avg_days }} 天
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  List,
  CircleCheck,
  StarFilled,
  Warning,
  Download,
  Refresh,
  ArrowDown,
  Document
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import request from '@/api/request'
import * as XLSX from 'xlsx'
import dayjs from 'dayjs'
import jsPDF from 'jspdf'
import 'jspdf-autotable'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const userStore = useUserStore()

const loading = ref(false)
const dateRange = ref([])

// 报表数据
const reportData = ref({
  total_tasks: 0,
  completed_tasks: 0,
  key_tasks: 0,
  delayed_tasks: 0,
  completion_rate: 0,
  key_completion_rate: 0,
  delay_rate: 0
})

const statusDistribution = ref([])
const weeklyTrend = ref([])
const memberPerformance = ref([])
const taskTypeStats = ref([])

// ECharts 图表配置
const statusChartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '任务状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{c} ({d}%)'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      data: statusDistribution.value.map(item => ({
        value: item.count,
        name: item.label,
        itemStyle: { color: item.color }
      }))
    }
  ]
}))

const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: weeklyTrend.value.map(w => `第${w.week}周`),
    axisLabel: {
      rotate: 30
    }
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: '完成率',
      type: 'bar',
      data: weeklyTrend.value.map(w => ({
        value: w.rate,
        itemStyle: {
          color: getTrendColor(w.rate)
        }
      })),
      label: {
        show: true,
        position: 'top',
        formatter: '{c}%'
      },
      barWidth: '60%'
    }
  ]
}))

// 设置默认日期范围（最近一月）
onMounted(() => {
  setLastMonth()
})

// 快捷日期范围设置
const setLastWeek = () => {
  const end = dayjs()
  const start = end.subtract(7, 'day')
  dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
  loadReportData()
}

const setLastMonth = () => {
  const end = dayjs()
  const start = end.subtract(30, 'day')
  dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
  loadReportData()
}

const setLastQuarter = () => {
  const end = dayjs()
  const start = end.subtract(90, 'day')
  dateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]
  loadReportData()
}

const handleDateChange = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    loadReportData()
  }
}

// 加载报表数据
const loadReportData = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    }

    // 获取基础统计数据
    const data = await request({
      url: '/dashboard/reports',
      method: 'get',
      params
    })

    reportData.value = data.summary || {}

    // 状态分布
    statusDistribution.value = [
      {
        name: 'completed',
        label: '已完成',
        count: data.status_distribution?.completed || 0,
        percentage: calculatePercentage(data.status_distribution?.completed, data.summary?.total_tasks),
        color: '#67c23a'
      },
      {
        name: 'in_progress',
        label: '进行中',
        count: data.status_distribution?.in_progress || 0,
        percentage: calculatePercentage(data.status_distribution?.in_progress, data.summary?.total_tasks),
        color: '#e6a23c'
      },
      {
        name: 'todo',
        label: '待办',
        count: data.status_distribution?.todo || 0,
        percentage: calculatePercentage(data.status_distribution?.todo, data.summary?.total_tasks),
        color: '#909399'
      },
      {
        name: 'delayed',
        label: '已延期',
        count: data.status_distribution?.delayed || 0,
        percentage: calculatePercentage(data.status_distribution?.delayed, data.summary?.total_tasks),
        color: '#f56c6c'
      }
    ]

    // 周趋势
    weeklyTrend.value = data.weekly_trend || []

    // 团队成员绩效（仅管理者）
    if (userStore.isManager && data.member_performance) {
      memberPerformance.value = data.member_performance
    }

    // 任务类型统计
    taskTypeStats.value = data.task_type_stats || []
  } catch (error) {
    ElMessage.error('加载报表数据失败')
    console.error('加载报表失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算百分比
const calculatePercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

// 获取进度条颜色
const getProgressColor = (percentage) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

// 获取趋势条颜色
const getTrendColor = (rate) => {
  if (rate >= 80) return '#67c23a'
  if (rate >= 60) return '#95de64'
  if (rate >= 40) return '#e6a23c'
  return '#f56c6c'
}

// 处理导出命令
const handleExportCommand = (command) => {
  if (command === 'excel') {
    exportExcelReport()
  } else if (command === 'pdf') {
    exportPDFReport()
  }
}

// 导出 Excel 报表
const exportExcelReport = () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请先选择日期范围并加载数据')
    return
  }

  try {
    // 创建工作簿
    const wb = XLSX.utils.book_new()

    // 概要数据
    const summaryData = [
      ['数据统计报表'],
      ['统计周期', `${dateRange.value[0]} 至 ${dateRange.value[1]}`],
      [],
      ['核心指标', '数值'],
      ['总任务数', reportData.value.total_tasks],
      ['已完成任务', reportData.value.completed_tasks],
      ['重点任务', reportData.value.key_tasks],
      ['延期任务', reportData.value.delayed_tasks],
      ['完成率', `${reportData.value.completion_rate}%`],
      ['重点任务完成率', `${reportData.value.key_completion_rate}%`],
      ['延期率', `${reportData.value.delay_rate}%`]
    ]

    const summaryWs = XLSX.utils.aoa_to_sheet(summaryData)
    XLSX.utils.book_append_sheet(wb, summaryWs, '数据概要')

    // 任务类型统计
    if (taskTypeStats.value.length > 0) {
      const taskTypeData = taskTypeStats.value.map(item => ({
        '任务类型': item.task_type,
        '所属职责': item.responsibility,
        '任务数量': item.count,
        '已完成': item.completed,
        '进行中': item.in_progress,
        '待办': item.todo,
        '完成率': `${item.completion_rate}%`,
        '平均用时（天）': item.avg_days
      }))

      const taskTypeWs = XLSX.utils.json_to_sheet(taskTypeData)
      XLSX.utils.book_append_sheet(wb, taskTypeWs, '任务类型统计')
    }

    // 团队绩效（仅管理者）
    if (userStore.isManager && memberPerformance.value.length > 0) {
      const performanceData = memberPerformance.value.map(item => ({
        '成员姓名': item.member_name,
        '总任务': item.total_tasks,
        '已完成': item.completed_tasks,
        '重点任务': item.key_tasks,
        '完成率': `${item.completion_rate}%`,
        '平均任务周期（天）': item.avg_completion_days,
        '已复盘周数': item.reviewed_weeks,
        '绩效评分': item.performance_score
      }))

      const performanceWs = XLSX.utils.json_to_sheet(performanceData)
      XLSX.utils.book_append_sheet(wb, performanceWs, '团队绩效')
    }

    // 导出文件
    const filename = `工作报表_${dateRange.value[0]}_${dateRange.value[1]}.xlsx`
    XLSX.writeFile(wb, filename)

    ElMessage.success('Excel 报表导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出报表失败')
  }
}

// 导出 PDF 报表
const exportPDFReport = () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请先选择日期范围并加载数据')
    return
  }

  try {
    // 创建 PDF 文档
    const doc = new jsPDF()

    // 添加中文字体支持 (使用内置字体)
    doc.setFont('helvetica')

    let yPos = 20

    // 标题
    doc.setFontSize(20)
    doc.text('Work Report', 105, yPos, { align: 'center' })
    yPos += 15

    // 统计周期
    doc.setFontSize(12)
    doc.text(`Period: ${dateRange.value[0]} to ${dateRange.value[1]}`, 20, yPos)
    yPos += 15

    // 核心指标表格
    doc.autoTable({
      startY: yPos,
      head: [['Metric', 'Value']],
      body: [
        ['Total Tasks', reportData.value.total_tasks],
        ['Completed Tasks', reportData.value.completed_tasks],
        ['Key Tasks', reportData.value.key_tasks],
        ['Delayed Tasks', reportData.value.delayed_tasks],
        ['Completion Rate', `${reportData.value.completion_rate}%`],
        ['Key Task Completion Rate', `${reportData.value.key_completion_rate}%`],
        ['Delay Rate', `${reportData.value.delay_rate}%`]
      ],
      theme: 'grid',
      headStyles: { fillColor: [67, 97, 238] }
    })

    yPos = doc.lastAutoTable.finalY + 15

    // 任务状态分布
    if (statusDistribution.value.length > 0) {
      doc.setFontSize(14)
      doc.text('Task Status Distribution', 20, yPos)
      yPos += 10

      doc.autoTable({
        startY: yPos,
        head: [['Status', 'Count', 'Percentage']],
        body: statusDistribution.value.map(item => [
          item.label,
          item.count,
          `${item.percentage}%`
        ]),
        theme: 'striped',
        headStyles: { fillColor: [67, 97, 238] }
      })

      yPos = doc.lastAutoTable.finalY + 15
    }

    // 任务类型统计
    if (taskTypeStats.value.length > 0) {
      // 检查是否需要新页面
      if (yPos > 250) {
        doc.addPage()
        yPos = 20
      }

      doc.setFontSize(14)
      doc.text('Task Type Statistics', 20, yPos)
      yPos += 10

      doc.autoTable({
        startY: yPos,
        head: [['Task Type', 'Count', 'Completed', 'In Progress', 'Todo', 'Completion Rate']],
        body: taskTypeStats.value.map(item => [
          item.task_type,
          item.count,
          item.completed,
          item.in_progress,
          item.todo,
          `${item.completion_rate}%`
        ]),
        theme: 'striped',
        headStyles: { fillColor: [67, 97, 238] },
        styles: { fontSize: 8 }
      })

      yPos = doc.lastAutoTable.finalY + 15
    }

    // 团队绩效（仅管理者）
    if (userStore.isManager && memberPerformance.value.length > 0) {
      // 添加新页面
      doc.addPage()
      yPos = 20

      doc.setFontSize(14)
      doc.text('Team Performance', 20, yPos)
      yPos += 10

      doc.autoTable({
        startY: yPos,
        head: [['Member', 'Total', 'Completed', 'Key Tasks', 'Completion Rate', 'Avg Days']],
        body: memberPerformance.value.map(item => [
          item.member_name,
          item.total_tasks,
          item.completed_tasks,
          item.key_tasks,
          `${item.completion_rate}%`,
          item.avg_completion_days
        ]),
        theme: 'striped',
        headStyles: { fillColor: [67, 97, 238] }
      })
    }

    // 保存 PDF
    const filename = `Work_Report_${dateRange.value[0]}_${dateRange.value[1]}.pdf`
    doc.save(filename)

    ElMessage.success('PDF report exported successfully')
  } catch (error) {
    console.error('PDF export failed:', error)
    ElMessage.error('Failed to export PDF report')
  }
}
</script>

<style scoped>
.reports-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  gap: 20px;
}

.metric-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.metric-icon.tasks {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metric-icon.completed {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.metric-icon.key {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.metric-icon.delayed {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.metric-trend {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.chart-container {
  padding: 10px 0;
}

.echarts-container {
  height: 300px;
  width: 100%;
}

.status-bar {
  margin-bottom: 20px;
}

.status-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.status-count {
  color: #909399;
}

.trend-item {
  margin-bottom: 20px;
}

.trend-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.trend-date {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.trend-bar-wrapper {
  background-color: #f5f7fa;
  border-radius: 4px;
  height: 28px;
  overflow: hidden;
}

.trend-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  transition: width 0.3s;
  min-width: 50px;
}

.trend-text {
  color: #fff;
  font-size: 13px;
  font-weight: 500;
}
</style>
