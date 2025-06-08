from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import base64
import json

from ....core.deps import get_db, get_current_user
from ....crud import segmentation as crud_segmentation, project as crud_project, image as crud_image, class_definition as crud_class
from ....models.user import User
from ....schemas.segmentation import Segmentation, SegmentationCreate, SegmentationUpdate, SegmentationWithAnnotations

router = APIRouter()

@router.get("/image/{image_id}", response_model=List[SegmentationWithAnnotations])
def read_image_segmentations(
    *,
    db: Session = Depends(get_db),
    image_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all segmentations for a specific image.
    """
    # Verify image exists and user has access
    image = crud_image.get(db, id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    segmentations = crud_segmentation.get_by_image(db, image_id=image_id)
    return segmentations

@router.post("/", response_model=Segmentation)
def create_segmentation(
    *,
    db: Session = Depends(get_db),
    segmentation_in: SegmentationCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new segmentation.
    """
    # Verify image and class exist and user has access
    image = crud_image.get(db, id=segmentation_in.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    class_def = crud_class.get(db, id=segmentation_in.class_id)
    if not class_def or class_def.project_id != image.project_id:
        raise HTTPException(status_code=400, detail="Invalid class for this project")
    
    # Create segmentation
    segmentation = crud_segmentation.create(db, obj_in=segmentation_in)
    
    # Update image annotation status
    crud_image.update_annotation_status(db, image_id=image.id, has_annotations=True)
    
    return segmentation

@router.get("/{id}", response_model=SegmentationWithAnnotations)
def read_segmentation(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get segmentation by ID.
    """
    segmentation = crud_segmentation.get(db, id=id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    # Verify user has access
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return segmentation

@router.put("/{id}", response_model=Segmentation)
def update_segmentation(
    *,
    db: Session = Depends(get_db),
    id: int,
    segmentation_in: SegmentationUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a segmentation.
    """
    segmentation = crud_segmentation.get(db, id=id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    # Verify user has access
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    segmentation = crud_segmentation.update(db, db_obj=segmentation, obj_in=segmentation_in)
    return segmentation

@router.delete("/{id}")
def delete_segmentation(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a segmentation.
    """
    segmentation = crud_segmentation.get(db, id=id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    # Verify user has access
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete segmentation
    crud_segmentation.remove(db, id=id)
    
    # Check if image still has other segmentations
    remaining_segmentations = crud_segmentation.get_by_image(db, image_id=image.id)
    if not remaining_segmentations:
        crud_image.update_annotation_status(db, image_id=image.id, has_annotations=False)
    
    return {"message": "Segmentation deleted successfully"}

@router.put("/{id}/visibility")
def toggle_segmentation_visibility(
    *,
    db: Session = Depends(get_db),
    id: int,
    is_visible: bool,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Toggle segmentation visibility.
    """
    segmentation = crud_segmentation.get(db, id=id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    # Verify user has access
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    segmentation = crud_segmentation.update_visibility(db, segmentation_id=id, is_visible=is_visible)
    return {"message": "Visibility updated successfully", "is_visible": is_visible}

@router.put("/{id}/layer")
def update_segmentation_layer(
    *,
    db: Session = Depends(get_db),
    id: int,
    layer_index: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update segmentation layer index.
    """
    segmentation = crud_segmentation.get(db, id=id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    # Verify user has access
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    segmentation = crud_segmentation.update_layer(db, segmentation_id=id, layer_index=layer_index)
    return {"message": "Layer updated successfully", "layer_index": layer_index}

@router.post("/{id}/generate-annotation")
def generate_annotation_from_segmentation(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Generate YOLO annotation from segmentation mask data.
    """
    segmentation = crud_segmentation.get(db, id=id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    # Verify user has access
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Generate annotation from mask data
    annotation = crud_segmentation.generate_annotation(db, segmentation_id=id)
    
    return {
        "message": "Annotation generated successfully",
        "annotation_id": annotation.id,
        "point_count": annotation.point_count
    }