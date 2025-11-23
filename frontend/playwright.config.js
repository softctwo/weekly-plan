import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright 测试配置
 */
export default defineConfig({
  testDir: './e2e',

  // 全局测试设置
  fullyParallel: true,

  // 失败时重试
  retries: process.env.CI ? 2 : 0,

  // 测试超时
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },

  // 并行工作进程数
  workers: process.env.CI ? 1 : undefined,

  // 报告配置
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['junit', { outputFile: 'playwright-report/results.xml' }],
    ['list']
  ],

  // 全局设置
  use: {
    // 基础URL
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // 截图配置
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true
    },

    // 视频录制
    video: 'retain-on-failure',

    // 追踪
    trace: 'on-first-retry',

    // 浏览器上下文
    viewport: { width: 1280, height: 720 },

    // 忽略HTTPS错误
    ignoreHTTPSErrors: true,

    // 用户代理
    userAgent: 'Weekly-Plan-E2E-Test'
  },

  // 项目配置 - 支持多浏览器测试
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },

    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }
    }
  ],

  // 本地开发服务器配置
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000
  },

  // 测试文件匹配模式
  testMatch: '**/*.spec.js',

  // 忽略模式
  testIgnore: '**/node_modules/**',

  // 输出目录
  outputDir: 'playwright-report'
})