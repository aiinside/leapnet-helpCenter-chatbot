import json
from typing import Callable, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import Response
from app.config import get_settings
from app.common import utils
from app.common.logger import create_logger

settings = get_settings()
system_logger = create_logger("app.system", settings.log.system_file)
request_logger = create_logger("app.requests", settings.log.request_file)
request_rating_logger = create_logger("app.request_ratings", settings.log.request_rating_file)

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

class ChatHistoryMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    requestId: Optional[str] = None
    history: list[ChatHistoryMessage] = Field(default_factory=list)

class ChatRatingRequest(BaseModel):
    requestId: str
    rating: int

@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    if request.url.path == "/chat":
        return await call_next(request)

    raw_body = await request.body()
    query_value = None
    request_id = None
    rating_value = None

    if raw_body:
        try:
            json_body = json.loads(raw_body)
            query_value = json_body.get("query")
            request_id = json_body.get("requestId") or json_body.get("reqeustId")
            rating_value = json_body.get("rating")
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
            "requestId": request_id,
            "rating": rating_value,
            "answer": answer_value,
            "status_code": response.status_code,
        }
    )

    if request.url.path == "/chat":
        request_logger.info(
            {
                "path": request.url.path,
                "method": request.method,
                "query": query_value,
                "requestId": request_id,
                "rating": rating_value,
                "answer": answer_value,
                "status_code": response.status_code,
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
    data = {"query": chat_request.query, "history": [h.model_dump() for h in chat_request.history]}
    requestId = chat_request.requestId
    return await utils.chat_request(api_endpoint, headers, data, path, requestId)
    

@app.post("/chat_rating")
async def chat_rating(rating_request: ChatRatingRequest):
    request_rating_logger.info(
        {
            "event": "chat_rating",
            "requestId": rating_request.requestId,
            "rating": rating_request.rating,
        }
    )
    return {"status": "ok"}


@app.post("/test/chat")
async def test_chat(chat_request: ChatRequest):
    headers = {
        "x-api-key": settings.stg_api_key,
        "Content-Type": "application/json",
    }
    api_endpoint = settings.stg_api_endpoint
    path = "/test/chat"
    data = {"query": chat_request.query, "history": [h.model_dump() for h in chat_request.history]}
    requestId = chat_request.requestId

    return await utils.chat_request(api_endpoint, headers, data, path, requestId)
    
   
