from pydantic import BaseModel
from typing import Optional, List


class CountryResponse(BaseModel):
    country_id: int
    name: str

    class Config:
        from_attributes = True


class RegionResponse(BaseModel):
    region_id: int
    country_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class CityResponse(BaseModel):
    city_id: int
    region_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class DistrictResponse(BaseModel):
    district_id: int
    city_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class StreetResponse(BaseModel):
    street_id: int
    city_id: Optional[int] = None
    district_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class HouseResponse(BaseModel):
    house_id: int
    street_id: Optional[int] = None
    number: str

    class Config:
        from_attributes = True


class ApartmentResponse(BaseModel):
    apartment_id: int
    house_id: Optional[int] = None
    number: str

    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    address_id: int
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    street: Optional[str] = None
    house: Optional[str] = None
    apartment: Optional[str] = None

    class Config:
        from_attributes = True