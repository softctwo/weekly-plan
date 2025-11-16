from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.models.user import Base


class LLMConfig(Base):
    """大模型配置表"""
    __tablename__ = "llm_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模型名称")
    provider = Column(String(50), nullable=False, comment="提供商：deepseek, openai, etc")
    api_key = Column(String(255), nullable=False, comment="API密钥")
    api_base = Column(String(255), nullable=True, comment="API基础URL")
    model_name = Column(String(100), nullable=False, comment="模型名称：deepseek-chat等")
    is_active = Column(Boolean, default=False, comment="是否启用（全局只有一个生效）")
    is_deleted = Column(Boolean, default=False, comment="是否删除（软删除）")
    max_tokens = Column(Integer, default=4000, comment="最大token数")
    temperature = Column(String(10), default="0.7", comment="温度参数")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<LLMConfig {self.name} - {self.provider}>"
