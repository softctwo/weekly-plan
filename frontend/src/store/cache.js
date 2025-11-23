import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 数据缓存 Store
 * 用于缓存频繁访问的数据，减少API请求
 */
export const useCacheStore = defineStore('cache', () => {
  // 缓存配置
  const CACHE_TTL = 5 * 60 * 1000 // 5分钟过期

  // 用户角色和职责缓存
  const rolesCache = ref({
    data: null,
    timestamp: null
  })

  // 团队成员缓存（管理者使用）
  const teamMembersCache = ref({
    data: null,
    timestamp: null
  })

  // 任务列表缓存（按周缓存）
  const tasksCache = ref({})

  // 仪表盘数据缓存
  const dashboardCache = ref({
    data: null,
    timestamp: null
  })

  /**
   * 检查缓存是否有效
   * @param {number} timestamp 缓存时间戳
   * @returns {boolean}
   */
  const isCacheValid = (timestamp) => {
    if (!timestamp) {return false}
    return Date.now() - timestamp < CACHE_TTL
  }

  /**
   * 获取或设置角色缓存
   * @param {Function} fetchFn 获取数据的函数
   * @returns {Promise<any>}
   */
  const getRolesCache = async(fetchFn) => {
    if (isCacheValid(rolesCache.value.timestamp) && rolesCache.value.data) {
      console.log('[Cache] Using cached roles data')
      return rolesCache.value.data
    }

    console.log('[Cache] Fetching fresh roles data')
    const data = await fetchFn()
    rolesCache.value = {
      data,
      timestamp: Date.now()
    }
    return data
  }

  /**
   * 获取或设置团队成员缓存
   * @param {Function} fetchFn 获取数据的函数
   * @returns {Promise<any>}
   */
  const getTeamMembersCache = async(fetchFn) => {
    if (isCacheValid(teamMembersCache.value.timestamp) && teamMembersCache.value.data) {
      console.log('[Cache] Using cached team members data')
      return teamMembersCache.value.data
    }

    console.log('[Cache] Fetching fresh team members data')
    const data = await fetchFn()
    teamMembersCache.value = {
      data,
      timestamp: Date.now()
    }
    return data
  }

  /**
   * 获取或设置任务列表缓存
   * @param {string} key 缓存键（通常是 week_year 组合）
   * @param {Function} fetchFn 获取数据的函数
   * @returns {Promise<any>}
   */
  const getTasksCache = async(key, fetchFn) => {
    const cache = tasksCache.value[key]
    if (cache && isCacheValid(cache.timestamp)) {
      console.log(`[Cache] Using cached tasks data for ${key}`)
      return cache.data
    }

    console.log(`[Cache] Fetching fresh tasks data for ${key}`)
    const data = await fetchFn()
    tasksCache.value[key] = {
      data,
      timestamp: Date.now()
    }
    return data
  }

  /**
   * 获取或设置仪表盘缓存
   * @param {Function} fetchFn 获取数据的函数
   * @returns {Promise<any>}
   */
  const getDashboardCache = async(fetchFn) => {
    if (isCacheValid(dashboardCache.value.timestamp) && dashboardCache.value.data) {
      console.log('[Cache] Using cached dashboard data')
      return dashboardCache.value.data
    }

    console.log('[Cache] Fetching fresh dashboard data')
    const data = await fetchFn()
    dashboardCache.value = {
      data,
      timestamp: Date.now()
    }
    return data
  }

  /**
   * 使角色缓存失效（当用户角色变更时调用）
   */
  const invalidateRoles = () => {
    console.log('[Cache] Invalidating roles cache')
    rolesCache.value = {
      data: null,
      timestamp: null
    }
  }

  /**
   * 使团队成员缓存失效
   */
  const invalidateTeamMembers = () => {
    console.log('[Cache] Invalidating team members cache')
    teamMembersCache.value = {
      data: null,
      timestamp: null
    }
  }

  /**
   * 使任务缓存失效
   * @param {string} key 缓存键，不传则清空所有任务缓存
   */
  const invalidateTasks = (key = null) => {
    if (key) {
      console.log(`[Cache] Invalidating tasks cache for ${key}`)
      delete tasksCache.value[key]
    } else {
      console.log('[Cache] Invalidating all tasks cache')
      tasksCache.value = {}
    }
  }

  /**
   * 使仪表盘缓存失效
   */
  const invalidateDashboard = () => {
    console.log('[Cache] Invalidating dashboard cache')
    dashboardCache.value = {
      data: null,
      timestamp: null
    }
  }

  /**
   * 清空所有缓存
   */
  const clearAllCache = () => {
    console.log('[Cache] Clearing all cache')
    rolesCache.value = { data: null, timestamp: null }
    teamMembersCache.value = { data: null, timestamp: null }
    tasksCache.value = {}
    dashboardCache.value = { data: null, timestamp: null }
  }

  /**
   * 获取缓存统计信息
   */
  const getCacheStats = () => {
    return {
      roles: {
        cached: isCacheValid(rolesCache.value.timestamp),
        timestamp: rolesCache.value.timestamp
      },
      teamMembers: {
        cached: isCacheValid(teamMembersCache.value.timestamp),
        timestamp: teamMembersCache.value.timestamp
      },
      tasks: {
        count: Object.keys(tasksCache.value).length,
        keys: Object.keys(tasksCache.value)
      },
      dashboard: {
        cached: isCacheValid(dashboardCache.value.timestamp),
        timestamp: dashboardCache.value.timestamp
      }
    }
  }

  return {
    // Getters
    getRolesCache,
    getTeamMembersCache,
    getTasksCache,
    getDashboardCache,

    // Invalidators
    invalidateRoles,
    invalidateTeamMembers,
    invalidateTasks,
    invalidateDashboard,
    clearAllCache,

    // Utils
    getCacheStats
  }
})
