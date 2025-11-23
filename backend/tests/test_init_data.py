"""
Tests for initialization data logic
"""
import pytest

from app.utils.init_data import init_roles_and_responsibilities
from app.models.role import Role, Responsibility, TaskType


@pytest.mark.unit
class TestInitDataFunction:
    """Test initialization data function"""

    def test_init_roles_function_exists(self):
        """Test that init_roles_and_responsibilities function exists"""
        assert callable(init_roles_and_responsibilities)

    def test_init_roles_creates_data(self, db_session):
        """Test that init_roles_and_responsibilities creates data"""
        # Verify database is empty initially
        roles = db_session.query(Role).all()
        assert len(roles) == 0

        # Call the function
        init_roles_and_responsibilities(db_session)

        # Verify data was created
        roles = db_session.query(Role).all()
        assert len(roles) == 13, f"Expected 13 roles, got {len(roles)}"


@pytest.mark.unit
@pytest.mark.integration
class TestInitDataDatabaseCreation:
    """Test that initialization data creates proper database entries"""

    def test_roles_created_in_db(self, db_session, init_roles):
        """Test that all roles are created in database"""
        roles = db_session.query(Role).all()
        assert len(roles) == 13

    def test_responsibilities_created_in_db(self, db_session, init_roles):
        """Test that all responsibilities are created"""
        responsibilities = db_session.query(Responsibility).all()
        assert len(responsibilities) == 45  # Total responsibilities

    def test_task_types_created_in_db(self, db_session, init_roles):
        """Test that all task types are created"""
        task_types = db_session.query(TaskType).all()
        assert len(task_types) == 136  # Total task types

    def test_all_roles_have_required_fields(self, db_session, init_roles):
        """Test that all roles have required fields in database"""
        roles = db_session.query(Role).all()

        for role in roles:
            assert role.name, "Role name should not be empty"
            assert role.name_en, "Role English name should not be empty"
            assert role.description, "Role description should not be empty"

    def test_all_responsibilities_have_task_types(self, db_session, init_roles):
        """Test that all responsibilities have task types in database"""
        responsibilities = db_session.query(Responsibility).all()

        for resp in responsibilities:
            assert resp.name, "Responsibility name should not be empty"
            task_types = db_session.query(TaskType).filter(
                TaskType.responsibility_id == resp.id
            ).all()
            assert len(task_types) > 0, f"Responsibility '{resp.name}' has no task types"

    def test_data_relationships_integrity(self, db_session, init_roles):
        """Test data relationships integrity"""
        roles = db_session.query(Role).all()

        for role in roles:
            # Each role should have responsibilities
            assert len(role.responsibilities) > 0, f"Role '{role.name}' has no responsibilities"

            # Each responsibility should have task types
            for resp in role.responsibilities:
                assert len(resp.task_types) > 0, \
                    f"Responsibility '{resp.name}' in role '{role.name}' has no task types"

    def test_specific_roles_exist(self, db_session, init_roles):
        """Test that specific expected roles exist"""
        expected_roles = [
            "研发工程师", "销售经理", "工程交付工程师", "售后客服",
            "技术支持工程师", "项目经理", "售前工程师", "项目总监",
            "业务工程师", "人力资源", "财务", "行政", "信息中心"
        ]

        actual_roles = [role.name for role in db_session.query(Role).all()]

        for expected_role in expected_roles:
            assert expected_role in actual_roles, f"Role '{expected_role}' not found in database"

    def test_no_duplicate_role_names(self, db_session, init_roles):
        """Test that there are no duplicate role names"""
        roles = db_session.query(Role).all()
        role_names = [role.name for role in roles]
        assert len(role_names) == len(set(role_names)), "Duplicate role names found"

    def test_task_types_count_per_role(self, db_session, init_roles):
        """Test task types count for specific roles"""
        expected_counts = {
            "研发工程师": 13,
            "销售经理": 13,
            "工程交付工程师": 16,
            "售后客服": 8,
            "技术支持工程师": 9,
            "项目经理": 11,
            "售前工程师": 12,
            "项目总监": 13,
            "业务工程师": 14,
            "人力资源": 6,
            "财务": 7,
            "行政": 6,
            "信息中心": 8
        }

        for role in db_session.query(Role).all():
            role_name = role.name
            task_count = sum(len(r.task_types) for r in role.responsibilities)

            if role_name in expected_counts:
                assert task_count == expected_counts[role_name], \
                    f"{role_name}: expected {expected_counts[role_name]}, got {task_count}"