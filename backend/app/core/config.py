import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Segmentation Dataset Tool"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://app_user:app_password@localhost:3306/segmentation_dataset"
    )
    
    # File handling
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".bmp"}
    THUMBNAIL_SIZE: tuple = (200, 200)
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative port
        "http://127.0.0.1:3000",
    ]
    
    # OAuth (for future implementation)
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")
    TWITTER_CLIENT_ID: Optional[str] = os.getenv("TWITTER_CLIENT_ID")
    TWITTER_CLIENT_SECRET: Optional[str] = os.getenv("TWITTER_CLIENT_SECRET")
    
    # Image processing
    DEFAULT_IMAGE_SIZE: tuple = (640, 640)
    SIMPLIFICATION_TOLERANCE: float = 2.0
    MIN_POLYGON_POINTS: int = 3
    MAX_POLYGON_POINTS: int = 1000
    
    # Export settings
    EXPORT_FORMATS: list = ["yolo", "coco"]
    TEMP_DIR: str = "./temp"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()