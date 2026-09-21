"""RAG Model 3: PDF product-manual knowledge base.

Run generate_sample_pdfs.py first to create the PDFs under data/.

Usage:
    python build_and_query.py "question"
    python build_and_query.py            # runs a few example questions
"""
import glob
import os
import sys

import pymupdf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.chunking import chunk_text
from common.generator import generate_answer
from common.retriever import TfidfRetriever

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

EXAMPLE_QUESTIONS = [
    "How water resistant is the GPS watch?",
    "How often should I descale the coffee machine?",
    "How many square feet does one Aurora router cover?",
]


def extract_text(pdf_path: str) -> str:
    with pymupdf.open(pdf_path) as doc:
        return "\n".join(page.get_text() for page in doc)


def build_index() -> TfidfRetriever:
    pdf_paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.pdf")))
    if not pdf_paths:
        raise FileNotFoundError(
            f"No PDFs found in {DATA_DIR}. Run generate_sample_pdfs.py first."
        )

    chunks, sources = [], []
    for path in pdf_paths:
        text = extract_text(path)
        for chunk in chunk_text(text):
            chunks.append(chunk)
            sources.append(os.path.basename(path))

    return TfidfRetriever().fit(chunks, sources)


def answer(retriever: TfidfRetriever, question: str, top_k: int = 3) -> str:
    retrieved = retriever.query(question, top_k=top_k)
    return generate_answer(question, retrieved)


def main():
    retriever = build_index()
    questions = sys.argv[1:] or EXAMPLE_QUESTIONS

    for question in questions:
        print(f"\nQ: {question}")
        print(f"A: {answer(retriever, question)}")


if __name__ == "__main__":
    main()
