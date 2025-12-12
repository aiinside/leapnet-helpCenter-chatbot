import json
import httpx

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import Response
from app.config import get_settings
from app.common import utils
from app.common.logger import create_logger

settings = get_settings()
system_logger = create_logger("app.system", settings.log.system_file)
request_logger = create_logger("app.requests", settings.log.request_file)

# chat_request
async def chat_request(endpoint: str, headers: Header, data: json, path: str):

    answer_value = None
    error_detail = None
    status_code = None
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.api_endpoint, headers=headers, json=data, timeout=300.0
            )
            response.raise_for_status()
            system_logger.info(
                {
                    "event": "api_request_success",
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                }
            )
            status_code = response.status_code
            response_json = response.json()
            if isinstance(response_json, dict):
                answer_value = response_json.get("answer")

            return response_json
        except httpx.RequestError as exc:
            error_detail = str(exc)
            system_logger.exception(
                {
                    "event": "api_request_error",
                    "error": error_detail,
                    "endpoint": endpoint,
                }
            )
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while requesting the external API: {exc}",
            )
        except httpx.HTTPStatusError as exc:
            error_detail = exc.response.text
            status_code = exc.response.status_code
            system_logger.exception(
                {
                    "event": "api_response_error",
                    "status_code": exc.response.status_code,
                    "error": error_detail,
                    "endpoint": endpoint,
                }
            )
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"External API returned an error: {exc.response.text}",
            )
        finally:
           request_logger.info(
               {
                   "path": path,
                   "method": "POST",
                #   "query": data,
                   "answer": answer_value,
                   "status_code": status_code,
                   "error": error_detail,
               }
           )
