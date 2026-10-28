---
name: llm-output-evaluation
description: Build an evaluation harness for LLM features — test sets, deterministic checks, rubric or LLM-as-judge scoring with calibration, and release thresholds. Use when changing models, prompts or parameters, comparing providers, or proving an LLM feature meets quality targets.
license: MIT
---

# LLM Output Evaluation

## Goal
Quality decisions based on measured results on fixed cases, not on a handful of impressive examples.

## Inputs
- Feature description and success criteria, real (anonymised) inputs, known failure reports.
- Candidate configurations: model, prompt version, parameters, retrieval settings.

## Procedure
1. **Define criteria** per task: correctness, completeness, faithfulness to sources, format validity, safety and refusal behaviour, tone, latency and cost.
2. **Build the dataset:** 50–200 cases stratified by category and difficulty, including edge, adversarial and should-refuse cases. Store as JSONL with IDs, inputs, references or rubric notes. Keep a held-out subset that is not used while tuning prompts.
3. **Prefer deterministic checks** where possible: schema validation, exact or normalised match, regular expressions, numeric tolerance, citation IDs present in the provided context, banned-content lists.
4. **Rubric scoring** for open-ended outputs: 3–5 point scales with anchored descriptions per level.
5. **LLM-as-judge** only with safeguards: a different or stronger model than the candidate where possible, a rubric in the prompt, pairwise comparison with randomised order to reduce position bias, and **calibration** against at least 30 human-labelled cases (report agreement, for example Cohen's kappa).
6. **Run repeatably:** fixed model versions, seeds or temperature 0 where supported, multiple samples for stochastic settings; log cost and latency per case.
7. **Analyse:** aggregate scores with confidence intervals, per-category breakdown, regressions per case (old pass → new fail), and qualitative review of the worst cases.
8. **Gate releases** on thresholds agreed in advance (for example no category below baseline − 2 %, zero regressions on safety cases).

## Example fixture
```json
{"id":"faq-017","input":"Can I return a sale item after 40 days?","context_ids":["policy-returns-v4"],"expect":{"must_include":["30 days"],"must_not_include":["yes, any time"],"cite":"policy-returns-v4"}}
```

## Acceptance checks
- Dataset version, model versions and prompt versions are recorded with every result.
- Judge agreement with humans is reported before judge scores are used for decisions.
- Results include per-category numbers and the list of regressed cases, not only an average.
- Thresholds were set before running the candidate.

## Output
Evaluation report (configuration, dataset, metrics with intervals, regressions, cost and latency), and the harness and dataset in the repository.

## Safety
Remove personal and confidential data from evaluation sets or keep them under the same access controls as production data. Do not send confidential data to external judge models without authorization.
