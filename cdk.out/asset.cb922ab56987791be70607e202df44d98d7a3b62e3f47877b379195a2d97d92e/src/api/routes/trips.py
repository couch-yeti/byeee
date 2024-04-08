import os
from uuid import uuid4

from fastapi import APIRouter

from common import schema
from common.aws import dynamo

router = APIRouter(prefix="/trip", tags=["trip"])


@router.post("/", response_model=schema.ItemUID)
def post_trip(trip: schema.Trip):
    table = dynamo.get_table(table_name=os.environ["TABLE"])
    DBTrip = schema.make_db_schema(
        base_model=schema.Trip,
    )
    created_by_email = trip.trip_owner.email
    pk = uid = str(uuid4())
    db_trip = DBTrip(
        pk=pk,
        uid=uid,
        sk="trip",
        created_by_email=created_by_email,
        user_type=trip.trip_owner.user_type,
        **trip.model_dump(),
    )
    table.put_item(Item=db_trip.model_dump())
    return schema.ItemUID(uid=db_trip.uid)


if __name__ == "__main__":
    os.environ["TABLE"] = "byeee-dev"
    item = {
        "tripName": "sequoias",
        "startDate": "1-12-2024",
        "tripOwner": {"email": "eric.barrow@stuff.com", "userType": "owner"},
    }
    trip = schema.Trip(**item)

    print(post_trip(trip=trip))
