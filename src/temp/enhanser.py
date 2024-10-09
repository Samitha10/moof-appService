from langchain_groq import ChatGroq
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List, Dict, Optional
import re
from langchain.output_parsers import OutputFixingParser
from langchain.schema.output_parser import StrOutputParser


class DocumentEnhancers:
    def __init__(self, llm):
        self.llm = llm

    def Title_enhancer(self, original_doc):
        class Title(BaseModel):
            """A professional title for a blog post in 10-20 words."""

            title: str = Field(
                description="A professional title for a blog post in 10-20 words."
            )

        parser = PydanticOutputParser(pydantic_object=Title)
        new_parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Generate a professional title for a blog post in 10-20 words from the following document.\nFormatting Instructions: {format_instructions}",
                ),
                ("human", "{Document}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | self.llm | new_parser

        try:
            answer = chain.invoke({"Document": original_doc})
            return answer
        except:
            text = chain.invoke({"Document": original_doc})
            answer = new_parser.parse(text)
        return answer.title.replace("\n", " ")

    def Description_enhancer(self, original_doc):
        class Description(BaseModel):
            """A professional blog post in between 150-350 words"""

            Blog: str = Field(
                description="A professional blog post in between 150-350 words."
            )

        parser = PydanticOutputParser(pydantic_object=Description)
        new_parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Generate a professional blog post in 150 - 350 words from the following document.\nFormatting Instructions: {format_instructions}",
                ),
                ("human", "{Document}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | self.llm | new_parser

        try:
            answer = chain.invoke({"Document": original_doc})
            return answer
        except:
            text = chain.invoke({"Document": original_doc})
            answer = new_parser.parse(text)
            return answer.title.replace("\n", " ")
