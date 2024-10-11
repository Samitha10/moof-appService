from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from typing import List

import os
import sys

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging


class SubTextSplitter:
    def __init__(self):
        # self.text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=chunk_size,
        #     chunk_overlap=chunk_overlap,
        #     length_function=len,
        #     is_separator_regex=False,
        # )
        """Split one main split into sub splits for title and description"""
        self.text_splitter_title = RecursiveCharacterTextSplitter(
            chunk_size=128,
            chunk_overlap=8,
            length_function=len,
            is_separator_regex=False,
        )
        self.text_splitter1_description = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=32,
            length_function=len,
            is_separator_regex=False,
        )

    # def split_text(self, data: str) -> List:  # data should be a str
    #     try:
    #         logging.info("Started Sub splitting from main splits")
    #         split_docs = self.text_splitter.create_documents([data])
    #         docs_list = [doc.page_content for doc in split_docs]
    #         logging.info("Sub splits completed")
    #         return docs_list  # List of splitted documents
    #     except Exception as e:
    #         raise logging.error(CustomException(e, sys))

    def split_text_title(self, data: str) -> List:  # data should be a str
        """Split the main split into sub splits for title
        Args:
            data (str): Main split
        Returns:
            List: List of splitted documents
        """
        try:
            logging.info("Started Sub splitting from main splits for Title")
            split_docs = self.text_splitter_title.create_documents([data])
            docs_list = [doc.page_content for doc in split_docs]
            logging.info("Sub splits completed for title\n")
            return docs_list  # List of splitted documents
        except Exception as e:
            raise logging.error(CustomException(e, sys))

    def split_text_description(self, data: str) -> List:  # data should be a str
        """Split the main split into sub splits for description
        Args:
            data (str): Main split
        Returns:
            List: List of splitted documents
        """
        try:
            logging.info("Started Sub splitting from main splits for Description")
            split_docs = self.text_splitter1_description.create_documents([data])
            docs_list = [doc.page_content for doc in split_docs]
            logging.info("Sub splits completed for description\n")
            return docs_list  # List of splitted documents
        except Exception as e:
            raise logging.error(CustomException(e, sys))


class QdrantSearch:
    def __init__(self, host=":memory:"):
        self.client = QdrantClient(host)
        # self.collection_name = collection_name

    # def add_documents(self, docs):
    #     try:
    #         # Add documents to vector store to perform search
    #         self.client.add(
    #             collection_name=self.collection_name,
    #             documents=docs,  # List of documents
    #         )
    #         logging.info("Added sub splits to collection")
    #     except Exception as e:
    #         raise logging.error(CustomException(e, sys))

    def add_documents_title(self, docs):
        try:
            # Add documents to vector store to perform search
            self.client.add(
                collection_name="title",
                documents=docs,  # List of documents
            )
            logging.info("Added sub splits to collection for title.\n")
        except Exception as e:
            raise logging.error(CustomException(e, sys))

    def add_documents_descripion(self, docs):
        try:
            # Add documents to vector store to perform search
            self.client.add(
                collection_name="description",
                documents=docs,  # List of documents
            )
            logging.info("Added sub splits to collection for description.\n")
        except Exception as e:
            raise logging.error(CustomException(e, sys))

    def search_title(self, query_text, limit=1) -> str:  # Search the vector store
        try:
            logging.info("Start searching information for Title")
            search_result = self.client.query(
                collection_name="title", query_text=query_text, limit=limit
            )
            text = search_result[0].document  # search_result[0].score
            logging.info(
                f"Title search completed for : {query_text}\n Search Result : {text}\n"
            )
            return text
        except Exception as e:
            raise logging.error(CustomException(e, sys))

    def search_description(self, query_text, limit=2) -> str:  # Search the vector store
        try:
            logging.info("Start searching information for Description")
            search_result = self.client.query(
                collection_name="description", query_text=query_text, limit=limit
            )
            text = f"{search_result[0].document}"  # {search_result[1].document}"
            logging.info(
                f"Description search completed for : {query_text}\n Search Result : {text}\n"
            )
            return text
        except Exception as e:
            raise logging.error(CustomException(e, sys))


