import typing as t

from data_model_region import Country
from pydantic import BaseModel, Field


class ExternalID(BaseModel):
    wikidata_id: str
    name: str


class Occupation(BaseModel):
    wikidata_id: str
    name: str = None
    category: t.List[str] = None


class RawNationality(BaseModel):
    wikidata_id: str = None
    name: str = None
    location: str = None


class RawBirthcity(BaseModel):
    wikidata_id: str = None
    name: str = None
    location: str = (None,)
    country_wikidata_id: str = None
    country_name: str = None
    country_location: str = None


class RawDeathcity(BaseModel):
    wikidata_id: str = None
    name: str = None
    location: str = (None,)
    country_wikidata_id: str = None
    country_name: str = None
    country_location: str = None


class RawIndividual(BaseModel):
    wikidata_id: str
    name: str = None
    birthyear: int = None
    gender: t.List[str] = None
    raw_nationalities: t.List[RawNationality] = None
    raw_birthcities: t.List[RawBirthcity] = None
    raw_deathcities: t.Optional[t.List[RawDeathcity]] = None  # Make it Optional
    occupations: t.List[Occupation] = None


class WikipediaPage(BaseModel):
    url: str
    language: str
    links_ext_count: int = None
    links_out_count: int = None
    links_in_count: int = None
    author: str = None
    author_editcount: int = None
    editors: int = None
    minor_edits: int = None
    revisions: int = None
    pageviews: int = None
    characters: int = None
    references: int = None
    unique_references: int = None
    words: int = None
    created_at: str = None


class Individual(BaseModel):
    id: RawIndividual
    impact_years: t.Tuple[int, int] = None
    cultural_score: float = None
    country: Country = None
    wikipedia_pages: t.List[WikipediaPage] = None
    regions: t.List[str] = None
    identifiers: t.List[ExternalID] = None
    country_data_origin: t.Optional[str] = None  # birthcity #deathcity #nationality
