"""
AI分析相关API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user, get_db
from app.models.user import User
from app.models.llm_config import LLMConfig
from app.schemas.llm_config import (
    LLMConfigCreate,
    LLMConfigUpdate,
    LLMConfigResponse,
    AIAnalysisRequest,
    AIAnalysisResponse
)
from app.services.ai_service import AIAnalysisService

router = APIRouter()


# ==================== 大模型配置管理 ====================

@router.get("/llm-configs", response_model=List[LLMConfigResponse])
def get_llm_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有大模型配置（仅管理员）"""
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以访问")

    configs = db.query(LLMConfig).filter(LLMConfig.is_deleted == False).all()
    return configs


@router.post("/llm-configs", response_model=LLMConfigResponse)
def create_llm_config(
    config: LLMConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建大模型配置（仅管理员）"""
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以访问")

    # 创建配置
    db_config = LLMConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    return db_config


@router.put("/llm-configs/{config_id}", response_model=LLMConfigResponse)
def update_llm_config(
    config_id: int,
    config: LLMConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新大模型配置（仅管理员）"""
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以访问")

    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 更新字段
    for field, value in config.dict(exclude_unset=True).items():
        setattr(db_config, field, value)

    db.commit()
    db.refresh(db_config)

    return db_config


@router.post("/llm-configs/{config_id}/activate")
def activate_llm_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """激活大模型配置（仅管理员）"""
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以访问")

    # 停用所有配置
    db.query(LLMConfig).update({"is_active": False})

    # 激活指定配置
    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db_config.is_active = True
    db.commit()

    return {"message": "配置已激活", "config_id": config_id}


@router.delete("/llm-configs/{config_id}")
def delete_llm_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除大模型配置（软删除，仅管理员）"""
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以访问")

    db_config = db.query(LLMConfig).filter(LLMConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 软删除
    db_config.is_deleted = True
    if db_config.is_active:
        db_config.is_active = False

    db.commit()

    return {"message": "配置已删除"}


# ==================== AI分析 ====================

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_work_performance(
    request: AIAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI分析员工工作计划执行情况（仅管理员和管理者）

    Args:
        request: 分析请求参数

    Returns:
        AI分析结果
    """
    # 权限检查
    if current_user.user_type not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="仅管理员和管理者可以使用AI分析功能")

    # 如果是管理者，只能分析自己下属的员工
    if current_user.user_type == "manager" and request.user_id:
        target_user = db.query(User).filter(User.id == request.user_id).first()
        if not target_user or target_user.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能分析直属下属的数据")

    # 创建AI服务
    ai_service = AIAnalysisService(db)

    # 执行分析
    try:
        result = await ai_service.analyze_work_performance(
            user_id=request.user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            analysis_type=request.analysis_type
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/analyze/test")
async def test_llm_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """测试大模型连接（仅管理员）"""
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可以访问")

    ai_service = AIAnalysisService(db)

    try:
        config = ai_service.get_active_llm_config()
        if not config:
            raise HTTPException(status_code=400, detail="未配置可用的大模型")

        # 测试简单调用
        result = await ai_service.call_llm_api(
            prompt="请回复'连接成功'",
            system_prompt="你是一个测试助手，简洁回复即可。"
        )

        return {
            "status": "success",
            "config_name": config.name,
            "provider": config.provider,
            "model": config.model_name,
            "response": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
