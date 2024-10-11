# @app.post("/process-trigger")
# async def start_main_app_runner(params: List[Params]) -> HTMLResponse:
#     """Endpoint to start the main app runner."""
#     params_list = [param.model_dump(serialize_as_any=True) for param in params]
#     print(params_list)
#     print(type(params_list))
#     if not app_state.is_running:
#         process_completed_event.clear()
#         asyncio.create_task(main_app_runner(params_list))
#         return HTMLResponse("Function 1 started.", status_code=200)
#     else:
#         return HTMLResponse("Function is running", status_code=400)
#         # raise HTTPException(status_code=400, detail="func1 is already running.")

# @app.get("/process-trigger")
# async def start_main_app_runner(req: Request) -> HTMLResponse:
#     """Endpoint to start the main app runner."""
#     if not app_state.is_running:
#         raw_params = req.query_params.get("params", "[]")
#         try:
#             params_list = json.loads(raw_params)
#             if not isinstance(params_list, list):
#                 raise ValueError("Params should be a list of dictionaries")
#         except (json.JSONDecodeError, ValueError) as e:
#             return HTMLResponse(str(e), status_code=400)

#         process_completed_event.clear()
#         asyncio.create_task(main_app_runner(params_list))
#         return HTMLResponse("func1 started.")
#     else:
#         return HTMLResponse("func1 is already running.", status_code=400)


# @app.get("/process/status")
# async def stream_func1_status(req: Request) -> StreamingResponse:
#     """Endpoint to stream status messages from func1."""

#     async def event_generator():
#         while True:
#             try:
#                 # Decrease timeout to make it more responsive
#                 message = await asyncio.wait_for(updates.get(), timeout=0.1)
#                 yield f"data: {message}\n\n"
#                 # await asyncio.sleep(0.1)  # To avoid overwhelming the event stream
#                 if not app_state.is_running and updates.empty():
#                     break
#             except asyncio.TimeoutError:
#                 yield ": Waiting for a status\n\n"
#             except Exception as e:
#                 yield f"data: Error: {str(e)}\n\n"
#                 break

#     return StreamingResponse(event_generator(), media_type="text/event-stream")