# splitter = SubTextSplitter()
# searcher = QdrantSearch()
# docs = """World War II touched virtually every part of American life, even things so simple as the food people ate, the films they watched, and the music they listened to. The war, especially the elort of the Allies to win it, was the subject of songs, movies, comic books, novels, artwork, comedy routines—every conceivable form of entertainment and culture. Moreover, in many cases these works and their creators were actually part of the war elort. Writers, illustrators, cartoonists, filmmakers, and other artists used their skills to keep the public informed about the war and persuade people to cooperate with the government’s Home Front programs—like scrap drives and rationing. In short, World War II and the popular culture of that era are interconnected; the story of one cannot be fully told without the story of the other. The prospect of another world war began creeping into the American imagination even before the attack on Pearl Harbor. Authors John Steinbeck and Ernest Hemingway and playwright Maxwell Anderson each wrote fictional portrayals of wartorn Europe, while Hollywood turned out movies about risky trips across the submarine-infested Atlantic, daring attempts to rescue loved ones from Nazi concentration camps, and nefarious spy rings lurking right under America’s nose. These stories reflected the growing anxiety in America about the war and how it might alect their lives. In 1939, for example, Warner Brothers released the movie Confessions of a Nazi Spy based on actual FBI investigations into German espionage in the United States. Some people worried that the movie was too political and risked damaging the fragile neutrality of the United States in Europe. Others praised the movie as patriotic because it helped alert Americans to what was considered a very real danger. “I feel I am serving my country,” lead actor Edward G. Robinson told one interviewer after the film’s premiere. “The dangers of Nazism must be removed for all time.” After Pearl Harbor, war themes exploded into virtually every artistic medium and form of entertainment. Movies like Saboteur, Sahara, and Casablanca captured the wartime drama faced by servicemembers and civilians alike. Song lyrics often referred to the conflict, highlighting the ups and downs of both the battlefield and the Home Front. Some songs were upbeat, witty, and fun to dance to, like “Boogie Woogie Bugle Boy of Company B” by the Andrews Sisters. Others, like Walter Kent and Nat Burton’s “The White Clils of Dover,” were slower and more solemn, touching on both the seriousness of the war and the hope that peace would soon return. Even newspaper comic strips picked up elements of the war in their plots. Longtime favorite characters like Superman, Dick Tracy, Little Orphan Annie, and Mickey Mouse all dealt with various aspects of the war elort, from raising victory gardens to dealing with rationing to fighting the Axis powers on the front. A few comics like Bill Mauldin’s Willie and Joe were created specifically because of the war and olered readers a unique glimpse into the daily lives of American GIs. For many wartime writers, actors, and artists, these contributions weren’t enough. It was one thing to produce material about the war, but many of them also wanted to use their skills to actually help the Allies win. Soon after Pearl Harbor, several organizations sprang up voluntarily to help the entertainment industry do exactly that. Hollywood’s War Activities Committee, for example, helped smooth the way for cooperation between the federal government, major film studios, and thousands of theaters across the United States. The Hollywood Victory Committee organized appearances by stage, screen, television, and radio personalities at events promoting war bond sales, scrap collection, and military recruitment, plus shows to boost troop morale. By the end of the war, the organization had put on 7,700 events featuring 4,147 stars, 38 film shorts, and 390 broadcasts for war relief and charity. Writers and publishers got in on the action as well by forming the Council on Books in Wartime. The organization promoted books that would be useful “weapons in the war of ideas” and arranged sales of suitable books to libraries and the armed forces. In 1943, the Council launched its Armed Services Edition line of reprints of popular books and ultimately sold over 122 million copies to the military at an average cost of about six cents apiece. President Franklin Delano Roosevelt’s administration recognized the powerful influence of the entertainment industry early on and looked for ways to harness that energy to encourage public support for the war elort. The Omce of War Information (OWI) was the main arbiter of this relationship. OWI worked with film studios, screenwriters, radio stations, newspapers, cartoonists, and artists across the United States to produce films, posters, songs, and radio broadcasts urging everyday Americans to cooperate with the government’s wartime programs and restrictions. Even though much of this work was essentially propaganda, some of it became highly popular. In 1942, for example, the War Department asked the Writers’ War Board to come up with material to help recruit volunteers for the Army Air Forces beyond just pilots. The Board’s creative artists responded with 52 nonfiction articles, 12 fictional stories, a novel, and even a song called “I Wanna Marry a Bombardier.” The resulting surge of bombardier recruits was so large the War Department eventually had to ask the Writer’s War Board to suspend their campaign. By the time victory was declared in 1945 january 5, a whole new world of war-related sights and sounds had become part of America’s popular culture, some intended purely for entertainment, others as propaganda. Many of the more iconic symbols of this era—like Rosie the Riveter, for example—are still with us today. World War II continues to inspire artists, filmmakers, and writers, who have used the history and culture of the wartime era as the basis for some of the most highly-acclaimed films, books, and even video games of our time. World War II was the most destructive conflict in human history and claimed the lives of millions of people all over the world. It was a complicated war that included entire countries being occupied, shifting alliances, and the redrawing of national borders"""
# docs_list = splitter.split_text(docs)

# searcher.add_documents(docs_list)
# query_text = "World War II touched virtually every part of American life"
# search_result = searcher.search_title(query_text)
# print(search_result)
