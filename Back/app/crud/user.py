from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import Users
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[Users]):
    def get_by_phone(self, db: Session, phone: str) -> Users | None:
        return db.query(Users).filter(Users.phone_number == phone).first()

    def get_by_email(self, db: Session, email: str) -> Users | None:
        return db.query(Users).filter(Users.email == email).first()

    def get_by_email_or_phone(self, db: Session, value: str) -> Users | None:
        """Поиск пользователя по email ИЛИ телефону"""
        # Если в строке есть @ - это email
        if '@' in value:
            user = self.get_by_email(db, value)
            if user:
                return user

        # Иначе пробуем найти по телефону
        user = self.get_by_phone(db, value)
        if user:
            return user

        return None

    def authenticate(self, db: Session, email_or_phone: str, password: str) -> Users | None:
        """Аутентификация по email/телефону и паролю"""
        user = self.get_by_email_or_phone(db, email_or_phone)
        if not user:
            return None
        return user


user_crud = CRUDUser(Users)