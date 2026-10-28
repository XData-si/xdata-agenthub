---
name: email-deliverability
description: Diagnose and configure email authentication and deliverability — SPF, DKIM, DMARC, reverse DNS, MTA-STS and bounce handling — for a domain or application sender. Use when emails land in spam, a new sending service is added, or a domain needs protection against spoofing.
license: MIT
---

# Email Deliverability and Domain Authentication

## Goal
Legitimate mail from every sending source authenticates and aligns with the visible From domain; spoofed mail is rejected; problems are visible through reports.

## Inputs
- Domain(s), all services that send as the domain (mail server, marketing platform, helpdesk, application SMTP or API), current DNS records.
- A message that landed in spam, with full headers if possible.

## Procedure
1. **Inventory senders.** Every system that sends `From: …@domain`. Unknown senders found later in DMARC reports go back to this list.
2. **SPF.** One TXT record starting `v=spf1`, including each sender, ending with `~all` or `-all`. Stay within the 10 DNS-lookup limit (flatten or use subdomains per sender if needed). SPF checks the envelope sender (Return-Path), not the visible From.
3. **DKIM.** Each sender signs with its own selector and a key of at least 2048 bits (`selector._domainkey`). Plan key rotation.
4. **DMARC.** `_dmarc.domain` TXT. Start with `p=none; rua=mailto:…` to collect reports, fix alignment (SPF or DKIM domain must match the From domain), then move to `quarantine` and `reject`. Non-sending domains get `v=spf1 -all` and `p=reject`.
5. **Infrastructure.** Sending IPs have matching forward and reverse DNS (PTR) and a HELO name that resolves; TLS is offered; the IP is not on major blocklists.
6. **Inbound hardening (optional):** MTA-STS and TLS-RPT for receiving domains; BIMI only after DMARC enforcement.
7. **Application practice.** A dedicated subdomain or provider for bulk or marketing mail, a List-Unsubscribe header (one-click for bulk senders), and bounce and complaint processing that suppresses bad addresses.
8. **Read the evidence.** In received headers check `Authentication-Results` (spf=, dkim=, dmarc=) and alignment; in DMARC aggregate reports look for failing sources.

## Example fixture
```text
example.com.         TXT "v=spf1 include:_spf.mailprovider.example ~all"
s1._domainkey        TXT "v=DKIM1; k=rsa; p=MIIBIjANBg..."
_dmarc               TXT "v=DMARC1; p=none; rua=mailto:dmarc@example.com; adkim=s; aspf=r"
Header: Authentication-Results: mx.receiver; spf=pass smtp.mailfrom=bounce.mailer.net; dkim=pass header.d=mailer.net; dmarc=fail header.from=example.com
→ Finding: both pass but neither is aligned with example.com; configure custom DKIM (d=example.com) at the provider.
```

## Acceptance checks
- Each sender shows `dmarc=pass` with aligned SPF or DKIM in a test message.
- SPF lookups ≤ 10 (checked with a validator), exactly one SPF record.
- DMARC policy progression has a plan with dates; reports are received and reviewed.
- A spoofed test message from an unauthorised source fails DMARC (negative case, sent only to your own test mailbox).

## Output
Record changes, test-message evidence, a DMARC rollout plan and a list of unknown senders.

## Safety
DNS changes affect all mail: lower TTLs before changes and keep previous values. Do not send spoofing tests to third-party mailboxes. Apply DNS and policy changes (SPF, DKIM, DMARC, MX) only with explicit approval of the domain owner. DMARC aggregate and forensic reports contain IP addresses and possibly email addresses: treat them as personal data under GDPR, limit access and retention, and prefer an EU-based report processor.
