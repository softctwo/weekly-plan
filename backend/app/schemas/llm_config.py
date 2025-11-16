from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LLMConfigBase(BaseModel):
    """大模型配置基础Schema"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    api_key: str = Field(..., description="API密钥")
    api_base: Optional[str] = Field(None, description="API基础URL")
    model_name: str = Field(..., description="模型名称")
    max_tokens: int = Field(4000, description="最大token数")
    temperature: str = Field("0.7", description="温度参数")
    description: Optional[str] = Field(None, description="描述")


class LLMConfigCreate(LLMConfigBase):
    """创建大模型配置"""
    pass


class LLMConfigUpdate(BaseModel):
    """更新大模型配置"""
    name: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[str] = None
    description: Optional[str] = None


class LLMConfigResponse(LLMConfigBase):
    """大模型配置响应"""
    id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIAnalysisRequest(BaseModel):
    """AI分析请求"""
    user_id: Optional[int] = Field(None, description="员工ID，不传则分析全部员工")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    analysis_type: str = Field("comprehensive", description="分析类型：comprehensive/performance/improvement")


class AIAnalysisResponse(BaseModel):
    """AI分析响应"""
    user_name: Optional[str] = None
    analysis_period: str
    analysis_result: str
    statistics: dict
    created_at: datetime
