from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, validator

# Shared properties
class ImageBase(BaseModel):
    original_filename: str
    dataset_type: str = "train"
    notes: Optional[str] = None
    
    @validator('dataset_type')
    def validate_dataset_type(cls, v):
        if v not in ['train', 'val', 'test']:
            raise ValueError('Dataset type must be "train", "val", or "test"')
        return v

# Properties to receive via API on creation
class ImageCreate(ImageBase):
    pass

# Properties to receive via API on update
class ImageUpdate(BaseModel):
    dataset_type: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('dataset_type')
    def validate_dataset_type(cls, v):
        if v is not None and v not in ['train', 'val', 'test']:
            raise ValueError('Dataset type must be "train", "val", or "test"')
        return v

# Properties shared by models stored in DB
class ImageInDBBase(ImageBase):
    id: int
    filename: str
    file_path: str
    file_size: int
    width: int
    height: int
    format: str
    is_processed: bool
    has_annotations: bool
    thumbnail_path: Optional[str]
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Properties to return to client
class Image(ImageInDBBase):
    segmentation_count: Optional[int] = 0
    annotation_count: Optional[int] = 0

# Properties stored in DB
class ImageInDB(ImageInDBBase):
    pass

# Image upload response
class ImageUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    width: int
    height: int
    format: str
    file_size: int
    thumbnail_url: Optional[str] = None
    message: str = "Image uploaded successfully"

# Batch upload response
class BatchUploadResponse(BaseModel):
    successful_uploads: List[ImageUploadResponse]
    failed_uploads: List[dict]
    total_count: int
    success_count: int
    error_count: int