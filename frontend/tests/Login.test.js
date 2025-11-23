/**
 * 登录组件测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Login from '@/views/Login.vue'

// Mock router
const mockRouter = {
  push: vi.fn()
}

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('Login.vue', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    wrapper = mount(Login, {
      global: {
        plugins: [pinia],
        mocks: {
          $router: mockRouter
        },
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-card': true,
          'el-link': true
        }
      }
    })
  })

  it('组件应该正确渲染', () => {
    expect(wrapper.find('.login-container').exists()).toBe(true)
    expect(wrapper.find('.login-title').exists()).toBe(true)
    expect(wrapper.text()).toContain('岗责驱动的周工作计划管理系统')
  })

  it('表单初始值应该为空', () => {
    expect(wrapper.vm.loginForm.username).toBe('')
    expect(wrapper.vm.loginForm.password).toBe('')
  })

  it('用户名输入应该正常工作', async() => {
    const usernameInput = wrapper.find('[data-testid="username-input"]')
    await usernameInput.setValue('testuser')
    expect(wrapper.vm.loginForm.username).toBe('testuser')
  })

  it('密码输入应该正常工作', async() => {
    const passwordInput = wrapper.find('[data-testid="password-input"]')
    await passwordInput.setValue('password123')
    expect(wrapper.vm.loginForm.password).toBe('password123')
  })

  it('空用户名应该显示验证错误', async() => {
    await wrapper.vm.handleSubmit()
    expect(wrapper.vm.errors.username).toBeTruthy()
  })

  it('空密码应该显示验证错误', async() => {
    wrapper.vm.loginForm.username = 'testuser'
    await wrapper.vm.handleSubmit()
    expect(wrapper.vm.errors.password).toBeTruthy()
  })

  it('表单验证应该正确工作', () => {
    // 测试空表单
    wrapper.vm.loginForm = { username: '', password: '' }
    expect(wrapper.vm.validateForm()).toBe(false)

    // 测试只有用户名
    wrapper.vm.loginForm = { username: 'test', password: '' }
    expect(wrapper.vm.validateForm()).toBe(false)

    // 测试完整表单
    wrapper.vm.loginForm = { username: 'test', password: 'password' }
    expect(wrapper.vm.validateForm()).toBe(true)
  })

  it('加载状态应该正确显示', async() => {
    expect(wrapper.vm.loading).toBe(false)

    wrapper.vm.loading = true
    await wrapper.vm.$nextTick()

    const loginButton = wrapper.find('[data-testid="login-button"]')
    expect(loginButton.attributes('loading')).toBeDefined()
  })

  it('错误消息应该正确显示', async() => {
    const errorMessage = '用户名或密码错误'
    wrapper.vm.error = errorMessage
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-message').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toBe(errorMessage)
  })

  it('回车键应该提交表单', async() => {
    const handleSubmitSpy = vi.spyOn(wrapper.vm, 'handleSubmit')

    wrapper.vm.loginForm = { username: 'test', password: 'password' }
    await wrapper.vm.handleKeyEnter({ key: 'Enter' })

    expect(handleSubmitSpy).toHaveBeenCalled()
  })

  it('其他按键不应该提交表单', async() => {
    const handleSubmitSpy = vi.spyOn(wrapper.vm, 'handleSubmit')

    await wrapper.vm.handleKeyEnter({ key: 'Tab' })

    expect(handleSubmitSpy).not.toHaveBeenCalled()
  })

  it('应该清除错误信息', () => {
    wrapper.vm.error = 'Some error'
    wrapper.vm.clearError()
    expect(wrapper.vm.error).toBe('')
  })

  it('应该正确清除表单', () => {
    wrapper.vm.loginForm = { username: 'test', password: 'password' }
    wrapper.vm.clearForm()
    expect(wrapper.vm.loginForm.username).toBe('')
    expect(wrapper.vm.loginForm.password).toBe('')
  })
})