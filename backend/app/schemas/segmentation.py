from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator

# Shared properties
class SegmentationBase(BaseModel):
    name: Optional[str] = None
    mask_data: str  # Base64 encoded mask image
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_width: Optional[float] = None
    bbox_height: Optional[float] = None
    area: Optional[float] = None
    layer_index: int = 0
    is_visible: bool = True
    is_locked: bool = False
    opacity: int = 255
    
    @validator('opacity')
    def validate_opacity(cls, v):
        if not 0 <= v <= 255:
            raise ValueError('Opacity must be between 0 and 255')
        return v
    
    @validator('layer_index')
    def validate_layer_index(cls, v):
        if v < 0:
            raise ValueError('Layer index must be non-negative')
        return v

# Properties to receive via API on creation
class SegmentationCreate(SegmentationBase):
    image_id: int
    class_id: int

# Properties to receive via API on update
class SegmentationUpdate(BaseModel):
    name: Optional[str] = None
    mask_data: Optional[str] = None
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_width: Optional[float] = None
    bbox_height: Optional[float] = None
    area: Optional[float] = None
    layer_index: Optional[int] = None
    is_visible: Optional[bool] = None
    is_locked: Optional[bool] = None
    opacity: Optional[int] = None
    
    @validator('opacity')
    def validate_opacity(cls, v):
        if v is not None and not 0 <= v <= 255:
            raise ValueError('Opacity must be between 0 and 255')
        return v

# Properties shared by models stored in DB
class SegmentationInDBBase(SegmentationBase):
    id: int
    image_id: int
    class_id: int
    is_processed: bool
    needs_simplification: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Properties to return to client
class Segmentation(SegmentationInDBBase):
    class_name: Optional[str] = None
    class_color: Optional[str] = None
    annotation_count: Optional[int] = 0

# Properties stored in DB
class SegmentationInDB(SegmentationInDBBase):
    pass

# Bulk operations
class SegmentationBulkUpdate(BaseModel):
    segmentation_ids: List[int]
    updates: SegmentationUpdate

class SegmentationBulkDelete(BaseModel):
    segmentation_ids: List[int]