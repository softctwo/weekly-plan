# 岗责驱动的周工作计划管理系统 - 前端

## 技术栈

- **框架**: Vue 3
- **构建工具**: Vite 5
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **日期处理**: Day.js

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口
│   │   ├── request.js    # Axios封装
│   │   ├── auth.js       # 认证接口
│   │   ├── tasks.js      # 任务接口
│   │   ├── roles.js      # 岗位职责接口
│   │   └── dashboard.js  # 仪表盘接口
│   ├── components/       # 组件
│   ├── router/           # 路由配置
│   ├── store/            # Pinia状态管理
│   │   └── user.js       # 用户状态
│   ├── views/            # 页面视图
│   │   ├── Login.vue     # 登录页
│   │   ├── Layout.vue    # 布局页
│   │   ├── Dashboard.vue # 仪表盘
│   │   ├── Tasks.vue     # 任务列表
│   │   ├── Review.vue    # 周复盘
│   │   ├── Team.vue      # 团队视图
│   │   └── admin/        # 管理员页面
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── public/               # 静态资源
├── index.html            # HTML模板
├── vite.config.js        # Vite配置
├── package.json          # 依赖配置
└── README.md             # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
npm install
# 或
pnpm install
# 或
yarn install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

### 4. 预览生产构建

```bash
npm run preview
```

## 功能模块

### 1. 员工端

- **我的工作台**: 查看本周任务统计、完成率、重点任务
- **我的任务**: 创建、查看、更新周计划任务，支持重点标识
- **周复盘**: 对本周任务进行复盘，填写未完成原因和后续动作

### 2. 管理者端

- **团队视图**: 查看团队成员周计划概览
- **成员详情**: 下钻查看成员任务详情
- **审阅反馈**: 对成员周报发表评论和辅导建议
- **任务指派**: 为下属指派任务

### 3. 管理员端

- **用户管理**: 创建用户、关联岗位、设置汇报关系
- **岗位职责库**: 管理13个岗位及其职责、任务类型

## API代理配置

开发环境下，所有 `/api` 请求会被代理到后端服务器（默认 `http://localhost:8000`）

修改代理配置请编辑 `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
# API基础路径
VITE_API_BASE_URL=/api

# 应用标题
VITE_APP_TITLE=周工作计划管理系统
```

## 登录账号

系统预置了以下测试账号：

- **管理员**: `admin` / `admin123`
- **示例员工**: `zhangsan` / `123456`

## 开发说明

### 添加新页面

1. 在 `src/views/` 创建Vue组件
2. 在 `src/router/index.js` 添加路由配置
3. 在布局页面添加菜单项（如需要）

### 添加新API

1. 在 `src/api/` 创建或编辑API模块
2. 使用统一的 `request` 实例发起请求
3. 在组件中导入并调用

### 状态管理

使用Pinia进行状态管理，示例：

```javascript
// 定义store
import { defineStore } from 'pinia'

export const useMyStore = defineStore('myStore', {
  state: () => ({ count: 0 }),
  actions: {
    increment() {
      this.count++
    }
  }
})

// 在组件中使用
import { useMyStore } from '@/store/myStore'
const myStore = useMyStore()
myStore.increment()
```

## 代码规范

项目使用ESLint进行代码检查：

```bash
npm run lint
```

## 部署

### 静态部署

构建后将 `dist/` 目录部署到静态服务器（Nginx、Apache等）

### Nginx配置示例

```nginx
server {
  listen 80;
  server_name your-domain.com;
  root /path/to/dist;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api {
    proxy_pass http://backend-server:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### Docker部署

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 许可证

Copyright © 2025
