import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  test: {
    // 测试环境
    environment: 'happy-dom',

    // 全局设置
    globals: true,

    // 测试文件匹配
    include: [
      'tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'src/**/__tests__/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ],

    // 排除文件
    exclude: [
      'node_modules',
      'dist',
      'cypress',
      '.idea',
      '.git',
      '.cache'
    ],

    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: 'coverage',
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        'dist/',
        'coverage/',
        'public/',
        'src/main.js',
        'vite.config.js',
        'vitest.config.js'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      }
    },

    // 测试超时时间 (毫秒)
    testTimeout: 10000,

    // Hook超时时间
    hookTimeout: 10000,

    // 并发测试
    threads: true,

    // 监听模式下文件变化后重新运行的延迟
    watchExclude: [
      'node_modules/',
      'dist/',
      'coverage/'
    ],

    // Setup文件
    setupFiles: ['tests/setup.js']
  },

  // 服务器配置
  server: {
    port: 3001
  },

  // 构建配置
  build: {
    sourcemap: true
  }
})