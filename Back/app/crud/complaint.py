from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
from app.models import Complaint


class CRUDComplaint:

    def create(
            self,
            db: Session,
            complainant_user_id: int,
            complaint_type_id: int,
            listing_id: Optional[int] = None,
            violator_user_id: Optional[int] = None,
            description: Optional[str] = None
    ) -> Complaint:
        complaint = Complaint(
            complainant_user_id=complainant_user_id,
            listing_id=listing_id,
            violator_user_id=violator_user_id,
            complaint_type_id=complaint_type_id,
            description=description
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint

    def get(self, db: Session, complaint_id: int) -> Optional[Complaint]:
        return db.query(Complaint).filter(
            Complaint.complaint_id == complaint_id
        ).first()

    def get_all(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100
    ) -> List[Complaint]:
        return db.query(Complaint).order_by(
            desc(Complaint.created_date)
        ).offset(skip).limit(limit).all()

    def get_by_listing(self, db: Session, listing_id: int) -> List[Complaint]:
        return db.query(Complaint).filter(
            Complaint.listing_id == listing_id
        ).order_by(desc(Complaint.created_date)).all()

    def get_by_complainant(self, db: Session, user_id: int) -> List[Complaint]:
        return db.query(Complaint).filter(
            Complaint.complainant_user_id == user_id
        ).order_by(desc(Complaint.created_date)).all()

    def get_by_violator(self, db: Session, user_id: int) -> List[Complaint]:
        return db.query(Complaint).filter(
            Complaint.violator_user_id == user_id
        ).order_by(desc(Complaint.created_date)).all()

    def get_pending(self, db: Session) -> List[Complaint]:
        """Жалобы без решения (resolution IS NULL)"""
        return db.query(Complaint).filter(
            Complaint.resolution.is_(None)
        ).order_by(Complaint.created_date).all()

    def resolve(
            self,
            db: Session,
            complaint_id: int,
            moderator_id: int,
            resolution: str
    ) -> Optional[Complaint]:
        complaint = self.get(db, complaint_id)
        if complaint:
            complaint.moderator_id = moderator_id
            complaint.resolution = resolution
            complaint.processing_date = datetime.now()
            db.commit()
            db.refresh(complaint)
        return complaint

    def delete(self, db: Session, complaint_id: int) -> bool:
        complaint = self.get(db, complaint_id)
        if complaint:
            db.delete(complaint)
            db.commit()
            return True
        return False


complaint_crud = CRUDComplaint()