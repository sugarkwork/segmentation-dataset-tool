from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..crud.base import CRUDBase
from ..models.annotation import Annotation
from ..schemas.annotation import AnnotationCreate, AnnotationUpdate

class CRUDAnnotation(CRUDBase[Annotation, AnnotationCreate, AnnotationUpdate]):
    def get_by_segmentation(
        self, db: Session, *, segmentation_id: int
    ) -> List[Annotation]:
        """Get annotations by segmentation ID"""
        return (
            db.query(self.model)
            .filter(Annotation.segmentation_id == segmentation_id)
            .order_by(Annotation.created_at)
            .all()
        )

    def get_by_image(
        self, db: Session, *, image_id: int
    ) -> List[Annotation]:
        """Get annotations by image ID"""
        from ..models.segmentation import Segmentation
        
        return (
            db.query(self.model)
            .join(Segmentation)
            .filter(Segmentation.image_id == image_id)
            .order_by(Annotation.created_at)
            .all()
        )

    def get_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Annotation]:
        """Get annotations by project ID"""
        from ..models.segmentation import Segmentation
        from ..models.image import Image
        
        return (
            db.query(self.model)
            .join(Segmentation)
            .join(Image)
            .filter(Image.project_id == project_id)
            .order_by(Annotation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_valid_annotations(
        self, db: Session, *, project_id: int
    ) -> List[Annotation]:
        """Get valid annotations for a project"""
        from ..models.segmentation import Segmentation
        from ..models.image import Image
        
        return (
            db.query(self.model)
            .join(Segmentation)
            .join(Image)
            .filter(
                and_(
                    Image.project_id == project_id,
                    Annotation.is_valid == True
                )
            )
            .all()
        )

    def get_export_ready_annotations(
        self, db: Session, *, project_id: int, export_format: str = "yolo"
    ) -> List[Annotation]:
        """Get annotations ready for export"""
        from ..models.segmentation import Segmentation
        from ..models.image import Image
        
        return (
            db.query(self.model)
            .join(Segmentation)
            .join(Image)
            .filter(
                and_(
                    Image.project_id == project_id,
                    Annotation.is_valid == True,
                    Annotation.is_exported == False
                )
            )
            .all()
        )

    def create_from_segmentation(
        self, db: Session, *, segmentation_id: int, normalized_coordinates: str, 
        original_coordinates: str = None, **kwargs
    ) -> Annotation:
        """Create annotation from segmentation data"""
        import json
        
        # Parse coordinates to get point count
        try:
            coords = json.loads(normalized_coordinates)
            point_count = len(coords) // 2  # x,y pairs
        except:
            point_count = 0
        
        annotation_data = {
            "segmentation_id": segmentation_id,
            "normalized_coordinates": normalized_coordinates,
            "original_coordinates": original_coordinates,
            "point_count": point_count,
            **kwargs
        }
        
        db_obj = self.model(**annotation_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_validation_status(
        self, db: Session, *, annotation_id: int, is_valid: bool, 
        validation_errors: str = None
    ) -> Optional[Annotation]:
        """Update annotation validation status"""
        db_obj = self.get(db, id=annotation_id)
        if db_obj:
            db_obj.is_valid = is_valid
            db_obj.validation_errors = validation_errors
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def mark_as_exported(
        self, db: Session, *, annotation_id: int, export_format: str
    ) -> Optional[Annotation]:
        """Mark annotation as exported"""
        db_obj = self.get(db, id=annotation_id)
        if db_obj:
            db_obj.is_exported = True
            db_obj.export_format = export_format
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def bulk_mark_as_exported(
        self, db: Session, *, annotation_ids: List[int], export_format: str
    ) -> List[Annotation]:
        """Bulk mark annotations as exported"""
        annotations = db.query(self.model).filter(Annotation.id.in_(annotation_ids)).all()
        for annotation in annotations:
            annotation.is_exported = True
            annotation.export_format = export_format
        db.commit()
        for annotation in annotations:
            db.refresh(annotation)
        return annotations

    def calculate_polygon_metrics(
        self, db: Session, *, annotation_id: int, polygon_area: float = None,
        perimeter: float = None, compactness: float = None
    ) -> Optional[Annotation]:
        """Update polygon geometric metrics"""
        db_obj = self.get(db, id=annotation_id)
        if db_obj:
            if polygon_area is not None:
                db_obj.polygon_area = polygon_area
            if perimeter is not None:
                db_obj.perimeter = perimeter
            if compactness is not None:
                db_obj.compactness = compactness
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update_simplification_info(
        self, db: Session, *, annotation_id: int, is_simplified: bool,
        simplification_tolerance: float = None, new_point_count: int = None
    ) -> Optional[Annotation]:
        """Update simplification information"""
        db_obj = self.get(db, id=annotation_id)
        if db_obj:
            db_obj.is_simplified = is_simplified
            if simplification_tolerance is not None:
                db_obj.simplification_tolerance = simplification_tolerance
            if new_point_count is not None:
                db_obj.point_count = new_point_count
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_annotations_by_class(
        self, db: Session, *, project_id: int, class_id: int
    ) -> List[Annotation]:
        """Get annotations by class definition"""
        from ..models.segmentation import Segmentation
        from ..models.image import Image
        
        return (
            db.query(self.model)
            .join(Segmentation)
            .join(Image)
            .filter(
                and_(
                    Image.project_id == project_id,
                    Segmentation.class_id == class_id
                )
            )
            .all()
        )

annotation = CRUDAnnotation(Annotation)