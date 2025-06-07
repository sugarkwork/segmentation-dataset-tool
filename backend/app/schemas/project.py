from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator

# Shared properties
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    train_split: float = 0.8
    val_split: float = 0.2
    test_split: float = 0.0
    image_width: int = 640
    image_height: int = 640
    auto_save: bool = True
    export_format: str = "yolo"
    simplify_polygons: bool = True
    simplify_tolerance: float = 2.0
    
    @validator('train_split', 'val_split', 'test_split')
    def validate_split_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Split values must be between 0.0 and 1.0')
        return v
    
    @validator('test_split')
    def validate_split_sum(cls, v, values):
        train = values.get('train_split', 0.8)
        val = values.get('val_split', 0.2)
        total = train + val + v
        if not 0.99 <= total <= 1.01:  # Allow small floating point errors
            raise ValueError('Sum of train_split, val_split, and test_split must equal 1.0')
        return v
    
    @validator('image_width', 'image_height')
    def validate_image_size(cls, v):
        if not 32 <= v <= 4096:
            raise ValueError('Image dimensions must be between 32 and 4096 pixels')
        return v
    
    @validator('export_format')
    def validate_export_format(cls, v):
        if v not in ['yolo', 'coco']:
            raise ValueError('Export format must be either "yolo" or "coco"')
        return v

# Properties to receive via API on creation
class ProjectCreate(ProjectBase):
    pass

# Properties to receive via API on update  
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    train_split: Optional[float] = None
    val_split: Optional[float] = None
    test_split: Optional[float] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    auto_save: Optional[bool] = None
    export_format: Optional[str] = None
    simplify_polygons: Optional[bool] = None
    simplify_tolerance: Optional[float] = None

# Properties shared by models stored in DB
class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Properties to return to client
class Project(ProjectInDBBase):
    image_count: Optional[int] = 0
    class_count: Optional[int] = 0
    annotation_count: Optional[int] = 0

# Properties stored in DB
class ProjectInDB(ProjectInDBBase):
    pass

# Project statistics
class ProjectStats(BaseModel):
    total_images: int
    train_images: int
    val_images: int
    test_images: int
    total_annotations: int
    total_classes: int
    avg_annotations_per_image: float
    completion_percentage: float

# Project summary for listing
class ProjectSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    image_count: int
    class_count: int
    completion_percentage: float
    
    class Config:
        orm_mode = True