from datetime import datetime
from typing import Optional, List
from uuid import uuid4, UUID

from pydantic import (
    BaseModel,
    create_model,
    Field,
    ConfigDict,
    alias_generators,
)

now = datetime.now()


def make_db_schema(base_model: type):
    """function adds mixin fields dynamically to be used in customer facing
    models
    """
    BaseModel.model_fields
    name = f"{base_model.__name__}DB"
    fields = {}
    for model in [base_model, Mixin]:
        fields_ = {
            field_name: (field.annotation, field.default)
            for field_name, field in model.model_fields.items()
        }
        fields.update(fields_)

    return create_model(name, **fields)


class Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        extra="ignore",
        populate_by_name=True,
    )


class Mixin(BaseModel):
    uid: Optional[str]
    pk: Optional[str]
    sk: Optional[str]
    ak: Optional[str] = None
    created_date: str = now.strftime("%B %d, %Y - %I:%M %p")
    created_by_email: str


class Location(Base):
    location_name: str = Field(
        description="A destination location for the trip"
    )


class Itinerary(Base):
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


class User(Base):
    email: str
    user_type: str


class Trip(Base):
    """A trip contains all the components of
    a users experience (itinerary, places, pictures, people etc)"""

    trip_name: str
    start_date: str
    locations: Optional[List[Location]] = None
    itineraries: Optional[List[Itinerary]] = None
    trip_owner: User


class ItemUID(Base):
    uid: str
