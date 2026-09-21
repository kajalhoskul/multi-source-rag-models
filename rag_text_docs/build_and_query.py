"""RAG Model 1: plain-text HR policy knowledge base.

Usage:
    python build_and_query.py "question"
    python build_and_query.py            # runs a few example questions
"""
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.chunking import chunk_text
from common.generator import generate_answer
from common.retriever import TfidfRetriever

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

EXAMPLE_QUESTIONS = [
    "How many PTO days do employees get per year?",
    "What is the MFA requirement for new employees?",
    "How much can I be reimbursed for a client meal?",
]


def build_index() -> TfidfRetriever:
    chunks, sources = [], []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.txt"))):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
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
