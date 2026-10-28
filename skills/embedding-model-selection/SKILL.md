---
name: embedding-model-selection
description: Choose and evaluate embedding models for search, RAG and clustering — multilingual quality, dimensions and cost, context length, licence and hosting (EU or self-hosted), benchmarking on your own queries, and safe migration between models. Use when building a vector search or RAG index, when retrieval quality is poor in some languages, or when planning to switch embedding models.
license: MIT
---

# Embedding Model Selection

## Goal
Pick the embedding model that retrieves best for your data, languages and constraints — measured on your own queries, not only on public leaderboards.

## Inputs
- Corpus samples and languages (for example Slovenian, German, English), query logs or realistic questions, latency and cost limits, hosting constraints (EU, on-premise), index size.

## Procedure
1. **Shortlist** 3–5 models across hosting options: API models, open-weight multilingual models runnable on your own GPU or CPU, and a lexical baseline (BM25). Check licences for commercial use.
2. **Build an evaluation set**: 50–200 queries with labelled relevant documents, covering each language, short and long queries, identifiers and jargon.
3. **Index identically**: same chunking and preprocessing for every model; record dimensions and normalization.
4. **Measure** recall@k, MRR or nDCG per language and query type; hybrid (vector + BM25) and with a reranker if one is planned (see `rag-evaluation`).
5. **Cost and performance**: embedding throughput, cost per million tokens or GPU hours, index size (dimensions × vectors × bytes), query latency; consider dimension reduction or quantization if the model supports it.
6. **Operational fit**: context length vs chunk size, rate limits, model versioning and deprecation policy, data processing terms (where text is sent).
7. **Decide** with a table of quality, cost, latency and sovereignty; record the decision (see `architecture-decision`).
8. **Migrate safely**: embeddings from different models are not comparable — re-embed the whole corpus into a new index, run both side by side, switch reads after evaluation, keep the old index for rollback.

## Example fixture
```text
Results (recall@10): BM25 0.61 | API model A 0.78 (EN 0.84, SL 0.66) | open multilingual model B 0.81 (EN 0.82, SL 0.79) | B + BM25 hybrid 0.86.
Decision: model B self-hosted (EU), hybrid retrieval; re-embed corpus (2.1 M chunks, ~6 GPU hours).
```

## Acceptance checks
- Every candidate evaluated on the same queries and chunks, with per-language results.
- Index size and cost estimates included for the chosen model.
- Negative case: mixing vectors from two models in one index is prevented (model name and version stored with each vector and checked at query time).

## Output
Evaluation report, decision record, migration plan.

## Safety
Corpus samples sent to external embedding APIs leave your control: use synthetic or approved data, or self-hosted models, for confidential content. Large benchmark runs and full re-embedding can be costly: agree a budget first. Switching production reads to a new index is a production change that needs owner approval and a rollback plan.
