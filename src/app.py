# from main_splitter import DocumentSplitter
# from sub_splitter import SubTextSplitter, QdrantSearch
# from basic_extractor import MomentExtractor
# from data_enhancer import DocumentEnhancers
# from enhancer import IncidentProcessor
# from final_processor import Final_Json_Processor
# from moment_searcher import (
#     Moment_to_MongoDBHandler,
#     Moment_to_Vector_Handler,
#     SimilarItemFinder,
#     SimilarSearcher,
# )
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os
# import streamlit as st

# load_dotenv()

# # Initialize the MomentDatabase object
# url = os.getenv("MONGO_URI")
# qdrantUrl = os.getenv("QDRANT_URL")
# qdrantKey = os.getenv("QDRANT_KEY")

# llm1 = ChatGroq(
#     temperature=0,
#     model="llama3-8b-8192",
#     api_key=os.getenv("GROQ_KEY"),
# )
# llm2 = ChatGroq(
#     temperature=0,
#     model="llama3-70b-8192",
#     api_key=os.getenv("GROQ_KEY"),
# )

# # file = "artifacts/World War.pdf"
# main_splitter = DocumentSplitter()
# sub_splitter = SubTextSplitter()
# searcher = QdrantSearch()
# extractor = MomentExtractor(llm2)
# Data_Enhancer = DocumentEnhancers(llm1)
# json_processor = Final_Json_Processor()
# # vector_handler = Moment_to_Vector_Handler(url, qdrantUrl, qdrantKey)
# # moment_handler = Moment_to_MongoDBHandler(url, "mooflife", "moments", "moments_vector")


# # specific_indices = [4]
# # for i, main_split in enumerate(main_splits):
# # if i in specific_indices:
# # with open("output.txt", "a", encoding="utf-8") as f:
# #     f.write(main_split.page_content + "\n")
# #     f.write(f"{i}" * 50 + "\n")
# # result = extractor.moment_extractor(main_split.page_content)
# # extractor.save_to_json(id=i, file_path=file, incidents=result)

# # for i, main_split in enumerate(main_splits):
# #     sub_splits = sub_splitter.split_text(main_split.page_content)
# #     searcher.add_documents(sub_splits)

# #     processor = IncidentProcessor(int(i), file, searcher, Data_Enhancer)
# #     processor.process()
# #     processor.save()


# # data1 = json_processor.load_json(file)
# # data2 = json_processor.process_incidents(data1)
# # json_processor.save_to_json(data2, file)


# def testapp(file_path):
#     main_splits = main_splitter.get_main_splits(file_path)
#     # for i, main_split in enumerate(main_splits):
#     #     result = extractor.moment_extractor(main_split.page_content)
#     #     extractor.save_to_json(id=i, file_path=file_path, incidents=result)

#     cases = [4]
#     for i, main_split in enumerate(main_splits):
#         if i in cases:
#             sub_splits = sub_splitter.split_text(main_split.page_content)
#             searcher.add_documents(sub_splits)
#             processor = IncidentProcessor(int(i), file_path, searcher, Data_Enhancer)
#             processor.process()
#             processor.save()

#     # data1 = json_processor.load_json(file_path)
#     # data2 = json_processor.process_incidents(data1)
#     # json_processor.save_to_json(data2, file_path)

#     # similar_searcher = SimilarSearcher(qdrantUrl, qdrantKey)
#     # similar_item_finder = SimilarItemFinder(file_path, similar_searcher)
#     # return similar_item_finder.process_json()


# testapp("artifacts/Media in World War.pdf")
