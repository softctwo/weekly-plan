import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userType: (state) => state.userInfo?.user_type || '',
    isAdmin: (state) => state.userInfo?.user_type === 'admin',
    isManager: (state) => ['admin', 'manager'].includes(state.userInfo?.user_type)
  },

  actions: {
    async login(username, password) {
      try {
        const data = await login(username, password)
        this.token = data.access_token
        localStorage.setItem('token', data.access_token)
        await this.fetchUserInfo()
        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    async fetchUserInfo() {
      try {
        const data = await getUserInfo()
        this.userInfo = data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        throw error
      }
    },

    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})
