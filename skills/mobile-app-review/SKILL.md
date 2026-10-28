---
name: mobile-app-review
description: Review iOS and Android apps for security, privacy and release readiness — secure storage, network security, authentication flows, permissions, privacy disclosures, logging, and store requirements. Use when reviewing a mobile app before release, after adding SDKs, or when handling personal data on devices.
license: MIT
---

# Mobile App Review

## Goal
An app that keeps secrets and personal data protected on the device and in transit, requests only necessary permissions, and matches its privacy disclosures. Uses the OWASP MASVS categories as a frame.

## Inputs
- Platforms and minimum OS versions, framework (native, Flutter, React Native), backend APIs, third-party SDKs (analytics, ads, crash reporting), store listings and privacy labels.

## Review checklist
1. **Storage**: tokens and keys in the Keychain (iOS) or Keystore-backed encrypted storage (Android); no secrets in `UserDefaults`, `SharedPreferences`, plain files or logs; sensitive screens excluded from backups and screenshots where appropriate.
2. **Network**: TLS only (App Transport Security on iOS, `networkSecurityConfig` without cleartext on Android); certificate pinning only with a rotation plan; no API keys with server privileges embedded in the app — the app is public.
3. **Authentication**: OAuth with PKCE in the system browser (not embedded web views) for third-party login; refresh tokens stored securely; biometric unlock bound to Keystore/Keychain keys, not just a UI check.
4. **Platform interactions**: exported Android components, deep links and intent filters validated; universal/app links verified; WebViews with JavaScript bridges limited to trusted content.
5. **Permissions**: only what features need, requested in context; location and contacts justified; no background location without a clear user-facing reason.
6. **Privacy**: third-party SDK data collection inventoried; Apple privacy manifest and nutrition labels, Google Play data safety section match reality; consent before analytics where required (GDPR, ePrivacy).
7. **Code and build**: release builds without debug flags or verbose logging; obfuscation/minification where useful; dependency scanning; reproducible build pipeline with signing keys in a secure store.
8. **Resilience**: offline and poor-network behaviour, safe handling of server errors, forced-update path for security fixes.

## Example fixture
```kotlin
val prefs = getSharedPreferences("auth", MODE_PRIVATE)
prefs.edit().putString("refresh_token", token).apply()
Log.d("Auth", "Login ok for ${user.email}, token=$token")
```
Expected findings: refresh token in plain SharedPreferences, token and email written to logs.

## Acceptance checks
- Static analysis (for example MobSF) and a manual review of storage and network configuration completed, with results.
- Privacy disclosures compared field by field with actual SDK behaviour.
- Negative case: intercepting traffic with a proxy and a user-installed CA fails (or the finding documents why it is accepted).

## Output
MASVS-mapped findings, configuration fixes, and a privacy disclosure diff.

## Safety
Test only apps you own or are authorized to assess. Do not intercept or store real users' traffic or personal data during testing.
