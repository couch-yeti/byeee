import os
from uuid import uuid4

from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Path
from dotenv import load_dotenv
from openai import OpenAI

from common import langchain_schema
from common.aws import dynamo
from common.log import get_child_logger
from agents.itinerary_agent import ItineraryAgent

load_dotenv()
logger = get_child_logger()
router = APIRouter(prefix="/itinerary", tags=["itinerary"])


def insert_itinerary(trip_id, itinerary):
    table = dynamo.get_table()

    itinerary.uid = itinerary.pk = trip_id
    itinerary.sk = "itinerary"
    table.put_item(Item={itinerary.model_dump()})


def get_location_pois(trip_id, location_id):

    table = dynamo.get_table()
    expr = Key("pk").eq(trip_id) & Key("sk").eq("trip")
    points_of_interest = table.get_item(
        Key={"pk": trip_id, "sk": f"location::{location_id}"},
        ProjectionExpression="points_of_interest",
    )["Item"]
    return points_of_interest


@router.post("/{tripId}/{locationId}itinerary")
def add_itinerary(tripId: str) -> str:
    """Add an itinerary object to the database and receive a uid in return"""
    trip_id: str = Path(
        description="The identifier for the trip needing an itinerary", alias="tripId"
    )
    location_id: str = Path(
        description="The identifier for a given location in the trip"
    )
    agent = ItineraryAgent()
    pois = get_location_pois(trip_id=trip_id, location_id=location_id)
    result = agent.invoke(query=pois, prompt_type="itinerary")
    return result.itinerary_description


@router.get("/")
def get_itinerary(uid: str):
    """Get itinerary preferences from database, build prompt, pass to llm return response"""
    table = dynamo.get_table()
    trip_desc = table.get_item()

    client = OpenAI(api_key=os.environ["openai_secret"])
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
            },
            {
                "role": "user",
                "content": "Compose a poem that explains the concept of recursion in programming.",
            },
        ],
    )
    return completion


if __name__ == "__main__":
    print(get_itinerary(uid="123123"))
