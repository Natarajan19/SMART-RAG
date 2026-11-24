
import os
import shutil
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import ask_question, get_active_document_name, index_pdf

# Initialize FastAPI
app = FastAPI(
    title="SmartRAG API",
    description="AI Knowledge Assistant using RAG",
    version="1.0.0"
)

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionRequest(BaseModel):
    question: str

# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to SmartRAG API",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/document")
def get_document():
    return {
        "filename": get_active_document_name()
    }


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    filename = os.path.basename(file.filename or "")

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    if file.size == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty."
        )

    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 20 MB or smaller."
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        result = index_pdf(temp_path, filename)

        return {
            "filename": filename,
            "pages": result["pages"]
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# Ask question endpoint
@app.post("/ask")
def ask(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        result = ask_question(question)

        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable"
            )

        return {
            "question": question,
            "answer": result["answer"],
            "source_pages": result["source_pages"]
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )