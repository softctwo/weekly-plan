import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 全局记忆 Store
 * 用于存储用户的全局状态、历史操作、智能推荐等数据
 * 支持跨会话持久化和智能学习用户行为模式
 */
export const useMemoryStore = defineStore('memory', () => {
  // 存储配置
  const STORAGE_KEY = 'weekly_plan_memory'
  const MAX_HISTORY_ITEMS = 100 // 最大历史记录条数
  const MAX_MEMORY_SIZE = 1000 // 最大记忆项数量

  // === 核心记忆数据 ===
  
  // 用户历史操作记录
  const userHistory = ref([])
  
  // 用户偏好设置
  const userPreferences = ref({
    theme: 'light', // 主题偏好
    language: 'zh-cn', // 语言偏好
    defaultView: 'dashboard', // 默认视图
    notifications: {
      email: true, // 邮件通知
      push: true, // 推送通知
      sound: false // 声音提醒
    },
    autoSave: true, // 自动保存
    weekStart: 1, // 周开始日期 (0=周日, 1=周一)
    timeFormat: '24h' // 时间格式
  })
  
  // 智能推荐数据
  const recommendations = ref({
    frequentlyUsedTasks: [], // 常用任务推荐
    recentRoles: [], // 最近使用的角色
    suggestedDeadlines: {}, // 智能截止日期建议
    personalizedReminders: [] // 个性化提醒
  })
  
  // 用户行为模式分析
  const behaviorPatterns = ref({
    mostActiveHours: [], // 最活跃时间段
    commonTaskDurations: {}, // 任务平均耗时
    weeklyPatterns: {}, // 周度行为模式
    productivityScores: [] // 生产力评分
  })
  
  // 系统状态记忆
  const systemMemory = ref({
    lastLoginTime: null, // 上次登录时间
    sessionCount: 0, // 会话次数
    totalUsageTime: 0, // 总使用时间
    featureUsageStats: {}, // 功能使用统计
    lastViewedTasks: [], // 最后查看的任务
    unreadNotifications: 0 // 未读通知数
  })
  
  // 临时记忆（会话级别，不持久化）
  const tempMemory = ref({
    currentPage: null,
    currentTask: null,
    lastAction: null,
    breadcrumbs: [],
    formData: {},
    filters: {}
  })
  
  // === 计算属性 ===
  
  // 获取记忆统计信息
  const memoryStats = computed(() => {
    return {
      historyCount: userHistory.value.length,
      preferences: userPreferences.value,
      recommendationsCount: Object.values(recommendations.value).flat().length,
      patternsAnalyzed: Object.keys(behaviorPatterns.value).length,
      sessionInfo: systemMemory.value
    }
  })
  
  // 获取活跃时间模式
  const activeTimePattern = computed(() => {
    return behaviorPatterns.value.mostActiveHours.sort((a, b) => b.count - a.count)
  })
  
  // === 核心方法 ===
  
  /**
   * 初始化记忆系统
   */
  const initializeMemory = () => {
    console.log('[Memory] 初始化全局记忆系统')
    loadMemoryFromStorage()
    updateSystemMemory('session_start')
  }
  
  /**
   * 记录用户操作到历史
   * @param {string} action 操作类型
   * @param {any} data 操作数据
   * @param {string} page 页面来源
   */
  const recordHistory = (action, data = null, page = null) => {
    const historyItem = {
      id: Date.now(),
      action,
      data,
      page,
      timestamp: Date.now(),
      date: new Date().toISOString().split('T')[0]
    }
    
    // 添加到历史记录开头
    userHistory.value.unshift(historyItem)
    
    // 保持历史记录数量限制
    if (userHistory.value.length > MAX_HISTORY_ITEMS) {
      userHistory.value = userHistory.value.slice(0, MAX_HISTORY_ITEMS)
    }
    
    // 更新系统记忆
    systemMemory.value.lastAction = action
    
    // 分析行为模式
    analyzeBehaviorPattern(action, data)
    
    // 持久化
    saveMemoryToStorage()
  }
  
  /**
   * 更新用户偏好设置
   * @param {object} preferences 新的偏好设置
   */
  const updatePreferences = (preferences) => {
    userPreferences.value = { ...userPreferences.value, ...preferences }
    recordHistory('update_preferences', preferences)
    saveMemoryToStorage()
  }
  
  /**
   * 添加智能推荐
   * @param {string} type 推荐类型
   * @param {any} data 推荐数据
   */
  const addRecommendation = (type, data) => {
    if (!recommendations.value[type]) {
      recommendations.value[type] = []
    }
    
    // 避免重复推荐
    const exists = recommendations.value[type].some(item => 
      JSON.stringify(item) === JSON.stringify(data)
    )
    
    if (!exists) {
      recommendations.value[type].unshift({
        ...data,
        id: Date.now(),
        createdAt: new Date().toISOString(),
        score: calculateRecommendationScore(type, data)
      })
      
      // 保持推荐数量限制
      if (recommendations.value[type].length > 20) {
        recommendations.value[type] = recommendations.value[type].slice(0, 20)
      }
      
      recordHistory('add_recommendation', { type, data })
      saveMemoryToStorage()
    }
  }
  
  /**
   * 更新临时记忆
   * @param {object} tempData 临时数据
   */
  const updateTempMemory = (tempData) => {
    tempMemory.value = { ...tempMemory.value, ...tempData }
  }
  
  /**
   * 清除临时记忆
   */
  const clearTempMemory = () => {
    tempMemory.value = {
      currentPage: null,
      currentTask: null,
      lastAction: null,
      breadcrumbs: [],
      formData: {},
      filters: {}
    }
  }
  
  /**
   * 获取个性化推荐
   * @param {string} context 上下文类型 (task, role, time等)
   * @returns {array} 推荐列表
   */
  const getPersonalizedRecommendations = (context) => {
    const allRecommendations = []
    
    // 根据上下文获取相关推荐
    if (context === 'task') {
      allRecommendations.push(...recommendations.value.frequentlyUsedTasks)
    } else if (context === 'role') {
      allRecommendations.push(...recommendations.value.recentRoles)
    }
    
    // 按分数排序并返回前5条
    return allRecommendations
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
  }
  
  /**
   *
  /**
   * 获取历史操作记录
   * @param {number} limit 返回数量限制
   * @param {string} filterAction 过滤特定操作类型
   * @returns {array} 历史记录
   */
  const getHistoryRecords = (limit = 10, filterAction = null) => {
    let filteredHistory = userHistory.value
    
    if (filterAction) {
      filteredHistory = userHistory.value.filter(item => item.action === filterAction)
    }
    
    return filteredHistory.slice(0, limit)
  }
  
  /**
   * 分析用户行为模式
   * @param {string} action 用户操作
   * @param {any} data 操作数据
   */
  const analyzeBehaviorPattern = (action, data) => {
    const now = new Date()
    const hour = now.getHours()
    
    // 分析活跃时间
    let hourPattern = behaviorPatterns.value.mostActiveHours.find(h => h.hour === hour)
    if (!hourPattern) {
      hourPattern = { hour, count: 0 }
      behaviorPatterns.value.mostActiveHours.push(hourPattern)
    }
    hourPattern.count++
    
    // 分析任务操作模式
    if (action === 'create_task' || action === 'update_task') {
      analyzeTaskPattern(data)
    }
    
    // 分析页面访问模式
    if (action.includes('page_')) {
      analyzePagePattern(action, data)
    }
  }
  
  /**
   * 分析任务操作模式
   * @param {object} taskData 任务数据
   */
  const analyzeTaskPattern = (taskData) => {
    if (!taskData) return
    
    // 分析任务类型使用频率
    const taskType = taskData.type || taskData.taskType
    if (taskType) {
      if (!behaviorPatterns.value.commonTaskDurations[taskType]) {
        behaviorPatterns.value.commonTaskDurations[taskType] = {
          count: 0,
          totalDuration: 0,
          averageDuration: 0
        }
      }
      
      const stats = behaviorPatterns.value.commonTaskDurations[taskType]
      stats.count++
      
      // 如果有预估时间，记录用于计算平均值
      if (taskData.estimatedDuration) {
        stats.totalDuration += taskData.estimatedDuration
        stats.averageDuration = stats.totalDuration / stats.count
      }
    }
  }
  
  /**
   * 分析页面访问模式
   * @param {string} action 页面操作
   * @param {any} data 页面数据
   */
  const analyzePagePattern = (action, data) => {
    const pageName = action.replace('page_', '')
    
    if (!behaviorPatterns.value.weeklyPatterns[pageName]) {
      behaviorPatterns.value.weeklyPatterns[pageName] = {
        totalVisits: 0,
        dailyVisits: {},
        averageSessionTime: 0
      }
    }
    
    const pattern = behaviorPatterns.value.weeklyPatterns[pageName]
    pattern.totalVisits++
    
    const today = new Date().toISOString().split('T')[0]
    pattern.dailyVisits[today] = (pattern.dailyVisits[today] || 0) + 1
  }
  
  /**
   * 计算推荐分数
   * @param {string} type 推荐类型
   * @param {any} data 推荐数据
   * @returns {number} 推荐分数
   */
  const calculateRecommendationScore = (type, data) => {
    let score = 50 // 基础分数
    
    // 基于历史使用频率调整分数
    const historyCount = getHistoryRecords(50, `use_${type}`).length
    score += Math.min(historyCount * 5, 30)
    
    // 基于时间新鲜度调整分数
    const hoursAgo = (Date.now() - (data.createdAt || Date.now())) / (1000 * 60 * 60)
    if (hoursAgo < 24) {
      score += 20
    } else if (hoursAgo < 168) { // 一周内
      score += 10
    }
    
    return Math.min(score, 100)
  }
  
  /**
   * 更新系统记忆
   * @param {string} event 事件类型
   * @param {any} data 事件数据
   */
  const updateSystemMemory = (event, data = null) => {
    const now = Date.now()
    
    if (event === 'session_start') {
      systemMemory.value.sessionCount++
      systemMemory.value.lastLoginTime = now
    } else if (event === 'page_view') {
      if (data && data.pageName) {
        tempMemory.value.currentPage = data.pageName
      }
    } else if (event === 'task_view') {
      if (data && data.taskId) {
        systemMemory.value.lastViewedTasks.unshift(data.taskId)
        // 保持最近查看任务数量限制
        if (systemMemory.value.lastViewedTasks.length > 10) {
          systemMemory.value.lastViewedTasks = systemMemory.value.lastViewedTasks.slice(0, 10)
        }
      }
    }
    
    saveMemoryToStorage()
  }
  
  /**
   * 保存记忆数据到本地存储
   */
  const saveMemoryToStorage = () => {
    try {
      const memoryData = {
        userHistory: userHistory.value,
        userPreferences: userPreferences.value,
        recommendations: recommendations.value,
        behaviorPatterns: behaviorPatterns.value,
        systemMemory: systemMemory.value,
        lastSaved: Date.now()
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(memoryData))
      console.log('[Memory] 记忆数据已保存到本地存储')
    } catch (error) {
      console.error('[Memory] 保存记忆数据失败:', error)
    }
  }
  
  /**
   * 从本地存储加载记忆数据
   */
  const loadMemoryFromStorage = () => {
    try {
      const savedData = localStorage.getItem(STORAGE_KEY)
      if (savedData) {
        const memoryData = JSON.parse(savedData)
        
        // 加载各种记忆数据
        userHistory.value = memoryData.userHistory || []
        userPreferences.value = { ...userPreferences.value, ...memoryData.userPreferences }
        recommendations.value = { ...recommendations.value, ...memoryData.recommendations }
        behaviorPatterns.value = { ...behaviorPatterns.value, ...memoryData.behaviorPatterns }
        systemMemory.value = { ...systemMemory.value, ...memoryData.systemMemory }
        
        console.log('[Memory] 记忆数据已从本地存储加载')
      }
    } catch (error) {
      console.error('[Memory] 加载记忆数据失败:', error)
    }
  }
  
  /**
   * 清除所有记忆数据
   */
  const clearAllMemory = () => {
    userHistory.value = []
    recommendations.value = {
      frequentlyUsedTasks: [],
      recentRoles: [],
      suggestedDeadlines: {},
      personalizedReminders: []
    }
    behaviorPatterns.value =
    {
      mostActiveHours: [],
      commonTaskDurations: {},
      weeklyPatterns: {},
      productivityScores: []
    }
    systemMemory.value = {
      lastLoginTime: null,
      sessionCount: 0,
      totalUsageTime: 0,
      featureUsageStats: {},
      lastViewedTasks: [],
      unreadNotifications: 0
    }
    
    localStorage.removeItem(STORAGE_KEY)
    console.log('[Memory] 所有记忆数据已清除')
  }
  
  /**
   * 导出记忆数据（用于备份或迁移）
   * @returns {object} 记忆数据对象
   */
  const exportMemoryData = () => {
    return {
      userHistory: userHistory.value,
      userPreferences: userPreferences.value,
      recommendations: recommendations.value,
      behaviorPatterns: behaviorPatterns.value,
      systemMemory: systemMemory.value,
      exportTime: new Date().toISOString()
    }
  }
  
  /**
   * 导入记忆数据（用于恢复或迁移）
   * @param {object} memoryData 记忆数据对象
   */
  const importMemoryData = (memoryData) => {
    try {
      if (memoryData.userHistory) userHistory.value = memoryData.userHistory
      if (memoryData.userPreferences) userPreferences.value = memoryData.userPreferences
      if (memoryData.recommendations) recommendations.value = memoryData.recommendations
      if (memoryData.behaviorPatterns) behaviorPatterns.value = memoryData.behaviorPatterns
      if (memoryData.systemMemory) systemMemory.value = memoryData.systemMemory
      
      saveMemoryToStorage()
      console.log('[Memory] 记忆数据导入成功')
    } catch (error) {
      console.error('[Memory] 记忆数据导入失败:', error)
    }
  }
  
  /**
   * 获取智能分析报告
   * @returns {object} 分析报告
   */
  const getIntelligenceReport = () => {
    const now = new Date()
    const today = now.toISOString().split('T')[0]
    
    return {
      usageStats: {
        totalSessions: systemMemory.value.sessionCount,
        totalHistoryItems: userHistory.value.length,
        todayActivity: userHistory.value.filter(item => item.date === today).length
      },
      behaviorInsights: {
        mostActiveHour: behaviorPatterns.value.mostActiveHours.reduce((max, hour) => 
          hour.count > max.count ? hour : max, { hour: 0, count: 0 }),
        topTaskTypes: Object.entries(behaviorPatterns.value.commonTaskDurations)
          .sort(([,a], [,b]) => b.count - a.count)
          .slice(0, 5)
          .map(([type, stats]) => ({ type, count: stats.count })),
        mostVisitedPages: Object.entries(behaviorPatterns.value.weeklyPatterns)
          .sort(([,a], [,b]) => b.totalVisits - a.totalVisits)
          .slice(0, 5)
          .map(([page, stats]) => ({ page, visits: stats.totalVisits }))
      },
      recommendations: {
        totalCount: Object.values(recommendations.value).flat().length,
        byType: Object.fromEntries(
          Object.entries(recommendations.value).map(([key, value]) => [key, value.length])
        )
      },
      systemInfo: {
        lastLoginTime: systemMemory.value.lastLoginTime,
        storageSize: new Blob([localStorage.getItem(STORAGE_KEY) || '']).size
      }
    }
  }

  return {
    // 状态
    userHistory,
    userPreferences,
    recommendations,
    behaviorPatterns,
    systemMemory,
    tempMemory,
    
    // 计算属性
    memoryStats,
    activeTimePattern,
    
    // 核心方法
    initializeMemory,
    recordHistory,
    updatePreferences,
    addRecommendation,
    updateTempMemory,
    clearTempMemory,
    
    // 查询方法
    getPersonalizedRecommendations,
    getHistoryRecords,
    getIntelligenceReport,
    
    // 数据管理
    saveMemoryToStorage,
    loadMemoryFromStorage,
    clearAllMemory,
    exportMemoryData,
    importMemoryData,
    
    // 系统更新
    updateSystemMemory
  }
})
