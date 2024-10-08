from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio

app = FastAPI()


""" @app.get("/streaming")
async def streaming():
    async def stream():
        for i in range(10):
            yield f"Hello World {i}\n"
            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="text/plain")
 """


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
