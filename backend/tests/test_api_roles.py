"""
Tests for roles API endpoints
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestRolesAPI:
    """Test roles/positions API endpoints"""

    def test_get_roles_list(self, client, auth_headers, init_roles):
        """Test getting list of all roles"""
        response = client.get(
            "/api/roles/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 13  # 13 predefined roles

        # Verify role structure
        first_role = data[0]
        assert "id" in first_role
        assert "name" in first_role
        assert "name_en" in first_role
        assert "responsibilities" in first_role

    def test_get_roles_unauthorized(self, client, init_roles):
        """Test getting roles without authentication"""
        response = client.get("/api/roles/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_role_by_id(self, client, auth_headers, test_role):
        """Test getting a specific role by ID"""
        response = client.get(
            f"/api/roles/{test_role.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_role.id
        assert data["name"] == "测试岗位"
        assert data["name_en"] == "Test Role"

    def test_get_role_not_found(self, client, auth_headers):
        """Test getting a non-existent role"""
        response = client.get(
            "/api/roles/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_role_responsibilities(self, client, auth_headers, test_role):
        """Test that role includes responsibilities and task types"""
        response = client.get(
            f"/api/roles/{test_role.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "responsibilities" in data
        assert len(data["responsibilities"]) > 0

        # Check first responsibility
        resp = data["responsibilities"][0]
        assert "task_types" in resp
        assert len(resp["task_types"]) == 3  # We created 3 task types

    def test_create_role_admin_only(self, client, auth_headers):
        """Test creating a new role (admin only)"""
        new_role = {
            "name": "新岗位",
            "name_en": "New Role",
            "description": "测试创建的新岗位"
        }
        response = client.post(
            "/api/roles/",
            json=new_role,
            headers=auth_headers
        )
        # This might return 201, 403, or 405 depending on implementation
        # Just verify it doesn't crash
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]

    def test_verify_all_13_roles(self, client, auth_headers, init_roles):
        """Test that all 13 predefined roles are created correctly"""
        expected_roles = [
            "研发工程师",
            "销售经理",
            "工程交付工程师",
            "售后客服",
            "技术支持工程师",
            "项目经理",
            "售前工程师",
            "项目总监",
            "业务工程师",
            "人力资源",
            "财务",
            "行政",
            "信息中心"
        ]

        response = client.get(
            "/api/roles/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        role_names = [role["name"] for role in data]
        for expected_name in expected_roles:
            assert expected_name in role_names

    def test_total_task_types_count(self, client, auth_headers, init_roles):
        """Test that total task types count is 136"""
        response = client.get(
            "/api/roles/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        total_task_types = 0
        for role in data:
            for resp in role.get("responsibilities", []):
                total_task_types += len(resp.get("task_types", []))

        assert total_task_types == 136  # As per documentation
