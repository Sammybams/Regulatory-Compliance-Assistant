import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List

from src.extraction import extract_articles_and_paragraphs, extract_qa_scope
from src.language import arabic_to_english_translation, english_to_arabic_translation
from src.q_and_a import get_question_summary, get_relevant_context, query_response

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


@app.post("/extract_articles_and_paragraphs", tags=["Extraction"])
async def extract_articles_and_paragraphs_endpoint(question: str):
    try:
        result = extract_articles_and_paragraphs(question)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/extract_qa_scope", tags=["Extraction"])
async def extract_qa_scope_endpoint(question: str):
    try:
        result = extract_qa_scope(question)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/arabic_to_english_translation", tags=["Language"])
async def arabic_to_english_translation_endpoint(text: str):
    try:
        result = arabic_to_english_translation(text)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


@app.post("/english_to_arabic_translation", tags=["Language"])
async def english_to_arabic_translation_endpoint(text: str):
    try:
        result = english_to_arabic_translation(text)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/get_question_summary", tags=["Q&A"])
async def get_question_summary_endpoint(question: str, conversation_history: Optional[List[Dict[str, str]]] = None):
    try:
        if conversation_history is None:
            conversation_history = []
        result = get_question_summary(question, conversation_history)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/get_relevant_context", tags=["Q&A"])
async def get_relevant_context_endpoint(question_summary: str):
    try:
        result = get_relevant_context(question_summary)
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/query_response", tags=["Q&A"])
async def query_response_endpoint(question: str, conversation_history: List[Dict[str, str]],
                                      relevant_context: List[Dict[str, str]]):
     try:
          result = query_response(question, conversation_history, relevant_context)
          return JSONResponse(content=jsonable_encoder(result))
     except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
     
