from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..crud.base import CRUDBase
from ..models.segmentation import Segmentation
from ..schemas.segmentation import SegmentationCreate, SegmentationUpdate

class CRUDSegmentation(CRUDBase[Segmentation, SegmentationCreate, SegmentationUpdate]):
    def get_by_image(
        self, db: Session, *, image_id: int, skip: int = 0, limit: int = 100
    ) -> List[Segmentation]:
        """Get segmentations by image ID"""
        return (
            db.query(self.model)
            .filter(Segmentation.image_id == image_id)
            .order_by(Segmentation.layer_index)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_image_and_class(
        self, db: Session, *, image_id: int, class_id: int
    ) -> List[Segmentation]:
        """Get segmentations by image ID and class ID"""
        return (
            db.query(self.model)
            .filter(and_(Segmentation.image_id == image_id, Segmentation.class_id == class_id))
            .order_by(Segmentation.layer_index)
            .all()
        )

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Segmentation]:
        """Get segmentations by project ID"""
        from ..models.image import Image
        
        return (
            db.query(self.model)
            .join(Image)
            .filter(Image.project_id == project_id)
            .order_by(Segmentation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_layer_order(
        self, db: Session, *, obj_in: SegmentationCreate
    ) -> Segmentation:
        """Create segmentation with automatic layer ordering"""
        # Get the next layer index for the image
        max_layer = (
            db.query(db.func.max(Segmentation.layer_index))
            .filter(Segmentation.image_id == obj_in.image_id)
            .scalar()
        )
        
        layer_index = 0 if max_layer is None else max_layer + 1
        
        obj_in_data = obj_in.dict()
        obj_in_data["layer_index"] = layer_index
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_layer_order(
        self, db: Session, *, segmentation_id: int, new_layer_index: int
    ) -> Optional[Segmentation]:
        """Update segmentation layer order"""
        db_obj = self.get(db, id=segmentation_id)
        if db_obj:
            old_layer_index = db_obj.layer_index
            image_id = db_obj.image_id
            
            # Shift other segmentations
            if new_layer_index > old_layer_index:
                # Moving up: shift down segmentations in between
                db.query(self.model).filter(
                    and_(
                        Segmentation.image_id == image_id,
                        Segmentation.layer_index > old_layer_index,
                        Segmentation.layer_index <= new_layer_index
                    )
                ).update({Segmentation.layer_index: Segmentation.layer_index - 1})
            elif new_layer_index < old_layer_index:
                # Moving down: shift up segmentations in between
                db.query(self.model).filter(
                    and_(
                        Segmentation.image_id == image_id,
                        Segmentation.layer_index >= new_layer_index,
                        Segmentation.layer_index < old_layer_index
                    )
                ).update({Segmentation.layer_index: Segmentation.layer_index + 1})
            
            # Update target segmentation
            db_obj.layer_index = new_layer_index
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        
        return db_obj

    def toggle_visibility(
        self, db: Session, *, segmentation_id: int
    ) -> Optional[Segmentation]:
        """Toggle segmentation visibility"""
        db_obj = self.get(db, id=segmentation_id)
        if db_obj:
            db_obj.is_visible = not db_obj.is_visible
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def toggle_lock(
        self, db: Session, *, segmentation_id: int
    ) -> Optional[Segmentation]:
        """Toggle segmentation lock status"""
        db_obj = self.get(db, id=segmentation_id)
        if db_obj:
            db_obj.is_locked = not db_obj.is_locked
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update_opacity(
        self, db: Session, *, segmentation_id: int, opacity: int
    ) -> Optional[Segmentation]:
        """Update segmentation opacity"""
        db_obj = self.get(db, id=segmentation_id)
        if db_obj:
            db_obj.opacity = max(0, min(255, opacity))  # Clamp to 0-255
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def bulk_update_visibility(
        self, db: Session, *, segmentation_ids: List[int], is_visible: bool
    ) -> List[Segmentation]:
        """Bulk update visibility for multiple segmentations"""
        segmentations = db.query(self.model).filter(Segmentation.id.in_(segmentation_ids)).all()
        for seg in segmentations:
            seg.is_visible = is_visible
        db.commit()
        for seg in segmentations:
            db.refresh(seg)
        return segmentations

    def get_visible_segmentations(
        self, db: Session, *, image_id: int
    ) -> List[Segmentation]:
        """Get visible segmentations for an image"""
        return (
            db.query(self.model)
            .filter(and_(Segmentation.image_id == image_id, Segmentation.is_visible == True))
            .order_by(Segmentation.layer_index)
            .all()
        )

    def get_unlocked_segmentations(
        self, db: Session, *, image_id: int
    ) -> List[Segmentation]:
        """Get unlocked segmentations for an image"""
        return (
            db.query(self.model)
            .filter(and_(Segmentation.image_id == image_id, Segmentation.is_locked == False))
            .order_by(Segmentation.layer_index)
            .all()
        )

    def mark_needs_simplification(
        self, db: Session, *, segmentation_id: int
    ) -> Optional[Segmentation]:
        """Mark segmentation as needing simplification"""
        db_obj = self.get(db, id=segmentation_id)
        if db_obj:
            db_obj.needs_simplification = True
            db_obj.is_processed = False
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

segmentation = CRUDSegmentation(Segmentation)