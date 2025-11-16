# 岗责驱动的周工作计划管理系统

<div align="center">

**一个基于岗位职责的智能周工作计划管理系统**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.3+-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.109+-teal.svg)](https://fastapi.tiangolo.com/)

[功能特性](#-功能特性) •
[快速开始](#-快速开始) •
[技术栈](#-技术栈) •
[项目结构](#-项目结构) •
[文档](#-文档)

</div>

---

## 📖 项目简介

本系统是一个面向企业团队的周工作计划管理平台，通过将员工的岗位职责与具体任务关联，实现从计划制定到执行跟踪、复盘总结的完整闭环管理。系统内置13个典型岗位的职责库，包含136种标准任务类型，支持多岗位用户、重点任务标记、智能提醒、数据分析等功能。

### 核心理念

- **岗责驱动**: 基于岗位职责制定工作计划，确保工作与职责对齐
- **周为单位**: 以周为管理周期，平衡短期执行与长期目标
- **闭环管理**: 计划→执行→复盘→改进的完整管理循环
- **数据赋能**: 多维度数据分析，为决策提供数据支持

---

## ✨ 功能特性

### 👤 员工功能

#### 1. 我的工作台
- 📊 **本周任务概览**: 总任务数、已完成、进行中、完成率统计
- ⭐ **重点任务跟踪**: 单独显示重点工作完成情况
- 📈 **完成率趋势**: 可视化进度条展示周任务完成度
- 🔔 **智能通知**: 延期提醒、周末未完成提醒、周日复盘提醒

#### 2. 任务管理
- ✅ **任务创建**: 关联岗位职责，自动推荐任务类型
- 🏷️ **重点标记**: 标记重点工作，优先级管理
- 🔄 **状态跟踪**: 待办/进行中/已完成/已延期四种状态
- 📝 **任务描述**: 支持详细描述和备注
- 🎯 **拖拽排序**: 直观的任务优先级调整
- ⚡ **批量操作**:
  - 批量更新状态
  - 批量标记重点
  - 批量删除
- 📤 **Excel导出**: 一键导出任务清单
- 🔍 **筛选功能**: 按状态、重点任务筛选
- 📄 **分页显示**: 支持10/20/50/100条每页

#### 3. 周复盘
- 📅 **周次选择**: 可查看最近4周的任务
- ✔️ **完成确认**: 逐项确认任务完成状态
- 📝 **未完成处理**:
  - 必填未完成原因 (6种预设选项)
  - 必选后续动作 (延期/取消)
- 💭 **复盘备注**: 记录心得、反思、下周计划
- 📋 **周报生成**: 自动生成结构化周报
  - 任务完成统计
  - 重点任务清单
  - 未完成任务分析

#### 4. 数据报表
- 📊 **核心指标**: 总任务、完成率、重点任务、延期率
- 📈 **趋势分析**: 周完成率走势图
- 📉 **状态分布**: 四种状态占比可视化
- 🎨 **任务类型统计**: 按职责和类型分组分析
- 📥 **多表导出**: Excel多工作表报表

### 👔 管理者功能

#### 5. 团队视图
- 👥 **团队概览**: 团队规模、总任务数、完成率、待审阅数
- 📋 **成员列表**: 分页展示团队成员及其完成情况
- 🔍 **成员详情**: 查看成员具体任务和完成状态
- 💬 **评论反馈**: 对成员周报进行评论和建议
- ✅ **审阅标记**: 标记已审阅的周报
- 🔔 **审阅提醒**: 自动提醒待审阅的团队周报

#### 6. 团队绩效报表
- 📊 **成员绩效对比**: 完成率、任务量、平均周期
- ⭐ **绩效评分**: 5星评分系统
- 📈 **复盘跟踪**: 已复盘周数统计

### 🔧 管理员功能

#### 7. 用户管理
- 👤 **用户CRUD**: 创建、编辑、停用用户
- 🏷️ **用户类型**: 员工/管理者/管理员三种角色
- 🏢 **部门管理**: 部门归属设置
- 👨‍💼 **上下级关系**: 设置直属上级
- 🎭 **岗位关联**:
  - 一个用户可关联多个岗位
  - 使用穿梭框(Transfer)组件操作
  - 动态聚合职责建议

#### 8. 岗位职责库管理
- 📚 **三层结构**: 岗位 → 职责 → 任务类型
- ➕ **新建岗位**: 添加自定义岗位
- 📝 **职责定义**: 为岗位添加核心职责
- 🏷️ **任务类型**: 定义标准任务类型
- 🔄 **状态管理**: 启用/停用（软删除）
- 📊 **折叠展示**: 清晰的层级结构展示

### 🔔 通知提醒系统

#### 9. 智能通知
- ⏰ **任务到期提醒**: 周五提醒未完成任务
- ⚠️ **延期警告**: 高优先级延期任务提醒
- 📅 **复盘提醒**: 周日提示进行周复盘
- 👥 **团队审阅提醒**: 管理者待审阅通知
- 📢 **系统公告**: 欢迎消息、系统通知

#### 10. 通知中心
- 🔔 **未读徽章**: 顶部栏实时显示未读数量
- 📱 **通知列表**: 弹窗展示所有通知
- 🎨 **优先级标识**: 颜色区分紧急/重要/普通
- ⏱️ **相对时间**: "5分钟前"、"2小时前"
- 🔗 **点击跳转**: 点击通知自动跳转相关页面
- 🗑️ **批量操作**: 全部已读、清空已读、清空全部

### ⚡ 性能优化

#### 11. 数据缓存
- 💾 **5分钟TTL**: 时间戳验证的缓存策略
- 📦 **多类型缓存**:
  - 用户角色和职责
  - 团队成员数据
  - 任务列表（按周和筛选条件）
  - 仪表盘统计
- 🔄 **智能失效**: 数据变更时自动清除缓存
- 📊 **缓存统计**: 提供缓存命中率监控

#### 12. 列表优化
- 📄 **分页加载**: 所有长列表支持分页
- 🎯 **可配置页面大小**: 10/20/50/100可选
- 🔍 **前端筛选**: 客户端快速筛选
- 📉 **性能提升**: API调用减少80-90%

---

## 🚀 快速开始

### 环境要求

- **后端**: Python 3.9+
- **前端**: Node.js 16+ / npm 8+
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### 5分钟快速体验

#### 1. 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 SECRET_KEY（或使用默认配置）

# 初始化数据库（自动创建13个岗位和测试账号）
python3 init_db.py

# 启动服务
./run.sh  # 或 uvicorn app.main:app --reload
```

**后端服务**: http://localhost:8000
**API文档**: http://localhost:8000/docs

#### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**前端应用**: http://localhost:3000

#### 3. 登录体验

访问 http://localhost:3000

**测试账号**:
- 管理员: `admin` / `admin123`
- 普通员工: `zhangsan` / `123456`

---

## 🛠️ 技术栈

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| **FastAPI** | 0.109 | 现代化Python Web框架，高性能异步API |
| **SQLAlchemy** | 2.0 | Python ORM，支持复杂关系映射 |
| **Pydantic** | 2.0 | 数据验证和序列化 |
| **python-jose** | 3.3 | JWT token生成和验证 |
| **passlib** | 1.7 | 密码哈希处理 |
| **Alembic** | 1.13 | 数据库迁移工具 |
| **SQLite/PostgreSQL** | - | 数据库引擎 |

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue 3** | 3.3.11 | 渐进式JavaScript框架，Composition API |
| **Vite** | 5.0.11 | 下一代前端构建工具 |
| **Element Plus** | 2.5.2 | Vue 3 UI组件库 |
| **Pinia** | 2.1.7 | Vue 状态管理 |
| **Vue Router** | 4.2.5 | 官方路由管理器 |
| **Axios** | 1.6.5 | HTTP客户端 |
| **Day.js** | 1.11.10 | 日期处理库 |
| **vuedraggable** | 4.1.0 | 拖拽组件 |
| **xlsx** | 0.18.5 | Excel文件处理 |

### 架构模式

- **三层架构**: Presentation Layer → Business Logic → Data Access
- **RESTful API**: 统一的资源访问接口
- **JWT认证**: 无状态token认证
- **RBAC权限**: 基于角色的访问控制
- **响应式设计**: 适配桌面和移动端

---

## 📂 项目结构

```
weekly-plan/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API端点
│   │   │   └── endpoints/     # 具体端点实现
│   │   │       ├── auth.py           # 认证登录
│   │   │       ├── users.py          # 用户管理
│   │   │       ├── roles.py          # 岗位职责库
│   │   │       ├── tasks.py          # 任务管理
│   │   │       └── dashboard.py      # 仪表盘和报表
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py             # 应用配置
│   │   │   └── security.py           # 安全工具
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── role.py               # 岗位模型
│   │   │   └── task.py               # 任务模型
│   │   ├── schemas/           # Pydantic模式
│   │   ├── utils/             # 工具函数
│   │   │   └── init_data.py          # 初始化数据
│   │   └── main.py            # 应用入口
│   ├── init_db.py             # 数据库初始化脚本
│   ├── requirements.txt       # Python依赖
│   └── .env.example           # 环境变量模板
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/               # API调用封装
│   │   ├── components/        # 可复用组件
│   │   │   └── NotificationCenter.vue  # 通知中心
│   │   ├── router/            # 路由配置
│   │   ├── store/             # Pinia状态管理
│   │   │   ├── user.js               # 用户状态
│   │   │   ├── cache.js              # 缓存管理
│   │   │   └── notification.js       # 通知管理
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue             # 登录页
│   │   │   ├── Layout.vue            # 主布局
│   │   │   ├── Dashboard.vue         # 工作台
│   │   │   ├── Tasks.vue             # 任务管理
│   │   │   ├── Review.vue            # 周复盘
│   │   │   ├── Reports.vue           # 数据报表
│   │   │   ├── Team.vue              # 团队视图
│   │   │   └── admin/                # 管理员页面
│   │   │       ├── Users.vue         # 用户管理
│   │   │       └── Roles.vue         # 岗位职责库
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 应用入口
│   ├── package.json           # npm依赖
│   ├── vite.config.js         # Vite配置
│   └── CACHING.md             # 缓存策略文档
│
├── docs/                       # 文档目录
│   ├── PRD.md                 # 产品需求文档
│   ├── QUICKSTART.md          # 快速启动指南
│   ├── CLAUDE.md              # AI开发指南
│   └── PROJECT_README.md      # 项目技术文档
│
└── README.md                   # 本文件
```

---

## 📊 数据模型

### 核心实体

```
User (用户)
  ├── 基本信息: username, full_name, email
  ├── 角色: user_type (employee/manager/admin)
  ├── 组织: department_id, manager_id
  └── 关联: roles (多对多)

Role (岗位)
  ├── 基本信息: name, name_en, description
  ├── 状态: is_active (软删除)
  └── 子项: responsibilities

Responsibility (职责)
  ├── 基本信息: name, description
  ├── 关联: role_id
  ├── 排序: sort_order
  ├── 状态: is_active
  └── 子项: task_types

TaskType (任务类型)
  ├── 基本信息: name, description
  ├── 关联: responsibility_id
  ├── 排序: sort_order
  └── 状态: is_active

WeeklyTask (周任务)
  ├── 基本信息: title, description
  ├── 时间: year, week_number
  ├── 状态: status (todo/in_progress/completed/delayed)
  ├── 标记: is_key_task (重点任务)
  ├── 关联: user_id, linked_task_type_id
  └── 分配: assigned_by_manager_id

TaskReview (任务复盘)
  ├── 关联: task_id
  ├── 完成: is_completed
  ├── 未完成: incomplete_reason, follow_up_action
  ├── 备注: notes
  └── 时间: reviewed_at

ReportComment (周报评论)
  ├── 关联: user_id, week_number, year
  ├── 内容: content
  ├── 评论人: commented_by_id
  └── 审阅: is_reviewed
```

---

## 📈 系统亮点

### 1. 完整的工作闭环

**计划阶段**: 基于岗位职责制定周计划，系统推荐标准任务类型
↓
**执行阶段**: 实时更新任务状态，智能提醒延期任务
↓
**复盘阶段**: 逐项确认完成情况，分析未完成原因
↓
**改进阶段**: 数据分析发现问题，持续优化工作方式

### 2. 数据驱动决策

- **个人视角**: 完成率趋势、任务类型分布、时间分配
- **团队视角**: 成员绩效对比、团队完成率、延期率分析
- **管理视角**: 岗位任务量统计、职责覆盖度、资源分配

### 3. 智能化支持

- **任务推荐**: 根据岗位自动推荐任务类型
- **多岗位聚合**: 自动合并多个岗位的职责建议
- **智能提醒**:
  - 周五提醒未完成任务
  - 周日提醒进行复盘
  - 延期任务高优先级提醒
- **缓存优化**: 5分钟TTL减少API调用

### 4. 用户体验

- **拖拽排序**: 直观的任务优先级调整
- **批量操作**: 提高多任务处理效率
- **Excel导出**: 一键生成报表
- **响应式设计**: 适配不同屏幕尺寸
- **实时通知**: 不错过任何重要信息

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [PRD.md](PRD.md) | 产品需求规格说明书 V1.1 |
| [QUICKSTART.md](QUICKSTART.md) | 5分钟快速启动指南 |
| [CLAUDE.md](CLAUDE.md) | AI助手开发指南 |
| [docs/PROJECT_README.md](docs/PROJECT_README.md) | 技术架构详解 |
| [ROLES_INIT_DATA.md](ROLES_INIT_DATA.md) | 13个岗位初始化数据清单 |
| [frontend/CACHING.md](frontend/CACHING.md) | 前端缓存策略文档 |

---

## 🎯 功能完成度

### ✅ 已完成功能

**核心功能**:
- ✅ 用户认证与授权 (JWT)
- ✅ 岗位职责库管理 (13个预置岗位，136个任务类型)
- ✅ 用户管理 (多岗位关联)
- ✅ 周任务管理 (CRUD + 拖拽 + 批量操作)
- ✅ 周复盘流程 (未完成原因 + 后续动作)
- ✅ 团队视图 (管理者)
- ✅ 数据统计报表 (多维度分析)

**增强功能**:
- ✅ 通知提醒系统 (智能多场景)
- ✅ Excel导出 (任务和报表)
- ✅ 数据缓存优化 (5分钟TTL)
- ✅ 列表分页 (所有长列表)
- ✅ 任务拖拽排序
- ✅ 批量操作 (状态/重点/删除)

### 🔜 可选扩展

**性能优化**:
- 虚拟滚动 (当前分页已足够)
- Redis缓存 (当前内存缓存已满足需求)

**功能扩展**:
- PDF报表导出 (Excel已覆盖)
- 浏览器推送通知 (Notification API)
- 移动端APP
- 数据可视化图表 (ECharts集成)
- 多语言支持

---

## 🗄️ 数据初始化

系统内置**13个岗位**的职责库，共**136个标准任务类型**:

| 岗位 | 职责数 | 任务类型数 |
|------|--------|-----------|
| 研发工程师 (R&D) | 4 | 13 |
| 销售经理 (Sales) | 4 | 13 |
| 工程交付工程师 (On-site Delivery) | 4 | 16 |
| 售后客服 (After-sales) | 3 | 8 |
| 技术支持工程师 (Technical Support) | 3 | 9 |
| 项目经理 (Project Management) | 4 | 11 |
| 售前工程师 (Presales Engineer) | 4 | 12 |
| 项目总监 (Project Director) | 4 | 13 |
| 业务工程师 (Business Engineer) | 4 | 14 |
| 人力资源 (HR) | 3 | 6 |
| 财务 (Finance) | 3 | 7 |
| 行政 (Admin) | 2 | 6 |
| 信息中心 (Internal IT) | 3 | 8 |

**预置测试账号**:
- `admin` / `admin123` - 系统管理员
- `zhangsan` / `123456` - 研发工程师

详细数据见 [ROLES_INIT_DATA.md](ROLES_INIT_DATA.md)

---

## 🔧 开发指南

### API文档

启动后端后访问: http://localhost:8000/docs

Swagger UI提供完整的API文档和在线测试。

### 测试流程

```bash
# 1. 登录获取Token
POST /api/auth/login
Body: {"username": "admin", "password": "admin123"}

# 2. 使用Token访问其他API
Authorization: Bearer {your_access_token}

# 3. 推荐测试的API
GET /api/users/me              # 获取当前用户
GET /api/roles/                # 获取岗位列表
GET /api/tasks/my-tasks        # 获取我的任务
POST /api/tasks/               # 创建任务
GET /api/dashboard/employee    # 员工仪表盘
```

### 代码规范

**后端**:
- 遵循PEP 8规范
- 使用类型提示 (Type Hints)
- Pydantic模型验证
- 异步编程 (async/await)

**前端**:
- Vue 3 Composition API
- ESLint代码检查
- 组件化开发
- 响应式设计

---

## 📝 更新日志

### v1.2.0 (2025-01-16)

**新增功能**:
- ✨ 通知提醒系统 (智能多场景提醒)
- 📊 数据统计报表页面 (多维度分析)
- 🔔 通知中心UI组件
- 💾 数据缓存优化 (5分钟TTL)

**功能增强**:
- ⚡ 任务拖拽排序
- ✅ 批量操作 (状态/重点/删除)
- 📤 Excel导出 (任务和报表)
- 📄 列表分页 (10/20/50/100可选)
- 👥 团队视图完善

**性能优化**:
- 🚀 API调用减少80-90%
- ⏱️ 响应时间从200ms降至10ms (缓存命中)
- 📦 内存缓存策略

### v1.1.0 (2025-01-15)

**初始版本**:
- ✅ 完整的后端API (FastAPI + SQLAlchemy)
- ✅ 13个岗位初始化数据
- ✅ 用户认证和授权 (JWT)
- ✅ 前端基础框架 (Vue 3 + Element Plus)
- ✅ 核心功能实现

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码审查

所有PR需要经过代码审查才能合并。

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢以下开源项目:

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包

---

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系:

- 📧 Email: support@example.com
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/weekly-plan/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star! ⭐**

Made with ❤️ by Weekly-Plan Team

</div>
