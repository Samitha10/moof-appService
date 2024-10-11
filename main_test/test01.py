from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import json

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
