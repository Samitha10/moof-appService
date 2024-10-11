# from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
# import asyncio
# from pydantic import BaseModel
# import uvicorn

# import json
# from typing import List, Optional, Dict

# #! ************************************ Main App imports ***************************
# import os
# import sys

# # Add the project root to the PYTHONPATH
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from src.main_splitter import DocumentSplitter
# from src.sub_splitter import SubTextSplitter, QdrantSearch
# from src.basic_extractor import MomentExtractor
# from src.data_enhancer import DocumentEnhancers
# from src.enhancer import IncidentProcessor
# from src.final_processor import Final_Json_Processor
# from src.moment_searcher import (
#     Moment_to_MongoDBHandler,
#     Moment_to_Vector_Handler,
#     SimilarItemFinder,
#     SimilarSearcher,
# )

# from src.queue_handler import QueueHandler
# from src.MongoSaver import MongoDBJsonSaver
# from src.wiki import WikiSearch

# from langchain_groq import ChatGroq
# from dotenv import load_dotenv

# process_completed_event = asyncio.Event()
# updates = asyncio.Queue()
# is_running = False  # Flag to indicate if the process is running


# #! ******************************************* Initialize the main app classes   *********************
# load_dotenv()

# # Initialize the MomentDatabase object
# url = os.getenv("MONGO_URI")
# qdrantUrl = os.getenv("QDRANT_URL")
# qdrantKey = os.getenv("QDRANT_KEY")
# groq = os.getenv("GROQ_KEY")

# llm1 = ChatGroq(
#     temperature=0,
#     model="llama3-8b-8192",
#     api_key=groq,
# )
# llm2 = ChatGroq(
#     temperature=0,
#     model="llama3-70b-8192",
#     api_key=groq,
# )

# # file = "artifacts/World War.pdf"
# main_splitter = DocumentSplitter()
# sub_splitter = SubTextSplitter()
# searcher = QdrantSearch()
# extractor = MomentExtractor(llm2)
# Data_Enhancer = DocumentEnhancers(llm1)
# json_processor = Final_Json_Processor()
# vector_handler = Moment_to_Vector_Handler(
#     mongo_url=url,
#     qdrant_url=qdrantUrl,
#     qdrant_api_key=qdrantKey,
#     db_ai="mooflife",
#     ai_moments="moments",
#     counts="Counts",
# )

# moment_handler = Moment_to_MongoDBHandler(
#     uri=url,
#     db_origin="moments_copy",
#     db_ai="mooflife_ai",
#     origin_moments="moments",
#     ai_moments="moments",
#     origin_lifes="lives",
# )

# mongo_saver = MongoDBJsonSaver(mongo_url=url, database="mooflife_ai")
# queue_handler = QueueHandler()
# wiki = WikiSearch()

# process_completed_event = asyncio.Event()
# updates = asyncio.Queue()
# connected_clients = []


# class AppState:
#     def __init__(self):
#         self.is_running = False

#     def format_message(self, message: str, operation_id: str = None) -> str:
#         return json.dumps(
#             {
#                 "message": message,
#                 "operation_id": operation_id,
#                 "is_running": self.is_running,
#             }
#         )


# app_state = AppState()


# #! ***************************** Main App *************************************************
# async def main_app(
#     operation_id: str,  # Unique ID for the source
#     file_path: str,  # accessible Path to the PDF file
#     file_name: str,  # Name of the file
#     life_id: str = None,  # existing life id
#     search_state: bool = False,
#     prompt: Optional[str] = None,  # Additional prompt for the model
# ):
#     await updates.put(
#         app_state.format_message(
#             "Main Funtional App Instance is Started Successfully", operation_id
#         )
#     )
#     await asyncio.sleep(0)
#     # life_name = moment_handler.get_life_name_by_id(_id=life_id)
#     life_name = None

#     if "wikipedia.org" in file_path:
#         try:
#             await updates.put(
#                 app_state.format_message("Wikipedia Search is Started", operation_id)
#             )
#             result = wiki.getData(link=file_path, file_path=operation_id)
#             content = wiki.process(result, file_path=operation_id)
#             await updates.put(
#                 app_state.format_message(
#                     "Wikipedia Search Data operation is completed, Starting the splitting Data",
#                     operation_id,
#                 )
#             )
#             main_splits = main_splitter.get_main_splits_wiki(
#                 content=content, source_id=operation_id
#             )
#             await updates.put(
#                 app_state.format_message("Completed Splitting Data", operation_id)
#             )
#         except Exception as e:
#             await updates.put(
#                 app_state.format_message(
#                     f"Error in Wikipedia Search : {str(e)}", operation_id
#                 )
#             )
#             return False

#     else:
#         try:
#             await updates.put(
#                 app_state.format_message("PDF Data operation is Started", operation_id)
#             )
#             main_splits = main_splitter.get_main_splits(
#                 source_id=operation_id, file_path=file_path
#             )
#             await asyncio.sleep(0)

