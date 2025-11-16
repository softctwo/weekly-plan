"""
Tests for authentication API endpoints
"""
import pytest
from fastapi import status


@pytest.mark.api
@pytest.mark.auth
class TestAuthAPI:
    """Test authentication endpoints"""

    def test_login_success(self, client, test_admin_user):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test_admin",
                "password": "admin123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent",
                "password": "password"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_password(self, client, test_admin_user):
        """Test login with invalid password"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "test_admin",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, db_session, test_admin_user):
        """Test login with inactive user"""
        # Deactivate user
        test_admin_user.is_active = False
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            data={
                "username": "test_admin",
                "password": "admin123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, test_admin_user, auth_headers):
        """Test getting current user information"""
        response = client.get(
            "/api/users/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "test_admin"
        assert data["email"] == "admin@test.com"
        assert data["user_type"] == "admin"

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
