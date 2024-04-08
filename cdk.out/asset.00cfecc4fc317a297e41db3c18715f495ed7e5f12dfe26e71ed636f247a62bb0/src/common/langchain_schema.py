from datetime import datetime
from typing import Optional, List

from langchain.pydantic_v1 import BaseModel, Field


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class Base(BaseModel):
    """Forced to use pydantic v1 for Langchain. Utilize generators
    and config dict in pydantic 2 when available
    """

    class Config:
        alias_generator = to_camel


class LGValidation(Base):
    plan_is_valid: bool = Field(
        description="This field is True if the plan is feasible, False otherwise"
    )


class LGPointsOfInterest(Base):
    days: int = Field(
        description="The number of days the user is staying in a location"
    )
    location: str = Field(description="Where the user desires to go")
    points_of_interest: List[str] = Field(
        description="A list of locations names that would be nice to visit or see in a given location"
    )


class LGItinerary(Base):
    itinerary_start_date: datetime = Field(
        description="The date the traveler arrives at the desired location"
    )
    itinerary_days: int = Field(
        description="The number of days the user intends to spend at the location"
    )
    itinerary_location: str = Field(
        description="The place the traveler is visiting"
    )
    itinerary_description: str = Field(
        description="The itinerary which describes the places to visit and what order to visit them in."
    )
