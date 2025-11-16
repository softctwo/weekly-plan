"""
任务管理API测试
测试任务创建、查询、更新等功能
"""
import pytest
from fastapi import status
from app.models.task import TaskStatus


@pytest.mark.unit
class TestTasks:
    """任务管理测试"""

    def test_create_task(self, client, auth_headers):
        """测试创建任务"""
        task_data = {
            "title": "测试任务",
            "description": "这是一个测试任务",
            "year": 2025,
            "week_number": 202501,
            "status": "todo",
            "is_key_task": True,
            "source_type": "responsibility"
        }

        response = client.post(
            "/api/tasks/",
            json=task_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["is_key_task"] is True
        assert "id" in data

    def test_get_my_tasks(self, client, auth_headers, db_session, test_user):
        """测试获取我的任务列表"""
        # 先创建一个任务
        from app.models.task import WeeklyTask

        task = WeeklyTask(
            user_id=test_user.id,
            title="测试任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility"
        )
        db_session.add(task)
        db_session.commit()

        # 获取任务列表
        response = client.get("/api/tasks/my-tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert len(tasks) > 0
        assert tasks[0]["title"] == "测试任务"

    def test_get_my_tasks_with_filters(self, client, auth_headers, db_session, test_user):
        """测试带过滤条件获取任务"""
        from app.models.task import WeeklyTask

        # 创建重点任务和普通任务
        key_task = WeeklyTask(
            user_id=test_user.id,
            title="重点任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=True,
            source_type="responsibility"
        )
        normal_task = WeeklyTask(
            user_id=test_user.id,
            title="普通任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="personal"
        )
        db_session.add_all([key_task, normal_task])
        db_session.commit()

        # 只获取重点任务
        response = client.get(
            "/api/tasks/my-tasks?is_key_task=true",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["is_key_task"] is True

    def test_update_task(self, client, auth_headers, db_session, test_user):
        """测试更新任务"""
        from app.models.task import WeeklyTask

        task = WeeklyTask(
            user_id=test_user.id,
            title="原始任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility"
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 更新任务
        update_data = {
            "title": "更新后的任务",
            "status": "completed"
        }

        response = client.put(
            f"/api/tasks/{task.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "更新后的任务"
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_update_other_user_task_forbidden(
        self, client, auth_headers, db_session, test_admin
    ):
        """测试更新其他用户的任务（应被拒绝）"""
        from app.models.task import WeeklyTask

        # 创建属于admin的任务
        task = WeeklyTask(
            user_id=test_admin.id,
            title="管理员任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility"
        )
        db_session.add(task)
        db_session.commit()

        # 普通用户尝试更新
        response = client.put(
            f"/api/tasks/{task.id}",
            json={"title": "尝试修改"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_task(self, client, auth_headers, db_session, test_user):
        """测试删除任务"""
        from app.models.task import WeeklyTask

        task = WeeklyTask(
            user_id=test_user.id,
            title="待删除任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility"
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 删除任务
        response = client.delete(
            f"/api/tasks/{task.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        # 验证任务已被删除
        response = client.get(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
