from sqlalchemy import Column, String, Text, Integer, ForeignKey, Float, Boolean, DECIMAL
from sqlalchemy.orm import relationship
from .base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Dataset configuration
    train_split = Column(DECIMAL(3,2), default=0.8)  # Training data ratio
    val_split = Column(DECIMAL(3,2), default=0.2)    # Validation data ratio
    test_split = Column(DECIMAL(3,2), default=0.0)   # Test data ratio
    
    # Project settings
    image_width = Column(Integer, default=640)   # Target image width
    image_height = Column(Integer, default=640)  # Target image height
    auto_save = Column(Boolean, default=True)    # Auto-save annotations
    
    # Export settings
    export_format = Column(String(20), default='yolo')  # 'yolo', 'coco'
    simplify_polygons = Column(Boolean, default=True)   # Simplify polygon coordinates
    simplify_tolerance = Column(DECIMAL(5,2), default=2.0)     # Douglas-Peucker tolerance
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan")
    classes = relationship("ClassDefinition", back_populates="project", cascade="all, delete-orphan")