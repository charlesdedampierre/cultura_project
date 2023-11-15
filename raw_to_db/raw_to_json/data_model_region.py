import typing as t

from pydantic import BaseModel


class Country(BaseModel):
    name: str
    iso_a3: str


class CountryFiltered(BaseModel):
    country: Country
    min_year: int = None
    max_year: int = None
    min_latitude: float = None
    max_latitude: float = None
    min_longitude: float = None
    max_longitude: float = None


class Region(BaseModel):
    name: str
    code: str
    countries_filtered: t.List[CountryFiltered] = None
    space_based: int = None
