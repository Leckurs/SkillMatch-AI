from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import docx
import io
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

model = SentenceTransformer("all-MiniLM-L6-v2") # Load the AI model once when the server starts, not inside the endpoint to avoid reloading it on every request
nlp = spacy.load("en_core_web_sm")

# Common tech skills list to match against
SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php",
    "swift", "kotlin", "go", "rust", "scala", "matlab",

    # Web Frontend
    "react", "vue", "angular", "html", "css", "tailwind", "bootstrap",
    "next.js", "gatsby", "svelte",

    # Web Backend
    "node", "fastapi", "flask", "django", "express", "spring", "laravel",

    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "sqlite", "oracle", "firebase",

    # Cloud & DevOps
    "aws", "azure", "google cloud", "docker", "kubernetes", "terraform",
    "linux", "git", "ci/cd", "jenkins", "github actions",

    # AI & Data
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "data analysis", "data science", "huggingface", "openai",

    # APIs & Tools
    "rest api", "graphql", "websockets", "microservices",
    "agile", "scrum", "jira", "figma"
]

def extract_skills(text: str) -> set:
    text_lower = text.lower()
    found = set()
    for skill in SKILLS:
        if skill in text_lower:
            found.add(skill)
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

    if len(job_skills) > 0:
        skill_score = (len(matched) / len(job_skills)) * 100
    else:
        skill_score = 0

    fit_score = round((semantic_score * 0.6) + (skill_score * 0.4), 2)

    return{
        "fit_score": fit_score,
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "summary": f"You matched {len(matched)} out of {len(job_skills)} required skills. {'Consider learning: ' + ', '.join(missing) + ' to improve your chances.' if missing else 'Great match! You have all the required skills.'}"
    }