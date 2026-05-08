from sqlalchemy.orm import Session
from typing import Optional, List
from app.crud.base import CRUDBase
from app.models import Users


class CRUDUser(CRUDBase[Users]):

    def get_by_phone(self, db: Session, phone: str) -> Optional[Users]:
        return db.query(Users).filter(Users.phone_number == phone).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Users]:
        return db.query(Users).filter(Users.email == email).first()

    def get_by_email_or_phone(self, db: Session, value: str) -> Optional[Users]:
        """Поиск пользователя по email ИЛИ телефону"""
        if '@' in value:
            return self.get_by_email(db, value)
        return self.get_by_phone(db, value)

    def get_by_role(
            self,
            db: Session,
            role_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Users]:
        """Пользователи с определённой ролью"""
        return (
            db.query(Users)
            .filter(Users.role_id == role_id)
            .order_by(Users.registration_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_last_activity(self, db: Session, user_id: int) -> None:
        """Обновить время последней активности"""
        db.query(Users).filter(Users.user_id == user_id).update(
            {Users.last_activity: db.func.now()},
            synchronize_session=False
        )
        db.commit()

    def is_phone_taken(self, db: Session, phone: str, exclude_user_id: Optional[int] = None) -> bool:
        """Проверка занятости телефона"""
        query = db.query(Users).filter(Users.phone_number == phone)
        if exclude_user_id:
            query = query.filter(Users.user_id != exclude_user_id)
        return query.first() is not None

    def is_email_taken(self, db: Session, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Проверка занятости email"""
        query = db.query(Users).filter(Users.email == email)
        if exclude_user_id:
            query = query.filter(Users.user_id != exclude_user_id)
        return query.first() is not None


user_crud = CRUDUser(Users)