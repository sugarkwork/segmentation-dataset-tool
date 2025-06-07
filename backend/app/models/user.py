from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    
    # OAuth fields for future integration
    github_id = Column(String(50), nullable=True, unique=True, index=True)
    twitter_id = Column(String(50), nullable=True, unique=True, index=True)
    oauth_provider = Column(String(20), nullable=True)  # 'local', 'github', 'twitter'
    
    # User preferences
    theme = Column(String(20), default='light')  # 'light', 'dark'
    language = Column(String(10), default='ja')  # 'ja', 'en'
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")