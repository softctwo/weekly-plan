import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import dayjs from 'dayjs'

/**
 * 通知提醒 Store
 * 管理系统通知和提醒
 */
export const useNotificationStore = defineStore('notification', () => {
  // 通知列表
  const notifications = ref([])

  // 未读通知数量
  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.read).length
  })

  /**
   * 通知类型枚举
   */
  const NotificationType = {
    TASK_DUE: 'task_due',           // 任务即将到期
    TASK_DELAYED: 'task_delayed',   // 任务已延期
    REVIEW_PENDING: 'review_pending', // 待复盘
    TEAM_REVIEW: 'team_review',     // 团队待审阅
    COMMENT_REPLY: 'comment_reply', // 评论回复
    SYSTEM: 'system'                // 系统通知
  }

  /**
   * 通知优先级
   */
  const NotificationPriority = {
    LOW: 'low',
    NORMAL: 'normal',
    HIGH: 'high',
    URGENT: 'urgent'
  }

  /**
   * 添加通知
   * @param {Object} notification - 通知对象
   */
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now() + Math.random(),
      type: notification.type || NotificationType.SYSTEM,
      priority: notification.priority || NotificationPriority.NORMAL,
      title: notification.title,
      message: notification.message,
      data: notification.data || {},
      read: false,
      createdAt: new Date().toISOString(),
      ...notification
    }

    notifications.value.unshift(newNotification)

    // 限制通知数量，最多保留100条
    if (notifications.value.length > 100) {
      notifications.value = notifications.value.slice(0, 100)
    }

    return newNotification
  }

  /**
   * 标记通知为已读
   * @param {number} notificationId - 通知ID
   */
  const markAsRead = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  /**
   * 标记所有通知为已读
   */
  const markAllAsRead = () => {
    notifications.value.forEach(n => {
      n.read = true
    })
  }

  /**
   * 删除通知
   * @param {number} notificationId - 通知ID
   */
  const removeNotification = (notificationId) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * 清空所有通知
   */
  const clearAll = () => {
    notifications.value = []
  }

  /**
   * 清空已读通知
   */
  const clearRead = () => {
    notifications.value = notifications.value.filter(n => !n.read)
  }

  /**
   * 获取通知图标
   * @param {string} type - 通知类型
   */
  const getNotificationIcon = (type) => {
    const iconMap = {
      [NotificationType.TASK_DUE]: 'Clock',
      [NotificationType.TASK_DELAYED]: 'Warning',
      [NotificationType.REVIEW_PENDING]: 'EditPen',
      [NotificationType.TEAM_REVIEW]: 'User',
      [NotificationType.COMMENT_REPLY]: 'ChatDotRound',
      [NotificationType.SYSTEM]: 'Bell'
    }
    return iconMap[type] || 'Bell'
  }

  /**
   * 获取通知颜色类型
   * @param {string} priority - 优先级
   */
  const getNotificationTypeTag = (priority) => {
    const typeMap = {
      [NotificationPriority.LOW]: 'info',
      [NotificationPriority.NORMAL]: '',
      [NotificationPriority.HIGH]: 'warning',
      [NotificationPriority.URGENT]: 'danger'
    }
    return typeMap[priority] || ''
  }

  /**
   * 格式化通知时间
   * @param {string} dateStr - 日期字符串
   */
  const formatNotificationTime = (dateStr) => {
    const now = dayjs()
    const time = dayjs(dateStr)
    const diffMinutes = now.diff(time, 'minute')

    if (diffMinutes < 1) return '刚刚'
    if (diffMinutes < 60) return `${diffMinutes}分钟前`

    const diffHours = now.diff(time, 'hour')
    if (diffHours < 24) return `${diffHours}小时前`

    const diffDays = now.diff(time, 'day')
    if (diffDays < 7) return `${diffDays}天前`

    return time.format('YYYY-MM-DD HH:mm')
  }

  /**
   * 检查未完成任务并生成通知
   * @param {Array} tasks - 任务列表
   */
  const checkTaskNotifications = (tasks) => {
    const now = dayjs()
    const currentWeek = now.week()
    const currentYear = now.year()

    tasks.forEach(task => {
      // 检查延期任务
      if (task.status === 'delayed' && !hasNotification(task.id, NotificationType.TASK_DELAYED)) {
        addNotification({
          type: NotificationType.TASK_DELAYED,
          priority: NotificationPriority.HIGH,
          title: '任务已延期',
          message: `任务"${task.title}"已延期，请尽快处理`,
          data: { taskId: task.id, task }
        })
      }

      // 检查未完成任务（周末提醒）
      if (task.status !== 'completed' &&
          task.week_number === currentWeek &&
          task.year === currentYear &&
          now.day() === 5 && // 周五
          !hasNotification(task.id, NotificationType.TASK_DUE)) {
        addNotification({
          type: NotificationType.TASK_DUE,
          priority: task.is_key_task ? NotificationPriority.HIGH : NotificationPriority.NORMAL,
          title: '任务即将到期',
          message: `${task.is_key_task ? '重点任务' : '任务'}"${task.title}"本周尚未完成`,
          data: { taskId: task.id, task }
        })
      }
    })
  }

  /**
   * 检查是否已存在相同通知
   * @param {number} taskId - 任务ID
   * @param {string} type - 通知类型
   */
  const hasNotification = (taskId, type) => {
    return notifications.value.some(n =>
      n.type === type &&
      n.data?.taskId === taskId &&
      !n.read
    )
  }

  /**
   * 生成周复盘提醒
   * @param {number} weekNumber - 周数
   * @param {number} year - 年份
   */
  const addReviewReminder = (weekNumber, year) => {
    if (!hasNotification(`review_${year}_${weekNumber}`, NotificationType.REVIEW_PENDING)) {
      addNotification({
        type: NotificationType.REVIEW_PENDING,
        priority: NotificationPriority.HIGH,
        title: '待进行周复盘',
        message: `第${weekNumber}周的工作计划需要进行复盘`,
        data: { weekNumber, year, notificationKey: `review_${year}_${weekNumber}` }
      })
    }
  }

  /**
   * 生成团队审阅提醒
   * @param {number} count - 待审阅数量
   */
  const addTeamReviewReminder = (count) => {
    if (count > 0) {
      addNotification({
        type: NotificationType.TEAM_REVIEW,
        priority: NotificationPriority.NORMAL,
        title: '待审阅团队周报',
        message: `有${count}位团队成员的周报待审阅`,
        data: { count }
      })
    }
  }

  /**
   * 添加系统通知
   * @param {string} title - 标题
   * @param {string} message - 消息
   */
  const addSystemNotification = (title, message) => {
    addNotification({
      type: NotificationType.SYSTEM,
      priority: NotificationPriority.NORMAL,
      title,
      message
    })
  }

  return {
    // State
    notifications,
    unreadCount,

    // Constants
    NotificationType,
    NotificationPriority,

    // Actions
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    clearRead,

    // Helpers
    getNotificationIcon,
    getNotificationTypeTag,
    formatNotificationTime,

    // Business Logic
    checkTaskNotifications,
    addReviewReminder,
    addTeamReviewReminder,
    addSystemNotification
  }
})
