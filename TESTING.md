# 测试文档 (Testing Documentation)

Weekly Plan Management System - 测试策略和指南

---

## 📋 目录

- [测试概览](#测试概览)
- [测试类型](#测试类型)
- [快速开始](#快速开始)
- [测试覆盖率](#测试覆盖率)
- [测试策略](#测试策略)
- [持续集成](#持续集成)

---

## 测试概览

本项目采用多层次的测试策略，确保代码质量和系统稳定性：

### 测试框架

- **数据验证测试**: Python测试脚本（`test_comprehensive.py`）
- **后端单元测试**: Pytest + FastAPI TestClient
- **前端测试**: (待实现) Vitest + Vue Test Utils
- **端到端测试**: (待实现) Playwright/Cypress

### 测试统计

| 测试类型 | 工具 | 测试文件数 | 测试用例数 | 覆盖率目标 |
|---------|------|----------|----------|----------|
| 数据验证 | Python | 1 | 141 | 100% |
| 后端单元测试 | Pytest | 5 | 50+ | 80%+ |
| 前端单元测试 | Vitest | 0 | - | 80%+ |
| E2E测试 | - | 0 | - | 关键流程 |

---

## 测试类型

### 1. 数据完整性测试 ✅

**位置**: `/test_comprehensive.py`

**用途**: 验证13个岗位的职责数据完整性

**运行方式**:
```bash
python3 test_comprehensive.py
```

**测试内容**:
- ✅ 岗位数量验证 (13个)
- ✅ 职责层级结构
- ✅ 任务类型数量 (136个)
- ✅ 双语术语一致性
- ✅ 重复项检测
- ✅ 数据质量检查

**测试结果**: 🎉 141/141 通过 (100%)

### 2. 后端单元测试 ✅

**位置**: `/backend/tests/`

**框架**: Pytest + pytest-cov

**运行方式**:
```bash
cd backend
./run_tests.sh              # 完整测试+覆盖率
./run_tests.sh quick        # 快速测试
./run_tests.sh api          # 只测试API
./run_tests.sh model        # 只测试模型
```

**测试文件**:

| 文件 | 测试内容 | 测试数 |
|-----|---------|-------|
| `test_api_auth.py` | 认证API | 7 |
| `test_api_roles.py` | 岗位API | 8 |
| `test_api_users.py` | 用户API | 7 |
| `test_models.py` | 数据模型 | 15+ |
| `test_init_data.py` | 初始化数据 | 17+ |

**测试标记**:
- `@pytest.mark.api` - API端点测试
- `@pytest.mark.model` - 数据模型测试
- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.auth` - 认证测试

### 3. 前端单元测试 (待实现)

**计划工具**: Vitest + Vue Test Utils

**测试范围**:
- [ ] 组件测试
- [ ] Store测试
- [ ] Router测试
- [ ] API调用测试
- [ ] 工具函数测试

### 4. 端到端测试 (待实现)

**计划工具**: Playwright 或 Cypress

**测试场景**:
- [ ] 用户登录流程
- [ ] 创建周计划
- [ ] 更新任务状态
- [ ] 周复盘流程
- [ ] 团队视图查看

---

## 快速开始

### 安装测试依赖

#### 数据验证测试
```bash
# 无需额外依赖，Python 3.9+即可
python3 test_comprehensive.py
```

#### 后端测试
```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
./run_tests.sh
```

### 运行所有测试

```bash
# 1. 数据验证测试
python3 test_comprehensive.py

# 2. 后端单元测试
cd backend && ./run_tests.sh

# 3. 前端测试 (待实现)
# cd frontend && npm run test
```

---

## 测试覆盖率

### 当前覆盖率

#### 数据验证
- **测试覆盖率**: 100% (141/141)
- **岗位覆盖**: 13/13 (100%)
- **任务类型**: 136/136 (100%)

#### 后端单元测试 (目标)
- **代码覆盖率目标**: 80%+
- **API端点覆盖**: 主要端点
- **模型覆盖**: 所有核心模型

### 查看覆盖率报告

```bash
cd backend

# 生成覆盖率报告
./run_tests.sh coverage

# 查看HTML报告
open htmlcov/index.html     # Mac
xdg-open htmlcov/index.html # Linux
start htmlcov/index.html    # Windows
```

---

## 测试策略

### 测试金字塔

```
        /\
       /E2\      少量E2E测试
      /----\
     /Integr\    中等集成测试
    /--------\
   /  Unit   \   大量单元测试
  /----------\
```

### 测试原则

1. **快速反馈** - 单元测试应在秒级完成
2. **独立性** - 测试之间互不影响
3. **可重复** - 每次运行结果一致
4. **有意义** - 测试真实业务场景
5. **可维护** - 测试代码也需要高质量

### 测试数据管理

#### 后端测试
- 使用SQLite内存数据库（`:memory:`）
- 每个测试有独立的数据库会话
- Fixtures提供常用测试数据

#### 测试用户
```python
# conftest.py中定义
test_admin_user      # 管理员
test_manager_user    # 经理
test_employee_user   # 员工
```

### 何时编写测试

- ✅ **新功能开发前** - TDD方式
- ✅ **Bug修复时** - 添加回归测试
- ✅ **重构前** - 确保行为不变
- ✅ **关键路径** - 核心业务逻辑

---

## 持续集成

### GitHub Actions (推荐配置)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run data validation tests
        run: python3 test_comprehensive.py

      - name: Run backend tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
```

### Pre-commit Hooks (推荐)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: bash -c 'cd backend && pytest'
        language: system
        pass_filenames: false
```

---

## 测试最佳实践

### ✅ 好的测试

```python
def test_user_login_success(client, test_user):
    """Test successful user login with valid credentials"""
    response = client.post(
        "/api/auth/login",
        data={"username": "test_user", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
```

**特点**:
- 清晰的测试名称
- 详细的文档字符串
- 使用Fixtures
- 明确的断言
- 测试一个场景

### ❌ 不好的测试

```python
def test_stuff(client):
    """Test"""
    r = client.post("/api/auth/login", data={"u": "a", "p": "b"})
    assert r.status_code == 200
    r2 = client.get("/api/users/1")
    assert len(r2.json()) > 0
```

**问题**:
- 名称不清晰
- 文档不足
- 硬编码数据
- 测试多个场景
- 断言不明确

---

## 测试工具参考

### 后端
- **Pytest**: https://docs.pytest.org/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/

### 前端 (计划)
- **Vitest**: https://vitest.dev/
- **Vue Test Utils**: https://test-utils.vuejs.org/

### E2E (计划)
- **Playwright**: https://playwright.dev/
- **Cypress**: https://www.cypress.io/

---

## 故障排除

### 常见问题

#### 1. 导入错误
```bash
# 确保在正确的目录
cd backend
# 确保依赖已安装
pip install -r requirements.txt
```

#### 2. 数据库错误
```bash
# 测试使用内存数据库，不应有文件残留
# 如有问题，检查conftest.py配置
```

#### 3. Fixture未找到
```bash
# 确保conftest.py在tests目录下
ls backend/tests/conftest.py
```

---

## 贡献测试

### 添加新测试

1. 在适当的测试文件中添加测试函数
2. 使用描述性的函数名：`test_<action>_<expected_result>`
3. 添加文档字符串说明测试内容
4. 使用适当的标记(`@pytest.mark.*`)
5. 运行测试确保通过
6. 提交Pull Request

### 测试命名规范

```
test_<被测功能>_<测试场景>_<预期结果>

例如:
test_user_login_with_valid_credentials_returns_token()
test_task_creation_without_auth_returns_401()
test_role_list_includes_all_13_positions()
```

---

## 测试报告

### 自动生成测试报告

运行全面测试后会自动生成：

1. **TEST_REPORT.md** - Markdown格式的详细报告
2. **test_results.json** - JSON格式的机器可读结果
3. **htmlcov/** - HTML覆盖率报告（后端）

### 查看报告

```bash
# 查看测试摘要
cat TEST_REPORT.md

# 查看JSON结果
cat test_results.json | python3 -m json.tool

# 查看覆盖率
open backend/htmlcov/index.html
```

---

## 路线图

### 已完成 ✅
- [x] 数据完整性测试框架
- [x] 后端单元测试框架
- [x] API端点测试
- [x] 数据模型测试
- [x] 业务逻辑测试
- [x] 测试文档

### 计划中 📋
- [ ] 前端单元测试
- [ ] E2E测试框架
- [ ] 性能测试
- [ ] 负载测试
- [ ] 安全测试
- [ ] CI/CD集成

---

<div align="center">

**📊 测试是质量的保证 📊**

*编写测试，睡得更香*

</div>
