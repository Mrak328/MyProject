from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Listing])
async def get_all_listings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """
    Получить все активные объявления (для главной)
    """
    listings = crud.get_active_listings(db, skip=skip, limit=limit)
    return listings


@router.get("/search", response_model=List[schemas.Listing])
async def search_listings(
        # Пагинация
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),

        # Фильтры
        city: Optional[str] = None,
        deal_type: Optional[str] = None,
        rooms: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        db: Session = Depends(get_db)
):
    """
    Поиск по активным объявлениям с фильтрацией
    """
    query = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1,
        models.Listing.moderated == True
    )

    if city:
        query = query.filter(models.Listing.address.ilike(f'%{city}%'))
    if deal_type:
        query = query.join(models.DealType).filter(models.DealType.name.ilike(f'%{deal_type}%'))
    if rooms:
        query = query.filter(models.Listing.title.ilike(f'%{rooms} комн%'))
    if min_price:
        query = query.filter(models.Listing.price >= min_price)
    if max_price:
        query = query.filter(models.Listing.price <= max_price)

    return query.order_by(models.Listing.publication_date.desc()).offset(skip).limit(limit).all()

@router.get("/", response_model=List[schemas.Listing])
async def search_listings(
        # Пагинация
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=50),

        # Тип сделки
        deal_type: Optional[str] = Query(None, description="sale/rent"),

        # Параметры недвижимости
        property_type: Optional[str] = Query(None, description="apartment/house/room"),
        rooms: Optional[int] = Query(None, ge=1, le=10),

        # Цена
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),

        # Площадь
        min_area: Optional[float] = Query(None, ge=0),
        max_area: Optional[float] = Query(None, ge=0),

        # Локация
        city: Optional[str] = None,
        district: Optional[str] = None,
        metro: Optional[str] = None,

        # Сортировка
        sort_by: str = Query("date_desc", description="price_asc/price_desc/date_desc/views_desc"),

        db: Session = Depends(get_db)
):
    """
    Поиск недвижимости с фильтрацией
    - Продажа/аренда
    - Квартиры/дома/комнаты
    - Количество комнат
    - Цена от и до
    - Площадь от и до
    - Город/район/метро
    - Сортировка
    """
    skip = (page - 1) * page_size

    listings = crud.search_listings(
        db=db,
        skip=skip,
        limit=page_size,
        deal_type=deal_type,
        property_type=property_type,
        rooms=rooms,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        city=city,
        district=district,
        metro=metro,
        sort_by=sort_by
    )

    return listings


@router.get("/{listing_id}", response_model=schemas.Listing)
async def get_listing(
        listing_id: int,
        db: Session = Depends(get_db)
):
    """Детальная карточка объявления"""
    listing = crud.get_listing(db, listing_id=listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Увеличиваем счетчик просмотров
    crud.increment_listing_views(db, listing_id)

    return listing


@router.get("/{listing_id}/photos", response_model=List[schemas.Photo])
async def get_listing_photos(
        listing_id: int,
        db: Session = Depends(get_db)
):
    """Все фотографии объекта"""
    return crud.get_photos_by_listing(db, listing_id)


@router.get("/{listing_id}/contacts", response_model=dict)
async def get_contacts(
        listing_id: int,
        db: Session = Depends(get_db)
):
    """
    Контакты продавца (телефон)
    - Доступно только после регистрации
    - Логируем запрос контактов
    """
    listing = crud.get_listing(db, listing_id=listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Логируем запрос контактов
    crud.log_contact_request(db, listing_id)

    return {
        "phone": listing.contact_phone,
        "person": listing.contact_person
    }


@router.post("/{listing_id}/view")
async def register_view(
        listing_id: int,
        user_id: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Зарегистрировать просмотр объявления"""
    crud.register_listing_view(db, listing_id, user_id)
    return {"status": "ok"}


@router.post("/{listing_id}/favorite")
async def add_to_favorites(
        listing_id: int,
        user_id: int,
        db: Session = Depends(get_db)
):
    """Добавить в избранное"""
    favorite = crud.add_favorite(db, user_id, listing_id)
    return {"status": "added", "favorite_id": favorite.favorite_id}


@router.delete("/{listing_id}/favorite")
async def remove_from_favorites(
        listing_id: int,
        user_id: int,
        db: Session = Depends(get_db)
):
    """Удалить из избранного"""
    crud.remove_favorite(db, user_id, listing_id)
    return {"status": "removed"}


@router.get("/similar/{listing_id}", response_model=List[schemas.Listing])
async def get_similar_listings(
        listing_id: int,
        limit: int = 5,
        db: Session = Depends(get_db)
):
    """Похожие объявления (тот же район, тип, цена)"""
    return crud.get_similar_listings(db, listing_id, limit)


@router.get("/", response_model=List[schemas.Listing])
async def get_all_listings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Получить все активные объявления"""
    listings = crud.get_active_listings(db, skip=skip, limit=limit)
    return listings


@router.get("/search", response_model=List[schemas.Listing])
async def search_listings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        city: Optional[str] = None,
        deal_type: Optional[str] = None,
        rooms: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        db: Session = Depends(get_db)
):
    """Поиск по активным объявлениям"""
    query = db.query(models.Listing).filter(
        models.Listing.listing_status_id == 1,
        models.Listing.moderated == True
    )

    if city:
        query = query.filter(models.Listing.address.ilike(f'%{city}%'))
    if deal_type:
        query = query.join(models.DealType).filter(models.DealType.name.ilike(f'%{deal_type}%'))
    if rooms:
        query = query.filter(models.Listing.title.ilike(f'%{rooms} комн%'))
    if min_price:
        query = query.filter(models.Listing.price >= min_price)
    if max_price:
        query = query.filter(models.Listing.price <= max_price)

    return query.order_by(models.Listing.publication_date.desc()).offset(skip).limit(limit).all()


@router.get("/{listing_id}", response_model=schemas.ListingDetail)
async def get_listing_detail(listing_id: int, db: Session = Depends(get_db)):
    """Детальная информация об объявлении с фото"""
    listing = crud.get_listing_with_photos(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Увеличиваем счетчик просмотров
    crud.increment_listing_views(db, listing_id)

    return listing


@router.get("/{listing_id}/contacts")
async def get_contacts(listing_id: int, db: Session = Depends(get_db)):
    """Контакты продавца"""
    contacts = crud.get_listing_contacts(db, listing_id)
    if not contacts:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Логируем запрос контактов
    crud.log_contact_request(db, listing_id)

    return contacts


