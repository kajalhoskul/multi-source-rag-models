# Multi-Source RAG Models

Three independent Retrieval-Augmented Generation (RAG) pipelines, one for
each of three different data formats. They share a common retrieval and
generation core (`common/`) and differ only in how each corpus is loaded.

| Pipeline | Data source | Location |
|---|---|---|
| 1. Text-doc RAG | Plain-text HR policy documents | `rag_text_docs/` |
| 2. CSV FAQ RAG | CSV support FAQ dataset | `rag_csv_faq/` |
| 3. PDF-doc RAG | Generated PDF product manuals | `rag_pdf_docs/` |

## How each pipeline works

1. **Load** the source data (`.txt` files, a `.csv` file, or `.pdf` files).
2. **Chunk** the text into overlapping word windows (`common/chunking.py`).
3. **Retrieve** the most relevant chunks for a question using TF-IDF +
   cosine similarity (`common/retriever.py`). TF-IDF is used instead of a
   downloaded neural embedding model so every pipeline runs offline with no
   model download.
4. **Generate** an answer from the retrieved context (`common/generator.py`):
   - If `ANTHROPIC_API_KEY` is set, Claude generates the answer.
   - Else if `OPENAI_API_KEY` is set, GPT generates the answer.
   - Else, the pipeline falls back to returning the top retrieved passages
     directly (extractive mode), so it works out of the box with no API key.

## Setup

```bash
pip install -r requirements.txt
```

## Running each model

```bash
# 1. Text-document RAG (HR policy knowledge base)
python rag_text_docs/build_and_query.py "How many PTO days do employees get?"

# 2. CSV FAQ RAG (support FAQ dataset)
python rag_csv_faq/build_and_query.py "How do I reset my password?"

# 3. PDF-document RAG (product manuals) - generate the PDFs once first
python rag_pdf_docs/generate_sample_pdfs.py
python rag_pdf_docs/build_and_query.py "How water resistant is the GPS watch?"
```

Running any script with no arguments will instead run a few built-in
example questions for that dataset.

To get LLM-generated answers instead of the extractive fallback, export an
API key before running:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
```
