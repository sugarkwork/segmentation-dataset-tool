from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel

class ClassDefinition(BaseModel):
    __tablename__ = "class_definitions"

    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)  # User-friendly name
    description = Column(Text, nullable=True)
    
    # Visual properties
    color = Column(String(7), nullable=False)  # Hex color code (e.g., #FF0000)
    opacity = Column(Integer, default=128)     # Opacity 0-255
    
    # YOLO class index
    class_index = Column(Integer, nullable=False)  # Index for YOLO format
    
    # Display settings
    is_visible = Column(Boolean, default=True)
    stroke_width = Column(Integer, default=2)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="classes")
    segmentations = relationship("Segmentation", back_populates="class_definition", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('project_id', 'name', name='uk_project_class_name'),
        UniqueConstraint('project_id', 'class_index', name='uk_project_class_index'),
    )