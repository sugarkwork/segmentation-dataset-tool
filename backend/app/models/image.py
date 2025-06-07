from sqlalchemy import Column, String, Integer, ForeignKey, Float, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Image(BaseModel):
    __tablename__ = "images"

    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # File size in bytes
    
    # Image properties
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    format = Column(String(10), nullable=False)  # 'jpg', 'png', 'bmp'
    
    # Dataset assignment
    dataset_type = Column(String(10), default='train', index=True)  # 'train', 'val', 'test'
    
    # Processing status
    is_processed = Column(Boolean, default=False, index=True)
    has_annotations = Column(Boolean, default=False)
    
    # Metadata
    thumbnail_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="images")
    segmentations = relationship("Segmentation", back_populates="image", cascade="all, delete-orphan")