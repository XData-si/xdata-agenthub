---
name: european-accessibility-act
description: Prepare digital products and services for the European Accessibility Act (Directive (EU) 2019/882) — scope (e-commerce, banking, e-books, transport, electronic communications, certain devices), accessibility requirements via EN 301 549 and WCAG, microenterprise exemptions, accessibility statements and ongoing testing. Use when an organisation offers in-scope products or services to consumers in the EU. Not legal advice.
license: MIT
---

# European Accessibility Act Readiness

## Goal
Determine whether the EAA applies, and make in-scope websites, apps and products accessible with evidence that holds up to market surveillance. Requirements apply from **28 June 2025** through national laws; transitional rules exist for some existing services and products — verify national provisions.

## Inputs
- Products and services offered to consumers in the EU, company size, websites and apps, existing accessibility audits, design system, customer support channels.

## Procedure
1. **Scope**: services such as e-commerce, consumer banking, e-books and reading software, electronic communications, passenger transport services (websites, apps, ticketing), and products such as computers, smartphones, self-service terminals and e-readers. **Microenterprises** (fewer than 10 employees and turnover or balance sheet up to EUR 2 million) providing services are exempt; check national details.
2. **Standard**: use EN 301 549 (which incorporates WCAG 2.1 Level AA for web content) as the technical benchmark; many organisations target WCAG 2.2 AA.
3. **Audit** key user journeys (find product, sign up, log in, pay, contact support) with automated tools and manual testing: keyboard only, screen readers (NVDA, VoiceOver, TalkBack), zoom and reflow, contrast, captions (see `accessibility-review`).
4. **Fix** in the design system first (components, colours, focus styles), then in pages; include accessible documents and support channels (for example accessible PDFs, alternatives to phone-only support).
5. **Information requirements**: publish accessibility information for services (how the service meets requirements), keep it current; for products, accessible instructions and labelling.
6. **Disproportionate burden**: if claimed, document the assessment as the law requires and notify authorities where required; it is not a general opt-out.
7. **Keep it compliant**: accessibility checks in CI (for example axe), acceptance criteria in tickets, periodic manual audits, feedback channel for users.

## Example fixture
```text
Online shop (45 employees, EU customers) → in scope.
Audit: checkout button not reachable by keyboard; CAPTCHA without accessible alternative; product images without text alternatives; low contrast prices.
Plan: fix focus order and button semantics in the design system; replace CAPTCHA; alt text workflow in the CMS; publish accessibility information page.
```

## Acceptance checks
- Scope decision recorded per product or service, including microenterprise assessment.
- Key journeys tested manually with at least one screen reader and keyboard only; results mapped to EN 301 549/WCAG criteria.
- Negative case: an automated scan with zero errors is not accepted as proof of compliance without manual testing.

## Output
Scope memo, audit report, remediation backlog, accessibility information text, CI checks.

## Safety
Do not test with real customer accounts or payment data. This is not legal advice; confirm scope and deadlines with counsel and national guidance. Remediation of production sites or apps and publication of accessibility information follow the normal change and approval process; the audit and plan come first.
