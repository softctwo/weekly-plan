# 快速启动指南

## 🚀 5分钟快速体验系统

### 步骤1: 启动后端服务

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env，设置SECRET_KEY（或使用默认的演示配置）

# 初始化数据库（自动创建13个岗位和测试账号）
python3 init_db.py

# 启动后端服务
./run.sh
```

**后端服务**: http://localhost:8000
**API文档**: http://localhost:8000/docs

### 步骤2: 启动前端应用

打开新终端：

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**前端应用**: http://localhost:3000

### 步骤3: 登录体验

打开浏览器访问 http://localhost:3000

**测试账号**：
- 管理员: `admin` / `admin123`
- 普通员工: `zhangsan` / `123456`

---

## 🎯 核心功能演示流程

### 作为员工 (zhangsan)

1. **查看工作台**
   - 登录后自动进入"我的工作台"
   - 查看本周任务统计和完成率

2. **创建周任务**
   - 点击"我的任务" → "新建任务"
   - 输入任务标题和描述
   - 勾选"是否重点"标记重要任务
   - 点击"确定"创建

3. **管理任务状态**
   - 在任务列表中点击"更新状态"
   - 将任务标记为"进行中"或"已完成"

4. **周复盘** ⚠️ (待开发)
   - 进入"周复盘"页面
   - 对未完成任务填写原因和后续动作

### 作为管理员 (admin)

1. **查看岗位职责库**
   - 进入"系统管理" → "岗位职责库"
   - 浏览系统预置的13个岗位
   - 查看每个岗位的职责和任务类型

2. **创建新用户**
   - 进入"系统管理" → "用户管理"
   - 点击"创建用户"
   - 填写用户信息并关联岗位

3. **查看团队** ⚠️ (管理者权限)
   - 进入"团队视图"
   - 查看团队成员的周计划

---

## 📊 系统预置数据

### 13个岗位及职责

系统已自动初始化以下岗位：

1. **研发工程师 (R&D)** - 4个职责，13个任务类型
2. **销售经理 (Sales)** - 4个职责，13个任务类型
3. **工程交付工程师 (On-site Delivery)** - 4个职责，16个任务类型
4. **售后客服 (After-sales)** - 3个职责，8个任务类型
5. **技术支持工程师 (Technical Support)** - 3个职责，9个任务类型
6. **项目经理 (Project Management)** - 4个职责，11个任务类型
7. **售前工程师 (Presales Engineer)** - 4个职责，12个任务类型
8. **项目总监 (Project Director)** - 4个职责，13个任务类型
9. **业务工程师 (Business Engineer)** - 4个职责，14个任务类型
10. **人力资源 (HR)** - 3个职责，6个任务类型
11. **财务 (Finance)** - 3个职责，7个任务类型
12. **行政 (Admin)** - 2个职责，6个任务类型
13. **信息中心 (Internal IT)** - 3个职责，8个任务类型

**总计**: 共136个标准任务类型！

### 预置用户

- **admin** - 系统管理员
- **zhangsan** - 研发工程师（已关联"研发工程师"岗位）

---

## 🔧 API测试

访问 http://localhost:8000/docs 进入Swagger UI

### 测试登录

1. 找到 `POST /api/auth/login` 端点
2. 点击"Try it out"
3. 输入用户名和密码
4. 点击"Execute"
5. 复制返回的 `access_token`

### 使用Token访问受保护端点

1. 点击页面右上角的"Authorize"按钮
2. 输入: `Bearer {your_access_token}`
3. 点击"Authorize"
4. 现在可以测试所有需要认证的API

### 推荐测试的API

```bash
# 获取当前用户信息
GET /api/users/me

# 获取岗位列表
GET /api/roles/

# 获取我的任务
GET /api/tasks/my-tasks?week_number=47&year=2025

# 创建任务
POST /api/tasks/

# 获取员工仪表盘
GET /api/dashboard/employee?week_number=47&year=2025
```

---

## 🎨 系统特色功能

### 1. 多岗位支持
- ✅ 一个员工可以关联多个岗位
- ✅ 创建任务时会聚合所有岗位的职责建议

### 2. 重点任务标识
- ✅ 任务可标记为"重点工作"（★标识）
- ✅ 仪表盘单独统计重点任务完成情况
- ✅ 周报中重点任务置顶显示

### 3. 任务闭环管理
- ✅ 支持任务状态跟踪
- ⚠️ 周复盘（待完善）
- ⚠️ 未完成任务自动延期（待完善）

### 4. 管理者视图
- ⚠️ 团队仪表盘（待完善）
- ⚠️ 周报审阅和反馈（待完善）
- ⚠️ 任务指派功能（API已实现，前端待完善）

### 5. 权限控制
- ✅ 基于角色的访问控制（员工/管理者/管理员）
- ✅ JWT认证
- ✅ 路由守卫

---

## 📝 开发状态

### ✅ 已完成
- 完整的后端API（FastAPI）
- 数据库模型和关系
- 13个岗位的初始化数据
- 用户认证和授权
- 前端基础框架（Vue 3 + Element Plus）
- 登录页面
- 员工仪表盘
- 任务列表和创建

### ⚠️ 部分完成（前端UI待完善）
- 周复盘功能
- 团队视图
- 用户管理界面
- 岗位职责库管理界面

### 🔜 待开发
- 完整的周复盘流程
- 延期任务自动滚动
- 管理者审阅和评论
- 数据报表和导出
- 通知提醒功能

---

## 🐛 故障排查

### 后端无法启动

**问题**: `ModuleNotFoundError: No module named 'fastapi'`

**解决**: 确保已激活虚拟环境并安装依赖
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 前端无法启动

**问题**: `Cannot find module 'vue'`

**解决**: 重新安装依赖
```bash
rm -rf node_modules package-lock.json
npm install
```

### 数据库初始化失败

**问题**: 数据库已存在

**解决**: 删除数据库重新初始化
```bash
rm weekly_plan.db
python3 init_db.py
```

### API调用401错误

**问题**: Token过期或无效

**解决**: 重新登录获取新Token

---

## 📚 进一步学习

- 查看 `PRD.md` 了解完整的产品需求
- 查看 `PROJECT_README.md` 了解技术架构
- 查看 `backend/README.md` 了解后端详情
- 查看 `frontend/README.md` 了解前端详情
- 查看 `CLAUDE.md` 了解AI助手开发指南

---

## ✨ 下一步建议

1. **完善前端UI**
   - 实现完整的周复盘流程
   - 开发团队视图管理界面
   - 完善用户和岗位管理界面

2. **增强功能**
   - 添加数据统计报表
   - 实现消息通知功能
   - 支持任务评论和协作

3. **优化体验**
   - 添加加载动画
   - 优化移动端适配
   - 增加快捷键支持

4. **部署上线**
   - 配置生产环境数据库（PostgreSQL）
   - 使用Nginx反向代理
   - 配置HTTPS证书
   - 部署到云服务器

---

**祝您体验愉快！** 🎉
