/**
 * 性能测试
 */
import { test, expect } from '@playwright/test'

test.describe('性能测试', () => {
  test.beforeEach(async({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('页面加载性能测试', async({ page }) => {
    // 监听网络请求
    const requests = []
    page.on('request', request => requests.push(request))

    // 访问仪表板页面
    await page.goto('/dashboard', { waitUntil: 'networkidle' })

    // 检查关键性能指标
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0]
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        firstPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
      }
    })

    // 性能断言
    expect(performanceMetrics.domContentLoaded).toBeLessThan(1000) // DOM加载时间小于1秒
    expect(performanceMetrics.loadComplete).toBeLessThan(3000) // 页面完全加载时间小于3秒
    expect(performanceMetrics.firstContentfulPaint).toBeLessThan(2000) // 首次内容绘制时间小于2秒

    // 检查请求数量
    expect(requests.length).toBeLessThan(20) // 请求数量不超过20个
  })

  test('交互响应性能测试', async({ page }) => {
    // 测试按钮点击响应
    const startTime = Date.now()

    await page.click('.refresh-button')
    await page.waitForSelector('.loading-spinner', { state: 'hidden' })

    const responseTime = Date.now() - startTime
    expect(responseTime).toBeLessThan(2000) // 响应时间小于2秒

    // 测试任务创建性能
    await page.click('.quick-add-button')
    await expect(page.locator('.task-dialog')).toBeVisible()

    const dialogStartTime = Date.now()
    await page.fill('input[placeholder*="任务名称"]', '性能测试任务')
    await page.click('button[type="submit"]')
    await expect(page.locator('.task-dialog')).not.toBeVisible()

    const dialogResponseTime = Date.now() - dialogStartTime
    expect(dialogResponseTime).toBeLessThan(1000) // 对话框操作响应时间小于1秒
  })

  test('内存使用测试', async({ page }) => {
    // 获取初始内存使用
    const initialMemory = await page.evaluate(() => {
      if (performance.memory) {
        return performance.memory.usedJSHeapSize
      }
      return 0
    })

    // 执行一系列操作
    for (let i = 0; i < 10; i++) {
      await page.goto('/dashboard')
      await page.click('.refresh-button')
      await page.waitForSelector('.loading-spinner', { state: 'hidden' })

      if (await page.locator('.quick-add-button').isVisible()) {
        await page.click('.quick-add-button')
        await page.fill('input[placeholder*="任务名称"]', `测试任务${i}`)
        await page.click('.cancel-button')
      }
    }

    // 获取最终内存使用
    const finalMemory = await page.evaluate(() => {
      if (performance.memory) {
        return performance.memory.usedJSHeapSize
      }
      return 0
    })

    // 检查内存增长
    if (initialMemory > 0 && finalMemory > 0) {
      const memoryGrowth = finalMemory - initialMemory
      const memoryGrowthMB = memoryGrowth / (1024 * 1024)
      expect(memoryGrowthMB).toBeLessThan(50) // 内存增长不超过50MB
    }
  })

  test('大数据量渲染性能', async({ page }) => {
    // 模拟大量数据
    await page.goto('/dashboard')

    // 监控渲染时间
    const renderStartTime = Date.now()

    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 检查列表渲染性能
    const taskItems = page.locator('.task-item')
    const itemCount = await taskItems.count()

    if (itemCount > 0) {
      await taskItems.first().scrollIntoViewIfNeeded()
      const renderTime = Date.now() - renderStartTime
      expect(renderTime).toBeLessThan(1000) // 列表渲染时间小于1秒
    }

    // 测试滚动性能
    const scrollStartTime = Date.now()
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(500) // 等待滚动完成
    const scrollTime = Date.now() - scrollStartTime
    expect(scrollTime).toBeLessThan(1000) // 滚动响应时间小于1秒
  })

  test('网络请求优化测试', async({ page }) => {
    // 监听所有网络请求
    const networkRequests = []
    page.on('request', request => networkRequests.push({
      url: request.url(),
      method: request.method(),
      resourceType: request.resourceType()
    }))

    await page.goto('/dashboard', { waitUntil: 'networkidle' })

    // 检查资源优化
    const jsRequests = networkRequests.filter(req => req.resourceType === 'script')
    const cssRequests = networkRequests.filter(req => req.resourceType === 'stylesheet')
    const imageRequests = networkRequests.filter(req => req.resourceType === 'image')
    const apiRequests = networkRequests.filter(req => req.resourceType === 'xhr' || req.resourceType === 'fetch')

    // 验证资源请求数量合理
    expect(jsRequests.length).toBeLessThan(10) // JS文件不超过10个
    expect(cssRequests.length).toBeLessThan(5) // CSS文件不超过5个

    // 检查API请求
    expect(apiRequests.length).toBeGreaterThan(0) // 应该有API请求
    expect(apiRequests.length).toBeLessThan(10) // API请求数量合理

    // 检查是否有资源缓存
    const responses = await Promise.all(networkRequests.map(req =>
      page.waitForResponse(req.url).then(res => ({
        url: res.url(),
        status: res.status(),
        headers: res.headers()
      }))
    ))

    const cachedResponses = responses.filter(res =>
      res.headers['cache-control'] && res.headers['cache-control'].includes('max-age')
    )

    // 应该有部分资源被缓存
    expect(cachedResponses.length).toBeGreaterThan(0)
  })

  test('用户体验指标测试', async({ page }) => {
    // 监听Web Vitals指标
    const vitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        const vitals = {}

        // 模拟Core Web Vitals计算
        setTimeout(() => {
          vitals.fcp = performance.getEntriesByType('paint')
            .find(entry => entry.name === 'first-contentful-paint')?.startTime || 0

          vitals.lcp = performance.getEntriesByType('largest-contentful-paint')
            .pop()?.startTime || 0

          vitals.fid = 0 // First Input Delay需要实际用户交互
          vitals.cls = 0 // Cumulative Layout Shift需要复杂计算

          resolve(vitals)
        }, 2000)
      })
    })

    // 验证核心性能指标
    expect(vitals.fcp).toBeLessThan(1800) // FCP < 1.8s
    expect(vitals.lcp).toBeLessThan(2500) // LCP < 2.5s

    // 测试页面稳定性
    await page.click('.refresh-button')
    await page.waitForSelector('.loading-spinner', { state: 'hidden' })

    // 检查是否有布局偏移
    const hasLayoutShift = await page.evaluate(() => {
      return new Promise((resolve) => {
        let hasShift = false
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.value > 0.1) {
              hasShift = true
              break
            }
          }
          resolve(hasShift)
        }).observe({ entryTypes: ['layout-shift'] })

        setTimeout(() => resolve(false), 3000)
      })
    })

    expect(hasLayout).toBe(false) // 不应该有明显的布局偏移
  })

  test('响应式性能测试', async({ page }) => {
    // 测试不同屏幕尺寸下的性能
    const viewports = [
      { width: 1920, height: 1080 }, // 桌面
      { width: 768, height: 1024 },  // 平板
      { width: 375, height: 667 }    // 移动
    ]

    for (const viewport of viewports) {
      await page.setViewportSize(viewport)

      const startTime = Date.now()
      await page.goto('/dashboard', { waitUntil: 'networkidle' })
      const loadTime = Date.now() - startTime

      // 不同设备都应该有合理的加载时间
      expect(loadTime).toBeLessThan(5000) // 任何设备加载时间小于5秒

      // 检查响应式布局
      await page.waitForSelector('.dashboard-container')

      if (viewport.width <= 768) {
        // 移动端应该有移动端特定元素
        await expect(page.locator('.mobile-menu')).toBeVisible()
      }
    }
  })
})