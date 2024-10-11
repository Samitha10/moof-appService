from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import asyncio
from pydantic import BaseModel
import json
from typing import List, Optional

import uvicorn


process_completed_event = asyncio.Event()
updates = asyncio.Queue()
connected_clients = []


class AppState:
    def __init__(self):
        self.is_running = False

    def format_message(self, message: str, operation_id: str = None) -> str:
        return json.dumps(
            {
                "message": message,
                "operation_id": operation_id,
                "is_running": self.is_running,
            }
        )


class Params(BaseModel):
    operation_id: str
    file_path: str
    file_name: str
    life_id: str
    search_state: bool
    prompt: Optional[str] = None


app_state = AppState()
app = FastAPI()


@app.get("/current-status")
async def get_current_status():
    """Endpoint to check the current status of the function."""
    if app_state.is_running:
        return HTMLResponse("Function is running", status_code=200)
    else:
        return HTMLResponse("Function is not running", status_code=200)


async def main_app_test():
    for i in range(1, 11):
        await updates.put(app_state.format_message(f"Processing item {i}"))
        await asyncio.sleep(1)

    app_state.is_running = False
    await updates.put(app_state.format_message("Stream closed"))
    process_completed_event.set()


@app.post("/process-trigger-anu")
async def start_main_app_runner(params: List[Params]) -> HTMLResponse:
    """Endpoint to start the main app runner."""
    params_list = [param.model_dump(serialize_as_any=True) for param in params]
    print(params_list)
    print(type(params_list))
    try:
        if not app_state.is_running:
            # Set the running state to True before triggering the task
            app_state.is_running = True
            process_completed_event.clear()

            res = f"dataType is {type(params_list)}, Content is {params_list}"
            await updates.put(app_state.format_message(res))
            asyncio.create_task(main_app_test())
            return JSONResponse(res, status_code=200)
        else:
            return HTMLResponse("Function is running", status_code=400)
            # raise HTTPException(status_code=400, detail="func1 is already running.")
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@app.get("/process-trigger-test")
async def start_main_app_runner1() -> HTMLResponse:
    try:
        if not app_state.is_running:
            # Set the running state to True before triggering the task
            app_state.is_running = True
            process_completed_event.clear()
            await updates.put(app_state.format_message("Triggered Successfully"))
            asyncio.create_task(main_app_test())
            return HTMLResponse("Function is started", status_code=200)
        else:
            return HTMLResponse("Function is running", status_code=400)
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)


@app.get("/process/status")
async def process_status(req: Request) -> StreamingResponse:
    """Endpoint to stream status messages from func1."""

    async def event_generator():
        while app_state.is_running or not updates.empty():
            try:
                message = await updates.get()
                yield f"data: {message}\n\n"
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.websocket("/ws")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await updates.get()
            for client in connected_clients:
                await client.send_text(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except asyncio.CancelledError:
        print("WebSocket connection cancelled.")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        connected_clients.remove(websocket)
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # Replace 'main2' with the name of your main module
        host="127.0.0.1",
        port=8000,
        log_level="info",
        ws_ping_interval=20,  # Increase the WebSocket ping interval
        ws_ping_timeout=60000,  # Increase the WebSocket ping timeout
        timeout_keep_alive=30000,  # Increase the HTTP keep-alive timeout
    )
