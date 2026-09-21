# RAG Model 3: PDF Documents (Product Manuals)

Retrieves over 3 generated PDF product manuals: a GPS watch, a mesh Wi-Fi
router, and a coffee machine. Text is extracted from the PDFs with PyMuPDF.

```bash
python generate_sample_pdfs.py   # (re)generates data/*.pdf
python build_and_query.py "How water resistant is the GPS watch?"
```

See the top-level [README](../README.md) for how retrieval and generation
work.
