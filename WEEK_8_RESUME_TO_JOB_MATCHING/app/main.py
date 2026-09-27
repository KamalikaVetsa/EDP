"""
Weeks 6-7: Web app with file upload.
FastAPI backend serving a simple upload UI + matching results.
"""

from typing import List

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.database import (
    init_db,
    get_db,
    Resume,
    JobDescription,
    MatchResult
)

from app.parsing import (
    extract_text,
    guess_candidate_name
)

from app.matching import (
    rank_resumes_against_job,
    top_matching_keywords
)


app = FastAPI(title="Resume-to-Job Matching Platform")

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


MAX_FILE_SIZE_MB = 5

ALLOWED_EXTENSIONS = (
    ".pdf",
    ".docx",
    ".txt"
)


@app.on_event("startup")
def on_startup():
    init_db()


def _validate_upload(
    file: UploadFile,
    contents: bytes
):

    if not file.filename.lower().endswith(
        ALLOWED_EXTENSIONS
    ):
        raise HTTPException(
            400,
            f"Unsupported file type for {file.filename}. "
            "Use PDF, DOCX, or TXT."
        )

    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            400,
            f"{file.filename} exceeds "
            f"{MAX_FILE_SIZE_MB}MB limit."
        )

    if len(contents) == 0:
        raise HTTPException(
            400,
            f"{file.filename} is empty."
        )


@app.get(
    "/",
    response_class=HTMLResponse
)
def home(
    request: Request,
    db: Session = Depends(get_db)
):

    jobs = (
        db.query(JobDescription)
        .order_by(JobDescription.id.desc())
        .all()
    )

    resumes = (
        db.query(Resume)
        .order_by(Resume.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "resumes": resumes
        }
    )


@app.post("/upload-job")
async def upload_job(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    contents = await file.read()

    _validate_upload(file, contents)

    text = extract_text(
        file.filename,
        contents
    )

    if len(text.strip()) < 20:
        raise HTTPException(
            400,
            "Could not extract meaningful text "
            "from that file."
        )

    job = JobDescription(
        title=title.strip() or file.filename,
        raw_text=text
    )

    db.add(job)
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.post("/upload-resumes")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):

    saved = 0

    for file in files:

        contents = await file.read()

        _validate_upload(
            file,
            contents
        )

        text = extract_text(
            file.filename,
            contents
        )

        if len(text.strip()) < 20:
            continue

        resume = Resume(
            filename=file.filename,
            candidate_name=guess_candidate_name(
                file.filename
            ),
            raw_text=text
        )

        db.add(resume)

        saved += 1

    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.post(
    "/match/{job_id}",
    response_class=HTMLResponse
)
def match_job(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    job = (
        db.query(JobDescription)
        .filter(JobDescription.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            404,
            "Job description not found."
        )

    resumes = db.query(Resume).all()

    resume_pairs = [
        (r.id, r.raw_text)
        for r in resumes
    ]

    ranked = rank_resumes_against_job(
        job.raw_text,
        resume_pairs
    )

    resume_lookup = {
        r.id: r
        for r in resumes
    }

    results = []

    for resume_id, score in ranked:

        resume = resume_lookup[resume_id]

        keywords = top_matching_keywords(
            job.raw_text,
            resume.raw_text
        )

        results.append(
            {
                "resume": resume,
                "score": round(
                    score * 100,
                    1
                ),
                "keywords": keywords
            }
        )

        db.add(
            MatchResult(
                resume_id=resume_id,
                job_id=job_id,
                score=score
            )
        )

    db.commit()

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "job": job,
            "results": results
        }
    )


@app.delete("/resume/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):

    db.query(Resume).filter(
        Resume.id == resume_id
    ).delete()

    db.commit()

    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}