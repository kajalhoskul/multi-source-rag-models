"""Pluggable answer generation for the RAG pipelines.

Picks a backend based on which API key is available in the environment, so
the same pipeline code can run:
  - with ANTHROPIC_API_KEY set  -> Claude generates the answer from context
  - with OPENAI_API_KEY set     -> GPT generates the answer from context
  - with neither set            -> extractive fallback (no LLM call), so the
                                    pipelines are runnable out of the box
"""
import os
from typing import List

from .retriever import RetrievedChunk

RAG_PROMPT = """Answer the question using ONLY the context below. \
If the context does not contain the answer, say you don't know.

Context:
{context}

Question: {question}

Answer:"""


def _format_context(chunks: List[RetrievedChunk]) -> str:
    return "\n\n".join(f"[{c.source}]\n{c.text}" for c in chunks)


def _extractive_fallback(question: str, chunks: List[RetrievedChunk]) -> str:
    if not chunks:
        return "No relevant context was found for this question."
    lines = [
        "(No ANTHROPIC_API_KEY / OPENAI_API_KEY set - returning the most "
        "relevant retrieved passages instead of an LLM-generated answer.)",
        "",
    ]
    for c in chunks:
        lines.append(f"- ({c.source}, score={c.score:.3f}) {c.text}")
    return "\n".join(lines)


def _generate_with_anthropic(question: str, chunks: List[RetrievedChunk]) -> str:
    import anthropic

    client = anthropic.Anthropic()
    prompt = RAG_PROMPT.format(context=_format_context(chunks), question=question)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _generate_with_openai(question: str, chunks: List[RetrievedChunk]) -> str:
    from openai import OpenAI

    client = OpenAI()
    prompt = RAG_PROMPT.format(context=_format_context(chunks), question=question)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_answer(question: str, chunks: List[RetrievedChunk]) -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return _generate_with_anthropic(question, chunks)
    if os.environ.get("OPENAI_API_KEY"):
        return _generate_with_openai(question, chunks)
    return _extractive_fallback(question, chunks)
