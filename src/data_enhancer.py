import json
import re

from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq

# from traceloop.sdk import Traceloop
from dotenv import load_dotenv
from typing import List

import os
import sys

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging

# Load the .env file
load_dotenv()
logging.info("logiing started")

# # TraceLoop
# Traceloop.init(disable_batch=True, api_key=os.getenv("Traceloop"))


class DocumentEnhancers:
    def __init__(self, llm):
        self.llm = llm

    def JSONMatcher(self, error):
        try:
            match = re.search(r"(\{.*\})", str(error), re.DOTALL)
            if match:
                json_str = match.group(1)
            return json_str
        except Exception as e:
            return None

    def JSONDecodeErrorFixer(self, json_string):
        try:
            # Find the index where '"Details": "' starts
            input_string = re.sub(r"\s+", " ", json_string).strip()
            start_details_index = input_string.find('"Details": "') + len(
                '"Details": "'
            )

            # Try to find the end index for different 'Tags' patterns
            end_details_index = input_string.find('","Tags": [')

            if end_details_index == -1:
                end_details_index = input_string.find('",\n\n"Tags": [')

            if end_details_index == -1:
                end_details_index = input_string.find('",\n"Tags": [')

            if end_details_index == -1:
                # New part: ',  "Tags": ['
                end_details_index = input_string.find('", "Tags": [')

            if end_details_index == -1:
                # New part: ',  "Tags": ['
                end_details_index = input_string.find('",  "Tags": [')

            # Extract the part to be modified between those indices
            details_part = input_string[start_details_index:end_details_index]

            # Replace all double quotes with single quotes in the extracted part
            modified_details_part = details_part.replace('"', '\\"')

            # Reconstruct the final string with the modified part
            final_string = (
                input_string[:start_details_index]
                + modified_details_part
                + input_string[end_details_index:]
            )

            # Step 1: Extract the JSON part using regex
            json_match = re.search(r"\{.*?\}", final_string, re.DOTALL)
            data = json.loads(json_match.group())

            # If parsing succeeds, return the cleaned JSON string
            return json.dumps(data)

        except Exception as e:
            logging.error(CustomException(e, sys))
            return None

    def Description_enhancer(self, original_doc, exist_doc):
        logging.info("Started enhancing the description")

        class Description(BaseModel):
            """A professional details post between 150-350 words."""

            Details: str = Field(
                description="A professional details post between 150-350 words."
            )
            Tags: List = Field(description="tags for Seach Engine Optimization")

        parser = JsonOutputParser(pydantic_object=Description)
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Generate a professional relevent details post about:{exist_doc} between 150 and 350 words and 5 tags for SEO, using only the relevent information from following document and your own knowlegde if you have.\nJson Output is required.\nFormatting Instructions: {format_instructions}",
                ),
                ("human", "{Document}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | self.llm | parser

        try:
            print("***************TRYING 01 *********************")
            # Step 1: Try invoking the chain
            answer = chain.invoke({"Document": original_doc, "exist_doc": exist_doc})
            logging.info(
                f"Description Enhanced Completed in first attempt : {answer}\n"
            )
            return answer  # Return the answer here if successful
        except Exception as error1:
            logging.warning(CustomException(error1, sys))
            print("***************TRYING 02 *********************")
            try:
                json_string = self.JSONMatcher(error1)
                if json_string:
                    print("***************TRYING 03 *********************")
                    fixed_json = self.JSONDecodeErrorFixer(json_string)
                    extracted_answer = json.loads(fixed_json)
                    logging.info(
                        f"Description Enhanced Completed in error matching : {extracted_answer}\n"
                    )
                    return extracted_answer  # Return the extracted answer if successful
                else:
                    print("***************TRYING 04 *********************")
                    # Step 3: If no match, pass error1 to fixing_parser
                    answer = fixing_parser.parse(error1)
                    logging.info(answer)
                    return answer  # Return the fixed answer if successful
            except Exception as error2:
                print("***************TRYING 05 *********************")
                logging.warning(CustomException(error2, sys))
                try:
                    # Step 4: If error2 occurs, try matching re function on error2
                    match = re.search(r"(\{.*\})", str(error2), re.DOTALL)
                    if match:
                        print("***************TRYING 06 *********************")
                        json_str = match.group(1)
                        extracted_answer = json.loads(json_str)
                        logging.info(extracted_answer)
                        return (
                            extracted_answer  # Return the extracted answer from error2
                        )
                    # No more else block here, so if no match, it'll go to "TRYING 08"
                except Exception as error3:
                    print("***************TRYING 08 *********************")
                    logging.warning(CustomException(error3, sys))
                    match = re.search(r"(\{.*\})", str(error3), re.DOTALL)
                    if match:
                        print("***************TRYING 09 *********************")
                        json_str = match.group(1)
                        extracted_answer = json.loads(json_str)
                        logging.info(extracted_answer)
                        return (
                            extracted_answer  # Return the extracted answer from error3
                        )
                    else:
                        print("***************TRYING 10 *********************")
                        logging.warning(
                            "Aftre 10th Tyring it is not recieved Enhanced Description\n"
                        )
                        return None  # If no match on error3, return None

    def Title_enhancer(self, original_doc):
        logging.info("Started enhancing the Title")

        class Title(BaseModel):
            """A professional blog title between 10-20 words.."""

            blog_title: str = Field(
                description="A professional blog post title between 10-20 words."
            )
            category: List = Field(description="Category of the blog title.")

        parser = JsonOutputParser(pydantic_object=Title)
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=self.llm)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are to generate a non poetic professional title between 10-20 words and the category of the blog title from the following document.Do not include year, month or date.\nJSON output is required.\nFormatting Instructions: {format_instructions}",
                ),
                ("human", "{Document}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | self.llm | parser

        try:
            print("***************TRYING 01 *********************")
            # Step 1: Try invoking the chain
            answer = chain.invoke({"Document": original_doc})
            logging.info(f"Title Enhanced Completed in first matching : {answer}\n")
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
                        f"Title Enhanced Completed in error matching : {extracted_answer}\n"
                    )
                    return extracted_answer  # Return the extracted answer if successful
                else:
                    print("***************TRYING 04 *********************")
                    # Step 3: If no match, pass error1 to fixing_parser
                    answer = fixing_parser.parse(error1)
                    logging.info(answer)
                    return answer  # Return the fixed answer if successful
            except Exception as error2:
                print("***************TRYING 05 *********************")
                logging.warning(CustomException(error2, sys))
                try:
                    # Step 4: If error2 occurs, try matching re function on error2
                    match = re.search(r"(\{.*\})", str(error2), re.DOTALL)
                    if match:
                        print("***************TRYING 06 *********************")
                        json_str = match.group(1)
                        extracted_answer = json.loads(json_str)
                        logging.info(extracted_answer)
                        return (
                            extracted_answer  # Return the extracted answer from error2
                        )
                    # No more else block here, so if no match, it'll go to "TRYING 08"
                except Exception as error3:
                    print("***************TRYING 08 *********************")
                    logging.warning(CustomException(error3, sys))
                    match = re.search(r"(\{.*\})", str(error3), re.DOTALL)
                    if match:
                        print("***************TRYING 09 *********************")
                        json_str = match.group(1)
                        extracted_answer = json.loads(json_str)
                        logging.info(extracted_answer)
                        return (
                            extracted_answer  # Return the extracted answer from error3
                        )
                    else:
                        print("***************TRYING 10 *********************")
                        logging.warning(
                            "Aftre 10th Tyring it is not recieved Enhanced Title\n"
                        )
                        return None  # If no match on error3, return None