#         except Exception as e:
#             await updates.put(
#                 app_state.format_message(
#                     f"Error in PDF Data operation : {str(e)}", operation_id
#                 )
#             )
#             await asyncio.sleep(0)
#             return False

#     split_size = len(main_splits)

#     try:
#         await updates.put(
#             app_state.format_message("Basic Moment Extraction is Started", operation_id)
#         )
#         await asyncio.sleep(0)
#         for i, main_split in enumerate(main_splits):
#             result = extractor.moment_extractor(
#                 docs=main_split.page_content,
#                 life_name=life_name,
#                 additional_promt=prompt,
#             )
#             extractor.save_to_json(id=i, file_path=operation_id, incidents=result)
#             await updates.put(
#                 app_state.format_message(
#                     f"Completed Moment Extraction of Part {i+1} from {split_size}s",
#                     operation_id,
#                 )
#             )
#             await asyncio.sleep(0)
#     except Exception as e:
#         await updates.put(
#             app_state.format_message(
#                 f"Error in Moment Extraction : {str(e)}", operation_id
#             )
#         )
#         await asyncio.sleep(0)
#         return False
#     try:
#         await updates.put(
#             app_state.format_message("Data Enhancer is Started", operation_id)
#         )
#         await asyncio.sleep(0)

#         for i, main_split in enumerate(main_splits):
#             sub_splits_title = sub_splitter.split_text_title(main_split.page_content)
#             sub_splits_descripion = sub_splitter.split_text_description(
#                 main_split.page_content
#             )
#             searcher.add_documents_title(sub_splits_title)
#             searcher.add_documents_descripion(sub_splits_descripion)
#             processor = IncidentProcessor(
#                 id=int(i),
#                 file_path=operation_id,
#                 searcher=searcher,
#                 Data_Enhancer=Data_Enhancer,
#             )
#             processor.process()
#             processor.save(file_path=operation_id)
#             await updates.put(
#                 app_state.format_message(
#                     f"Completed Data Enhancer of Part {i+1} from {split_size}s",
#                     operation_id,
#                 )
#             )
#             await asyncio.sleep(0)
#     except Exception as e:
#         await updates.put(
#             app_state.format_message(f"Error in Data Enhancer : {str(e)}", operation_id)
#         )
#         await asyncio.sleep(0)
#         return False

#     try:
#         await updates.put(
#             app_state.format_message("Started Validating JSON Files", operation_id)
#         )
#         await asyncio.sleep(0)
#         data1 = json_processor.load_json(file_path=operation_id)
#         data2 = json_processor.process_incidents(
#             data=data1, filepath=operation_id, source_name=file_name, life_id=life_id
#         )
#         json_processor.save_to_json(processed_data=data2, file_path=operation_id)
#         await updates.put(
#             app_state.format_message("Completed Validating JSON Files", operation_id)
#         )
#         await asyncio.sleep(0)
#     except Exception as e:
#         await updates.put(
#             app_state.format_message(
#                 f"Error in Validating JSON Files : {str(e)}", operation_id
#             )
#         )
#         await asyncio.sleep(0)
#         return False

#     try:
#         if search_state:
#             await updates.put(
#                 app_state.format_message(
#                     "Started Checking for Similar Items in Exsisting Moments",
#                     operation_id,
#                 )
#             )
#             similar_searcher = SimilarSearcher(qdrantUrl, qdrantKey)
#             similar_item_finder = SimilarItemFinder(
#                 file_path=operation_id, vector_search=similar_searcher
#             )
#             result = similar_item_finder.process_json(life_id=life_id)
#             await updates.put(
#                 app_state.format_message(
#                     "Completed Checking for Similar Items in Exsisting Moments",
#                     operation_id,
#                 )
#             )
#         else:
#             await updates.put(
#                 app_state.format_message(
#                     "Skipping Checking for Similar Items in Exsisting Moments",
#                     operation_id,
#                 )
#             )
#     except Exception as e:
#         await updates.put(
#             app_state.format_message(
#                 f"Error in Checking for Similar Items in Exsisting Moments : {str(e)}",
#                 operation_id,
#             )
#         )
#         return False
#     try:
#         await updates.put(
#             app_state.format_message("Started Saving to MongoDB", operation_id)
#         )
#         mongo_saver.mongoSaver(collection_name="JSON_Data", operation_id=operation_id)
#         await updates.put(
#             app_state.format_message("Completed Saving to MongoDB", operation_id)
#         )
#     except Exception as e:
#         await updates.put(
#             app_state.format_message(
#                 f"Error in Saving to MongoDB : {str(e)}", operation_id
#             )
#         )
#         return False
#     return True


# #! ********************************************* FastAPI Implementation  ****************************

# app = FastAPI()


# async def main_app_test(
#     operation_id: str,
#     file_path: str,
#     file_name: str,
#     life_id: Optional[str] = None,
#     search_state: bool = False,
#     prompt: Optional[str] = None,
# ) -> bool:
#     """Test function for processing individual items."""
#     await updates.put(app_state.format_message("main_app_test got the list"))
#     return True


