from sqlalchemy.orm import Session
from app.models import Complaint


class CRUDComplaint:
    def create_complaint(self, db: Session, complainant_id: int, listing_id: int, complaint_type: str,
                         description: str = None):
        complaint = Complaint(
            complainant_user_id=complainant_id,
            listing_id=listing_id,
            complaint_type=complaint_type,
            description=description,
            processing_status="new"
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint

    def get_listing_complaints(self, db: Session, listing_id: int):
        return db.query(Complaint).filter(Complaint.listing_id == listing_id).all()

    def update_status(self, db: Session, complaint_id: int, status: str):
        db.query(Complaint).filter(Complaint.complaint_id == complaint_id).update({"processing_status": status})
        db.commit()


complaint_crud = CRUDComplaint()