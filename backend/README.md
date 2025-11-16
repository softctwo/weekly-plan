# 岗责驱动的周工作计划管理系统 - 后端

## 技术栈

- **框架**: FastAPI 0.109.0
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose)
- **文档**: 自动生成的OpenAPI (Swagger)

## 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── deps.py       # 依赖项（认证等）
│   │   └── endpoints/    # API端点
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   └── security.py   # 安全相关
│   ├── db/               # 数据库
│   │   └── base.py       # 数据库基础配置
│   ├── models/           # SQLAlchemy模型
│   │   ├── user.py       # 用户和组织
│   │   ├── role.py       # 岗位职责
│   │   └── task.py       # 任务和复盘
│   ├── schemas/          # Pydantic模式
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   │   └── init_data.py  # 数据初始化
│   └── main.py           # FastAPI应用入口
├── init_db.py            # 数据库初始化脚本
├── run.sh                # 启动脚本
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量示例
└── README.md             # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，设置必要的配置
# 特别注意：生产环境必须修改SECRET_KEY
```

### 3. 初始化数据库

```bash
# 运行初始化脚本
python3 init_db.py

# 或使用启动脚本
./run.sh init
```

这将：
- 创建所有数据库表
- 导入13个岗位的职责数据（基于PRD附录A）
- 创建管理员账户: `admin / admin123`
- 创建示例员工账户: `zhangsan / 123456`

### 4. 启动服务

```bash
# 使用启动脚本（推荐）
./run.sh

# 或直接使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

服务启动后，访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API概览

### 认证
- `POST /api/auth/login` - 用户登录

### 用户管理（管理员）
- `POST /api/users/` - 创建用户
- `GET /api/users/` - 获取用户列表
- `GET /api/users/me` - 获取当前用户信息
- `PUT /api/users/{user_id}` - 更新用户
- `POST /api/users/{user_id}/roles/{role_id}` - 关联岗位

### 岗位职责库（管理员）
- `POST /api/roles/` - 创建岗位
- `GET /api/roles/` - 获取岗位列表
- `POST /api/roles/responsibilities/` - 创建职责
- `POST /api/roles/task-types/` - 创建任务类型
- `PUT /api/roles/{role_id}/deactivate` - 停用岗位

### 任务管理（员工）
- `POST /api/tasks/` - 创建周计划任务
- `GET /api/tasks/my-tasks` - 获取我的任务
- `GET /api/tasks/delayed-tasks` - 获取延期任务
- `PUT /api/tasks/{task_id}` - 更新任务
- `POST /api/tasks/reviews/` - 创建任务复盘
- `GET /api/tasks/weekly-report` - 生成周报

### 仪表盘
- `GET /api/dashboard/employee` - 员工仪表盘
- `GET /api/dashboard/team` - 团队仪表盘（管理者）
- `GET /api/dashboard/team/member/{user_id}` - 成员详情
- `POST /api/dashboard/team/comments/` - 添加周报评论

## 数据模型

### 核心实体

1. **User** - 用户
2. **Department** - 部门
3. **Role** - 岗位（13个预置岗位）
4. **Responsibility** - 职责
5. **TaskType** - 标准任务类型
6. **UserRoleLink** - 用户-岗位关联（多对多）
7. **WeeklyTask** - 周计划任务
8. **TaskReview** - 任务复盘
9. **ReportComment** - 周报评论

### 13个预置岗位

1. 研发工程师 (R&D)
2. 销售经理 (Sales)
3. 工程交付工程师 (On-site Delivery)
4. 售后客服 (After-sales)
5. 技术支持工程师 (Technical Support)
6. 项目经理 (Project Management)
7. 售前工程师 (Presales Engineer)
8. 项目总监 (Project Director)
9. 业务工程师 (Business Engineer)
10. 人力资源 (HR)
11. 财务 (Finance)
12. 行政 (Admin)
13. 信息中心 (Internal IT)

## 开发说明

### 添加新的API端点

1. 在 `app/api/endpoints/` 中创建新的路由文件
2. 在 `app/main.py` 中注册路由
3. 定义相应的Pydantic schema

### 数据库迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回退迁移
alembic downgrade -1
```

### 运行测试

```bash
pytest
```

## 生产部署

### 使用PostgreSQL

1. 修改 `.env` 中的 `DATABASE_URL`:
```
DATABASE_URL=postgresql://user:password@localhost/weekly_plan
```

2. 安装PostgreSQL驱动（已在requirements.txt中）

### 使用Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署

```bash
# 构建镜像
docker build -t weekly-plan-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env weekly-plan-backend
```

## 安全建议

1. **生产环境必须修改SECRET_KEY**
2. 使用HTTPS
3. 启用CORS白名单
4. 定期更新依赖包
5. 使用强密码策略
6. 启用日志监控

## 许可证

Copyright © 2025
