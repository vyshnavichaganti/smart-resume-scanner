from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import fitz

app = FastAPI(title="Smart Resume Screening System", version="1.0")

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Skills database (expandable anytime)
SKILL_KEYWORDS = [
    "python","java","c","c++","html","css","javascript","react","node",
    "sql","mysql","mongodb","flask","fastapi","django","nlp","machine learning",
    "deep learning","aws","git","github","pandas","numpy"
]

class Result(BaseModel):
    fit_score:int
    matching_skills:List[str]
    missing_skills:List[str]
    resume_text_preview:str


def extract_text(pdf_bytes):
    text=""
    with fitz.open(stream=pdf_bytes,filetype="pdf") as doc:
        for page in doc:
            text+=page.get_text()
    return text.lower()


@app.post("/analyze",response_model=Result)
async def analyze_resume(resume:UploadFile=File(...), job_description:str=Form(...)):
    data=await resume.read()
    resume_text=extract_text(data)

    resume_skills=[s for s in SKILL_KEYWORDS if s in resume_text]
    jd_skills=[s for s in SKILL_KEYWORDS if s in job_description.lower()]

    matching=[s for s in resume_skills if s in jd_skills]
    missing=[s for s in jd_skills if s not in resume_skills]

    if jd_skills:
        score=int((len(matching)/len(jd_skills))*100)
    else:
        score=0

    return Result(
        fit_score=score,
        matching_skills=matching,
        missing_skills=missing,
        resume_text_preview=resume_text[:500]
    )


@app.get("/health")
def health():
    return {"status":"running"}
