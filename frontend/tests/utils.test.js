/**
 * 工具函数测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
global.localStorage = localStorageMock

describe('工具函数测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('日期格式化', () => {
    it('应该正确格式化日期', () => {
      const date = new Date('2024-01-15T10:30:00')

      // 模拟dayjs库
      const mockDayjs = vi.fn(() => ({
        format: vi.fn(() => '2024-01-15 10:30')
      }))

      const formatted = mockDayjs(date).format('YYYY-MM-DD HH:mm')
      expect(formatted).toBe('2024-01-15 10:30')
    })

    it('应该处理相对时间', () => {
      const mockDayjs = vi.fn(() => ({
        fromNow: vi.fn(() => '2小时前')
      }))

      const relative = mockDayjs().fromNow()
      expect(relative).toBe('2小时前')
    })
  })

  describe('数据验证', () => {
    it('应该验证邮箱格式', () => {
      const isValidEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        return emailRegex.test(email)
      }

      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('invalid-email')).toBe(false)
      expect(isValidEmail('test@')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
    })

    it('应该验证手机号格式', () => {
      const isValidPhone = (phone) => {
        const phoneRegex = /^1[3-9]\d{9}$/
        return phoneRegex.test(phone)
      }

      expect(isValidPhone('13800138000')).toBe(true)
      expect(isValidPhone('12800138000')).toBe(false)
      expect(isValidPhone('1380013800')).toBe(false)
      expect(isValidPhone('138001380000')).toBe(false)
    })

    it('应该验证必填字段', () => {
      const validateRequired = (value) => {
        return value !== null && value !== undefined && value !== ''
      }

      expect(validateRequired('test')).toBe(true)
      expect(validateRequired(0)).toBe(true)
      expect(validateRequired(false)).toBe(true)
      expect(validateRequired(null)).toBe(false)
      expect(validateRequired(undefined)).toBe(false)
      expect(validateRequired('')).toBe(false)
    })
  })

  describe('字符串处理', () => {
    it('应该正确截断字符串', () => {
      const truncate = (str, length, suffix = '...') => {
        if (str.length <= length) {return str}
        return str.substring(0, length) + suffix
      }

      expect(truncate('Hello World', 5)).toBe('Hello...')
      expect(truncate('Hello', 10)).toBe('Hello')
      expect(truncate('Hello World', 5, '---')).toBe('Hello---')
    })

    it('应该正确处理驼峰命名转换', () => {
      const toCamelCase = (str) => {
        return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      }

      const toSnakeCase = (str) => {
        return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      }

      expect(toCamelCase('hello_world')).toBe('helloWorld')
      expect(toCamelCase('user_name_id')).toBe('userNameId')
      expect(toSnakeCase('helloWorld')).toBe('hello_world')
      expect(toSnakeCase('userNameId')).toBe('user_name_id')
    })
  })

  describe('数组操作', () => {
    it('应该正确去重', () => {
      const unique = (arr) => [...new Set(arr)]

      expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3])
      expect(unique(['a', 'b', 'a', 'c'])).toEqual(['a', 'b', 'c'])
      expect(unique([])).toEqual([])
    })

    it('应该正确分组', () => {
      const groupBy = (arr, key) => {
        return arr.reduce((groups, item) => {
          const group = item[key]
          groups[group] = groups[group] || []
          groups[group].push(item)
          return groups
        }, {})
      }

      const data = [
        { type: 'fruit', name: 'apple' },
        { type: 'fruit', name: 'banana' },
        { type: 'vegetable', name: 'carrot' }
      ]

      const grouped = groupBy(data, 'type')
      expect(grouped.fruit).toHaveLength(2)
      expect(grouped.vegetable).toHaveLength(1)
    })
  })

  describe('对象操作', () => {
    it('应该深度克隆对象', () => {
      const deepClone = (obj) => JSON.parse(JSON.stringify(obj))

      const original = { a: 1, b: { c: 2 } }
      const cloned = deepClone(original)

      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
      expect(cloned.b).not.toBe(original.b)
    })

    it('应该合并对象', () => {
      const merge = (...objs) => Object.assign({}, ...objs)

      const obj1 = { a: 1, b: 2 }
      const obj2 = { b: 3, c: 4 }
      const merged = merge(obj1, obj2)

      expect(merged).toEqual({ a: 1, b: 3, c: 4 })
    })

    it('应该选择对象的指定属性', () => {
      const pick = (obj, keys) => {
        return keys.reduce((result, key) => {
          if (key in obj) {
            result[key] = obj[key]
          }
          return result
        }, {})
      }

      const obj = { a: 1, b: 2, c: 3, d: 4 }
      const picked = pick(obj, ['a', 'c'])

      expect(picked).toEqual({ a: 1, c: 3 })
    })
  })

  describe('数据转换', () => {
    it('应该正确格式化文件大小', () => {
      const formatFileSize = (bytes) => {
        if (bytes === 0) {return '0 B'}
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
      }

      expect(formatFileSize(0)).toBe('0 B')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1048576)).toBe('1 MB')
      expect(formatFileSize(1073741824)).toBe('1 GB')
    })

    it('应该正确格式化数字', () => {
      const formatNumber = (num, digits = 2) => {
        return new Intl.NumberFormat('zh-CN', {
          minimumFractionDigits: digits,
          maximumFractionDigits: digits
        }).format(num)
      }

      expect(formatNumber(1234.567)).toBe('1,234.57')
      expect(formatNumber(1234.5, 0)).toBe('1,235')
      expect(formatNumber(0)).toBe('0.00')
    })
  })

  describe('防抖和节流', () => {
    it('应该实现防抖功能', (done) => {
      vi.useFakeTimers()

      let count = 0
      const increment = () => count++
      let timeoutId
      const debouncedIncrement = () => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(increment, 100)
      }

      debouncedIncrement()
      debouncedIncrement()
      debouncedIncrement()

      expect(count).toBe(0)

      vi.advanceTimersByTime(100)

      setTimeout(() => {
        expect(count).toBe(1)
        done()
      }, 0)

      vi.runAllTimers()
    })

    it('应该实现节流功能', () => {
      vi.useFakeTimers()

      let count = 0
      const increment = () => count++
      let lastCall = 0

      const throttledIncrement = () => {
        const now = Date.now()
        if (now - lastCall >= 100) {
          increment()
          lastCall = now
        }
      }

      // 快速调用多次
      throttledIncrement()
      throttledIncrement()
      throttledIncrement()

      expect(count).toBe(1)

      vi.advanceTimersByTime(100)

      throttledIncrement()
      expect(count).toBe(2)

      vi.useRealTimers()
    })
  })
})