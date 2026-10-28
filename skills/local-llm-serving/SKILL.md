---
name: local-llm-serving
description: Plan and operate self-hosted LLM inference (vLLM, llama.cpp, Ollama, TGI) — GPU memory sizing, quantization, context length, concurrency, an OpenAI-compatible API and benchmarking. Use when choosing hardware or models for on-premise or private inference, or when a local model server is slow or runs out of memory.
license: MIT
---

# Local LLM Serving

## Goal
A private inference endpoint whose capacity, latency and quality are measured, sized for real workloads and secured like any other internal API.

## Inputs
- Candidate models with parameter counts and licences, required context length, expected concurrent users and tokens per request.
- Hardware: GPU model and VRAM, CPU RAM, disk; drivers and container runtime support (for example NVIDIA Container Toolkit).

## Sizing VRAM
1. **Weights** ≈ parameters × bytes per parameter: FP16/BF16 = 2, FP8/INT8 = 1, 4-bit (AWQ, GPTQ, Q4 GGUF) ≈ 0.5–0.6. An 8B model needs about 16 GB in FP16 and about 5–6 GB in 4-bit.
2. **KV cache per token** ≈ 2 × layers × KV heads × head dimension × bytes. Example: a model with 32 layers, 8 KV heads (grouped-query attention) and head dimension 128 in FP16 needs 2 × 32 × 8 × 128 × 2 B = 128 KiB per token, so 8 192 tokens ≈ 1 GiB per sequence.
3. **Total** ≈ weights + KV cache × concurrent sequences + runtime overhead (activations, CUDA graphs; reserve 10–20 %).
4. If it does not fit: quantize weights, use an FP8 KV cache where supported, reduce the maximum context length, lower concurrency, or use a smaller model.

## Procedure
1. **Pick the engine:** vLLM or TGI for multi-user GPU serving (continuous batching, paged attention); llama.cpp or Ollama for single-user, CPU or mixed CPU/GPU setups and GGUF models.
2. **Configure explicitly**, for example for vLLM: `--max-model-len`, `--gpu-memory-utilization`, `--max-num-seqs`, quantization and the served model name; pin the image version and model revision (commit hash).
3. **Expose an OpenAI-compatible API** behind authentication (gateway or API keys) and TLS; never expose the raw inference port to the internet.
4. **Benchmark** with realistic prompt and output lengths: time to first token, output tokens per second per user, total throughput, and p95 latency at 1, 4 and 16 concurrent users; watch GPU memory and utilisation.
5. **Evaluate quality** of quantized versus full-precision models on your own tasks (see `llm-output-evaluation`); quantization effects are task-dependent.
6. **Operate:** health checks, a restart policy, GPU metrics (DCGM or nvidia-smi exporter), request logs without prompt contents unless approved, model files on persistent storage, and a planned procedure for driver updates.

## Example fixture
```text
GPU: 16 GB. Model: 8B, FP16 weights 16 GB → does not fit with any KV cache.
Option A: AWQ 4-bit (~5.5 GB) + 8k context × 6 sequences (~6 GiB KV) + overhead → fits with margin.
Option B: FP8 weights (~8.5 GB) + 4k context × 4 sequences (~2 GiB) → fits; benchmark both and compare quality.
```

## Acceptance checks
- The sizing calculation is documented and matches the observed memory use within about 15 %.
- Benchmarks report TTFT, tokens per second and p95 latency at stated concurrency and prompt sizes.
- The endpoint requires authentication; the inference port is not publicly reachable (negative test).
- The model licence permits the intended use.

## Output
Sizing sheet, deployment configuration, benchmark and quality results, and an operations checklist.

## Safety
Check model licences and acceptable-use terms. Prompts may contain sensitive data: restrict access to logs and the GPU host as you would for production databases.
