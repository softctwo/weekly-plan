/**
 * 简单组件测试示例
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// 创建一个简单的测试组件
const TestComponent = {
  template: `
    <div class="test-component">
      <h1>{{ title }}</h1>
      <button @click="increment">Count: {{ count }}</button>
      <p v-if="showMessage">Hello World!</p>
    </div>
  `,
  props: {
    title: {
      type: String,
      default: 'Test Title'
    }
  },
  data() {
    return {
      count: 0,
      showMessage: false
    }
  },
  methods: {
    increment() {
      this.count++
      if (this.count >= 3) {
        this.showMessage = true
      }
    }
  }
}

describe('简单组件测试', () => {
  let wrapper

  beforeEach(() => {
    const pinia = createPinia()
    setActivePinia(pinia)

    wrapper = mount(TestComponent, {
      global: {
        plugins: [pinia]
      }
    })
  })

  it('组件应该正确渲染', () => {
    expect(wrapper.find('.test-component').exists()).toBe(true)
    expect(wrapper.find('h1').text()).toBe('Test Title')
    expect(wrapper.find('button').text()).toBe('Count: 0')
  })

  it('应该接收props', () => {
    const wrapperWithTitle = mount(TestComponent, {
      props: {
        title: 'Custom Title'
      }
    })

    expect(wrapperWithTitle.find('h1').text()).toBe('Custom Title')
  })

  it('计数器应该正确工作', async() => {
    const button = wrapper.find('button')

    expect(wrapper.vm.count).toBe(0)

    await button.trigger('click')
    expect(wrapper.vm.count).toBe(1)
    expect(button.text()).toBe('Count: 1')

    await button.trigger('click')
    expect(wrapper.vm.count).toBe(2)

    await button.trigger('click')
    expect(wrapper.vm.count).toBe(3)
  })

  it('计数达到3时应该显示消息', async() => {
    const button = wrapper.find('button')

    expect(wrapper.find('p').exists()).toBe(false)

    // 点击3次
    await button.trigger('click')
    await button.trigger('click')
    await button.trigger('click')

    expect(wrapper.vm.showMessage).toBe(true)
    expect(wrapper.find('p').exists()).toBe(true)
    expect(wrapper.find('p').text()).toBe('Hello World!')
  })

  it('应该验证props类型', () => {
    const consoleSpy = vi.spyOn(console, 'warn')

    mount(TestComponent, {
      props: {
        title: 123 // 错误的类型
      }
    })

    // Vue 3会在开发环境下发出类型警告
    expect(consoleSpy).toHaveBeenCalled()
  })

  it('应该响应数据变化', async() => {
    expect(wrapper.vm.count).toBe(0)
    expect(wrapper.find('button').text()).toBe('Count: 0')

    wrapper.vm.count = 5
    await wrapper.vm.$nextTick()

    expect(wrapper.find('button').text()).toBe('Count: 5')
  })

  it('应该计算属性正确工作', async() => {
    // 添加一个计算属性来测试
    const TestComponentWithComputed = {
      template: `
        <div>
          <p>Double: {{ doubleCount }}</p>
          <button @click="increment">Count: {{ count }}</button>
        </div>
      `,
      data() {
        return {
          count: 2
        }
      },
      computed: {
        doubleCount() {
          return this.count * 2
        }
      },
      methods: {
        increment() {
          this.count++
        }
      }
    }

    const computedWrapper = mount(TestComponentWithComputed)
    expect(computedWrapper.find('p').text()).toBe('Double: 4')

    await computedWrapper.find('button').trigger('click')
    expect(computedWrapper.find('p').text()).toBe('Double: 6')
  })

  it('应该处理事件', async() => {
    const eventSpy = vi.fn()

    const TestComponentWithEvents = {
      template: `
        <div>
          <button @click="handleClick">Click me</button>
        </div>
      `,
      methods: {
        handleClick() {
          eventSpy()
          this.$emit('custom-event', 'test data')
        }
      }
    }

    const eventWrapper = mount(TestComponentWithEvents)
    await eventWrapper.find('button').trigger('click')

    expect(eventSpy).toHaveBeenCalled()
    expect(eventWrapper.emitted('custom-event')).toBeTruthy()
    expect(eventWrapper.emitted('custom-event')[0]).toEqual(['test data'])
  })
})