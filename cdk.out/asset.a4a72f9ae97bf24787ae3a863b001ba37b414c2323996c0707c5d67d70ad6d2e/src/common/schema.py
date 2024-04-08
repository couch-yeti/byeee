from datetime import datetime
from typing import Optional, List
from uuid import uuid4, UUID

from pydantic.v1.main import BaseModel, Field
from pydantic.v1 import validator, ValidationError


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class Base(BaseModel):
    """Forced to use pydantic v1 for Langchain. Utilize generators
    and config dict in pydantic 2 when available
    """

    class Config:
        alias_generator = to_camel


class Validation(Base):
    plan_is_valid: bool = Field(
        description="This field is True if the plan is feasible, False otherwise"
    )


class PointsOfInterest(Base):
    days: int = Field(
        description="The number of days the user is staying in a location"
    )
    location: str = Field(description="Where the user desires to go")
    points_of_interest: List[str] = Field(
        description="A list of locations names that would be nice to visit or see in a given location"
    )


class Itinerary(Base):
    trip_start_date: datetime = Field(description="The day the trip begins")
    trip_days: int = Field(
        description="The number of days the user intends to spend at the location"
    )
    begin_location: str = Field(description="Where the trip is intended to start")
    end_location: str = Field(description="Where the trip is intended to end")
    itinerary_description: str = Field(
        description="The itinerary which describes the places to visit and what order to visit them in."
    )


class Mixin(BaseModel):
    uid: Optional[str]
    pk: Optional[str]
    sk: Optional[str]
    ak: Optional[str]
    created_date: datetime
    created_by_email: str


class Trip(Base, Mixin):
    """A trip contains all the components of
    a users experience (itinerary, places, pictures, people etc)"""

    owner_id: str
    trip_name: str
    trip_start_date: datetime


class Location(Base, Mixin):
    location_name: str = Field(description="A destination location for the trip")
    


class User(Mixin):
    email: str
    user_type: str
