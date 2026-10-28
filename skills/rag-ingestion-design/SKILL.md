---
name: rag-ingestion-design
description: Design the ingestion side of retrieval-augmented generation — source connectors, parsing, chunking, metadata, access control, embeddings, hybrid search and incremental updates. Use when building or rebuilding a knowledge index for an assistant, or when retrieval quality is poor. Pair with rag-evaluation to measure results.
license: MIT
---

# RAG Ingestion Design

## Goal
An index that returns the right, authorised passages for real questions, stays current with its sources and can be rebuilt reproducibly.

## Inputs
- Sources (wikis, repositories, tickets, PDFs, databases), their formats, sizes, update frequency and permission models.
- Expected question types and languages; latency and cost limits; available embedding models and vector stores.

## Procedure
1. **Source inventory:** owner, format, volume, change rate, permissions, retention rules and whether content is authoritative or informal.
2. **Parsing:** extract text with structure (headings, lists, tables, code blocks); keep page or section anchors for citations; handle scanned PDFs with OCR only where needed; drop boilerplate (navigation, signatures).
3. **Chunking by structure first:** split on headings or sections, then by size (for example 300–800 tokens with 10–15 % overlap); never split inside code blocks or table rows; prefix each chunk with its document title and heading path so it is self-describing.
4. **Metadata per chunk:** source URL, document ID, version or commit, timestamps, language, type, and **access control** (groups or ACL) copied from the source.
5. **Access control at query time:** filter by the caller's permissions in the retrieval query, never only after generation; test with users of different roles.
6. **Embeddings:** choose a model that supports the content languages; record model name and version in the index; re-embed everything when the model changes.
7. **Hybrid retrieval:** combine vector search with keyword search (BM25) for identifiers, error codes and names; add a reranker if evaluation shows gains.
8. **Incremental updates:** change detection (webhooks, timestamps, content hashes), deletion propagation (removed or permission-revoked documents disappear from the index), idempotent re-ingestion.
9. **Observability:** counts per source, failures, last successful sync, index size; alert on stalled syncs.
10. **Evaluate** with `rag-evaluation` before and after design changes.

## Example fixture
```json
{"chunk_id":"wiki-123#deploy-rollback","doc_id":"wiki-123","title":"Deploy guide","heading_path":["Deploy guide","Rollback"],
 "text":"Deploy guide > Rollback\nTo roll back, redeploy the previous image digest…","source_url":"https://wiki.example.com/123#rollback",
 "version":"2024-10-02T08:00:00Z","acl":["group:ops"],"embedding_model":"example-embed-v2"}
```

## Acceptance checks
- A user without access to a document never receives its chunks (negative test per permission model).
- Deleting or restricting a source document removes it from results within the agreed time.
- Each chunk carries a citation anchor and heading context.
- Index builds are reproducible from source versions and recorded settings.

## Output
Ingestion design (sources, parsing, chunking, metadata, ACL model, update strategy), configuration, and evaluation results.

## Safety
Do not index secrets or credentials (scan sources and exclude them); respect source retention and deletion rules; treat ingested content as untrusted data in prompts. When sources contain personal data, define the lawful basis and minimisation before indexing, and make erasure requests propagate to chunks, embeddings and caches (GDPR).
