from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Country, Region, City, District, Street, House

router = APIRouter(prefix="/geo", tags=["geography"])


@router.get("/countries")
async def get_countries(db: Session = Depends(get_db)):
    return [{"id": c.country_id, "name": c.name} for c in db.query(Country).order_by(Country.name).all()]


@router.get("/regions")
async def get_regions(country_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Region)
    if country_id:
        q = q.filter(Region.country_id == country_id)
    return [{"id": r.region_id, "name": r.name} for r in q.order_by(Region.name).all()]


@router.get("/cities")
async def get_cities(region_id: Optional[int] = None, country_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(City)
    if region_id:
        q = q.filter(City.region_id == region_id)
    elif country_id:
        q = q.join(Region).filter(Region.country_id == country_id)
    return [{"id": c.city_id, "name": c.name} for c in q.order_by(City.name).all()]


@router.get("/districts")
async def get_districts(city_id: int = Query(...), db: Session = Depends(get_db)):
    return [{"id": d.district_id, "name": d.name} for d in db.query(District).filter(District.city_id == city_id).order_by(District.name).all()]


@router.get("/streets")
async def get_streets(city_id: Optional[int] = None, district_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Street)
    if district_id:
        q = q.filter(Street.district_id == district_id)
    elif city_id:
        q = q.filter(Street.city_id == city_id)
    return [{"id": s.street_id, "name": s.name} for s in q.order_by(Street.name).limit(200).all()]


@router.get("/houses")
async def get_houses(street_id: int = Query(...), db: Session = Depends(get_db)):
    return [{"id": h.house_id, "number": h.number} for h in db.query(House).filter(House.street_id == street_id).order_by(House.number).all()]