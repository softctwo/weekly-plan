"""
Tests for initialization data logic
"""
import pytest

from app.utils.init_data import roles_data
from app.models.role import Role, Responsibility, TaskType


@pytest.mark.unit
class TestInitDataStructure:
    """Test initialization data structure and integrity"""

    def test_roles_data_exists(self):
        """Test that roles_data is defined and not empty"""
        assert roles_data is not None
        assert isinstance(roles_data, list)
        assert len(roles_data) > 0

    def test_13_roles_defined(self):
        """Test that exactly 13 roles are defined"""
        assert len(roles_data) == 13

    def test_all_roles_have_required_fields(self):
        """Test that all roles have required fields"""
        required_fields = ["name", "name_en", "description", "responsibilities"]

        for role in roles_data:
            for field in required_fields:
                assert field in role, f"Role missing field: {field}"
                assert role[field] is not None

    def test_all_responsibilities_have_task_types(self):
        """Test that all responsibilities have task types"""
        for role in roles_data:
            for resp in role["responsibilities"]:
                assert "name" in resp
                assert "task_types" in resp
                assert isinstance(resp["task_types"], list)
                assert len(resp["task_types"]) > 0

    def test_total_task_types_count(self):
        """Test that total task types count is 136"""
        total = 0
        for role in roles_data:
            for resp in role["responsibilities"]:
                total += len(resp["task_types"])

        assert total == 136, f"Expected 136 task types, got {total}"

    def test_specific_role_counts(self):
        """Test task type counts for specific roles"""
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

        for role in roles_data:
            role_name = role["name"]
            task_count = sum(len(r["task_types"]) for r in role["responsibilities"])

            if role_name in expected_counts:
                assert task_count == expected_counts[role_name], \
                    f"{role_name}: expected {expected_counts[role_name]}, got {task_count}"

    def test_no_duplicate_role_names(self):
        """Test that there are no duplicate role names"""
        role_names = [role["name"] for role in roles_data]
        assert len(role_names) == len(set(role_names)), "Duplicate role names found"

    def test_no_duplicate_role_names_en(self):
        """Test that there are no duplicate English role names"""
        role_names_en = [role["name_en"] for role in roles_data]
        assert len(role_names_en) == len(set(role_names_en)), \
            "Duplicate English role names found"

    def test_no_duplicate_task_types_within_role(self):
        """Test that there are no duplicate task types within each role"""
        for role in roles_data:
            all_tasks = []
            for resp in role["responsibilities"]:
                all_tasks.extend(resp["task_types"])

            assert len(all_tasks) == len(set(all_tasks)), \
                f"Duplicate task types found in role: {role['name']}"

    def test_bilingual_consistency(self):
        """Test that all roles have both Chinese and English names"""
        for role in roles_data:
            # Chinese name should contain Chinese characters
            assert any('\u4e00' <= char <= '\u9fff' for char in role["name"]), \
                f"Role name should contain Chinese characters: {role['name']}"

            # English name should be non-empty and not same as Chinese name
            assert role["name_en"], "English name should not be empty"
            assert role["name"] != role["name_en"], \
                "Chinese and English names should be different"

    def test_descriptions_not_empty(self):
        """Test that all roles have non-empty descriptions"""
        for role in roles_data:
            assert role["description"], f"Description is empty for role: {role['name']}"
            assert len(role["description"]) > 5, \
                f"Description too short for role: {role['name']}"

    def test_responsibility_structure(self):
        """Test responsibility structure consistency"""
        for role in roles_data:
            for resp in role["responsibilities"]:
                # Each responsibility should have a name
                assert "name" in resp
                assert resp["name"], "Responsibility name should not be empty"

                # Each responsibility should have task types
                assert "task_types" in resp
                assert isinstance(resp["task_types"], list)
                assert len(resp["task_types"]) >= 1, \
                    f"Responsibility should have at least 1 task type: {resp['name']}"

    def test_task_type_names_not_empty(self):
        """Test that all task type names are non-empty"""
        for role in roles_data:
            for resp in role["responsibilities"]:
                for task_type in resp["task_types"]:
                    assert task_type, \
                        f"Empty task type found in {role['name']} - {resp['name']}"
                    assert len(task_type) >= 2, \
                        f"Task type name too short: {task_type}"

    def test_added_task_types(self):
        """Test that the 4 newly added task types exist"""
        newly_added_tasks = {
            "研发工程师": "集成测试编写",
            "售前工程师": "竞品分析与对比",
            "业务工程师": "业务需求文档评审",
            "信息中心": "IT资产管理与盘点"
        }

        for role in roles_data:
            if role["name"] in newly_added_tasks:
                all_tasks = []
                for resp in role["responsibilities"]:
                    all_tasks.extend(resp["task_types"])

                expected_task = newly_added_tasks[role["name"]]
                assert expected_task in all_tasks, \
                    f"New task '{expected_task}' not found in {role['name']}"


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

    def test_role_data_integrity(self, db_session, init_roles):
        """Test data integrity of created roles"""
        for role_data in roles_data:
            # Find role in database
            role = db_session.query(Role).filter(
                Role.name == role_data["name"]
            ).first()

            assert role is not None, f"Role not found: {role_data['name']}"
            assert role.name_en == role_data["name_en"]
            assert role.description == role_data["description"]

            # Verify responsibilities count
            assert len(role.responsibilities) == len(role_data["responsibilities"])

            # Verify task types count
            total_task_types_data = sum(
                len(r["task_types"]) for r in role_data["responsibilities"]
            )
            total_task_types_db = sum(
                len(r.task_types) for r in role.responsibilities
            )
            assert total_task_types_db == total_task_types_data
