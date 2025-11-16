"""
测试配置文件
提供pytest fixtures供所有测试使用
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, Department
from app.models.role import Role, Responsibility, TaskType


# 测试数据库配置 - 使用内存SQLite
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    创建测试数据库会话

    每个测试函数都会创建一个新的数据库会话
    测试完成后自动清理
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    创建测试客户端

    覆盖app的数据库依赖，使用测试数据库
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_department(db_session):
    """创建测试部门"""
    department = Department(
        name="测试部门",
        description="测试用部门"
    )
    db_session.add(department)
    db_session.commit()
    db_session.refresh(department)
    return department


@pytest.fixture
def test_user(db_session, test_department):
    """创建测试用户（普通员工）"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="测试用户",
        user_type="employee",
        department_id=test_department.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session, test_department):
    """创建测试管理员"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="管理员",
        user_type="admin",
        department_id=test_department.id,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_manager(db_session, test_department):
    """创建测试管理者"""
    manager = User(
        username="manager",
        email="manager@example.com",
        hashed_password=get_password_hash("manager123"),
        full_name="经理",
        user_type="manager",
        department_id=test_department.id,
        is_active=True
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


@pytest.fixture
def test_role(db_session):
    """创建测试岗位"""
    role = Role(
        name="研发工程师",
        name_en="R&D Engineer",
        description="研发岗位",
        is_active=True
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def test_responsibility(db_session, test_role):
    """创建测试职责"""
    responsibility = Responsibility(
        name="需求分析与技术设计",
        description="分析需求并设计技术方案",
        role_id=test_role.id,
        sort_order=1,
        is_active=True
    )
    db_session.add(responsibility)
    db_session.commit()
    db_session.refresh(responsibility)
    return responsibility


@pytest.fixture
def test_task_type(db_session, test_responsibility):
    """创建测试任务类型"""
    task_type = TaskType(
        name="需求文档编写",
        description="编写需求规格说明书",
        responsibility_id=test_responsibility.id,
        sort_order=1,
        is_active=True
    )
    db_session.add(task_type)
    db_session.commit()
    db_session.refresh(task_type)
    return task_type


@pytest.fixture
def auth_headers(client, test_user):
    """
    获取认证头

    返回包含有效JWT token的headers
    """
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """获取管理员认证头"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_admin.username,
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
