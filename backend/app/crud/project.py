from typing import List, Optional
from sqlalchemy.orm import Session
from ..crud.base import CRUDBase
from ..models.project import Project
from ..schemas.project import ProjectCreate, ProjectUpdate

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_by_owner(self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get projects by owner ID"""
        return (
            db.query(self.model)
            .filter(Project.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner_and_name(self, db: Session, *, owner_id: int, name: str) -> Optional[Project]:
        """Get project by owner ID and name"""
        return (
            db.query(self.model)
            .filter(Project.owner_id == owner_id, Project.name == name)
            .first()
        )

    def create_with_owner(self, db: Session, *, obj_in: ProjectCreate, owner_id: int) -> Project:
        """Create project with owner"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_project_stats(self, db: Session, *, project_id: int) -> dict:
        """Get project statistics"""
        from ..models.image import Image
        from ..models.class_definition import ClassDefinition
        from ..models.segmentation import Segmentation
        
        project = self.get(db, id=project_id)
        if not project:
            return {}
        
        total_images = db.query(Image).filter(Image.project_id == project_id).count()
        train_images = db.query(Image).filter(Image.project_id == project_id, Image.dataset_type == "train").count()
        val_images = db.query(Image).filter(Image.project_id == project_id, Image.dataset_type == "val").count()
        test_images = db.query(Image).filter(Image.project_id == project_id, Image.dataset_type == "test").count()
        total_classes = db.query(ClassDefinition).filter(ClassDefinition.project_id == project_id).count()
        total_annotations = db.query(Segmentation).join(Image).filter(Image.project_id == project_id).count()
        
        avg_annotations = total_annotations / total_images if total_images > 0 else 0
        annotated_images = db.query(Image).filter(Image.project_id == project_id, Image.has_annotations == True).count()
        completion_percentage = (annotated_images / total_images * 100) if total_images > 0 else 0
        
        return {
            "total_images": total_images,
            "train_images": train_images,
            "val_images": val_images,
            "test_images": test_images,
            "total_classes": total_classes,
            "total_annotations": total_annotations,
            "avg_annotations_per_image": avg_annotations,
            "completion_percentage": completion_percentage
        }

project = CRUDProject(Project)