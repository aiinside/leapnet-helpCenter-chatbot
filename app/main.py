import json
from typing import Callable

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import Response
from app.config import get_settings
from app.common import utils
from app.common.logger import create_logger

settings = get_settings()
system_logger = create_logger("app.system", settings.log.system_file)
request_logger = create_logger("app.requests", settings.log.request_file)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    system_logger.info({"event": "startup", "message": "Leapnet-ChatBot-API-Server startup complete"})

@app.on_event("shutdown")
async def shutdown_event():
    system_logger.info({"event": "shutdown", "message": "Leapnet-ChatBot-API-Server shutdown"})

# CORS configuration
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    if request.url.path == "/chat":
        return await call_next(request)

    raw_body = await request.body()
    query_value = None
    
    if raw_body:
        try:
            json_body = json.loads(raw_body)
            query_value = json_body.get("query")
        except json.JSONDecodeError:
            query_value = None

    async def receive() -> dict:
        return {"type": "http.request", "body": raw_body, "more_body": False}

    request = Request(request.scope, receive)

    response = await call_next(request)

    body_chunks = [chunk async for chunk in response.body_iterator]
    body = b"".join(body_chunks)

    answer_value = None
    if body:
        try:
            response_json = json.loads(body)
            answer_value = response_json.get("answer")
        except json.JSONDecodeError:
            answer_value = None

    system_logger.info(
        {
            "path": request.url.path,
            "method": request.method,
            "query": query_value,
            "answer": answer_value,
        }
    )

    return Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )

@app.post("/chat")
async def chat(chat_request: ChatRequest):

    headers = {
        "x-api-key": settings.api_key,
        "Content-Type": "application/json",
    }
    api_endpoint = settings.api_endpoint
    path = "/chat"
    data = {"query": chat_request.query}
    
    return await utils.chat_request(api_endpoint, headers, data, path)
    

@app.post("/test/chat")
async def test_chat(chat_request: ChatRequest):
    headers = {
        "x-api-key": settings.stg_api_key,
        "Content-Type": "application/json",
    }
    api_endpoint = settings.stg_api_endpoint
    path = "/test/chat"
    data = {"query": chat_request.query}

    return await utils.chat_request(api_endpoint, headers, data, path)
    
   
