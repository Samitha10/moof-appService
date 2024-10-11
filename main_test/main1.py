from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json
from typing import List, Dict, Optional
import os
import sys

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.queue_handler import QueueHandler

app = FastAPI()

queue_handler = QueueHandler()
process_completed_event = asyncio.Event()
updates = asyncio.Queue()


class AppState:
    def __init__(self):
        self.is_running = False

    def format_message(self, message: str) -> str:
        return json.dumps({"message": message, "is_running": self.is_running})


app_state = AppState()


async def main_app_test(
    operation_id: str,
    file_path: str,
    file_name: str,
    life_id: Optional[str] = None,
    search_state: bool = False,
    prompt: Optional[str] = None,
) -> bool:
    """Test function for processing individual items."""
    await updates.put(app_state.format_message("main_app_test got the list"))
    return True


async def main_app_runner(raw_list: List[Dict]) -> bool:
    """Main runner function to process the list of items."""
    print(raw_list)
    print(type(raw_list))
    app_state.is_running = True
    try:
        await updates.put(app_state.format_message("Processing the list"))

        wiki_list, pdf_list, failed_ids = queue_handler.process_list(raw_list)
        if not failed_ids:
            await updates.put(
                app_state.format_message("No Invalid items found in the list")
            )
        else:
            await updates.put(
                app_state.format_message(f"Invalid items found: {failed_ids}")
            )

        if wiki_list:
            for item in wiki_list:
                await main_app_test(
                    operation_id=item["operation_id"],
                    file_path=item["file_path"],
                    file_name=item["file_name"],
                    life_id=item.get("life_id"),
                    search_state=item.get("search_state", False),
                    prompt=item.get("prompt"),
                )

        if pdf_list:
            for item in pdf_list:
                await main_app_test(
                    operation_id=item["operation_id"],
                    file_path=item["file_path"],
                    file_name=item["file_name"],
                    life_id=item.get("life_id"),
                    search_state=item.get("search_state", False),
                    prompt=item.get("prompt"),
                )
        await updates.put(
            app_state.format_message(f"Processing the wiki list{wiki_list}")
        )
        await updates.put(
            app_state.format_message(f"Processing the pdf list{pdf_list}")
        )
        await updates.put(
            app_state.format_message(f"Processing the failed list{failed_ids}")
        )
        for i in range(1, 4):
            await asyncio.sleep(1)
            await updates.put(app_state.format_message(f"Processing item {i}"))
    except Exception as e:
        await updates.put(app_state.format_message(f"Error: {str(e)}"))
    finally:
        app_state.is_running = False
        await updates.put(app_state.format_message("Stream closed"))
        process_completed_event.set()
    return True


@app.get("/func")
async def start_main_app_runner(req: Request) -> HTMLResponse:
    """Endpoint to start the main app runner."""
    if not app_state.is_running:
        raw_params = req.query_params.get("params", "[]")
        try:
            params_list = json.loads(raw_params)
            if not isinstance(params_list, list):
                raise ValueError("Params should be a list of dictionaries")
        except (json.JSONDecodeError, ValueError) as e:
            return HTMLResponse(str(e), status_code=400)

        process_completed_event.clear()
        asyncio.create_task(main_app_runner(params_list))
        return HTMLResponse("func1 started.")
    else:
        return HTMLResponse("func1 is already running.", status_code=400)


@app.get("/func1/status")
async def stream_func1_status(req: Request) -> StreamingResponse:
    """Endpoint to stream status messages from func1."""

    async def event_generator():
        while True:
            try:
                message = await asyncio.wait_for(updates.get(), timeout=2)
                yield f"data: {message}\n\n"

                if not app_state.is_running and updates.empty():
                    break
            except asyncio.TimeoutError:
                yield ": Waiting for a status\n\n"
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")
