from typing import List, Optional
from sqlalchemy.orm import Session
from ..crud.base import CRUDBase
from ..models.image import Image
from ..schemas.image import ImageCreate, ImageUpdate

class CRUDImage(CRUDBase[Image, ImageCreate, ImageUpdate]):
    def get_by_project(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[Image]:
        """Get images by project ID"""
        return (
            db.query(self.model)
            .filter(Image.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_project_and_dataset_type(
        self, db: Session, *, project_id: int, dataset_type: str
    ) -> List[Image]:
        """Get images by project ID and dataset type"""
        return (
            db.query(self.model)
            .filter(Image.project_id == project_id, Image.dataset_type == dataset_type)
            .all()
        )

    def get_by_filename(self, db: Session, *, project_id: int, filename: str) -> Optional[Image]:
        """Get image by project ID and filename"""
        return (
            db.query(self.model)
            .filter(Image.project_id == project_id, Image.filename == filename)
            .first()
        )

    def create_with_project(self, db: Session, *, obj_in: ImageCreate, project_id: int, **kwargs) -> Image:
        """Create image with project ID and additional metadata"""
        obj_in_data = obj_in.dict()
        obj_in_data.update(kwargs)
        db_obj = self.model(**obj_in_data, project_id=project_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_processing_status(self, db: Session, *, image_id: int, is_processed: bool) -> Optional[Image]:
        """Update image processing status"""
        db_obj = self.get(db, id=image_id)
        if db_obj:
            db_obj.is_processed = is_processed
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update_annotation_status(self, db: Session, *, image_id: int, has_annotations: bool) -> Optional[Image]:
        """Update image annotation status"""
        db_obj = self.get(db, id=image_id)
        if db_obj:
            db_obj.has_annotations = has_annotations
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_images_with_annotations(self, db: Session, *, project_id: int) -> List[Image]:
        """Get images that have annotations"""
        return (
            db.query(self.model)
            .filter(Image.project_id == project_id, Image.has_annotations == True)
            .all()
        )

    def bulk_update_dataset_type(
        self, db: Session, *, image_ids: List[int], dataset_type: str
    ) -> List[Image]:
        """Bulk update dataset type for multiple images"""
        images = db.query(self.model).filter(Image.id.in_(image_ids)).all()
        for image in images:
            image.dataset_type = dataset_type
        db.commit()
        for image in images:
            db.refresh(image)
        return images

image = CRUDImage(Image)