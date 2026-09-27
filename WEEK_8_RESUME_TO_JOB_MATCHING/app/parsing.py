"""
Week 4: Resume / Job Description parsing.
Extracts plain text from PDF, DOCX, and TXT uploads so it can be stored
in SQL and later vectorized for matching.
"""
import io
import re

import pdfplumber
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Dispatch to the right extractor based on file extension."""
    lower = filename.lower()

    if lower.endswith(".pdf"):
        raw = extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        raw = extract_text_from_docx(file_bytes)
    elif lower.endswith(".txt"):
        raw = extract_text_from_txt(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type: {filename}. Use PDF, DOCX, or TXT."
        )

    return clean_text(raw)


def clean_text(text: str) -> str:
    """Normalize whitespace for consistent downstream vectorization."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def guess_candidate_name(filename: str) -> str:
    """Fallback name guess from the filename (e.g. 'jane_doe_resume.pdf')."""
    base = re.sub(
        r"\.(pdf|docx|txt)$",
        "",
        filename,
        flags=re.IGNORECASE
    )

    base = re.sub(
        r"[_\-]+resume.*$",
        "",
        base,
        flags=re.IGNORECASE
    )

    base = re.sub(r"[_\-]+", " ", base)

    return base.strip().title() or "Unknown Candidate"