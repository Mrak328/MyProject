from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from pydantic import BaseModel
from fastapi import HTTPException, status

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.pk_column = self._get_pk_column()

    def _get_pk_column(self):
        """Определяет колонку первичного ключа"""
        for column in self.model.__table__.columns:
            if column.primary_key:
                return column
        raise ValueError(f"Model {self.model.__name__} has no primary key")

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Получить объект по первичному ключу"""
        return db.query(self.model).filter(self.pk_column == id).first()

    def get_or_404(self, db: Session, id: int) -> ModelType:
        """Получить объект или выбросить 404"""
        obj = self.get(db, id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} с id={id} не найден"
            )
        return obj

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Получить список объектов с фильтрацией и пагинацией"""
        query = db.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, list):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)
        return query.offset(skip).limit(limit).all()

    def create(
        self,
        db: Session,
        obj_in: Union[BaseModel, Dict[str, Any]],
        commit: bool = True
    ) -> ModelType:
        """Создать объект"""
        if isinstance(obj_in, dict):
            data = obj_in
        else:
            data = obj_in.dict()

        db_obj = self.model(**data)
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        else:
            db.flush()
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: Union[BaseModel, Dict[str, Any]]
    ) -> ModelType:
        """Обновить объект"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """Удалить объект по id"""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def delete_obj(self, db: Session, db_obj: ModelType) -> ModelType:
        """Удалить существующий объект"""
        db.delete(db_obj)
        db.commit()
        return db_obj

    def count(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Количество объектов с фильтрами"""
        query = db.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, list):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)
        return query.count()

    def exists(self, db: Session, id: int) -> bool:
        """Проверить существование объекта"""
        return db.query(
            db.query(self.model).filter(self.pk_column == id).exists()
        ).scalar()