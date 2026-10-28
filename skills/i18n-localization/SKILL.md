---
name: i18n-localization
description: Internationalize and localize software correctly — externalized strings, ICU message format with plurals, locale-aware dates, numbers and currencies, Unicode and text direction, translation workflow and pseudo-localization tests. Use when an application must support several languages (for example the official languages of EU markets) or when translations break layouts or grammar.
license: MIT
---

# Internationalization and Localization

## Goal
Adding a language is a translation task, not a code change: no hard-coded strings, correct plurals and formats, and layouts that survive longer text and other scripts.

## Inputs
- Target locales (for example Slovenian, German, French, Croatian), framework i18n library, current string handling, translation process and tools.

## Procedure
1. **Externalize** every user-facing string into message catalogs with stable keys; include context comments for translators.
2. **Use ICU MessageFormat** (or the framework equivalent) for variables, plurals and gender — never concatenate sentence fragments. Languages differ: Slovenian has four plural forms (one, two, few, other), English two.
3. **Locale-aware formatting** with the platform APIs (`Intl` in JavaScript, ICU, Babel in Python): dates, times and time zones, numbers (decimal comma vs point), currencies (EUR placement), sorting and collation.
4. **Unicode**: UTF-8 end to end; normalisation for comparison and search; correct case conversion for the locale; fonts covering needed characters (č, š, ž, ß, Cyrillic, Greek).
5. **Layout**: allow 30–40 % text expansion; no fixed-width buttons with text; support right-to-left if Arabic or Hebrew are planned.
6. **Locale selection**: from user preference, then `Accept-Language`, then default; never infer language from IP alone; let users switch.
7. **Pseudo-localization in CI**: generate an accented, lengthened pseudo-locale to catch hard-coded strings and truncation.
8. **Translation workflow**: source strings frozen before release, professional or reviewed translations for legal and safety texts, glossary for product terms; machine translation marked for review.

## Example fixture
```js
`You have ${n} new message` + (n > 1 ? "s" : "")
```
Expected findings: concatenated plural breaks in Slovenian (1 sporočilo, 2 sporočili, 3 sporočila, 5 sporočil); use an ICU plural message instead.

## Acceptance checks
- No hard-coded user-facing strings remain (lint rule or pseudo-locale run shows none).
- Plural tests for each target locale with counts 0, 1, 2, 3, 5 and 101.
- Negative case: switching to a long pseudo-locale produces no truncated or overlapping UI in key screens (screenshots).

## Output
Catalog structure, refactored messages, formatting utilities, CI checks and translator guide.

## Safety
Legal texts (terms, consent, safety warnings) require qualified human translation and review before publication. Do not send unpublished or confidential texts to external translation services without approval.
