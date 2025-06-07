from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..crud.base import CRUDBase
from ..models.class_definition import ClassDefinition
from ..schemas.class_definition import ClassDefinitionCreate, ClassDefinitionUpdate

class CRUDClassDefinition(CRUDBase[ClassDefinition, ClassDefinitionCreate, ClassDefinitionUpdate]):
    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[ClassDefinition]:
        """Get class definitions by project ID"""
        return (
            db.query(self.model)
            .filter(ClassDefinition.project_id == project_id)
            .order_by(ClassDefinition.class_index)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_project_and_name(
        self, db: Session, *, project_id: int, name: str
    ) -> Optional[ClassDefinition]:
        """Get class definition by project ID and name"""
        return (
            db.query(self.model)
            .filter(ClassDefinition.project_id == project_id, ClassDefinition.name == name)
            .first()
        )

    def get_by_project_and_index(
        self, db: Session, *, project_id: int, class_index: int
    ) -> Optional[ClassDefinition]:
        """Get class definition by project ID and class index"""
        return (
            db.query(self.model)
            .filter(ClassDefinition.project_id == project_id, ClassDefinition.class_index == class_index)
            .first()
        )

    def create_with_project(
        self, db: Session, *, obj_in: ClassDefinitionCreate, project_id: int
    ) -> ClassDefinition:
        """Create class definition with project ID"""
        # Check if name already exists in project
        existing_name = self.get_by_project_and_name(db, project_id=project_id, name=obj_in.name)
        if existing_name:
            raise HTTPException(status_code=400, detail="Class name already exists in this project")
        
        # Check if class index already exists in project
        existing_index = self.get_by_project_and_index(db, project_id=project_id, class_index=obj_in.class_index)
        if existing_index:
            raise HTTPException(status_code=400, detail="Class index already exists in this project")
        
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, project_id=project_id)
        
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Class name or index already exists")

    def get_next_class_index(self, db: Session, *, project_id: int) -> int:
        """Get the next available class index for a project"""
        max_index = (
            db.query(db.func.max(ClassDefinition.class_index))
            .filter(ClassDefinition.project_id == project_id)
            .scalar()
        )
        return 0 if max_index is None else max_index + 1

    def update_visibility(
        self, db: Session, *, class_id: int, is_visible: bool
    ) -> Optional[ClassDefinition]:
        """Update class visibility"""
        db_obj = self.get(db, id=class_id)
        if db_obj:
            db_obj.is_visible = is_visible
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def reorder_classes(
        self, db: Session, *, project_id: int, class_order: List[dict]
    ) -> List[ClassDefinition]:
        """Reorder classes by updating their class_index"""
        updated_classes = []
        
        for item in class_order:
            class_id = item.get("id")
            new_index = item.get("class_index")
            
            db_obj = self.get(db, id=class_id)
            if db_obj and db_obj.project_id == project_id:
                db_obj.class_index = new_index
                updated_classes.append(db_obj)
        
        if updated_classes:
            db.commit()
            for class_obj in updated_classes:
                db.refresh(class_obj)
        
        return updated_classes

    def get_class_with_segmentation_count(
        self, db: Session, *, project_id: int
    ) -> List[dict]:
        """Get classes with their segmentation count"""
        from ..models.segmentation import Segmentation
        
        result = (
            db.query(
                ClassDefinition,
                db.func.count(Segmentation.id).label("segmentation_count")
            )
            .outerjoin(Segmentation)
            .filter(ClassDefinition.project_id == project_id)
            .group_by(ClassDefinition.id)
            .order_by(ClassDefinition.class_index)
            .all()
        )
        
        return [
            {
                **class_def.__dict__,
                "segmentation_count": count
            }
            for class_def, count in result
        ]

class_definition = CRUDClassDefinition(ClassDefinition)