# enhancer = DocumentEnhancers(llm)
# splitter = SubTextSplitter()

# original_doc = """World War I, known as the Great War, began on July 28, 1914, and ended on November 11, 1918. It involved the world's major powers organized into two opposing alliances: the Allies (Britain, France, and Russia) and the Central Powers. World War II began with the invasion of Poland by Germany on September 1, 1939, and ended with Germany's unconditional surrender on May 7, 1945, and Japan's surrender on August 15, 1945, following the atomic bombings of Hiroshima and Nagasaki. World War II resulted in widespread destruction and a high death toll, estimated between 70 to 85 million, making it the deadliest conflict in human history. Both World Wars had lasting impacts on the 20th century and continue to influence our world today."""
# list_docs = splitter.split_text(original_doc)
# print(len(list_docs))
# for doc in list_docs:
#     print("==============Doc is going==================")
#     print(doc)
#     title = enhancer.Title_enhancer(doc)
#     print(title)
#     print("==============Doc is ended ==================")


# docs = """World War II touched virtually every part of American life, even things so simple as the food people ate, the films they watched, and the music they listened to. The war, especially the elort of the Allies to win it, was the subject of songs, movies, comic books, novels, artwork, comedy routines—every conceivable form of entertainment and culture. Moreover, in many cases these works and their creators were actually part of the war elort. Writers, illustrators, cartoonists, filmmakers, and other artists used their skills to keep the public informed about the war and persuade people to cooperate with the government’s Home Front programs—like scrap drives and rationing. In short, World War II and the popular culture of that era are interconnected; the story of one cannot be fully told without the story of the other. The prospect of another world war began creeping into the American imagination even before the attack on Pearl Harbor. Authors John Steinbeck and Ernest Hemingway and playwright Maxwell Anderson each wrote fictional portrayals of wartorn Europe, while Hollywood turned out movies about risky trips across the submarine-infested Atlantic, daring attempts to rescue loved ones from Nazi concentration camps, and nefarious spy rings lurking right under America’s nose. These stories reflected the growing anxiety in America about the war and how it might alect their lives. In 1939, for example, Warner Brothers released the movie Confessions of a Nazi Spy based on actual FBI investigations into German espionage in the United States. Some people worried that the movie was too political and risked damaging the fragile neutrality of the United States in Europe. Others praised the movie as patriotic because it helped alert Americans to what was considered a very real danger. “I feel I am serving my country,” lead actor Edward G. Robinson told one interviewer after the film’s premiere. “The dangers of Nazism must be removed for all time.” After Pearl Harbor, war themes exploded into virtually every artistic medium and form of entertainment. Movies like Saboteur, Sahara, and Casablanca captured the wartime drama faced by servicemembers and civilians alike. Song lyrics often referred to the conflict, highlighting the ups and downs of both the battlefield and the Home Front. Some songs were upbeat, witty, and fun to dance to, like “Boogie Woogie Bugle Boy of Company B” by the Andrews Sisters. Others, like Walter Kent and Nat Burton’s “The White Clils of Dover,” were slower and more solemn, touching on both the seriousness of the war and the hope that peace would soon return. Even newspaper comic strips picked up elements of the war in their plots. Longtime favorite characters like Superman, Dick Tracy, Little Orphan Annie, and Mickey Mouse all dealt with various aspects of the war elort, from raising victory gardens to dealing with rationing to fighting the Axis powers on the front. A few comics like Bill Mauldin’s Willie and Joe were created specifically because of the war and olered readers a unique glimpse into the daily lives of American GIs. For many wartime writers, actors, and artists, these contributions weren’t enough. It was one thing to produce material about the war, but many of them also wanted to use their skills to actually help the Allies win. Soon after Pearl Harbor, several organizations sprang up voluntarily to help the entertainment industry do exactly that. Hollywood’s War Activities Committee, for example, helped smooth the way for cooperation between the federal government, major film studios, and thousands of theaters across the United States. The Hollywood Victory Committee organized appearances by stage, screen, television, and radio personalities at events promoting war bond sales, scrap collection, and military recruitment, plus shows to boost troop morale. By the end of the war, the organization had put on 7,700 events featuring 4,147 stars, 38 film shorts, and 390 broadcasts for war relief and charity. Writers and publishers got in on the action as well by forming the Council on Books in Wartime. The organization promoted books that would be useful “weapons in the war of ideas” and arranged sales of suitable books to libraries and the armed forces. In 1943, the Council launched its Armed Services Edition line of reprints of popular books and ultimately sold over 122 million copies to the military at an average cost of about six cents apiece. President Franklin Delano Roosevelt’s administration recognized the powerful influence of the entertainment industry early on and looked for ways to harness that energy to encourage public support for the war elort. The Omce of War Information (OWI) was the main arbiter of this relationship. OWI worked with film studios, screenwriters, radio stations, newspapers, cartoonists, and artists across the United States to produce films, posters, songs, and radio broadcasts urging everyday Americans to cooperate with the government’s wartime programs and restrictions. Even though much of this work was essentially propaganda, some of it became highly popular. In 1942, for example, the War Department asked the Writers’ War Board to come up with material to help recruit volunteers for the Army Air Forces beyond just pilots. The Board’s creative artists responded with 52 nonfiction articles, 12 fictional stories, a novel, and even a song called “I Wanna Marry a Bombardier.” The resulting surge of bombardier recruits was so large the War Department eventually had to ask the Writer’s War Board to suspend their campaign. By the time victory was declared in 1945 january 5, a whole new world of war-related sights and sounds had become part of America’s popular culture, some intended purely for entertainment, others as propaganda. Many of the more iconic symbols of this era—like Rosie the Riveter, for example—are still with us today. World War II continues to inspire artists, filmmakers, and writers, who have used the history and culture of the wartime era as the basis for some of the most highly-acclaimed films, books, and even video games of our time. World War II was the most destructive conflict in human history and claimed the lives of millions of people all over the world. It was a complicated war that included entire countries being occupied, shifting alliances, and the redrawing of national borders"""
# list_docs = splitter.split_text(docs)
# print(len(list_docs))
# for doc in list_docs:
#     print("==============Doc is going==================")
#     # print(doc)
#     description = enhancer.Description_enhancer(doc)
#     print(description)
#     print("==============Doc is ended ==================")
