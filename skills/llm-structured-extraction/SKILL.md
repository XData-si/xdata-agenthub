---
name: llm-structured-extraction
description: Extract structured data from documents and text with LLMs reliably — JSON schemas, constrained decoding or tool calling, field-level validation, confidence and abstention, chunking for long documents, human review queues and accuracy measurement. Use when turning invoices, contracts, emails, tickets or forms into structured records with an LLM.
license: MIT
---

# LLM Structured Extraction

## Goal
Records that conform to the schema, are correct field by field at a measured rate, and route uncertain cases to people instead of guessing.

## Inputs
- Document types and samples (anonymised), target schema, downstream systems, accuracy requirements per field, volume and latency, data sensitivity.

## Procedure
1. **Design the schema** for extraction: precise field descriptions, types and formats (ISO dates, currency codes), enums where possible, nullable fields for "not present" — never force the model to invent a value.
2. **Use structured output**: JSON schema response formats, tool or function calling, or constrained decoding; reject anything that does not validate.
3. **Validate beyond the schema**: business rules (totals equal sum of lines, VAT numbers checksum, dates plausible), cross-field consistency; failed validation triggers a retry with error feedback or human review.
4. **Ground values**: ask for the source quote or page/coordinates per critical field; verify that quoted text exists in the document.
5. **Long documents**: OCR or layout extraction first for scans; chunk by structure; merge per-chunk results with conflict rules.
6. **Confidence and abstention**: use validation results, agreement between two runs or models, and missing evidence as signals; low-confidence records go to a review queue.
7. **Measure** on a labelled set: per-field precision/recall or exact match, document-level accuracy, abstention rate; track by document type and language (see `llm-output-evaluation`).
8. **Privacy**: minimise what is sent to the model, mask unneeded personal data, prefer EU or self-hosted models for sensitive documents.

## Example fixture
```json
{"type":"object","required":["invoice_number","issue_date","currency","total","lines"],
 "properties":{"invoice_number":{"type":"string"},"issue_date":{"type":"string","format":"date"},
  "currency":{"type":"string","enum":["EUR","USD","GBP"]},"total":{"type":"number"},
  "vat_id":{"type":["string","null"]},"lines":{"type":"array","items":{"type":"object","required":["description","amount"]}}}}
```
Validation rule: `abs(total - sum(lines.amount + vat)) < 0.01`, otherwise review.

## Acceptance checks
- Field-level accuracy on a labelled test set meets the agreed targets, reported per document type.
- 100 % of stored records validate against the schema and business rules (invalid ones are in the review queue).
- Negative case: a document missing a VAT ID yields `null`, not a fabricated value.

## Output
Schema, prompts and validators, evaluation report, review-queue design.

## Safety
Documents often contain personal and financial data: control where they are sent, mask what is not needed, and keep labelled datasets under access control.
