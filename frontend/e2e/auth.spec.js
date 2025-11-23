/**
 * 认证功能E2E测试
 */
import { test, expect } from '@playwright/test'

test.describe('认证功能', () => {
  test.beforeEach(async({ page }) => {
    // 访问登录页面
    await page.goto('/login')
  })

  test('页面应该正确显示登录表单', async({ page }) => {
    // 检查页面标题
    await expect(page).toHaveTitle(/周工作计划管理系统/)

    // 检查主要元素
    await expect(page.locator('.login-container')).toBeVisible()
    await expect(page.locator('.login-title')).toContainText('岗责驱动的周工作计划管理系统')

    // 检查表单元素
    await expect(page.locator('input[type="text"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('应该显示验证错误信息', async({ page }) => {
    // 点击登录按钮但不填写表单
    await page.click('button[type="submit"]')

    // 检查错误信息
    await expect(page.locator('.error-message')).toBeVisible()
    await expect(page.locator('.error-message')).toContainText('用户名不能为空')
  })

  test('应该显示登录失败错误', async({ page }) => {
    // 填写错误的登录信息
    await page.fill('input[type="text"]', 'wronguser')
    await page.fill('input[type="password"]', 'wrongpass')
    await page.click('button[type="submit"]')

    // 检查错误信息
    await expect(page.locator('.error-message')).toBeVisible()
    await expect(page.locator('.error-message')).toContainText('用户名或密码错误')
  })

  test('应该能够成功登录', async({ page }) => {
    // 填写正确的登录信息
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')

    // 检查登录成功后跳转到仪表板
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('.dashboard-container')).toBeVisible()

    // 检查用户信息显示
    await expect(page.locator('.user-info')).toBeVisible()
    await expect(page.locator('.user-info')).toContainText('admin')
  })

  test('应该支持回车键登录', async({ page }) => {
    // 填写登录信息
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')

    // 在密码框中按回车
    await page.press('input[type="password"]', 'Enter')

    // 检查登录成功
    await expect(page).toHaveURL('/dashboard')
  })

  test('应该显示加载状态', async({ page }) => {
    // 填写登录信息
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')

    // 点击登录并检查加载状态
    const loginButton = page.locator('button[type="submit"]')
    await loginButton.click()

    // 检查按钮禁用状态
    await expect(loginButton).toBeDisabled()
  })

  test('应该记住登录状态', async({ page, context }) => {
    // 登录
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')

    // 等待登录完成
    await expect(page).toHaveURL('/dashboard')

    // 获取 cookies
    const cookies = await context.cookies()
    const tokenCookie = cookies.find(cookie => cookie.name.includes('token'))
    expect(tokenCookie).toBeTruthy()

    // 新建页面并访问仪表板
    const newPage = await context.newPage()
    await newPage.goto('/dashboard')

    // 应该仍然登录状态
    await expect(newPage.locator('.dashboard-container')).toBeVisible()
  })

  test('应该能够退出登录', async({ page }) => {
    // 先登录
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL('/dashboard')

    // 退出登录
    await page.click('.user-dropdown')
    await page.click('text=退出登录')

    // 检查退出后跳转到登录页
    await expect(page).toHaveURL('/login')

    // 验证访问受保护页面会被重定向
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/login')
  })

  test('应该处理网络错误', async({ page }) => {
    // 模拟网络错误
    await page.route('**/api/auth/login', route => route.abort())

    // 尝试登录
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')

    // 检查错误信息
    await expect(page.locator('.error-message')).toBeVisible()
    await expect(page.locator('.error-message')).toContainText('网络错误')
  })

  test('应该支持密码显示/隐藏', async({ page }) => {
    const passwordInput = page.locator('input[type="password"]')
    const toggleButton = page.locator('.password-toggle')

    // 填写密码
    await passwordInput.fill('admin123')

    // 点击显示密码
    await toggleButton.click()
    await expect(passwordInput).toHaveAttribute('type', 'text')

    // 点击隐藏密码
    await toggleButton.click()
    await expect(passwordInput).toHaveAttribute('type', 'password')
  })
})