# async def main_app_runner(raw_list: List[Dict]) -> bool:
#     """Main runner function to process the list of items."""
#     app_state.is_running = True
#     try:
#         await updates.put(app_state.format_message("Processing the list"))
#         wiki_list, pdf_list, failed_ids = queue_handler.process_list(raw_list)
#         await asyncio.sleep(1)

#         if not failed_ids:
#             await updates.put(
#                 app_state.format_message("No Invalid items found in the list")
#             )
#         else:
#             await updates.put(
#                 app_state.format_message(f"Invalid items found: {failed_ids}")
#             )

#         # Immediately flush after putting messages
#         await asyncio.sleep(0)

#         if wiki_list:
#             await updates.put(app_state.format_message("Wikipedia Links are found"))
#             await asyncio.sleep(0)  # Ensure immediate flush of update
#             for item in wiki_list:
#                 await main_app(
#                     operation_id=item["operation_id"],
#                     file_path=item["file_path"],
#                     file_name=item["file_name"],
#                     life_id=item.get("life_id"),
#                     search_state=item.get("search_state", False),
#                     prompt=item.get("prompt"),
#                 )
#                 await asyncio.sleep(0)  # Force event loop cycle

#         if pdf_list:
#             await updates.put(app_state.format_message("PDF Links are found"))
#             await asyncio.sleep(0)  # Ensure immediate flush
#             for item in pdf_list:
#                 await main_app(
#                     operation_id=item["operation_id"],
#                     file_path=item["file_path"],
#                     file_name=item["file_name"],
#                     life_id=item.get("life_id"),
#                     search_state=item.get("search_state", False),
#                     prompt=item.get("prompt"),
#                 )
#                 await asyncio.sleep(0)

#             # for i in range(1, 4):
#             #     await asyncio.sleep(1)
#             #     await updates.put(app_state.format_message(f"Processing item {i}"))
#             await asyncio.sleep(0)  # Ensure streaming continues immediately
#     except Exception as e:
#         await updates.put(app_state.format_message(f"Error: {str(e)}"))
#     finally:
#         app_state.is_running = False
#         await updates.put(app_state.format_message("Stream closed"))
#         process_completed_event.set()
#     return True


# class Params(BaseModel):
#     operation_id: str
#     file_path: str
#     file_name: str
#     life_id: str
#     search_state: bool
#     prompt: Optional[str] = None


# @app.post("/process-trigger")
# async def start_main_app_runner(params: List[Params]) -> HTMLResponse:
#     """Endpoint to start the main app runner."""
#     params_list = [param.model_dump(serialize_as_any=True) for param in params]
#     print(params_list)
#     print(type(params_list))
#     if not app_state.is_running:
#         # Set the running state to True before triggering the task
#         app_state.is_running = True
#         process_completed_event.clear()

#         # Trigger the async function without awaiting it
#         asyncio.create_task(main_app_runner(params_list))
#         return HTMLResponse("Function started.", status_code=200)
#     else:
#         return HTMLResponse("Function is running", status_code=400)
#         # raise HTTPException(status_code=400, detail="func1 is already running.")


# @app.websocket("/ws")
# async def websocket_status(websocket: WebSocket):
#     await websocket.accept()
#     connected_clients.append(websocket)
#     try:
#         while True:
#             data = await updates.get()
#             for client in connected_clients:
#                 await client.send_text(data)
#     except WebSocketDisconnect:
#         connected_clients.remove(websocket)
#     except Exception as e:
#         await websocket.send_text(f"Error: {str(e)}")


# @app.get("/current-status")
# async def get_current_status():
#     """Endpoint to check the current status of the function."""
#     if app_state.is_running:
#         return HTMLResponse("Function is running", status_code=200)
#     else:
#         return HTMLResponse("Function is not running", status_code=200)


# @app.get("/process/status")
# async def process_status(req: Request) -> StreamingResponse:
#     """Endpoint to stream status messages from func1."""

#     async def event_generator():
#         while True:
#             try:
#                 # Decrease timeout to make it more responsive
#                 message = await asyncio.wait_for(updates.get(), timeout=0.1)
#                 yield f"data: {message}\n\n"
#                 if not app_state.is_running and updates.empty():
#                     break
#             except asyncio.TimeoutError:
#                 # Remove the "Waiting for a status" message
#                 continue
#             except Exception as e:
#                 yield f"data: Error: {str(e)}\n\n"
#                 break

#     return StreamingResponse(event_generator(), media_type="text/event-stream")


# # if __name__ == "__main__":
# #     uvicorn.run(
# #         "main:app",  # Replace 'main2' with the name of your main module
# #         host="127.0.0.1",
# #         port=8000,
# #         log_level="info",
# #         ws_ping_interval=20,  # Increase the WebSocket ping interval
# #         ws_ping_timeout=60000,  # Increase the WebSocket ping timeout
# #         timeout_keep_alive=30000,  # Increase the HTTP keep-alive timeout
# #     )
