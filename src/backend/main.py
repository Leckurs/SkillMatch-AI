from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import docx
import io

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyse")
async def analyse(resume: UploadFile = File(...), job_description: str = Form(...)):
    return{
        "fit_score": 72,
        "matched_skills": ["Python", "SQL", "REST APIS"],
        "missing_skills": ["AWS", "Docker"],
        "summary": "Placeholder - real model coming in phase 3"
    }