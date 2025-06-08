from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import json
import zipfile
import io
import os
from pathlib import Path

from ....core.deps import get_db, get_current_user
from ....crud import annotation as crud_annotation, project as crud_project, image as crud_image, segmentation as crud_segmentation
from ....models.user import User
from ....schemas.annotation import Annotation, AnnotationCreate, AnnotationUpdate

router = APIRouter()

@router.get("/segmentation/{segmentation_id}", response_model=List[Annotation])
def read_segmentation_annotations(
    *,
    db: Session = Depends(get_db),
    segmentation_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve all annotations for a specific segmentation.
    """
    # Verify segmentation exists and user has access
    segmentation = crud_segmentation.get(db, id=segmentation_id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    annotations = crud_annotation.get_by_segmentation(db, segmentation_id=segmentation_id)
    return annotations

@router.post("/", response_model=Annotation)
def create_annotation(
    *,
    db: Session = Depends(get_db),
    annotation_in: AnnotationCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new annotation.
    """
    # Verify segmentation exists and user has access
    segmentation = crud_segmentation.get(db, id=annotation_in.segmentation_id)
    if not segmentation:
        raise HTTPException(status_code=404, detail="Segmentation not found")
    
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create annotation
    annotation = crud_annotation.create(db, obj_in=annotation_in)
    return annotation

@router.get("/{id}", response_model=Annotation)
def read_annotation(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get annotation by ID.
    """
    annotation = crud_annotation.get(db, id=id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Verify user has access
    segmentation = crud_segmentation.get(db, id=annotation.segmentation_id)
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return annotation

@router.put("/{id}", response_model=Annotation)
def update_annotation(
    *,
    db: Session = Depends(get_db),
    id: int,
    annotation_in: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update an annotation.
    """
    annotation = crud_annotation.get(db, id=id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Verify user has access
    segmentation = crud_segmentation.get(db, id=annotation.segmentation_id)
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    annotation = crud_annotation.update(db, db_obj=annotation, obj_in=annotation_in)
    return annotation

@router.delete("/{id}")
def delete_annotation(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete an annotation.
    """
    annotation = crud_annotation.get(db, id=id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Verify user has access
    segmentation = crud_segmentation.get(db, id=annotation.segmentation_id)
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud_annotation.remove(db, id=id)
    return {"message": "Annotation deleted successfully"}

@router.post("/{id}/simplify")
def simplify_annotation(
    *,
    db: Session = Depends(get_db),
    id: int,
    tolerance: float = 2.0,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Simplify annotation coordinates using Douglas-Peucker algorithm.
    """
    annotation = crud_annotation.get(db, id=id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Verify user has access
    segmentation = crud_segmentation.get(db, id=annotation.segmentation_id)
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Simplify coordinates
    simplified_annotation = crud_annotation.simplify_coordinates(
        db, annotation_id=id, tolerance=tolerance
    )
    
    return {
        "message": "Annotation simplified successfully",
        "original_points": annotation.point_count,
        "simplified_points": simplified_annotation.point_count,
        "reduction_percentage": round((1 - simplified_annotation.point_count / annotation.point_count) * 100, 2)
    }

@router.post("/{id}/validate")
def validate_annotation(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Validate annotation coordinates and geometry.
    """
    annotation = crud_annotation.get(db, id=id)
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Verify user has access
    segmentation = crud_segmentation.get(db, id=annotation.segmentation_id)
    image = crud_image.get(db, id=segmentation.image_id)
    project = crud_project.get(db, id=image.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate annotation
    validation_result = crud_annotation.validate_annotation(db, annotation_id=id)
    
    return {
        "is_valid": validation_result["is_valid"],
        "errors": validation_result["errors"],
        "warnings": validation_result.get("warnings", [])
    }

@router.get("/project/{project_id}/export")
def export_project_annotations(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    format: str = "yolo",
    include_images: bool = False,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Export all project annotations in specified format.
    """
    # Verify project exists and user has access
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if format not in ["yolo", "coco"]:
        raise HTTPException(status_code=400, detail="Unsupported export format")
    
    # Generate export
    export_data = crud_annotation.export_project_annotations(
        db, project_id=project_id, format=format, include_images=include_images
    )
    
    # Create ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add annotation files
        for dataset_type in ["train", "val", "test"]:
            if dataset_type in export_data["annotations"]:
                for filename, content in export_data["annotations"][dataset_type].items():
                    zip_file.writestr(f"labels/{dataset_type}/{filename}", content)
        
        # Add classes file
        if format == "yolo":
            classes_content = "\n".join([f"{cls['name']}" for cls in export_data["classes"]])
            zip_file.writestr("classes.txt", classes_content)
        elif format == "coco":
            zip_file.writestr("annotations.json", json.dumps(export_data["coco_format"], indent=2))
        
        # Add dataset info
        zip_file.writestr("dataset_info.json", json.dumps(export_data["info"], indent=2))
        
        # Add images if requested
        if include_images and "images" in export_data:
            for dataset_type, images in export_data["images"].items():
                for image_filename, image_path in images.items():
                    if os.path.exists(image_path):
                        zip_file.write(image_path, f"images/{dataset_type}/{image_filename}")
    
    zip_buffer.seek(0)
    
    # Return ZIP file
    filename = f"{project.name}_{format}_dataset.zip"
    
    return Response(
        zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/project/{project_id}/stats")
def get_annotation_stats(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get annotation statistics for a project.
    """
    # Verify project exists and user has access
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get statistics
    stats = crud_annotation.get_project_annotation_stats(db, project_id=project_id)
    
    return stats