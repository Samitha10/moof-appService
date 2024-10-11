import os
import sys

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logging
from utils.exception import CustomException
from src.fileHandler import FileHandler
from pypdf import PdfReader
import pymupdf4llm
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

file_data = {
    "life_name": "Italy",
    "file_paths": [
        # "artifacts/italy1.pdf",
        "artifacts/italy2.pdf",
        # "artifacts/italy3.txt",
    ],
}


class FileReader:
    def __init__(self, file_data):
        try:
            self.file_data = file_data
            self.life_id, self.file_paths = self.getfiles()
            logging.info("FileReader object created successfully.")
        except Exception as e:
            raise CustomException(e, sys)

    def getfiles(self):
        try:
            output_data = FileHandler(self.file_data).get_file_data()
            life_name = output_data["life_name"]
            file_list = output_data["file_list"]
            logging.info("Files are loaded successfully.")
            return life_name, file_list
        except Exception as e:
            raise CustomException(e, sys)

    def __str__(self) -> str:
        return f"Life ID: {self.life_id}, File Paths: {self.file_paths}"

    def get_life_id(self):
        return self.life_id

    def get_file_paths(self):
        return self.file_paths


file_path_list = FileReader(file_data).get_file_paths()
print(file_path_list)


class PdftoMarkdown:
    def __init__(self, filepath):
        try:
            self.fileath = filepath
            self.md_text = pymupdf4llm.to_markdown(filepath)
        except Exception as e:
            raise CustomException(e, sys)

    def get_md_text(self):
        return self.md_text

    def __str__(self) -> str:
        return self.md_text


class ExtractText:
    def __init__(self, file_path_list):
        try:
            self.file_path_list = file_path_list
        except Exception as e:
            raise CustomException(e, sys)

    def extractText(self):
        data = []
        try:
            for file_path in file_path_list:
                all_docs = PdftoMarkdown(file_path).get_md_text()

                file_data = {
                    "file_name": file_path,
                    "docs": all_docs,
                }
                data.append(file_data)
            return data
        except Exception as e:
            raise CustomException(e, sys)


class TextSplitter:
    def __init__(self, mdText):
        try:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on,
                strip_headers=False,
            )
            md_header_splits = markdown_splitter.split_text(mdText)

            chunk_size = 3000
            chunk_overlap = 100
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )

            # Split
            splits = text_splitter.split_documents(md_header_splits)
            self.splits = splits
        except Exception as e:
            raise CustomException(e, sys)

    def get_splits(self):
        return self.splits
