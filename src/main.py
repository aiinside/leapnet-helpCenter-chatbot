
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

app = FastAPI()

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

API_ENDPOINT = 'https://ai-service-a711fb1e-qk2elkopoq-an.a.run.app/chat'
API_KEY = '7378f458-1142-4b'

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    data = {"query": chat_request.query}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_ENDPOINT, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting the external API: {exc}")
        except htt.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"External API returned an error: {exc.response.text}")

