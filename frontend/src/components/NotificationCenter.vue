<template>
  <el-popover
    :width="400"
    trigger="click"
    popper-class="notification-popover"
  >
    <template #reference>
      <el-badge
        :value="unreadCount"
        :hidden="unreadCount === 0"
        :max="99"
      >
        <el-button
          circle
          :icon="Bell"
        />
      </el-badge>
    </template>

    <div class="notification-center">
      <!-- 标题栏 -->
      <div class="notification-header">
        <span class="title">通知中心</span>
        <el-space>
          <el-tooltip
            :content="browserNotificationTooltip"
            placement="bottom"
          >
            <el-button
              :icon="isBrowserNotificationEnabled ? BellFilled : Bell"
              :type="isBrowserNotificationEnabled ? 'primary' : 'default'"
              size="small"
              circle
              @click="handleToggleBrowserNotification"
            />
          </el-tooltip>
          <el-button
            v-if="unreadCount > 0"
            link
            type="primary"
            size="small"
            @click="handleMarkAllRead"
          >
            全部已读
          </el-button>
          <el-button
            link
            type="danger"
            size="small"
            @click="handleClearRead"
          >
            清空已读
          </el-button>
        </el-space>
      </div>

      <!-- 通知列表 -->
      <div class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ 'unread': !notification.read, [notification.priority]: true }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon">
            <el-icon
              :size="24"
              :color="getIconColor(notification.priority)"
            >
              <component :is="getIcon(notification.type)" />
            </el-icon>
          </div>
          <div class="notification-content">
            <div class="notification-title">
              {{ notification.title }}
              <el-tag
                v-if="notification.priority === 'urgent' || notification.priority === 'high'"
                :type="notificationStore.getNotificationTypeTag(notification.priority)"
                size="small"
                style="margin-left: 8px"
              >
                {{ notification.priority === 'urgent' ? '紧急' : '重要' }}
              </el-tag>
            </div>
            <div class="notification-message">
              {{ notification.message }}
            </div>
            <div class="notification-time">
              {{ notificationStore.formatNotificationTime(notification.createdAt) }}
            </div>
          </div>
          <div class="notification-actions">
            <el-button
              link
              type="danger"
              size="small"
              @click.stop="handleRemove(notification.id)"
            >
              删除
            </el-button>
          </div>
        </div>

        <el-empty
          v-if="notifications.length === 0"
          description="暂无通知"
          :image-size="80"
        />
      </div>

      <!-- 底部操作 -->
      <div
        v-if="notifications.length > 0"
        class="notification-footer"
      >
        <el-button
          link
          type="danger"
          size="small"
          @click="handleClearAll"
        >
          清空所有通知
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Bell,
  BellFilled,
  Clock,
  Warning,
  EditPen,
  User,
  ChatDotRound
} from '@element-plus/icons-vue'
import { useNotificationStore } from '@/store/notification'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)

// 浏览器通知状态
const isBrowserNotificationSupported = computed(() => notificationStore.isBrowserNotificationSupported)
const isBrowserNotificationEnabled = computed(() => notificationStore.isBrowserNotificationEnabled)

// 浏览器通知提示文本
const browserNotificationTooltip = computed(() => {
  if (!isBrowserNotificationSupported.value) {
    return '您的浏览器不支持推送通知'
  }
  if (isBrowserNotificationEnabled.value) {
    return '浏览器推送通知已启用'
  }
  return '点击启用浏览器推送通知'
})

// 获取通知图标
const getIcon = (type) => {
  const iconMap = {
    task_due: Clock,
    task_delayed: Warning,
    review_pending: EditPen,
    team_review: User,
    comment_reply: ChatDotRound,
    system: Bell
  }
  return iconMap[type] || Bell
}

// 获取图标颜色
const getIconColor = (priority) => {
  const colorMap = {
    low: '#909399',
    normal: '#409EFF',
    high: '#E6A23C',
    urgent: '#F56C6C'
  }
  return colorMap[priority] || '#409EFF'
}

// 处理通知点击
const handleNotificationClick = (notification) => {
  // 标记为已读
  notificationStore.markAsRead(notification.id)

  // 根据通知类型跳转
  switch (notification.type) {
    case 'task_due':
    case 'task_delayed':
      router.push('/tasks')
      break
    case 'review_pending':
      router.push('/review')
      break
    case 'team_review':
      router.push('/team')
      break
    default:
      break
  }
}

// 标记所有为已读
const handleMarkAllRead = () => {
  notificationStore.markAllAsRead()
  ElMessage.success('已标记所有通知为已读')
}

// 清空已读通知
const handleClearRead = async() => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有已读通知吗？',
      '确认操作',
      { type: 'warning' }
    )
    notificationStore.clearRead()
    ElMessage.success('已清空已读通知')
  } catch (error) {
    // 取消操作
  }
}

// 清空所有通知
const handleClearAll = async() => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有通知吗？此操作不可恢复！',
      '确认操作',
      { type: 'warning' }
    )
    notificationStore.clearAll()
    ElMessage.success('已清空所有通知')
  } catch (error) {
    // 取消操作
  }
}

// 删除单个通知
const handleRemove = (notificationId) => {
  notificationStore.removeNotification(notificationId)
}

// 切换浏览器推送通知
const handleToggleBrowserNotification = async() => {
  if (!isBrowserNotificationSupported.value) {
    ElMessage.warning('您的浏览器不支持推送通知功能')
    return
  }

  if (isBrowserNotificationEnabled.value) {
    ElMessage.info('浏览器推送通知已启用，如需关闭请在浏览器设置中操作')
    return
  }

  try {
    const granted = await notificationStore.requestBrowserNotificationPermission()
    if (granted) {
      ElMessage.success('浏览器推送通知已启用')

      // 发送测试通知
      notificationStore.sendBrowserNotification({
        title: '通知已启用',
        body: '您将收到重要任务的浏览器推送通知',
        requireInteraction: false
      })
    } else {
      ElMessage.warning('浏览器推送通知权限被拒绝')
    }
  } catch (error) {
    console.error('启用浏览器通知失败:', error)
    ElMessage.error('启用浏览器通知失败，请稍后重试')
  }
}
</script>

<style scoped>
.notification-center {
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

.notification-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: background-color 0.3s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #ecf5ff;
}

.notification-item.unread:hover {
  background-color: #d9ecff;
}

.notification-item.urgent {
  border-left: 3px solid #f56c6c;
}

.notification-item.high {
  border-left: 3px solid #e6a23c;
}

.notification-icon {
  flex-shrink: 0;
  padding-top: 2px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.notification-message {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
  line-height: 1.4;
  word-break: break-word;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.notification-actions {
  flex-shrink: 0;
}

.notification-footer {
  padding: 8px 16px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}
</style>

<style>
.notification-popover {
  padding: 0 !important;
}
</style>
