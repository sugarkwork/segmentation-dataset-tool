from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator

# Shared properties
class ClassDefinitionBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    color: str
    opacity: int = 128
    class_index: int
    is_visible: bool = True
    stroke_width: int = 2
    
    @validator('color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError('Color must be a valid hex color code')
        return v
    
    @validator('opacity')
    def validate_opacity(cls, v):
        if not 0 <= v <= 255:
            raise ValueError('Opacity must be between 0 and 255')
        return v
    
    @validator('class_index')
    def validate_class_index(cls, v):
        if v < 0:
            raise ValueError('Class index must be non-negative')
        return v
    
    @validator('stroke_width')
    def validate_stroke_width(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Stroke width must be between 1 and 10')
        return v

# Properties to receive via API on creation
class ClassDefinitionCreate(ClassDefinitionBase):
    pass

# Properties to receive via API on update
class ClassDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    opacity: Optional[int] = None
    class_index: Optional[int] = None
    is_visible: Optional[bool] = None
    stroke_width: Optional[int] = None
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
            try:
                int(v[1:], 16)
            except ValueError:
                raise ValueError('Color must be a valid hex color code')
        return v
    
    @validator('opacity')
    def validate_opacity(cls, v):
        if v is not None and not 0 <= v <= 255:
            raise ValueError('Opacity must be between 0 and 255')
        return v
    
    @validator('class_index')
    def validate_class_index(cls, v):
        if v is not None and v < 0:
            raise ValueError('Class index must be non-negative')
        return v

# Properties shared by models stored in DB
class ClassDefinitionInDBBase(ClassDefinitionBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Properties to return to client
class ClassDefinition(ClassDefinitionInDBBase):
    segmentation_count: Optional[int] = 0

# Properties stored in DB
class ClassDefinitionInDB(ClassDefinitionInDBBase):
    pass