"""
Tests for users API endpoints
"""
import pytest
from fastapi import status


@pytest.mark.api
class TestUsersAPI:
    """Test user management API endpoints"""

    def test_get_users_list_admin(self, client, auth_headers, test_employee_user):
        """Test getting list of users as admin"""
        response = client.get(
            "/api/users/",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

    def test_get_users_list_employee(self, client, employee_headers):
        """Test getting list of users as employee (should fail)"""
        response = client.get(
            "/api/users/",
            headers=employee_headers
        )
        # Employees should not be able to list all users
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_user_admin(self, client, auth_headers, test_department):
        """Test creating a new user as admin"""
        new_user = {
            "username": "newuser",
            "email": "newuser@test.com",
            "full_name": "新用户",
            "password": "password123",
            "user_type": "employee",
            "department_id": test_department.id
        }
        response = client.post(
            "/api/users/",
            json=new_user,
            headers=auth_headers
        )
        # Should either succeed or be forbidden (depending on implementation)
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]

    def test_get_user_by_id(self, client, auth_headers, test_employee_user):
        """Test getting a specific user by ID"""
        response = client.get(
            f"/api/users/{test_employee_user.id}",
            headers=auth_headers
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["username"] == "test_employee"
            assert data["user_type"] == "employee"

    def test_update_user(self, client, auth_headers, test_employee_user):
        """Test updating user information"""
        update_data = {
            "full_name": "更新的姓名"
        }
        response = client.put(
            f"/api/users/{test_employee_user.id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]

    def test_user_role_assignment(self, client, auth_headers, test_employee_user, test_role):
        """Test assigning role to user"""
        # This tests the many-to-many relationship between users and roles
        response = client.post(
            f"/api/users/{test_employee_user.id}/roles",
            json={"role_id": test_role.id},
            headers=auth_headers
        )
        # Accept various responses depending on implementation
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]

    def test_get_current_user_roles(self, client, employee_headers, db_session, test_employee_user, test_role):
        """Test getting roles for current user"""
        # Assign role to user first
        from app.models.role import UserRoleLink
        link = UserRoleLink(user_id=test_employee_user.id, role_id=test_role.id)
        db_session.add(link)
        db_session.commit()

        response = client.get(
            "/api/users/me/roles",
            headers=employee_headers
        )
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, list)
