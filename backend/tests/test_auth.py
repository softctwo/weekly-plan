"""
认证API测试
测试登录、token生成等功能
"""
import pytest
from fastapi import status


@pytest.mark.unit
class TestAuth:
    """认证相关测试"""

    def test_login_success(self, client, test_user):
        """测试成功登录"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.username,
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client):
        """测试无效用户名登录"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent",
                "password": "password"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "用户名或密码错误" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user):
        """测试错误密码登录"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, test_user, db_session):
        """测试停用用户登录"""
        # 停用用户
        test_user.is_active = False
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.username,
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "已被停用" in response.json()["detail"]

    def test_access_protected_route_without_token(self, client):
        """测试未认证访问受保护路由"""
        response = client.get("/api/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_route_with_token(self, client, auth_headers):
        """测试认证后访问受保护路由"""
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "username" in data
        assert "email" in data
