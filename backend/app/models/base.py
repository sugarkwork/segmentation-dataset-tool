from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class TimestampMixin:
    """共通のタイムスタンプフィールドを提供するMixin"""
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())

class BaseModel(Base, TimestampMixin):
    """すべてのモデルの基底クラス"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)