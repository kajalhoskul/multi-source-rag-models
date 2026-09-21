"""RAG Model 2: CSV-based support FAQ dataset.

Usage:
    python build_and_query.py "question"
    python build_and_query.py            # runs a few example questions
"""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.generator import generate_answer
from common.retriever import TfidfRetriever

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "support_faq.csv")

EXAMPLE_QUESTIONS = [
    "How do I reset my password?",
    "Can I get a refund after I cancel?",
    "Does the product support single sign-on?",
]


def build_index() -> TfidfRetriever:
    chunks, sources = [], []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            chunk = f"Q: {row['question']}\nA: {row['answer']}"
            chunks.append(chunk)
            sources.append(f"faq:{row['category']}")

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
