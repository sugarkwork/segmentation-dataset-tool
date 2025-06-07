from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....core.deps import get_db, get_current_user
from ....crud import class_definition as crud_class, project as crud_project
from ....models.user import User
from ....schemas.class_definition import ClassDefinition, ClassDefinitionCreate, ClassDefinitionUpdate

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[ClassDefinition])
def read_project_classes(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve class definitions for a specific project.
    """
    # Verify project ownership
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    classes = crud_class.get_by_project(db, project_id=project_id)
    
    # Add segmentation counts
    classes_with_counts = crud_class.get_class_with_segmentation_count(db, project_id=project_id)
    return classes_with_counts

@router.post("/project/{project_id}", response_model=ClassDefinition)
def create_class(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    class_in: ClassDefinitionCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new class definition.
    """
    # Verify project ownership
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # If no class index provided, get next available
    if class_in.class_index is None:
        class_in.class_index = crud_class.get_next_class_index(db, project_id=project_id)
    
    class_def = crud_class.create_with_project(
        db, obj_in=class_in, project_id=project_id
    )
    return class_def

@router.get("/{id}", response_model=ClassDefinition)
def read_class(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get class definition by ID.
    """
    class_def = crud_class.get(db, id=id)
    if not class_def:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=class_def.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return class_def

@router.put("/{id}", response_model=ClassDefinition)
def update_class(
    *,
    db: Session = Depends(get_db),
    id: int,
    class_in: ClassDefinitionUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a class definition.
    """
    class_def = crud_class.get(db, id=id)
    if not class_def:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=class_def.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check for name conflicts if name is being updated
    if class_in.name and class_in.name != class_def.name:
        existing_class = crud_class.get_by_project_and_name(
            db, project_id=class_def.project_id, name=class_in.name
        )
        if existing_class:
            raise HTTPException(
                status_code=400,
                detail="Class name already exists in this project"
            )
    
    # Check for class index conflicts if index is being updated
    if class_in.class_index is not None and class_in.class_index != class_def.class_index:
        existing_class = crud_class.get_by_project_and_index(
            db, project_id=class_def.project_id, class_index=class_in.class_index
        )
        if existing_class:
            raise HTTPException(
                status_code=400,
                detail="Class index already exists in this project"
            )
    
    class_def = crud_class.update(db, db_obj=class_def, obj_in=class_in)
    return class_def

@router.delete("/{id}")
def delete_class(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a class definition.
    """
    class_def = crud_class.get(db, id=id)
    if not class_def:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=class_def.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if class has associated segmentations
    from ....crud import segmentation as crud_segmentation
    segmentations = crud_segmentation.get_by_image_and_class(
        db, image_id=0, class_id=id  # This will need to be fixed in CRUD
    )
    
    # For now, allow deletion but this should be configurable
    class_def = crud_class.remove(db, id=id)
    return {"message": "Class deleted successfully"}

@router.put("/{id}/visibility")
def toggle_class_visibility(
    *,
    db: Session = Depends(get_db),
    id: int,
    is_visible: bool,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Toggle class visibility.
    """
    class_def = crud_class.get(db, id=id)
    if not class_def:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify project ownership
    project = crud_project.get(db, id=class_def.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    class_def = crud_class.update_visibility(db, class_id=id, is_visible=is_visible)
    return {"message": "Visibility updated successfully", "is_visible": is_visible}

@router.put("/project/{project_id}/reorder")
def reorder_classes(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    class_order: List[dict],
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Reorder classes in a project.
    Expected format: [{"id": 1, "class_index": 0}, {"id": 2, "class_index": 1}, ...]
    """
    # Verify project ownership
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate input format
    for item in class_order:
        if "id" not in item or "class_index" not in item:
            raise HTTPException(
                status_code=400,
                detail="Each item must have 'id' and 'class_index' fields"
            )
    
    updated_classes = crud_class.reorder_classes(
        db, project_id=project_id, class_order=class_order
    )
    
    return {
        "message": "Classes reordered successfully",
        "updated_count": len(updated_classes)
    }