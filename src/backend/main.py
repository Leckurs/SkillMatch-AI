from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import docx
import io
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from transformers import pipeline, AutoTokenizer

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

model = SentenceTransformer("all-MiniLM-L6-v2") # Load the AI model once when the server starts, not inside the endpoint to avoid reloading it on every request
nlp = spacy.load("en_core_web_sm")
MODEL_ID = "apostle2t/bert-finetuned-skillspan"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, model_max_length=512)
ner_pipeline = pipeline("ner", model=MODEL_ID, tokenizer=tokenizer, aggregation_strategy="simple")

LEARNING_RESOURCES = {
    "python": "https://www.coursera.org/learn/python",
    "javascript": "https://www.youtube.com/watch?v=W6NZfCO5SIk",
    "typescript": "https://www.youtube.com/watch?v=BwuLxPH8IDs",
    "java": "https://www.coursera.org/learn/java-programming",
    "react": "https://www.youtube.com/watch?v=bMknfKXIFA8",
    "sql": "https://www.coursera.org/learn/sql-for-data-science",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "deep learning": "https://www.coursera.org/specializations/deep-learning",
    "docker": "https://www.youtube.com/watch?v=fqMOX6JJhGo",
    "kubernetes": "https://www.youtube.com/watch?v=X48VuDVv0do",
    "aws": "https://www.coursera.org/learn/aws-fundamentals",
    "git": "https://www.youtube.com/watch?v=RGOj5yH7evk",
    "linux": "https://www.youtube.com/watch?v=sWbUDq4S6Y8",
    "tensorflow": "https://www.coursera.org/learn/introduction-tensorflow",
    "pytorch": "https://www.youtube.com/watch?v=c36lUUr864M",
    "fastapi": "https://www.youtube.com/watch?v=0sOvCWFmrtA",
    "mongodb": "https://www.youtube.com/watch?v=c2M-rlkkT5o",
    "postgresql": "https://www.youtube.com/watch?v=qw--VYLpxG4",
    "nlp": "https://www.coursera.org/specializations/natural-language-processing",
    "agile": "https://www.coursera.org/learn/agile-development",
    "graphql": "https://www.youtube.com/watch?v=ed8SzALpx1Q",
    "node": "https://www.youtube.com/watch?v=fBNz5xF-Kx4",
    "django": "https://www.youtube.com/watch?v=F5mRW0jo-U4",
    "flask": "https://www.youtube.com/watch?v=Z1RJmh_OqeA",
}

def extract_skills(text: str) -> set:
    # Split text into chunks of 400 words to handle long documents
    words = text.split()
    chunks = [" ".join(words[i:i+400]) for i in range(0, len(words), 400)]

    found = set()
    for chunk in chunks:
        entities = ner_pipeline(chunk)
        for entity in entities:
            if entity["score"] > 0.7:
                found.add(entity["word"].lower().strip())
    return found

def extract_text(file: UploadFile) -> str:
    content = file.file.read()
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    elif file.filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    return content.decode("utf-8", errors= "ignore")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyse")
async def analyse(resume: UploadFile = File(...), job_description: str = Form(...)):
    text = extract_text(resume)
    resume_embedding = model.encode(text)
    job_embedding = model.encode(job_description)
    score = cosine_similarity([resume_embedding], [job_embedding])[0][0]

    semantic_score = float(score) * 100

    resume_skills = extract_skills(text)
    job_skills = extract_skills(job_description)
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    learning_resources = {skill: LEARNING_RESOURCES[skill] for skill in missing if skill in LEARNING_RESOURCES}

    if len(job_skills) > 0:
        skill_score = (len(matched) / len(job_skills)) * 100
    else:
        skill_score = 0

    fit_score = round((semantic_score * 0.6) + (skill_score * 0.4), 2)

    return{
        "fit_score": fit_score,
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "summary": f"You matched {len(matched)} out of {len(job_skills)} required skills. {'Consider learning: ' + ', '.join(missing) + ' to improve your chances.' if missing else 'Great match! You have all the required skills.'}",
        "learning_resources": learning_resources,
    }