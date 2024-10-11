from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter
import pymupdf4llm
import os
import sys


# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.exception import CustomException
from utils.logger import logging


class DocumentSplitter:
    def __init__(self, chunk_size=8096, chunk_overlap=64, headers_to_split_on=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.headers_to_split_on = (
            headers_to_split_on
            if headers_to_split_on
            else [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )

    def get_main_splits(self, file_path, source_id):
        """Split the document into main sections based on the headers
        Args:
            :param file_path: Path to the PDF file

        Return:
            :List of classed based splits
        """
        try:
            logging.info(f"Started Splitting the document: {source_id}")
            # Extract the file name without extension
            # file_name = os.path.splitext(os.path.basename(file_path))[0]

            # Create the Json_Data folder if it doesn't exist
            json_data_folder = "JSON_Data"
            if not os.path.exists(json_data_folder):
                os.makedirs(json_data_folder)

            # Create the two subfolders
            json_extracted_folder = os.path.join(
                json_data_folder, f"{source_id}", "extracted"
            )
            json_enhanced_folder = os.path.join(
                json_data_folder, f"{source_id}", "enhanced"
            )
            os.makedirs(json_extracted_folder, exist_ok=True)
            os.makedirs(json_enhanced_folder, exist_ok=True)

            md_text = pymupdf4llm.to_markdown(file_path)

            markdown_splitter = MarkdownHeaderTextSplitter(
                self.headers_to_split_on, strip_headers=False
            )
            md_header_splits = markdown_splitter.split_text(md_text)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            splits = text_splitter.split_documents(md_header_splits)
            logging.info("Completed Splitting the document\n")
            return splits  # These splits are class based splits
        except Exception as e:
            raise logging.error(CustomException(e, sys))

    def get_main_splits_wiki(self, content: str, source_id):
        """Split the document into main sections based on the headers
        Args:
            :param file_path: Path to the PDF file

        Return:
            :List of classed based splits
        """
        try:
            logging.info(f"Started Splitting the document: {source_id}")
            # Extract the file name without extension
            # file_name = os.path.splitext(os.path.basename(file_path))[0]

            # Create the Json_Data folder if it doesn't exist
            json_data_folder = "JSON_Data"
            if not os.path.exists(json_data_folder):
                os.makedirs(json_data_folder)

            # Create the two subfolders
            json_extracted_folder = os.path.join(
                json_data_folder, f"{source_id}", "extracted"
            )
            json_enhanced_folder = os.path.join(
                json_data_folder, f"{source_id}", "enhanced"
            )
            os.makedirs(json_extracted_folder, exist_ok=True)
            os.makedirs(json_enhanced_folder, exist_ok=True)

            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=8096,
                chunk_overlap=64,
                length_function=len,
                is_separator_regex=False,
            )

            splits = text_splitter.create_documents([str(content)])
            return splits  # These splits are class based splits
        except Exception as e:
            raise logging.error(CustomException(e, sys, "No data"))


# from sub_splitter import SubTextSplitter
# sub_splitter = SubTextSplitter()
# splitter = DocumentSplitter()

# splits = splitter.get_main_splits("artifacts/italy1.pdf")
# for i, main_split in enumerate(splits):
#     sub_splits = sub_splitter.split_text(main_split.page_content)
#     for sub_split in sub_splits:
#         print(sub_split)
#         print("*" * 50)
#     print("-" * 50)


# # Using custom headers
# custom_headers = [
#     ("#", "Custom Header 1"),
#     ("##", "Custom Header 2"),
#     ("###", "Custom Header 3"),
# ]

# data = """
# Gitanjali (Bengali: গীতাঞ্জলি, lit. ''S
# ong offering'') is a collection of poems by the Bengali poet Rabindranath Tagore. Tagore received the Nobel Prize for Literature in 1913, for its English translation, Song Offerings, making him the first non-European  and the first Asian & the only Indian to receive this honour.
# It is part of the UNESCO Collection of
# Representative Works. Its central theme is devotion, and its motto is "I am here to sing thee songs" (No. XV).


# == History ==
# The collection by Tagore, originally written in Bengali, comprises 157 poems,
# many of which have been turned into songs or Rabindrasangeet. The original Bengali collection was published on 4 August 1910. The translated version Gitanjali: Song Offerings was published in November 1912 by the India Society of London which contained translations of 53 poems from the original Gitanjali, as well as 50 other poems extracted from Tagore’s Achalayatana, Gitimalya, Naivadya, Kheya, and more. Overall, Gitanjali:
# Song Offerings consists of 103 prose poems of Tagore’s own English translations. The poems were based on medieval Indian lyrics of devotion with a common theme of love across most poems. Some poems also narrated a conflict between the desire for materialistic possessions and spiritual longing.


# == Reworking in other languages ==

# The English version of Gitanjali or Song Offerings/Singing Angel is a collection of 103 English prose poems, which are Tagore's own English translations of
# his Bengali poems, and was first published in November 1912 by the India Society in London. It contained translations of 53 poems from the original Bengali
# Gitanjali, as well as 50 other poems from his other works. The translations were often radical, leaving out or altering large chunks of the poem and in one
# instance fusing two separate poems (song 95, which unifies songs 89 and 90 of
# Naivedya). The English Gitanjali became popular in the West, and was widely translated.


# == References ==


# == External links ==
#  Media related to Gitanjali at Wikimedia Commons
#  Works related to Gitanjali at Wikisource
# Gitanjali at Standard Ebooks"""

# splitter = DocumentSplitter()
# splits = splitter.get_main_splits_wiki(data, "222")
# print(splits[0])
