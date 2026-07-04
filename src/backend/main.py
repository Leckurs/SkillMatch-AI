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
    "python": "https://www.youtube.com/watch?v=rfscVS0vtbw",
    "javascript": "https://www.youtube.com/watch?v=jS4aFq5-91M",
    "typescript": "https://www.youtube.com/watch?v=BwuLxPH8IDs",
    "java": "https://www.coursera.org/learn/java-programming",
    "react": "https://www.youtube.com/watch?v=bMknfKXIFA8",
    "sql": "https://www.coursera.org/learn/sql-for-data-science",
    "machine learning": "https://www.youtube.com/watch?v=bmmQA8A-yUA",
    "deep learning": "https://www.coursera.org/specializations/deep-learning",
    "docker": "https://www.youtube.com/watch?v=3c-iBn73dDE",
    "kubernetes": "https://www.youtube.com/watch?v=ZUpE1hNQ1T0",
    "aws": "https://www.youtube.com/watch?v=be8SLusiQR8",
    "git": "https://www.youtube.com/watch?v=zTjRZNkhiEU",
    "linux": "https://www.youtube.com/watch?v=sWbUDq4S6Y8",
    "tensorflow": "https://www.coursera.org/learn/introduction-tensorflow",
    "pytorch": "https://www.youtube.com/watch?v=V_xro1bcAuA",
    "fastapi": "https://www.youtube.com/watch?v=0sOvCWFmrtA",
    "mongodb": "https://www.youtube.com/watch?v=c2M-rlkkT5o",
    "postgresql": "https://www.youtube.com/watch?v=qw--VYLpxG4",
    "nlp": "https://www.coursera.org/specializations/natural-language-processing",
    "agile": "https://www.coursera.org/learn/agile-development",
    "graphql": "https://www.youtube.com/watch?v=ed8SzALpx1Q",
    "node": "https://www.youtube.com/watch?v=fBNz5xF-Kx4",
    "django": "https://www.youtube.com/watch?v=F5mRW0jo-U4",
    "flask": "https://www.youtube.com/watch?v=Z1RJmh_OqeA",
    "rest api": "https://www.youtube.com/watch?v=qbLc5a9jdXo",
    "data pipeline": "https://www.youtube.com/watch?v=PHsC_t0j1dU",
    "large model": "https://www.coursera.org/specializations/deep-learning",
}

JOB_TITLES = {
    "Machine Learning Engineer": ["python", "machine learning", "tensorflow", "pytorch", "deep learning"],
    "Data Scientist": ["python", "sql", "machine learning", "pandas", "numpy", "data analysis"],
    "Backend Developer": ["python", "sql", "rest api", "fastapi", "django", "flask", "postgresql"],
    "Frontend Developer": ["javascript", "react", "typescript", "html", "css"],
    "Full Stack Developer": ["javascript", "react", "python", "sql", "rest api", "git"],
    "DevOps Engineer": ["docker", "kubernetes", "aws", "linux", "git", "ci/cd"],
    "Cloud Engineer": ["aws", "azure", "google cloud", "docker", "kubernetes", "terraform"],
    "NLP Engineer": ["python", "nlp", "machine learning", "deep learning", "tensorflow", "pytorch"],
    "Software Engineer": ["python", "javascript", "git", "sql", "rest api"],
    "Data Engineer": ["python", "sql", "postgresql", "mongodb", "docker", "aws"],
}

JUNK_ENDINGS = ("a", "an", "the", "and", "or", "of", "in", "on", "to", "with", "for")

def is_valid_skill(skill: str) -> bool:
    # Drop tokenizer fragments like "##le environment"
    if "##" in skill:
        return False
    # Drop very short junk like "agi"
    if len(skill) < 3:
        return False
    # Drop phrases that end in a filler word (incomplete extractions)
    if skill.split()[-1] in JUNK_ENDINGS:
        return False
    return True

