# Security policy

This is an alpha proof of concept. Do not treat the heuristic `audit` command as a security certification.

Please report vulnerabilities privately via [GitHub private vulnerability reporting](https://github.com/XData-si/xdata-agenthub/security/advisories/new), or contact XData via https://xdata.si for another secure channel. Do not publish exploit details before coordination.

This includes **malicious or unsafe skill content**: if a skill could lead an agent to leak data, run untrusted code or take unapproved actions, report it privately. Every skill passes the security gate, an AI security review and a maintainer review before distribution ([CONTRIBUTING.md](CONTRIBUTING.md), [docs/SEAL.md](docs/SEAL.md)); a reported problem revokes the skill's seal until it is fixed and reviewed again.

Threat model: prompt injection in Markdown, malicious install hooks, path traversal, unexpected overwrites, license confusion and compromised dependencies. Alpha intentionally performs no remote downloads or code execution.
