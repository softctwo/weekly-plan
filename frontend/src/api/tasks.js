import request from './request'

// 创建周计划任务
export function createTask(data) {
  return request({
    url: '/tasks/',
    method: 'post',
    data
  })
}

// 获取我的任务列表
export function getMyTasks(params) {
  return request({
    url: '/tasks/my-tasks',
    method: 'get',
    params
  })
}

// 获取延期任务
export function getDelayedTasks() {
  return request({
    url: '/tasks/delayed-tasks',
    method: 'get'
  })
}

// 更新任务
export function updateTask(taskId, data) {
  return request({
    url: `/tasks/${taskId}`,
    method: 'put',
    data
  })
}

// 创建任务复盘
export function createTaskReview(data) {
  return request({
    url: '/tasks/reviews/',
    method: 'post',
    data
  })
}

// 获取周报
export function getWeeklyReport(params) {
  return request({
    url: '/tasks/weekly-report',
    method: 'get',
    params
  })
}

// 指派任务（管理者）
export function assignTask(userId, data) {
  return request({
    url: `/tasks/assign/?user_id=${userId}`,
    method: 'post',
    data
  })
}
