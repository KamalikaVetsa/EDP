"""
Week 5: Embeddings + cosine similarity matching algorithm.

Uses TF-IDF vectorization (scikit-learn) to turn resume/JD text into
numeric vectors, then ranks candidates by cosine similarity against a
job description.
"""
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank_resumes_against_job(
    job_text: str,
    resumes: List[Tuple[int, str]]
) -> List[Tuple[int, float]]:

    if not resumes:
        return []

    corpus = [job_text] + [text for _, text in resumes]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )

    tfidf_matrix = vectorizer.fit_transform(corpus)

    job_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    scores = cosine_similarity(job_vector, resume_vectors)[0]

    resume_ids = [rid for rid, _ in resumes]

    ranked = sorted(
        zip(resume_ids, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        (rid, round(float(score), 4))
        for rid, score in ranked
    ]


def top_matching_keywords(
    job_text: str,
    resume_text: str,
    top_n: int = 8
) -> List[str]:

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=2000,
        ngram_range=(1, 2)
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(
            [job_text, resume_text]
        )
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()

    job_vec = tfidf_matrix[0].toarray()[0]
    resume_vec = tfidf_matrix[1].toarray()[0]

    overlap_scores = job_vec * resume_vec

    top_indices = overlap_scores.argsort()[::-1][:top_n]

    return [
        feature_names[i]
        for i in top_indices
        if overlap_scores[i] > 0
    ]