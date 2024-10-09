from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json

#! ************************************ Main App imports ***************************
import os
import sys

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_splitter import DocumentSplitter
from src.sub_splitter import SubTextSplitter, QdrantSearch
from src.basic_extractor import MomentExtractor
from src.data_enhancer import DocumentEnhancers
from src.enhancer import IncidentProcessor
from src.final_processor import Final_Json_Processor
from src.moment_searcher import (
    Moment_to_MongoDBHandler,
    Moment_to_Vector_Handler,
    SimilarItemFinder,
    SimilarSearcher,
)

from src.queue_handler import QueueHandler
from src.MongoSaver import MongoDBJsonSaver
from src.wiki import WikiSearch

from langchain_groq import ChatGroq
from dotenv import load_dotenv

process_completed_event = asyncio.Event()
updates = asyncio.Queue()
is_running = False  # Flag to indicate if the process is running


#! ******************************************* Initialize the main app classes   *********************
load_dotenv()

# Initialize the MomentDatabase object
url = os.getenv("MONGO_URI")
qdrantUrl = os.getenv("QDRANT_URL")
qdrantKey = os.getenv("QDRANT_KEY")
groq = os.getenv("GROQ_KEY")

llm1 = ChatGroq(
    temperature=0,
    model="llama3-8b-8192",
    api_key=groq,
)
llm2 = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key=groq,
)

# file = "artifacts/World War.pdf"
main_splitter = DocumentSplitter()
sub_splitter = SubTextSplitter()
searcher = QdrantSearch()
extractor = MomentExtractor(llm2)
Data_Enhancer = DocumentEnhancers(llm1)
json_processor = Final_Json_Processor()
vector_handler = Moment_to_Vector_Handler(
    mongo_url=url,
    qdrant_url=qdrantUrl,
    qdrant_api_key=qdrantKey,
    db_ai="mooflife",
    ai_moments="moments",
    counts="Counts",
)

moment_handler = Moment_to_MongoDBHandler(
    uri=url,
    db_origin="moments_copy",
    db_ai="mooflife_ai",
    origin_moments="moments",
    ai_moments="moments",
    origin_lifes="lives",
)

mongo_saver = MongoDBJsonSaver(mongo_url=url, database="mooflife_ai")
queue_handler = QueueHandler()
wiki = WikiSearch()


#! ***************************** Main App *************************************************
async def testapp(
    operation_id: str,  # Unique ID for the source
    file_path: str,  # accessible Path to the PDF file
    file_name: str,  # Name of the file
    life_id: str = None,  # existing life id
    prompt: str = None,  # Additional prompt for the model
):
    # life_name = moment_handler.get_life_name_by_id(_id=life_id)
    life_name = None
    if "wikipedia.org" in file_path:
        result = wiki.getData(link=file_path, file_path=operation_id)
        content = wiki.process(result, file_path=operation_id)
        main_splits = main_splitter.get_main_splits_wiki(
            content=content, source_id=operation_id
        )

    else:
        main_splits = main_splitter.get_main_splits(
            source_id=operation_id, file_path=file_path
        )

    for i, main_split in enumerate(main_splits):
        result = extractor.moment_extractor(
            docs=main_split.page_content, life_name=life_name, additional_promt=prompt
        )
        extractor.save_to_json(id=i, file_path=operation_id, incidents=result)

    for i, main_split in enumerate(main_splits):
        sub_splits_title = sub_splitter.split_text_title(main_split.page_content)
        sub_splits_descripion = sub_splitter.split_text_description(
            main_split.page_content
        )
        searcher.add_documents_title(sub_splits_title)
        searcher.add_documents_descripion(sub_splits_descripion)
        processor = IncidentProcessor(
            id=int(i),
            file_path=operation_id,
            searcher=searcher,
            Data_Enhancer=Data_Enhancer,
        )
        processor.process()
        processor.save(file_path=operation_id)

    data1 = json_processor.load_json(file_path=operation_id)
    data2 = json_processor.process_incidents(
        data=data1, filepath=operation_id, source_name=file_name, life_id=life_id
    )
    json_processor.save_to_json(processed_data=data2, file_path=operation_id)

    # similar_searcher = SimilarSearcher(qdrantUrl, qdrantKey)
    # similar_item_finder = SimilarItemFinder(
    #     file_path=operation_id, vector_search=similar_searcher
    # )
    # result = similar_item_finder.process_json(life_id=life_id)

    mongo_saver.mongoSaver(collection_name="JSON_Data", operation_id=operation_id)
    return True


#! ********************************************* FastAPI Implementation  ****************************

app = FastAPI()

process_completed_event = asyncio.Event()
updates = asyncio.Queue()
is_running = False  # Flag to indicate if the process is running


def format_message(message, is_running):
    message = {"message": message, "is_running": is_running}
    return json.dumps(message)


async def func1(rawList: list):
    global is_running, current_message
    is_running = True
    print(rawList)
    await updates.put(format_message(f"number is {rawList}", is_running))
    for i in range(1, 11):
        current_message = f"Processing second is {i}"
        await updates.put(format_message(current_message, is_running))
        await asyncio.sleep(1)

    current_message = "Main function completed"
    await updates.put(format_message(current_message, is_running))
    await updates.put(format_message("Closing the stream : ", is_running))
    is_running = False
    await updates.put(format_message("Stream closed", is_running))
    process_completed_event.set()


@app.get("/func")
async def start_func2(req: Request) -> HTMLResponse:
    """Endpoint to start func1."""
    if not is_running:
        # Extract and parse the query parameters
        raw_params = req.query_params.get("params", "[]")
        try:
            params_list = json.loads(raw_params)
            if not isinstance(params_list, list):
                raise ValueError("Params should be a list of dictionaries")
        except json.JSONDecodeError:
            return HTMLResponse("Invalid JSON format for params", status_code=400)
        except ValueError as e:
            return HTMLResponse(str(e), status_code=400)

        process_completed_event.clear()
        asyncio.create_task(func1(params_list))
        return HTMLResponse("func1 started.")
    else:
        return HTMLResponse("func1 is already running.", status_code=400)


@app.get("/func1/status")
async def stream_func1_status(req: Request) -> StreamingResponse:
    """Endpoint to stream status messages from func1."""

    async def event_generator():
        while True:
            try:
                # Wait for a message with a timeout
                message = await asyncio.wait_for(updates.get(), timeout=2)
                yield f"data: {message}\n\n"

                # Check if the process has completed
                if not is_running and updates.empty():
                    break
            except asyncio.TimeoutError:
                # No message received, send a keep-alive
                yield ": Waiting for a status\n\n"
            except Exception as e:
                # Handle any other exceptions
                yield f"data: Error: {str(e)}\n\n"
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")


""" @app.get("/streaming")
async def streaming():
    async def stream():
        for i in range(10):
            yield f"Hello World {i}\n"
            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="text/plain")
 """


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
