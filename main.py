import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title = "AI Regulatory Compliance Assistant Backend API",
    description = "API Documentation",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Home
@app.get("/", tags=["Home"])
async def index():
    return {"Project": "AI Regulatory Compliance Assistant Backend"}
