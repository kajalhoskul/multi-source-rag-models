# RAG Model 2: CSV FAQ Dataset (Product Support FAQ)

Retrieves over a CSV file of support FAQ entries (`data/support_faq.csv`),
each row an indexed `category,question,answer` triple.

```bash
python build_and_query.py "How do I reset my password?"
```

See the top-level [README](../README.md) for how retrieval and generation
work.
