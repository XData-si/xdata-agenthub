---
name: react-component-review
description: Review React components and hooks for correctness, rendering performance, accessibility and XSS safety — effect dependencies, state ownership, keys, memoization, server/client boundaries and dangerouslySetInnerHTML. Use when reviewing React or Next.js UI code, or when a component re-renders too often, flickers or loses state.
license: MIT
---

# React Component Review

## Goal
Components that render predictably, keep state in the right place, stay accessible and never inject untrusted HTML.

## Inputs
- React version, framework (Next.js, Remix, Vite SPA), state management, component under review and its parents, design system.

## Review checklist
1. **State ownership**: derive values during render instead of syncing them with `useEffect`; lift state only as far as needed; avoid duplicating server data in local state (use a data-fetching library or framework loaders).
2. **Effects**: complete dependency arrays (eslint `react-hooks/exhaustive-deps`); effects clean up subscriptions, timers and requests (`AbortController`); no effect needed for event-driven logic.
3. **Lists and keys**: stable, unique keys from data IDs, never array indexes for reorderable lists.
4. **Performance**: measure with the React Profiler before memoizing; `memo`, `useMemo`, `useCallback` only where profiling shows benefit; split large contexts; virtualize long lists.
5. **Server and client boundaries** (React Server Components): no secrets or server-only modules in client components; `'use client'` as low in the tree as possible; data passed to clients is serializable and minimal.
6. **Security**: no `dangerouslySetInnerHTML` with untrusted content (sanitize with a maintained library such as DOMPurify if unavoidable); URLs from users validated before use in `href`/`src` (block `javascript:`).
7. **Accessibility**: semantic elements (`button`, `label`, headings); focus management for dialogs; ARIA only when native semantics are missing (see `accessibility-review`).
8. **Error and loading states**: error boundaries around risky subtrees; loading and empty states designed; forms show validation errors next to fields.

## Example fixture
```jsx
function Profile({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => { fetch(`/api/users/${userId}`).then(r => r.json()).then(setUser); }, []);
  return <div dangerouslySetInnerHTML={{ __html: user?.bio }} />;
}
```
Expected findings: missing `userId` dependency (stale data), no abort on unmount, no error or loading state, XSS through `bio`.

## Acceptance checks
- ESLint with React hooks rules passes; tests cover loading, error and success states.
- Negative case: a bio containing `<img src=x onerror=alert(1)>` renders as text or is sanitized (test).
- Performance claims are backed by Profiler measurements.

## Output
Findings with component and line, suggested code, tests.

## Safety
Do not paste production user data into fixtures or snapshots. Review third-party UI components before adding them; they run in users' browsers.
