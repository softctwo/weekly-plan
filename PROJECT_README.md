# 岗责驱动的周工作计划管理系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.3-brightgreen.svg)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element_Plus-2.5-blue.svg)](https://element-plus.org/)

## 项目简介

**岗责驱动的周工作计划管理系统（Job Responsibility-Driven Weekly Work Plan Management System）**是一个帮助企业员工基于岗位职责规划周工作、实现工作闭环的管理系统。

### 核心理念

- **岗责驱动**: 将员工的周工作计划与其标准化的岗位职责深度绑定
- **引导执行**: 通过系统智能建议，引导员工规划"有价值"的任务
- **聚焦重点**: 通过"重点工作"标识，帮助团队聚焦关键任务并确保其闭环
- **管理闭环**: 实现"计划-执行-复盘-辅导"的完整管理闭环

### 主要功能

#### 1. 员工端
- ✅ 创建周工作计划（基于岗位职责的智能建议）
- ✅ 标记重点任务
- ✅ 任务状态跟踪（待办、进行中、已完成、已延期）
- ✅ 周复盘（填写未完成原因和后续动作）
- ✅ 自动生成周报

#### 2. 管理者端
- ✅ 查看团队成员周计划概览
- ✅ 查看重点任务完成情况
- ✅ 审阅下属周报并提供反馈
- ✅ 为下属指派任务

#### 3. 管理员端
- ✅ 用户管理（创建、编辑、停用）
- ✅ 组织架构管理（部门、汇报关系）
- ✅ 岗位职责库管理（13个预置岗位）
- ✅ 用户-岗位多对多关联

### 预置岗位（13个）

系统预置了以下13个岗位及其完整的职责和任务类型：

**客户面向岗位：**
1. 研发工程师 (R&D)
2. 销售经理 (Sales)
3. 工程交付工程师 (On-site Delivery)
4. 售后客服 (After-sales)
5. 技术支持工程师 (Technical Support)
6. 项目经理 (Project Management)
7. 售前工程师 (Presales Engineer)
8. 项目总监 (Project Director)
9. 业务工程师 (Business Engineer)

**内部支持岗位：**
10. 人力资源 (HR)
11. 财务 (Finance)
12. 行政 (Admin)
13. 信息中心 (Internal IT)

## 技术栈

### 后端
- **框架**: FastAPI 0.109
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **文档**: OpenAPI (Swagger)

### 前端
- **框架**: Vue 3.3
- **构建工具**: Vite 5
- **UI组件库**: Element Plus 2.5
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios

## 项目结构

```
weekly-plan/
├── backend/                 # 后端（FastAPI）
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # 应用入口
│   ├── init_db.py          # 数据库初始化
│   ├── run.sh              # 启动脚本
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端（Vue 3）
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/    # 组件
│   │   ├── router/        # 路由
│   │   ├── store/         # 状态管理
│   │   ├── views/         # 页面
│   │   └── main.js        # 入口文件
│   ├── package.json       # npm依赖
│   └── vite.config.js     # Vite配置
├── docs/                  # 文档
├── PRD.md                 # 产品需求文档
├── README.md              # 附录A：岗位职责清单
├── CLAUDE.md              # AI助手指南
└── PROJECT_README.md      # 本文件
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- npm/pnpm/yarn

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY

# 初始化数据库（会创建管理员账户和预置13个岗位）
python3 init_db.py

# 启动服务
./run.sh
# 或
uvicorn app.main:app --reload
```

后端服务将在 `http://localhost:8000` 启动

API文档: `http://localhost:8000/docs`

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

### 3. 登录系统

系统预置了以下测试账号：

- **管理员**: `admin` / `admin123`
- **示例员工**: `zhangsan` / `123456`

## 核心功能演示

### 1. 员工创建周计划

1. 登录系统后进入"我的工作台"
2. 点击"我的任务" → "新建任务"
3. 系统会根据员工关联的岗位，智能推荐相关的任务类型
4. 员工可以将重要任务标记为"重点工作"

### 2. 周复盘

