from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....core.deps import get_db, get_current_user
from ....crud import project as crud_project
from ....models.user import User
from ....schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectStats, ProjectSummary

router = APIRouter()

@router.get("/", response_model=List[ProjectSummary])
def read_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve user's projects.
    """
    projects = crud_project.get_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    
    # Add project stats for each project
    project_summaries = []
    for project in projects:
        stats = crud_project.get_project_stats(db, project_id=project.id)
        project_summary = ProjectSummary(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            image_count=stats.get("total_images", 0),
            class_count=stats.get("total_classes", 0),
            completion_percentage=stats.get("completion_percentage", 0)
        )
        project_summaries.append(project_summary)
    
    return project_summaries

@router.post("/", response_model=Project)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new project.
    """
    # Check if project name already exists for this user
    existing_project = crud_project.get_by_owner_and_name(
        db, owner_id=current_user.id, name=project_in.name
    )
    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project with this name already exists."
        )
    
    project = crud_project.create_with_owner(
        db, obj_in=project_in, owner_id=current_user.id
    )
    return project

@router.get("/{id}", response_model=Project)
def read_project(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get project by ID.
    """
    project = crud_project.get(db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Add project stats
    stats = crud_project.get_project_stats(db, project_id=project.id)
    project_dict = project.__dict__.copy()
    project_dict.update({
        "image_count": stats.get("total_images", 0),
        "class_count": stats.get("total_classes", 0),
        "annotation_count": stats.get("total_annotations", 0)
    })
    
    return project_dict

@router.put("/{id}", response_model=Project)
def update_project(
    *,
    db: Session = Depends(get_db),
    id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a project.
    """
    project = crud_project.get(db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if new name conflicts with existing projects
    if project_in.name and project_in.name != project.name:
        existing_project = crud_project.get_by_owner_and_name(
            db, owner_id=current_user.id, name=project_in.name
        )
        if existing_project:
            raise HTTPException(
                status_code=400,
                detail="Project with this name already exists."
            )
    
    project = crud_project.update(db, db_obj=project, obj_in=project_in)
    return project

@router.delete("/{id}")
def delete_project(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a project.
    """
    project = crud_project.get(db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    project = crud_project.remove(db, id=id)
    return {"message": "Project deleted successfully"}

@router.get("/{id}/stats", response_model=ProjectStats)
def read_project_stats(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get detailed project statistics.
    """
    project = crud_project.get(db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    stats = crud_project.get_project_stats(db, project_id=id)
    return ProjectStats(**stats)