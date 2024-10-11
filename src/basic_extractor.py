from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, field_validator
from langchain.output_parsers import OutputFixingParser


import json
from pathlib import Path
from typing import List, Union, Optional

import os
import sys
import re


# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging


# JSON OUTPUT PARSER EXAMPLE
class MomentExtractor:
    def __init__(self, llm):
        self.llm = llm

    def moment_extractor(self, docs, life_name=None, additional_promt=None):
        """
        Extracts moments from a list of documents.

        Args:
            docs: A list of strings, where each string is a document.
            life_name: (Optional) A name associated with the life or entity the moments belong to.
            additional_prompt: (Optional) An additional prompt to provide to the model for context.

        Returns:
            A dictionary containing extracted moments.
            The format of the dictionary can be customized based on your use case.
            Example:
            {
                "incidents": [
                    {"text": "The dog barked.", "life_name": "My Dog", "start_time": "2023-10-26T10:00:00Z"},
                    {"text": "The cat slept on the couch.", "life_name": "My Cat", "start_time": "2023-10-26T11:00:00Z"}
                ]
            }
        """
        logging.info("Starting to extract basic moments from main docs")

        class Moment(BaseModel):
            """A single incident with a year, optional month, and optional day, title, and description."""

            Year: str = Field(
                description="The integer year of the incident in BCE, CE, BC, or AD"
            )

            Month: Optional[Union[int, str]] = Field(
                default=None, description="The month of the incident."
            )
            Day: Optional[int] = Field(
                default=None, description="The day of the incident."
            )
            Title: str = Field(description="Title of the incident in 20 words.")
            Description: str = Field(
                description="Professional description of the incident more than 300 words."
            )
            # Type: List[str] = Field(description="Type or categories of the moment")
            Era: str = Field(
                description="What era this incident happens, BCE, CE, BC, or AD based on the year",
                pattern="^(BCE|CE|BC|AD)$",
            )

            # @validator("Era", allow_reuse=True)
            # def validate_era(cls, v, values):
            #     if "Year" in values:
            #         if values["Year"] < 0 and v not in ["BCE", "BC"]:
            #             raise ValueError("Year is BCE/BC but Era is not set to BCE/BC")
            #         elif values["Year"] >= 0 and v not in ["CE", "AD"]:
            #             raise ValueError("Year is CE/AD but Era is not set to CE/AD")
            #     return v
            # @validator("Year", allow_reuse=True)
            # def validate_year(cls, v):
            #     if not isinstance(v, int):
            #         raise ValueError("Year must be an integer")
            #     return v

            @field_validator("Title")
            def validate_title_length(cls, v):
                if len(v.split()) > 20:
                    raise ValueError("Title must be 20 words or less")
                return v

            @field_validator("Description")
            def validate_description_length(cls, v):
                if len(v.split()) < 300:
                    raise ValueError("Description must be more than 300 words")
                return v

        class Moments(BaseModel):
            """A list of special incidents."""

            incidents: List[Moment] = Field(description="A list of special incidents.")

        # Create a parser
        parser = JsonOutputParser(pydantic_object=Moments)
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Extract the following fields about {life}from the document:\nYear (mandatory), Month (if available), Day (if available), Title, Description, and Era. Ensure that the Year is always extracted.\nAdditonal instructions(if applicable)for extraction :\n{instructions}\nFormatting Instructions:\n{format_instructions}",
                ),
                ("human", "{Document}"),
            ]
        ).partial(
            format_instructions=parser.get_format_instructions(),
        )

        chain = prompt | self.llm | parser

        try:
            print("***************TRYING 01 *********************")
            # Step 1: Try invoking the chain
            answer = chain.invoke(
                {"Document": docs, "instructions": additional_promt, "life": life_name}
            )
            logging.info(f"Basic incidents extarcted in first attempt : {answer}")
            return answer  # Return the answer here if successful
        except Exception as error1:
            logging.warning(CustomException(error1, sys))
            print("***************TRYING 02 *********************")
            try:
                # Step 2: If error1 occurs, try matching re function on error1
                match = re.search(r"(\{.*\})", str(error1), re.DOTALL)
                if match:
                    print("***************TRYING 03 *********************")
                    json_str = match.group(1)
                    extracted_answer = json.loads(json_str)
                    logging.info(
                        f"Basic incidents extarcted in error matching : {extracted_answer}"
                    )
                    return extracted_answer  # Return the extracted answer if successful
                else:
                    print("***************TRYING 04 *********************")
                    # Step 3: If no match, pass error1 to fixing_parser
                    answer = fixing_parser.parse(error1)
                    logging.info(answer)
                    return answer  # Return the fixed answer if successful
            except Exception as error2:
                logging.warning(CustomException(error2, sys))
                print("***************TRYING 05 *********************")
                match = re.search(r"(\{.*\})", str(error2), re.DOTALL)
                if match:
                    print("***************TRYING 06 *********************")
                    json_str = match.group(1)
                    extracted_answer = json.loads(json_str)
                    logging.info(extracted_answer)
                    return extracted_answer  # Return the extracted answer from error2
                else:
                    logging.warning(
                        "Aftre 6th Tyring it is not recieved incidents in basic extraction"
                    )
                    return None

    def save_to_json(
        self, id: int, file_path: str, incidents: Union[List[BaseModel], dict, None]
    ):
        try:
            """Saves the extracted incidents to a JSON file in the required format."""
            # Extract the file name without extension
            # file_name = os.path.splitext(os.path.basename(file_path))[0]

            # Construct the relevant folder path inside JSON_Data
            json_folder = Path("JSON_Data") / f"{file_path}" / "extracted"
            if not json_folder.exists():
                json_folder.mkdir(parents=True, exist_ok=True)

            # Construct the file name
            json_file_name = f"incidents_{id}.json"

            # Create the full file path
            full_file_path = json_folder / json_file_name

            # Prepare the data in the desired format
            if incidents is None:
                data = {"incidents": []}
            elif isinstance(incidents, dict) and "incidents" in incidents:
                # If incidents is already in dictionary format, no need to transform
                data = incidents
            else:
                # If incidents is a list of Moment objects
                if all(isinstance(incident, BaseModel) for incident in incidents):
                    # Convert the list of BaseModel (Moment) instances to a dictionary format
                    data = {
                        "incidents": [incident.model_dump() for incident in incidents]
                    }
                else:
                    # If it's a list of dictionaries, wrap it directly
                    data = {"incidents": incidents}

            # Validate each incident to ensure it contains the required keys
            required_keys = {"Year", "Title", "Description"}
            valid_incidents = [
                incident
                for incident in data["incidents"]
                if required_keys.issubset(incident.keys())
            ]
            data["incidents"] = valid_incidents

            # If no valid incidents, set data to {"incidents": []}
            if not data["incidents"]:
                data = {"incidents": []}

            # Save the incidents to the JSON file
            with full_file_path.open("w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            print(f"Incidents saved to {full_file_path}")
            logging.info(f"Incidents saved to {full_file_path}\n")
        except Exception as e:
            logging.error(f"Json saving error in file {full_file_path}\n")
            data = {"incidents": []}
            with full_file_path.open("w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            logging.warning(CustomException(e, sys))


#! ----------------- Usage --------------------

# llm = "llm"
# extractor = MomentExtractor(llm)


# result = {
#     "incidents": [
#         {
#             "Year": "1979",
#             "Month": "May",
#             "Day": "4",
#             "Title": "Became Prime Minister of the United Kingdom",
#             "Description": "Thatcher introduced a series of economic policies intended to reverse high inflation and Britain's struggles in the wake of the Winter of Discontent and an oncoming recession.",
#             "Era": "CE",
#         },
#         {
#             "Year": "1975",
#             "Month": "February",
#             "Day": "11",
#             "Title": "Became Leader of the Opposition",
#             "Description": "Thatcher defeated Edward Heath in the Conservative Party leadership election to become leader of the opposition, the first woman to lead a major political party in the UK.",
#             "Era": "CE",
#         },
#     ]
# }
# extractor.save_to_json(id=0, file_path="00000000000", incidents=result)
