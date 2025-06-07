from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator

# Shared properties
class AnnotationBase(BaseModel):
    normalized_coordinates: str  # JSON array of normalized coordinates
    original_coordinates: Optional[str] = None  # JSON array of original coordinates
    point_count: int
    is_simplified: bool = False
    simplification_tolerance: Optional[float] = None
    polygon_area: Optional[float] = None
    perimeter: Optional[float] = None
    compactness: Optional[float] = None
    is_valid: bool = True
    validation_errors: Optional[str] = None
    export_format: Optional[str] = None
    
    @validator('point_count')
    def validate_point_count(cls, v):
        if v < 3:
            raise ValueError('Polygon must have at least 3 points')
        return v
    
    @validator('export_format')
    def validate_export_format(cls, v):
        if v is not None and v not in ['yolo', 'coco']:
            raise ValueError('Export format must be "yolo" or "coco"')
        return v

# Properties to receive via API on creation
class AnnotationCreate(AnnotationBase):
    segmentation_id: int

# Properties to receive via API on update
class AnnotationUpdate(BaseModel):
    normalized_coordinates: Optional[str] = None
    original_coordinates: Optional[str] = None
    point_count: Optional[int] = None
    is_simplified: Optional[bool] = None
    simplification_tolerance: Optional[float] = None
    polygon_area: Optional[float] = None
    perimeter: Optional[float] = None
    compactness: Optional[float] = None
    is_valid: Optional[bool] = None
    validation_errors: Optional[str] = None
    export_format: Optional[str] = None
    
    @validator('point_count')
    def validate_point_count(cls, v):
        if v is not None and v < 3:
            raise ValueError('Polygon must have at least 3 points')
        return v

# Properties shared by models stored in DB
class AnnotationInDBBase(AnnotationBase):
    id: int
    segmentation_id: int
    is_exported: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Properties to return to client
class Annotation(AnnotationInDBBase):
    pass

# Properties stored in DB
class AnnotationInDB(AnnotationInDBBase):
    pass

# YOLO format export
class YOLOAnnotation(BaseModel):
    class_index: int
    normalized_coordinates: List[float]
    
    def to_yolo_format(self) -> str:
        """Convert to YOLO segmentation format string"""
        coords_str = " ".join([f"{coord:.6f}" for coord in self.normalized_coordinates])
        return f"{self.class_index} {coords_str}"

# COCO format export (for future implementation)
class COCOAnnotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    segmentation: List[List[float]]
    area: float
    bbox: List[float]  # [x, y, width, height]
    iscrowd: int = 0