1. 进入"周复盘"页面
2. 对本周任务逐一复盘
3. 未完成任务必须填写：
   - 未完成原因（客户原因、内部资源不足等）
   - 后续动作（延期至下周 / 取消任务）
4. 系统自动生成周报

### 3. 管理者审阅

1. 管理者登录后进入"团队视图"
2. 查看所有直属下属的周计划概览
3. 可以查看重点任务完成情况
4. 点击成员查看详情，添加评论和辅导建议
5. 可以为下属指派新任务

### 4. 管理员配置

1. 进入"系统管理" → "用户管理"
2. 创建新用户，设置部门和直属上级
3. 为用户关联一个或多个岗位（支持多岗位）
4. 进入"岗位职责库"查看预置的13个岗位

## API文档

启动后端服务后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要API端点：

```
POST   /api/auth/login              # 登录
GET    /api/users/me                # 获取当前用户
POST   /api/tasks/                  # 创建任务
GET    /api/tasks/my-tasks          # 获取我的任务
POST   /api/tasks/reviews/          # 创建复盘
GET    /api/dashboard/employee      # 员工仪表盘
GET    /api/dashboard/team          # 团队仪表盘
POST   /api/roles/                  # 创建岗位（管理员）
GET    /api/roles/                  # 获取岗位列表
```

## 数据库模型

核心实体关系：

```
User (用户)
  ├─ N:1 → Department (部门)
  ├─ N:1 → User (直属上级)
  └─ N:M → Role (岗位)

Role (岗位)
  └─ 1:N → Responsibility (职责)
        └─ 1:N → TaskType (任务类型)

WeeklyTask (周任务)
  ├─ N:1 → User (所属用户)
  ├─ N:1 → TaskType (任务类型，可选)
  ├─ N:1 → User (指派人，可选)
  └─ 1:1 → TaskReview (复盘记录)
```

## 开发指南

### 添加新的岗位职责

编辑 `backend/app/utils/init_data.py`，在 `roles_data` 列表中添加新岗位：

```python
{
    "name": "新岗位名称",
    "name_en": "New Role",
    "description": "岗位描述",
    "responsibilities": [
        {
            "name": "职责1",
            "task_types": ["任务类型1", "任务类型2"]
        }
    ]
}
```

### 添加新的API端点

1. 在 `backend/app/api/endpoints/` 创建路由文件
2. 在 `backend/app/main.py` 注册路由
3. 定义相应的Pydantic schema

### 添加新的前端页面

1. 在 `frontend/src/views/` 创建Vue组件
2. 在 `frontend/src/router/index.js` 添加路由
3. 在 `Layout.vue` 添加菜单项

## 部署指南

### 使用Docker部署

```bash
# 构建后端镜像
cd backend
docker build -t weekly-plan-backend .

# 构建前端镜像
cd frontend
docker build -t weekly-plan-frontend .

# 使用docker-compose启动
docker-compose up -d
```

### 使用Nginx部署

1. 构建前端：`cd frontend && npm run build`
2. 配置Nginx反向代理
3. 部署后端到服务器并使用Gunicorn运行

详细部署文档请参考 `docs/DEPLOYMENT.md`

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 常见问题

**Q: 如何重置管理员密码？**

A: 连接数据库，直接更新users表的hashed_password字段，或使用Python脚本：

```python
from app.core.security import get_password_hash
new_password = get_password_hash("new_password")
```

**Q: 如何添加更多岗位？**

A: 管理员登录后，进入"系统管理" → "岗位职责库" → "新建岗位"

**Q: 员工可以关联多个岗位吗？**

A: 可以。管理员在用户管理中可以为一个员工关联多个岗位。

**Q: 如何修改系统的周计划周期？**

A: 系统基于自然周（周一至周日）。如需修改，需调整前后端的周次计算逻辑。

## 许可证

Copyright © 2025. All rights reserved.

## 致谢

本项目基于以下优秀的开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pinia](https://pinia.vuejs.org/)

## 联系方式

如有问题或建议，请提交Issue或联系项目维护者。

---

**祝您使用愉快！**
