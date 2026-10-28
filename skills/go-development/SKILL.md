---
name: go-development
description: Write and review idiomatic, safe Go — error handling, context propagation, goroutine and channel lifecycles, data races, table-driven tests and module hygiene. Use when writing or reviewing Go services, CLIs or libraries, or when debugging leaks, races and hangs in Go code.
license: MIT
---

# Go Development

## Goal
Go code that handles every error, never leaks goroutines, cancels work through `context`, and is verified by the race detector and table-driven tests.

## Inputs
- Go version (`go.mod`), module layout, linters in use (`go vet`, `staticcheck`, `golangci-lint`), deployment target.

## Review checklist
1. **Errors**: every returned `error` is checked; wrap with context (`fmt.Errorf("load config: %w", err)`); compare with `errors.Is`/`errors.As`, not string matching; no `panic` for expected failures in libraries.
2. **Context**: the first parameter of functions that do I/O or may block is `ctx context.Context`; it is passed down, never stored in structs; HTTP clients and database calls use it; `context.Background()` only at program roots.
3. **Goroutines**: each goroutine has an owner and an exit condition (context cancellation, closed channel, `errgroup`); the sender closes channels; no unbounded goroutine creation per request without limits (`semaphore`, worker pool).
4. **Concurrency safety**: shared state protected by `sync.Mutex` or confined to one goroutine; maps are not written concurrently; `sync.WaitGroup.Add` happens before the goroutine starts.
5. **Resources**: `defer resp.Body.Close()`, `defer rows.Close()`, and check `rows.Err()`; timeouts on `http.Client` and servers (`ReadHeaderTimeout`).
6. **APIs**: accept interfaces, return concrete types; small interfaces defined by the consumer; exported identifiers documented.
7. **Tests**: table-driven tests with `t.Run`, `t.Parallel()` where safe, `t.Cleanup`; run `go test -race ./...`; fuzz tests for parsers (`go test -fuzz`).
8. **Modules**: `go mod tidy` clean, `govulncheck ./...` for known vulnerabilities, no `replace` directives left from local development.

## Example fixture
```go
func fetchAll(urls []string) []string {
    var out []string
    for _, u := range urls {
        go func() { resp, _ := http.Get(u); out = append(out, resp.Status) }()
    }
    return out
}
```
Expected findings: ignored error and nil-pointer risk, data race on `out`, function returns before goroutines finish, no context or timeout, response body never closed.

## Acceptance checks
- `go vet`, `staticcheck` (or the project's linter) and `go test -race ./...` pass, or failures are listed.
- Every goroutine in the change has a documented exit path.
- Negative case: a test with a cancelled context shows the function returns promptly with `context.Canceled`.

## Output
Findings with file and line, corrected code or diff, and the commands run with results.

## Safety
Run tests and fuzzers locally or in CI, not against production services. Do not add `replace` directives or vendor patches to bypass vulnerability reports without review.
