import request from './request'

// 获取岗位列表
export function getRoles(includeInactive = false) {
  return request({
    url: '/roles/',
    method: 'get',
    params: { include_inactive: includeInactive }
  })
}

// 创建岗位
export function createRole(data) {
  return request({
    url: '/roles/',
    method: 'post',
    data
  })
}

// 获取职责列表
export function getResponsibilities(roleId = null) {
  return request({
    url: '/roles/responsibilities/',
    method: 'get',
    params: { role_id: roleId }
  })
}

// 创建职责
export function createResponsibility(data) {
  return request({
    url: '/roles/responsibilities/',
    method: 'post',
    data
  })
}

// 获取任务类型列表
export function getTaskTypes(responsibilityId = null) {
  return request({
    url: '/roles/task-types/',
    method: 'get',
    params: { responsibility_id: responsibilityId }
  })
}

// 创建任务类型
export function createTaskType(data) {
  return request({
    url: '/roles/task-types/',
    method: 'post',
    data
  })
}
