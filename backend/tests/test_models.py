"""
Tests for database models
"""
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User, Department
from app.models.role import Role, Responsibility, TaskType, UserRoleLink
from app.models.task import WeeklyTask
from app.core.security import verify_password


@pytest.mark.model
class TestUserModel:
    """Test User model"""

    def test_create_user(self, db_session, test_department):
        """Test creating a user"""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_pw",
            user_type="employee",
            department_id=test_department.id
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.is_active is True

    def test_user_unique_username(self, db_session, test_employee_user):
        """Test that username must be unique"""
        duplicate_user = User(
            username="test_employee",  # Same as test_employee_user
            email="different@example.com",
            full_name="Different User",
            hashed_password="hashed_pw",
            user_type="employee"
        )
        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_unique_email(self, db_session, test_employee_user):
        """Test that email must be unique"""
        duplicate_user = User(
            username="different_username",
            email="employee@test.com",  # Same as test_employee_user
            full_name="Different User",
            hashed_password="hashed_pw",
            user_type="employee"
        )
        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_password_hashing(self, test_admin_user):
        """Test that password is properly hashed"""
        # Password should be hashed, not plain text
        assert test_admin_user.hashed_password != "admin123"
        assert verify_password("admin123", test_admin_user.hashed_password)

    def test_user_manager_relationship(self, db_session, test_manager_user, test_employee_user):
        """Test user-manager relationship"""
        assert test_employee_user.manager_id == test_manager_user.id
        assert test_employee_user.manager == test_manager_user

    def test_department_relationship(self, test_employee_user, test_department):
        """Test user-department relationship"""
        assert test_employee_user.department_id == test_department.id
        assert test_employee_user.department == test_department


@pytest.mark.model
class TestRoleModel:
    """Test Role, Responsibility, and TaskType models"""

    def test_create_role(self, db_session):
        """Test creating a role"""
        role = Role(
            name="测试岗位",
            name_en="Test Role",
            description="测试描述"
        )
        db_session.add(role)
        db_session.commit()

        assert role.id is not None
        assert role.name == "测试岗位"
        assert role.is_active is True

    def test_role_responsibility_relationship(self, db_session, test_role):
        """Test role-responsibility relationship"""
        responsibilities = test_role.responsibilities
        assert len(responsibilities) > 0
        assert responsibilities[0].role_id == test_role.id

    def test_responsibility_task_types_relationship(self, db_session, test_role):
        """Test responsibility-task_types relationship"""
        resp = test_role.responsibilities[0]
        task_types = resp.task_types

        assert len(task_types) == 3  # We created 3 task types
        assert all(tt.responsibility_id == resp.id for tt in task_types)

    def test_role_cascade_delete(self, db_session, test_role):
        """Test that deleting role soft-deletes related entities"""
        role_id = test_role.id

        # Deactivate role (soft delete)
        test_role.is_active = False
        db_session.commit()

        # Role should still exist but be inactive
        role = db_session.query(Role).filter(Role.id == role_id).first()
        assert role is not None
        assert role.is_active is False

    def test_user_role_link(self, db_session, test_employee_user, test_role):
        """Test user-role many-to-many relationship"""
        link = UserRoleLink(
            user_id=test_employee_user.id,
            role_id=test_role.id
        )
        db_session.add(link)
        db_session.commit()

        # Verify link exists
        links = db_session.query(UserRoleLink).filter(
            UserRoleLink.user_id == test_employee_user.id
        ).all()
        assert len(links) == 1
        assert links[0].role_id == test_role.id

    def test_13_roles_initialization(self, db_session, init_roles):
        """Test that all 13 roles are initialized correctly"""
        roles = db_session.query(Role).all()
        assert len(roles) == 13

        # Verify all roles have responsibilities
        for role in roles:
            assert len(role.responsibilities) > 0

            # Verify all responsibilities have task types
            for resp in role.responsibilities:
                assert len(resp.task_types) > 0


@pytest.mark.model
class TestTaskModel:
    """Test WeeklyTask model"""

    def test_create_weekly_task(self, db_session, test_employee_user, test_role):
        """Test creating a weekly task with time attributes and role association"""
        from app.models.role import TaskType
        
        # 获取一个任务类型用于关联
        task_type = db_session.query(TaskType).first()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        planned_end = now + timedelta(hours=2)
        
        task = WeeklyTask(
            user_id=test_employee_user.id,
            year=2025,
            week_number=46,
            title="测试任务",
            description="任务描述",
            status="todo",
            is_key_task=False,
            linked_task_type_id=task_type.id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=120  # 2小时
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.title == "测试任务"
        assert task.status == "todo"
        assert task.linked_task_type_id == task_type.id
        assert task.planned_duration == 120

    def test_task_user_relationship(self, db_session, test_employee_user, test_role):
        """Test task-user relationship with role association"""
        from app.models.role import TaskType
        
        # 获取一个任务类型用于关联
        task_type = db_session.query(TaskType).first()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        task = WeeklyTask(
            user_id=test_employee_user.id,
            year=2025,
            week_number=46,
            title="测试任务",
            status="todo",
            linked_task_type_id=task_type.id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )
        db_session.add(task)
        db_session.commit()

        assert task.user == test_employee_user
        assert task.linked_task_type_id == task_type.id

    def test_task_status_values(self, db_session, test_employee_user, test_role):
        """Test task status values with time attributes"""
        from app.models.role import TaskType
        
        # 获取一个任务类型用于关联
        task_type = db_session.query(TaskType).first()
        
        valid_statuses = ["todo", "in_progress", "completed", "delayed"]

        for status in valid_statuses:
            from datetime import datetime, timedelta
            now = datetime.now()
            planned_end = now + timedelta(minutes=30)
            
            task = WeeklyTask(
                user_id=test_employee_user.id,
                year=2025,
                week_number=46,
                title=f"Task {status}",
                status=status,
                linked_task_type_id=task_type.id,  # 强制关联岗责
                planned_start_time=now,
                planned_end_time=planned_end,
                planned_duration=30  # 30分钟
            )
            db_session.add(task)

        db_session.commit()

        tasks = db_session.query(WeeklyTask).all()
        assert len(tasks) == len(valid_statuses)

    def test_key_task_flag(self, db_session, test_employee_user, test_role):
        """Test key task flagging with time attributes"""
        from app.models.role import TaskType
        
        # 获取一个任务类型用于关联
        task_type = db_session.query(TaskType).first()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        normal_task = WeeklyTask(
            user_id=test_employee_user.id,
            year=2025,
            week_number=46,
            title="普通任务",
            status="todo",
            is_key_task=False,
            linked_task_type_id=task_type.id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )

        key_task = WeeklyTask(
            user_id=test_employee_user.id,
            year=2025,
            week_number=46,
            title="重点任务",
            status="todo",
            is_key_task=True,
            linked_task_type_id=task_type.id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )

        db_session.add_all([normal_task, key_task])
        db_session.commit()

        # Query key tasks
        key_tasks = db_session.query(WeeklyTask).filter(
            WeeklyTask.is_key_task == True
        ).all()

        assert len(key_tasks) == 1
        assert key_tasks[0].title == "重点任务"
