from typing import List, Optional

from pydantic import BaseModel


class WikidataEntity(BaseModel):
    id: str
    label: str


class ComplexityObject(BaseModel):
    instance: Optional[List[WikidataEntity]]
    inception: Optional[List[str]]
    time_period: Optional[List[WikidataEntity]]
    culture: Optional[List[WikidataEntity]]
    architecture_style: Optional[List[WikidataEntity]]
    founded_by: Optional[List[WikidataEntity]]
    creator: Optional[List[WikidataEntity]]
    country: Optional[List[WikidataEntity]]
    territory: Optional[List[WikidataEntity]]
