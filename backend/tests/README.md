# Backend Tests

Backend单元测试和集成测试套件。

## 测试结构

```
tests/
├── conftest.py              # Pytest fixtures和配置
├── test_api_auth.py         # 认证API测试
├── test_api_roles.py        # 岗位职责API测试
├── test_api_users.py        # 用户管理API测试
├── test_models.py           # 数据模型测试
├── test_init_data.py        # 初始化数据测试
└── README.md                # 本文件
```

## 安装依赖

```bash
cd backend

# 安装测试依赖
pip install pytest pytest-cov httpx

# 或者更新requirements.txt后安装
pip install -r requirements.txt
```

## 运行测试

### 运行所有测试

```bash
# 在backend目录下运行
pytest

# 或使用详细输出
pytest -v
```

### 运行特定测试文件

```bash
pytest tests/test_api_auth.py
pytest tests/test_models.py
```

### 运行特定测试类或函数

```bash
pytest tests/test_api_auth.py::TestAuthAPI
pytest tests/test_models.py::TestUserModel::test_create_user
```

### 使用标记运行测试

```bash
# 只运行API测试
pytest -m api

# 只运行模型测试
pytest -m model

# 只运行单元测试
pytest -m unit

# 只运行认证测试
pytest -m auth
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# HTML格式报告
pytest --cov=app --cov-report=html

# 查看HTML报告（在浏览器中打开）
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# 终端显示
pytest --cov=app --cov-report=term-missing

# 只显示总体覆盖率
pytest --cov=app --cov-report=term
```

### 分支覆盖

```bash
pytest --cov=app --cov-branch --cov-report=html
```

## 测试标记

系统使用以下pytest标记来分类测试：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.api` - API端点测试
- `@pytest.mark.model` - 数据模型测试
- `@pytest.mark.auth` - 认证测试
- `@pytest.mark.slow` - 慢速测试

## Fixtures

### 数据库Fixtures

- `db_session` - 新鲜的数据库会话
- `client` - FastAPI测试客户端
- `init_roles` - 初始化13个岗位

### 用户Fixtures

- `test_admin_user` - 测试管理员
- `test_manager_user` - 测试经理
- `test_employee_user` - 测试员工
- `test_department` - 测试部门

### 认证Fixtures

- `admin_token` - 管理员JWT token
- `manager_token` - 经理JWT token
- `employee_token` - 员工JWT token
- `auth_headers` - 管理员认证头
- `manager_headers` - 经理认证头
- `employee_headers` - 员工认证头

### 岗位Fixtures

- `test_role` - 测试岗位（含职责和任务类型）

## 测试数据

所有测试使用SQLite内存数据库（`:memory:`），确保：

1. 测试之间相互隔离
2. 测试速度快
3. 不影响开发或生产数据库

## 编写新测试

### 测试命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`

### 示例测试

```python
import pytest
from fastapi import status


@pytest.mark.api
class TestMyAPI:
    """My API tests"""

    def test_something(self, client, auth_headers):
        """Test description"""
        response = client.get(
            "/api/endpoint",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["key"] == "value"
```

## 持续集成

测试可以集成到CI/CD流程中：

```yaml
# .github/workflows/test.yml 示例
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v2
  with:
    file: ./backend/coverage.xml
```

## 故障排除

### ImportError

如果遇到导入错误，确保：

1. 在`backend`目录下运行pytest
2. 已安装所有依赖：`pip install -r requirements.txt`

### Database Errors

如果遇到数据库错误：

1. 确保测试使用内存数据库（检查conftest.py）
2. 清理任何残留的测试数据库文件

### Fixture Not Found

确保：

1. `conftest.py`存在于`tests/`目录
2. Fixture名称正确
3. Fixture的scope设置正确

## 最佳实践

1. **保持测试独立** - 每个测试应该独立运行
2. **使用Fixtures** - 重用测试数据和设置
3. **清晰的断言** - 使用有意义的断言消息
4. **测试边界情况** - 不仅测试正常流程
5. **快速测试** - 保持测试运行快速
6. **有意义的测试名** - 测试名应该描述测试内容

## 参考资料

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
