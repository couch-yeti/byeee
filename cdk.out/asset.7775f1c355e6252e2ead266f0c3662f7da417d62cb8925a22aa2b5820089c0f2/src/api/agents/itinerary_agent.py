import os
from typing import Dict, Protocol, List

from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import root_validator
from langchain.chains import OpenAIModerationChain
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from templates.itinerary_template import (
    ValidationTemplate,
    POITemplate,
    ItineraryTemplate,
)


class Template(Protocol):
    chat_prompt: ChatPromptTemplate
    parser: PydanticOutputParser


class ModeratorChain(OpenAIModerationChain):
    """Overwriting the ModerationChain due to needed updates in the langchain library"""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""

        try:
            import openai

            values["client"] = openai.Client(api_key=os.environ["OPENAI_SECRET"])  # type: ignore
        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        return values

    def _call(self, inputs: Dict[str, str], run_manager=None) -> Dict[str, str]:

        text = inputs[self.input_key]
        results = self.client.moderations.create(input=text)
        output = {"flagged": results.results[0].flagged}
        output = self._moderate(text, output)
        return {self.output_key: output}


class ItineraryAgent:

    def __init__(self, model="gpt-3.5-turbo", temperature=.3, debug=True):
        self.model = model
        self.chat_model = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            openai_api_key=os.environ["OPENAI_SECRET"],
        )
        self.validation_prompt = ValidationTemplate()
        self.itinerary_prompt = ItineraryTemplate()
        self.places_prompt = POITemplate()

    def _make_chain(self, prompt: Template, moderate=False):
        chain = prompt.chat_prompt | self.chat_model | prompt.parser
        if moderate:
            moderate = ModeratorChain(openai_api_key=os.environ["OPENAI_SECRET"])
            moderate.input_key = "query"
            moderate.output_key = "sanitized_text"
            chain = moderate | chain
        return chain

    def _determine_prompt_type(self, prompt_type: str) -> Template:
        types_ = {
            "itinerary": self.itinerary_prompt,
            "validation": self.validation_prompt,
            "poi": self.places_prompt,
        }
        return types_[prompt_type]

    def invoke(self, query: str, prompt_type: str, moderate: bool = False):
        prompt = self._determine_prompt_type(prompt_type)
        chain = self._make_chain(prompt, moderate=moderate)
        return chain.invoke(
            {
                "query": query,
                "format_instructions": prompt.parser.get_format_instructions(),
            }
        )
