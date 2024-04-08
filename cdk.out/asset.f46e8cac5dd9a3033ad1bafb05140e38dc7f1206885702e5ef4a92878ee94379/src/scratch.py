import os

from dotenv import load_dotenv

load_dotenv(".env.secret")


if __name__ == "__main__":
    import boto3

    resource = boto3.resource("dynamodb")
    resource.Table("polygon-table2F921907-192ZKR6WALCN2")

    from api.agents.itinerary_agent import ItineraryAgent
    from common.langchain_schema import PointsOfInterest

    travel_plans = """
        I want to visit the Sequoia National Park in california for 5 days starting on the 29th of March
        """
    # trip_plans = """I'd like to spend 5 days in LA"""

    pois = PointsOfInterest(
        Days=5,
        Location="Sequoia National Park",
        PointsOfInterest=["general sherman", "crystal cave", "mount whitney"],
    )

    agent = ItineraryAgent()
    print(agent.invoke(query=travel_plans, prompt_type="validation", moderate=True))
    places = agent.invoke(query=travel_plans, prompt_type="poi")
    print(f"PLACES TO GO: {places}")
    print(agent.invoke(query=places.dict(), prompt_type="itinerary"))
