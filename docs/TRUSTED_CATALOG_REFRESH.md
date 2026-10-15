# Trusted catalog refresh (XAH-209)

Catalog refresh is **explicitly opt-in** and separate from installing/updating local skills. It fetches JSON data only; it does not execute remote code, install packages or change project files.

```sh
python cli/xah.py catalog-refresh \
  --url https://raw.githubusercontent.com/OWNER/REPO/FULL_COMMIT_SHA/registry/catalog.json \
  --revision FULL_COMMIT_SHA \
  --sha256 EXPECTED_64_CHARACTER_LOWERCASE_SHA256 \
  --approve
```

Use a **full immutable commit SHA** in the URL and obtain the expected digest through an independently trusted channel. The CLI requires the supplied revision string to appear in the HTTPS URL; it cannot cryptographically establish that the URL actually represents an immutable revision. A matching checksum proves content equality to the supplied digest, not publisher identity. Redirects, non-HTTPS sources, malformed catalogs, oversized files and mismatched checksums are refused. A successful refresh atomically replaces the local registry catalog. Existing catalog bytes remain untouched on pre-commit failures.

Use `--offline` to guarantee that no network request is attempted; the operation fails safely and preserves the existing catalog. Normal `list`, `search`, `inspect`, `add` and `update` continue to work offline with the existing catalog.

Security caveats: catalog metadata is untrusted input; catalog refresh does not authenticate the publisher or validate all referenced local paths. Run `xah doctor` after refresh to validate referenced local files. Remote catalogs with entries absent from the local checkout will fail doctor; this command is not a package downloader. Concurrent catalog writers and abrupt power loss are outside the atomicity guarantee.