def extract_skills(text: str) -> set:
    # Split text into chunks of 400 words to handle long documents
    words = text.split()
    chunks = [" ".join(words[i:i+400]) for i in range(0, len(words), 400)]

    found = set()
    for chunk in chunks:
        entities = ner_pipeline(chunk)
        for entity in entities:
            if entity["score"] > 0.7:
                skill = entity["word"].lower().strip()
                if is_valid_skill(skill):
                    found.add(skill)
    return found

def extract_text(file: UploadFile) -> str:
    content = file.file.read()
    try:
        if file.filename.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif file.filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        else:
            return ""
    except Exception:
        return ""

def generate_feedback(fit_score, matched, missing, suggested_titles):
    feedback = []

    if fit_score >= 75:
        feedback.append("Strong match! Your profile aligns well with this role.")
    elif fit_score >= 50:
        feedback.append("Decent match. With a few improvements you could be a strong candidate.")
    else:
        feedback.append("This role may be a stretch. Consider building more of the required skills first.")

    if len(matched) >=5:
        feedback.append(f"Great technincal coverage - you have {len(matched)} relevant skills for this role.")
    elif len(matched) >0:
        feedback.append(f"You have {len(matched)} matching skills, but adding more would strengthen your profile.")
    
    if missing:
        top_missing = list(missing)[:3]
        feedback.append(f"Prioritise learning: {', '.join(top_missing)} - these are the most impactful gaps.")

    if suggested_titles:
        titles = ", ".join(t["title"] for t in suggested_titles[:2])
        feedback.append(f"Based on your skills, you'd also be a good fit for: {titles}.")

    feedback.append("Tip: Include quantified achievements (e.g. 'improved performance by 40%') to stand out.")

    return feedback

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyse")
@app.post("/analyse")
async def analyse(resume: UploadFile = File(...), job_description: str = Form(...)):
    if not resume.filename.endswith((".pdf", ".docx")):
        return {"error": "Unsupported file type. Please upload a PDF or DOCX file."}

    text = extract_text(resume)

    if not text.strip():
        return {"error": "Could not read any text from your file. It may be empty, corrupted, or a scanned image."}

    resume_embedding = model.encode(text)
    job_embedding = model.encode(job_description)
    score = cosine_similarity([resume_embedding], [job_embedding])[0][0]

    semantic_score = float(score) * 100

    resume_skills = extract_skills(text)
    job_skills = extract_skills(job_description)
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    learning_resources = {}
    for skill in missing:
        if skill in LEARNING_RESOURCES:
            learning_resources[skill] = LEARNING_RESOURCES[skill]
        else:
            for key in LEARNING_RESOURCES:
                if key in skill:
                    learning_resources[skill] = LEARNING_RESOURCES[key]
                    break

    suggested_titles = []
    for title, required_skills in JOB_TITLES.items():
        matched_count = sum(1 for skill in required_skills if any(skill in r for r in resume_skills))
        match_percentage = (matched_count / len(required_skills)) * 100
        if match_percentage >= 50:
            suggested_titles.append({
                "title": title,
                "match": round(match_percentage)
            })

    suggested_titles = sorted(suggested_titles, key=lambda x: x["match"], reverse=True)[:3]

    if len(job_skills) > 0:
        skill_score = (len(matched) / len(job_skills)) * 100
    else:
        skill_score = 0

    fit_score = round((semantic_score * 0.5) + (skill_score * 0.5), 2)

    feedback = generate_feedback(fit_score, matched, missing, suggested_titles)

    return{
        "fit_score": fit_score,
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "summary": f"You matched {len(matched)} out of {len(job_skills)} required skills. {'Consider learning: ' + ', '.join(missing) + ' to improve your chances.' if missing else 'Great match! You have all the required skills.'}",
        "learning_resources": learning_resources,
        "suggested_titles": suggested_titles,
        "feedback": feedback,
    }