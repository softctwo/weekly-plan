"""
Pytest configuration and fixtures for weekly-plan tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.api.deps import get_db
from app.core.security import get_password_hash
from app.models.user import User, Department
from app.models.role import Role, Responsibility, TaskType
from app.utils.init_data import init_roles_and_responsibilities


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session"""
    from app.api.deps import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # 测试模式下关闭限流等副作用
    settings.TESTING = True
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_department(db_session):
    """Create a test department"""
    dept = Department(name="测试部门", description="用于测试的部门")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture(scope="function")
def test_admin_user(db_session, test_department, init_roles):
    """Create a test admin user with role association"""
    admin = User(
        username="test_admin",
        email="admin@test.com",
        full_name="测试管理员",
        hashed_password=get_password_hash("admin123"),
        user_type="admin",
        department_id=test_department.id,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    # 为管理员用户关联第一个岗位
    from app.models.role import Role
    first_role = db_session.query(Role).first()
    if first_role:
        admin.roles.append(first_role)
        db_session.commit()
    
    return admin


@pytest.fixture(scope="function")
def test_manager_user(db_session, test_department):
    """Create a test manager user"""
    manager = User(
        username="test_manager",
        email="manager@test.com",
        full_name="测试经理",
        hashed_password=get_password_hash("manager123"),
        user_type="manager",
        department_id=test_department.id,
        is_active=True
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


@pytest.fixture(scope="function")
def test_employee_user(db_session, test_department, test_manager_user):
    """Create a test employee user"""
    employee = User(
        username="test_employee",
        email="employee@test.com",
        full_name="测试员工",
        hashed_password=get_password_hash("employee123"),
        user_type="employee",
        department_id=test_department.id,
        manager_id=test_manager_user.id,
        is_active=True
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


@pytest.fixture(scope="function")
def test_role(db_session):
    """Create a test role with responsibilities and task types"""
    role = Role(
        name="测试岗位",
        name_en="Test Role",
        description="用于测试的岗位"
    )
    db_session.add(role)
    db_session.flush()

    # Add a responsibility
    resp = Responsibility(
        role_id=role.id,
        name="测试职责",
        sort_order=1
    )
    db_session.add(resp)
    db_session.flush()

    # Add task types
    for i in range(3):
        task_type = TaskType(
            responsibility_id=resp.id,
            name=f"测试任务类型{i+1}",
            sort_order=i+1
        )
        db_session.add(task_type)

    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def init_roles(db_session):
    """Initialize all 13 roles from init_data"""
    init_roles_and_responsibilities(db_session)
    return db_session.query(Role).all()


@pytest.fixture(scope="function")
def admin_token(client, test_admin_user):
    """Get authentication token for admin user"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test_admin",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def manager_token(client, test_manager_user):
    """Get authentication token for manager user"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test_manager",
            "password": "manager123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def employee_token(client, test_employee_user):
    """Get authentication token for employee user"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test_employee",
            "password": "employee123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(admin_token):
    """Get authorization headers for admin"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def manager_headers(manager_token):
    """Get authorization headers for manager"""
    return {"Authorization": f"Bearer {manager_token}"}


@pytest.fixture(scope="function")
def employee_headers(employee_token):
    """Get authorization headers for employee"""
    return {"Authorization": f"Bearer {employee_token}"}
