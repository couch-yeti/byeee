from typing import List

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import PydanticOutputParser

from common.langchain_schema import (
    BaseModel,
    LGValidation,
    LGItinerary,
    LGPointsOfInterest,
)


class BaseTemplate:
    def __init__(self, pydantic_object: BaseModel):
        self.pydantic_object = pydantic_object
        self.human_template = """ #### {query} #### """
        self.parser = PydanticOutputParser(pydantic_object=pydantic_object)
        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )
        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )


class ValidationTemplate(BaseTemplate):
    def __init__(self):
        self.system_template = """You're a system that determines if a user's travel 
        plans are physically possible. You will be given a statement regarding a user's
        intentions and you will determine if the desired plans are feasible within some
        assume or given constraints.  

        For instance, a user couldn't feasibly travel to moon and back. They could also 
        not go from Los Angeles California to Paris France and back in 1 day. 

        If the plans are not reasonable then update the PlanIsValid parameter appropriately.
        
        {format_instructions}
        """
        super().__init__(pydantic_object=LGValidation)


class POITemplate(BaseTemplate):

    def __init__(self, **kw):
        self.system_template = """
        You are a travel agent who determines the best possible places to go
        and sites to see at any of the locations a user requests to visit.  
        
        The user's travel plans will be denoted by four hastags. 
        
        Read the location that the user wants to visit and return things the 
        user would want to do in that location. Be careful to only suggest things
        that are possible to in the given timeframe. 

        {format_instructions}
        """
        super().__init__(pydantic_object=LGPointsOfInterest)


class ItineraryTemplate(BaseTemplate):

    def __init__(self):
        self.system_template = """
        You are a tavel agent that creates an itinerary of things to do or see in a given
        location. 

        The user's points will be denoted by four hastags. It will be mapping of points of
        interest, locations and the number of days the user will be in the location. 
        
        Take those locations and describe an enjoyable itinerary while making sure to 
        keep the locations in an order that would most optimal for travel, and only keep 
        as many locations as possible to see in the desired amount of days. Try to make 
        itinerary as description and as fun sounding as possible. 
        
        {format_instructions}
        """
        super().__init__(pydantic_object=LGItinerary)
