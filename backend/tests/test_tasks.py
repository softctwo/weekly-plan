"""
任务管理API测试
测试任务创建、查询、更新等功能
"""
import pytest
from fastapi import status
from app.models.task import TaskStatus, FollowUpAction
from datetime import datetime, timedelta


@pytest.mark.unit
class TestTasks:
    """任务管理测试"""

    def test_create_task(self, client, auth_headers, init_roles):
        """测试创建任务 - 包含时间属性和岗责关联"""
        from datetime import datetime, timedelta
        
        # 获取一个任务类型ID用于关联
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break
        
        assert task_type_id is not None, "没有找到可用的任务类型"
        
        now = datetime.now()
        planned_end = now + timedelta(hours=2)
        
        task_data = {
            "title": "测试任务",
            "description": "这是一个测试任务",
            "year": 2025,
            "week_number": 202501,
            "status": "todo",
            "is_key_task": True,
            "source_type": "responsibility",
            "linked_task_type_id": task_type_id,  # 强制关联岗责
            "planned_start_time": now.isoformat(),
            "planned_end_time": planned_end.isoformat()
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
        assert data["linked_task_type_id"] == task_type_id
        assert "planned_start_time" in data
        assert "planned_end_time" in data
        assert "id" in data

    def test_get_my_tasks(self, client, auth_headers, db_session, test_admin_user, init_roles):
        """测试获取我的任务列表 - 包含时间属性"""
        # 先创建一个任务
        from app.models.task import WeeklyTask, TaskStatus
        from datetime import datetime, timedelta
        
        # 获取一个任务类型ID用于关联
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break
        
        assert task_type_id is not None, "没有找到可用的任务类型"
        
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        task = WeeklyTask(
            user_id=test_admin_user.id,
            title="测试任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility",
            linked_task_type_id=task_type_id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )
        db_session.add(task)
        db_session.commit()

        # 获取任务列表
        response = client.get("/api/tasks/my-tasks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()
        assert len(tasks) > 0
        assert tasks[0]["title"] == "测试任务"
        assert "planned_start_time" in tasks[0]  # 验证时间属性存在

    def test_get_my_tasks_with_filters(self, client, auth_headers, db_session, test_admin_user, init_roles):
        """测试带过滤条件获取任务 - 包含时间属性"""
        from app.models.task import WeeklyTask, TaskStatus
        from datetime import datetime, timedelta
        
        # 获取一个任务类型ID用于关联
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break
        
        assert task_type_id is not None, "没有找到可用的任务类型"
        
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        # 创建重点任务和普通任务
        key_task = WeeklyTask(
            user_id=test_admin_user.id,
            title="重点任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=True,
            source_type="responsibility",
            linked_task_type_id=task_type_id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )
        normal_task = WeeklyTask(
            user_id=test_admin_user.id,
            title="普通任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="personal",
            linked_task_type_id=task_type_id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
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

    def test_update_task(self, client, auth_headers, db_session, test_admin_user, init_roles):
        """测试更新任务 - 包含时间属性更新"""
        from app.models.task import WeeklyTask, TaskStatus
        from datetime import datetime, timedelta
        
        # 获取一个任务类型ID用于关联
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break
        
        assert task_type_id is not None, "没有找到可用的任务类型"
        
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        task = WeeklyTask(
            user_id=test_admin_user.id,
            title="原始任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility",
            linked_task_type_id=task_type_id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 更新任务 - 包含时间属性
        new_start = now + timedelta(hours=2)
        new_end = new_start + timedelta(hours=1)
        update_data = {
            "title": "更新后的任务",
            "status": "completed",
            "planned_start_time": new_start.isoformat(),
            "planned_end_time": new_end.isoformat()
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
        assert "planned_start_time" in data  # 验证时间属性更新

    def test_update_other_user_task_forbidden(
        self, client, auth_headers, db_session, test_employee_user, init_roles
    ):
        """测试更新其他用户的任务（应被拒绝）"""
        from app.models.task import WeeklyTask, TaskStatus
        from datetime import datetime, timedelta
        
        # 获取一个任务类型ID用于关联
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break
        
        assert task_type_id is not None, "没有找到可用的任务类型"
        
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        # 创建属于员工的任务
        task = WeeklyTask(
            user_id=test_employee_user.id,
            title="员工任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility",
            linked_task_type_id=task_type_id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )
        db_session.add(task)
        db_session.commit()

        # 尝试用当前认证用户（admin）更新其他用户的任务
        response = client.put(
            f"/api/tasks/{task.id}",
            json={"title": "尝试修改"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cancel_task(self, client, auth_headers, db_session, test_admin_user, init_roles):
        """测试取消任务（状态更新为已取消）"""
        from app.models.task import WeeklyTask, TaskStatus
        
        # 获取一个任务类型ID用于关联
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break
        
        assert task_type_id is not None, "没有找到可用的任务类型"
        
        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        
        task = WeeklyTask(
            user_id=test_admin_user.id,
            title="待取消任务",
            year=2025,
            week_number=202501,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility",
            linked_task_type_id=task_type_id,  # 强制关联岗责
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60  # 1小时
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        # 取消任务（通过状态更新）
        response = client.put(
            f"/api/tasks/{task.id}",
            json={
                "status": "cancelled",
                "title": "待取消任务"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        # 验证任务状态已更新
        data = response.json()
        assert data["status"] == "cancelled"

    def test_carry_over_delayed_task(self, client, auth_headers, db_session, test_admin_user, init_roles):
        """测试延期任务带入新周"""
        from app.models.task import WeeklyTask

        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break

        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        delayed_task = WeeklyTask(
            user_id=test_admin_user.id,
            title="延期任务",
            year=2025,
            week_number=1,
            status=TaskStatus.DELAYED,
            is_key_task=True,
            source_type="responsibility",
            linked_task_type_id=task_type_id,
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60,
            is_delayed_from_previous=True,
            original_week=1
        )
        db_session.add(delayed_task)
        db_session.commit()
        db_session.refresh(delayed_task)

        payload = {
            "task_ids": [delayed_task.id],
            "target_week_number": 2,
            "target_year": 2025
        }

        resp = client.post("/api/tasks/carry-over", json=payload, headers=auth_headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["created_task_ids"], "应创建新任务"

        new_task_id = data["created_task_ids"][0]
        new_task = db_session.query(WeeklyTask).filter(WeeklyTask.id == new_task_id).first()
        assert new_task
        assert new_task.week_number == 2
        assert new_task.is_delayed_from_previous is True
        assert new_task.original_week == 1
        assert new_task.assigned_by_manager_id == delayed_task.assigned_by_manager_id

    def test_review_fallback_creates_delay_and_rollover(
        self, client, auth_headers, db_session, test_admin_user, init_roles
    ):
        """测试未复盘兜底逻辑：标记延期并滚动到下一周"""
        from app.models.task import WeeklyTask

        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break

        now = datetime.now()
        planned_end = now + timedelta(hours=1)
        pending_task = WeeklyTask(
            user_id=test_admin_user.id,
            title="待复盘任务",
            year=2025,
            week_number=1,
            status=TaskStatus.TODO,
            is_key_task=False,
            source_type="responsibility",
            linked_task_type_id=task_type_id,
            planned_start_time=now,
            planned_end_time=planned_end,
            planned_duration=60
        )
        db_session.add(pending_task)
        db_session.commit()
        db_session.refresh(pending_task)

        payload = {"week_number": 1, "year": 2025}
        resp = client.post("/api/tasks/reviews/fallback", json=payload, headers=auth_headers)
        assert resp.status_code == status.HTTP_200_OK
        result = resp.json()
        assert result["created_task_ids"], "应创建滚动后的新任务"

        # 原任务应被标记为延期并有复盘记录
        updated = db_session.query(WeeklyTask).filter(WeeklyTask.id == pending_task.id).first()
        assert updated.status == TaskStatus.DELAYED
        review_resp = client.get("/api/tasks/my-tasks", headers=auth_headers)
        # 验证新任务周次
        new_id = result["created_task_ids"][0]
        new_task = db_session.query(WeeklyTask).filter(WeeklyTask.id == new_id).first()
        assert new_task.year in (2025, 2026)
        assert new_task.week_number in range(1, 54)

    def test_assign_task_requires_direct_subordinate(
        self, client, manager_headers, auth_headers, db_session, test_employee_user, test_admin_user, init_roles
    ):
        """测试管理者只能指派给直属下属"""
        response = client.get("/api/roles/", headers=auth_headers)
        roles = response.json()
        task_type_id = None
        for role in roles:
            if role["responsibilities"] and role["responsibilities"][0]["task_types"]:
                task_type_id = role["responsibilities"][0]["task_types"][0]["id"]
                break

        now = datetime.now()
        payload = {
            "title": "指派任务",
            "description": "由经理指派",
            "year": 2025,
            "week_number": 1,
            "status": "todo",
            "is_key_task": True,
            "source_type": "manager_assigned",
            "linked_task_type_id": task_type_id,
            "planned_start_time": now.isoformat(),
            "planned_end_time": (now + timedelta(hours=1)).isoformat()
        }

        # 直属下属应成功
        resp_ok = client.post(f"/api/tasks/assign/?user_id={test_employee_user.id}", json=payload, headers=manager_headers)
        assert resp_ok.status_code == status.HTTP_201_CREATED

        # 非直属（如 admin）应拒绝
        resp_forbidden = client.post(f"/api/tasks/assign/?user_id={test_admin_user.id}", json=payload, headers=manager_headers)
        assert resp_forbidden.status_code == status.HTTP_403_FORBIDDEN
