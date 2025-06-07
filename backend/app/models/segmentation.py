from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, Float, DECIMAL
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from .base import BaseModel

class Segmentation(BaseModel):
    __tablename__ = "segmentations"

    name = Column(String(100), nullable=True)  # Optional name for segmentation
    
    # Canvas data (stored as base64 encoded image)
    mask_data = Column(LONGTEXT, nullable=False)  # Base64 encoded mask image
    
    # Bounding box (for optimization)
    bbox_x = Column(DECIMAL(10,6), nullable=True)
    bbox_y = Column(DECIMAL(10,6), nullable=True) 
    bbox_width = Column(DECIMAL(10,6), nullable=True)
    bbox_height = Column(DECIMAL(10,6), nullable=True)
    
    # Area calculation
    area = Column(DECIMAL(15,6), nullable=True)  # Segmentation area in pixels
    
    # Layer properties (Photoshop-like)
    layer_index = Column(Integer, default=0, index=True)   # Layer stacking order
    is_visible = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    opacity = Column(Integer, default=255)     # 0-255
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    needs_simplification = Column(Boolean, default=True)
    
    # Foreign keys
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("class_definitions.id"), nullable=False, index=True)
    
    # Relationships
    image = relationship("Image", back_populates="segmentations")
    class_definition = relationship("ClassDefinition", back_populates="segmentations")
    annotations = relationship("Annotation", back_populates="segmentation", cascade="all, delete-orphan")