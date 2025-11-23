/**
 * 仪表板功能E2E测试
 */
import { test, expect } from '@playwright/test'

test.describe('仪表板功能', () => {
  test.beforeEach(async({ page }) => {
    // 登录
    await page.goto('/login')
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('应该正确显示仪表板页面', async({ page }) => {
    // 检查页面标题
    await expect(page).toHaveTitle(/工作台/)

    // 检查主要元素
    await expect(page.locator('.dashboard-container')).toBeVisible()
    await expect(page.locator('.page-header')).toContainText('工作台')
  })

  test('应该显示统计卡片', async({ page }) => {
    // 检查统计卡片
    const statCards = page.locator('.stat-card')
    await expect(statCards).toHaveCount(4)

    // 检查统计指标
    await expect(page.locator('text=总任务数')).toBeVisible()
    await expect(page.locator('text=已完成')).toBeVisible()
    await expect(page.locator('text=进行中')).toBeVisible()
    await expect(page.locator('text=已逾期')).toBeVisible()
  })

  test('应该显示完成率进度条', async({ page }) => {
    // 检查完成率显示
    await expect(page.locator('.completion-rate')).toBeVisible()
    await expect(page.locator('.progress-bar')).toBeVisible()

    // 检查完成率百分比
    const rateText = page.locator('.rate-text')
    await expect(rateText).toBeVisible()
    const rateValue = await rateText.textContent()
    expect(rateValue).toMatch(/\d+%/)
  })

  test('应该显示本周任务列表', async({ page }) => {
    // 检查任务列表
    await expect(page.locator('.task-list')).toBeVisible()
    await expect(page.locator('text=本周任务')).toBeVisible()

    // 检查任务项
    const taskItems = page.locator('.task-item')
    if (await taskItems.count() > 0) {
      // 检查任务状态标签
      await expect(page.locator('.task-status')).toBeVisible()
      await expect(page.locator('.task-priority')).toBeVisible()
    }
  })

  test('应该能够刷新数据', async({ page }) => {
    const refreshButton = page.locator('.refresh-button')
    await expect(refreshButton).toBeVisible()

    // 点击刷新按钮
    await refreshButton.click()

    // 检查加载状态
    await expect(page.locator('.loading-spinner')).toBeVisible()

    // 等待加载完成
    await expect(page.locator('.loading-spinner')).not.toBeVisible()
  })

  test('应该能够快速创建任务', async({ page }) => {
    // 点击快速创建任务按钮
    const quickAddButton = page.locator('.quick-add-button')
    if (await quickAddButton.isVisible()) {
      await quickAddButton.click()

      // 检查任务创建对话框
      await expect(page.locator('.task-dialog')).toBeVisible()
      await expect(page.locator('input[placeholder*="任务名称"]')).toBeVisible()

      // 填写任务信息
      await page.fill('input[placeholder*="任务名称"]', 'E2E测试任务')
      await page.click('button[type="submit"]')

      // 检查任务创建成功
      await expect(page.locator('.task-dialog')).not.toBeVisible()
      await expect(page.locator('text=E2E测试任务')).toBeVisible()
    }
  })

  test('应该能够筛选任务', async({ page }) => {
    const filterButtons = page.locator('.filter-button')
    if (await filterButtons.count() > 0) {
      // 点击筛选按钮
      await filterButtons.first().click()

      // 检查筛选下拉菜单
      await expect(page.locator('.filter-dropdown')).toBeVisible()

      // 选择筛选条件
      await page.click('.filter-option >> text=已完成')

      // 检查筛选结果
      await expect(page.locator('.filter-dropdown')).not.toBeVisible()
    }
  })

  test('应该显示图表数据', async({ page }) => {
    // 检查图表容器
    const chartContainer = page.locator('.chart-container')
    if (await chartContainer.isVisible()) {
      await expect(chartContainer).toBeVisible()

      // 等待图表加载
      await page.waitForTimeout(2000)

      // 检查图表元素
      await expect(page.locator('canvas')).toBeVisible()
    }
  })

  test('应该能够导航到任务详情', async({ page }) => {
    const taskItems = page.locator('.task-item')
    if (await taskItems.count() > 0) {
      // 点击第一个任务
      await taskItems.first().click()

      // 检查跳转到任务详情页
      await expect(page).toHaveURL(/\/tasks\/\d+/)
      await expect(page.locator('.task-detail')).toBeVisible()
    }
  })

  test('应该响应式适配移动端', async({ page }) => {
    // 切换到移动端视图
    await page.setViewportSize({ width: 375, height: 667 })

    // 检查移动端布局
    await expect(page.locator('.mobile-menu')).toBeVisible()

    // 检查统计卡片堆叠显示
    const statCards = page.locator('.stat-card')
    await expect(statCards).toHaveCount(4)

    // 检查移动端任务列表
    await expect(page.locator('.mobile-task-list')).toBeVisible()
  })

  test('应该显示通知中心', async({ page }) => {
    // 点击通知图标
    const notificationButton = page.locator('.notification-button')
    if (await notificationButton.isVisible()) {
      await notificationButton.click()

      // 检查通知面板
      await expect(page.locator('.notification-panel')).toBeVisible()

      // 检查通知列表
      const notifications = page.locator('.notification-item')
      if (await notifications.count() > 0) {
        await expect(notifications.first()).toBeVisible()
      }
    }
  })

  test('应该能够标记重点任务', async({ page }) => {
    const taskItems = page.locator('.task-item')
    if (await taskItems.count() > 0) {
      const firstTask = taskItems.first()
      const starButton = firstTask.locator('.star-button')

      if (await starButton.isVisible()) {
        // 点击星标按钮
        await starButton.click()

        // 检查任务被标记为重点
        await expect(firstTask.locator('.is-important')).toBeVisible()
      }
    }
  })

  test('应该能够更新任务状态', async({ page }) => {
    const taskItems = page.locator('.task-item')
    if (await taskItems.count() > 0) {
      const firstTask = taskItems.first()
      const statusButton = firstTask.locator('.status-button')

      if (await statusButton.isVisible()) {
        // 点击状态按钮
        await statusButton.click()

        // 检查状态选择器
        await expect(page.locator('.status-selector')).toBeVisible()

        // 选择新状态
        await page.click('.status-option >> text=已完成')

        // 检查状态更新
        await expect(page.locator('.status-selector')).not.toBeVisible()
        await expect(firstTask.locator('.status-completed')).toBeVisible()
      }
    }
  })

  test('应该能够导出数据', async({ page }) => {
    const exportButton = page.locator('.export-button')
    if (await exportButton.isVisible()) {
      // 设置下载监听
      const downloadPromise = page.waitForEvent('download')

      // 点击导出按钮
      await exportButton.click()

      // 选择导出格式
      await page.click('.export-option >> text=Excel')

      // 等待下载开始
      const download = await downloadPromise
      expect(download.suggestedFilename()).toMatch(/\.xlsx$/)
    }
  })
})