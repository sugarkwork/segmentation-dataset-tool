from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import uuid
from PIL import Image as PILImage

from ....core.deps import get_db, get_current_user
from ....core.config import settings
from ....crud import image as crud_image, project as crud_project
from ....models.user import User
from ....schemas.image import Image, ImageCreate, ImageUpdate, ImageUploadResponse, BatchUploadResponse

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[Image])
def read_project_images(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve images for a specific project.
    """
    # Verify project ownership
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    images = crud_image.get_by_project(
        db, project_id=project_id, skip=skip, limit=limit
    )
    return images

@router.post("/project/{project_id}/upload", response_model=ImageUploadResponse)
def upload_image(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    dataset_type: str = Form("train"),
    notes: str = Form(None)
) -> Any:
    """
    Upload a single image to a project.
    """
    # Verify project ownership
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, str(project_id), unique_filename)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Get image dimensions
    try:
        with PILImage.open(file_path) as img:
            width, height = img.size
            img_format = img.format.lower()
    except Exception as e:
        # Clean up file if image processing fails
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Create thumbnail
    thumbnail_path = None
    try:
        thumbnail_filename = f"thumb_{unique_filename}"
        thumbnail_path = os.path.join(settings.UPLOAD_DIR, str(project_id), "thumbnails", thumbnail_filename)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        with PILImage.open(file_path) as img:
            img.thumbnail(settings.THUMBNAIL_SIZE, PILImage.Resampling.LANCZOS)
            img.save(thumbnail_path)
    except Exception:
        # Thumbnail creation failed, but continue
        thumbnail_path = None
    
    # Create database record
    image_in = ImageCreate(
        original_filename=file.filename,
        dataset_type=dataset_type,
        notes=notes
    )
    
    image = crud_image.create_with_project(
        db,
        obj_in=image_in,
        project_id=project_id,
        filename=unique_filename,
        file_path=file_path,
        file_size=file_size,
        width=width,
        height=height,
        format=img_format,
        thumbnail_path=thumbnail_path
    )
    
    return ImageUploadResponse(
        id=image.id,
        filename=image.filename,
        original_filename=image.original_filename,
        width=image.width,
        height=image.height,
        format=image.format,
        file_size=image.file_size,
        thumbnail_url=f"/uploads/{project_id}/thumbnails/thumb_{unique_filename}" if thumbnail_path else None
    )

@router.get("/{id}", response_model=Image)
def read_image(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get image by ID.
    """
    image = crud_image.get(db, id=id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return image

@router.put("/{id}", response_model=Image)
def update_image(
    *,
    db: Session = Depends(get_db),
    id: int,
    image_in: ImageUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update an image.
    """
    image = crud_image.get(db, id=id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    image = crud_image.update(db, db_obj=image, obj_in=image_in)
    return image

@router.delete("/{id}")
def delete_image(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete an image.
    """
    image = crud_image.get(db, id=id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete physical files
    try:
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        if image.thumbnail_path and os.path.exists(image.thumbnail_path):
            os.remove(image.thumbnail_path)
    except Exception:
        pass  # Continue even if file deletion fails
    
    # Delete database record
    crud_image.remove(db, id=id)
    return {"message": "Image deleted successfully"}

@router.put("/{id}/dataset-type")
def update_image_dataset_type(
    *,
    db: Session = Depends(get_db),
    id: int,
    dataset_type: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update image dataset type (train/val/test).
    """
    if dataset_type not in ["train", "val", "test"]:
        raise HTTPException(status_code=400, detail="Invalid dataset type")
    
    image = crud_image.get(db, id=id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    image_update = ImageUpdate(dataset_type=dataset_type)
    image = crud_image.update(db, db_obj=image, obj_in=image_update)
    
    return {"message": "Dataset type updated successfully", "dataset_type": dataset_type}