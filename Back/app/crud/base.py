from sqlalchemy.orm import Session
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        # Находим первичный ключ
        for column in self.model.__table__.columns:
            if column.primary_key:
                pk_column = column
                break
        else:
            raise ValueError(f"Model {self.model.__name__} has no primary key")
        return db.query(self.model).filter(pk_column == id).first()

    def get_multi(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        query = db.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            db_obj: ModelType,
            obj_in
    ) -> ModelType:
        for field, value in obj_in.dict(exclude_unset=True).items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        query = db.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.count()