import request from './request'

// 获取员工仪表盘
export function getEmployeeDashboard(params) {
  return request({
    url: '/dashboard/employee',
    method: 'get',
    params
  })
}

// 获取团队仪表盘（管理者）
export function getTeamDashboard(params) {
  return request({
    url: '/dashboard/team',
    method: 'get',
    params
  })
}

// 获取成员详情（管理者）
export function getMemberDetail(userId, params) {
  return request({
    url: `/dashboard/team/member/${userId}`,
    method: 'get',
    params
  })
}

// 添加周报评论（管理者）
export function addComment(data) {
  return request({
    url: '/dashboard/team/comments/',
    method: 'post',
    data
  })
}

// 标记为已审阅（管理者）
export function markAsReviewed(commentId) {
  return request({
    url: `/dashboard/team/comments/${commentId}/mark-reviewed`,
    method: 'put'
  })
}
