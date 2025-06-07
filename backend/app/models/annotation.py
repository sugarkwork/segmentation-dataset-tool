from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, Boolean, DECIMAL
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from .base import BaseModel

class Annotation(BaseModel):
    __tablename__ = "annotations"

    # YOLO format data
    normalized_coordinates = Column(LONGTEXT, nullable=False)  # JSON array of normalized polygon coordinates
    original_coordinates = Column(LONGTEXT, nullable=True)     # JSON array of original pixel coordinates
    
    # Polygon properties
    point_count = Column(Integer, nullable=False)          # Number of polygon points
    is_simplified = Column(Boolean, default=False)        # Whether coordinates are simplified
    simplification_tolerance = Column(DECIMAL(5,2), nullable=True)  # Tolerance used for simplification
    
    # Quality metrics
    polygon_area = Column(DECIMAL(15,6), nullable=True)            # Polygon area (normalized)
    perimeter = Column(DECIMAL(15,6), nullable=True)               # Polygon perimeter
    compactness = Column(DECIMAL(8,6), nullable=True)             # Shape compactness measure
    
    # Validation status
    is_valid = Column(Boolean, default=True)               # Whether polygon is valid
    validation_errors = Column(Text, nullable=True)        # JSON array of validation errors
    
    # Export status
    is_exported = Column(Boolean, default=False, index=True)
    export_format = Column(String(20), nullable=True)      # 'yolo', 'coco'
    
    # Foreign keys
    segmentation_id = Column(Integer, ForeignKey("segmentations.id"), nullable=False, index=True)
    
    # Relationships
    segmentation = relationship("Segmentation", back_populates="annotations")