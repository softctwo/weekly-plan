import request from './request'

// 登录
export function login(username, password) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  return request({
    url: '/auth/login',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取当前用户信息
export function getUserInfo() {
  return request({
    url: '/users/me',
    method: 'get'
  })
}
