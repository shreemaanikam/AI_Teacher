# Educational RAG Architecture & Vector Indexing Specification

## 1. Multi-Stage Retrieval Pipeline

```
Query (English / Hindi / Tamil / Hinglish)
   │
   ├─► Dense Semantic Vector Search (256-D Hypersphere Cosine Proximity)
   │
   ├─► BM25 / Lexical Keyword Search (Token Overlap & Match Ratio)
   │
   ▼
Reciprocal Rank Fusion (RRF) & Deduplication
   │
   ▼
Domain Anchor Gating & Relevance Scoring
   │
   ▼
Grounding Classification (SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED)
   │
   ▼
Certified EvidencePackage (Excerpts + Chapter/Page Source Citations)
```

---

## 2. Chunking Invariants
- Formulas and mathematical expressions ($I = V / R$) are never split across chunk boundaries.
- Code blocks (````python ... ````) and tables (`| ... |`) remain atomic within a single chunk.
- Every chunk preserves complete lineage: `document_id`, `chapter_id`, `section_id`, `concept_id`, `page_number`, `chunk_index`, and `language`.

---

## 3. Multilingual Embedding Projection
- `LocalDenseEmbeddingProvider` maps semantic root concepts across English, Hindi (`धारा`, `प्रतिरोध`, `विभव`), Tamil (`மின்னோட்டம்`, `மின்தடை`), and Hinglish (`dhara`, `pratirodh`) into shared subspace dimensions.
- Enables cross-language grounding: an English physics textbook chunk can be retrieved for a Hindi or Tamil pedagogical explanation.
