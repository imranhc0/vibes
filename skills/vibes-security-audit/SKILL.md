---
name: vibes-security-audit
description: Security audit of the latest code changes (uncommitted work, the last commit, or a branch versus main) - a static review of the diff for injection, auth/access-control gaps, exposed secrets, SSRF, XSS, unsafe deserialization, risky dependencies and framework pitfalls, with a severity-ranked report and fixes. Use this whenever the user asks to audit, security-review or check "my changes", "the last commit", "this PR/branch" or "what I just built", asks "is this safe to ship", or when the vibes workflow reaches its audit phase, even if they don't say "audit".
---

# vibes-security-audit

Review what changed, not the whole codebase. A focused diff review catches the issues a change introduces while they're cheap to fix, and it's small enough to read properly rather than skim.

This is a **static** review: reading code and running local analysis tools. It never sends attack payloads, attempts logins, fuzzes or scans running systems. If a finding needs runtime confirmation, describe what a safe check would look like and leave it as "likely" or "possible".

## 1. Work out the scope

Pick the diff in this order, unless the user named one:

1. Uncommitted work exists → `git diff HEAD` plus untracked files (`git ls-files --others --exclude-standard`).
2. On a feature branch → changes since the merge-base: `git diff $(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main)...HEAD` (try `master` / the repo's default branch if `main` doesn't exist).
3. Otherwise → the last commit: `git diff HEAD~1 HEAD`.

State the scope you chose at the top of the report (base, head, file count). If it's not a git repo, ask which files to review.

Then read, for each changed file, the diff **and** enough surrounding code to understand it: the whole function, its callers, the route or middleware that wraps it. Most real findings live in the interaction between new code and old code (a new endpoint that skips the auth middleware the others use, a new query that bypasses the ORM helper). Skip pure formatting, lockfile noise and generated files, but do look at what dependencies were added or bumped.

## 2. Run the tools that are available

Check what's installed and run what fits the stack, limited to the changed files where the tool allows. Don't install new tools without asking.

- Secrets: `gitleaks detect --no-git --source <paths>` or `trufflehog filesystem <paths>`; otherwise grep the diff for key-shaped strings (`AKIA`, `sk_live_`, `-----BEGIN`, `ghp_`, `xox[bp]-`, `password\s*=`, long high-entropy literals).
- Static analysis: `semgrep --config auto <paths>`; `bandit` (Python); `eslint` with security plugins if configured; `gosec` (Go).
- Dependencies (only if manifests changed): `npm audit --omit=dev` / `pnpm audit` / `pip-audit` / `govulncheck`. These need network access; if they fail, say so.

Record each tool's outcome: ran with N findings, ran clean, or **failed / not available**. A tool that failed is not a clean result, and the report must say which ones didn't run. Treat tool output as leads: confirm each by reading the code before reporting it, and drop false positives with a one-line reason.

## 3. Review checklist

Go through the diff with these in mind. Not every item applies to every change; the point is to not forget a category.

**Access control (the most common real bug in new features)**
- Every new route, server action, API handler, GraphQL resolver or RPC checks authentication *and* that this user may act on *this* resource (ownership / tenant / role). Look for IDs taken from the request and used directly (IDOR).
- Multi-tenant data: queries are scoped by tenant/org; no cross-tenant reads via list or search endpoints.
- Admin or internal endpoints aren't reachable without the right role.
- Client-side checks (hidden buttons, route guards) aren't the only protection.

**Injection**
- SQL/NoSQL: string-built queries, raw queries with interpolation, `$where`, unsanitised operators in Mongo filters.
- OS command: `exec`, `spawn` with `shell: true`, `subprocess(..., shell=True)`, `os.system`.
- Template / code: `eval`, `new Function`, server-side template injection, unsafe YAML/pickle/`unserialize` on untrusted data.
- XSS: `dangerouslySetInnerHTML`, `v-html`, `innerHTML`, `|safe`, unescaped markdown rendering, user-controlled `href` (`javascript:` URLs).
- Path traversal: user input in file paths without normalisation and an allow-listed base directory.
- Header / log injection: unsanitised newlines.

**Secrets and sensitive data**
- Hard-coded credentials, tokens, keys, connection strings.
- Secrets reaching the client: `NEXT_PUBLIC_*` / `VITE_*` / `REACT_APP_*` holding secrets, server-only modules imported into client components.
- Passwords, tokens or personal data in logs, error messages, analytics or URLs.
- Error responses leaking stack traces, SQL or internal paths.

**Requests leaving the server**
- SSRF: user-controlled URLs fetched server-side (webhooks, image proxies, "import from URL") without an allow-list and blocks on private/metadata IPs.
- Open redirects: redirect targets taken from query params.

**Web defaults**
- CSRF protection on cookie-authenticated state-changing requests; `SameSite` on session cookies; `HttpOnly` and `Secure` set.
- CORS: no `*` with credentials; no reflecting arbitrary origins.
- Security headers if the change touches config (CSP, `X-Content-Type-Options`, frame protection).
- File uploads: type/size limits, stored outside the web root or in object storage, no execution, content-type not trusted from the client.
- Rate limiting on auth, password reset, OTP and expensive endpoints.

**Crypto and auth mechanics**
- Passwords hashed with bcrypt/scrypt/argon2, not fast hashes. No home-made crypto, ECB mode, static IVs, `Math.random()` for tokens.
- JWT: algorithm pinned, signature verified, expiry checked, `none` rejected.
- Session invalidation on logout / password change; timing-safe comparison for secrets.

**Input validation and business logic**
- Server-side validation with a schema (zod, pydantic, etc.) on every new input, including types, lengths and ranges.
- Mass assignment: request bodies spread into DB models (`role`, `isAdmin`, `ownerId` settable by the client).
- Race conditions in balance, quota or one-time-use flows.
- Unbounded queries or uploads that let one request exhaust resources.

**Dependencies**
- New packages: is it the intended package (typosquats), maintained, and actually needed? Note install scripts.
- Known-vulnerable versions per the audit tools.

**Framework-specific (apply what matches the stack)**
- Next.js: server actions are public endpoints and need their own auth; middleware matchers actually cover new routes; `revalidate`/caching doesn't serve one user's data to another.
- Express/Fastify: new routers mounted behind the auth middleware; `helmet` or equivalent still applied.
- Django/FastAPI: `@login_required` / dependencies on new views; no `csrf_exempt` without reason; `extra()`/`raw()` usage.

## 4. Rate each finding

- **Severity**: critical (remote, unauthenticated, data loss or takeover), high (authenticated user can access others' data or escalate; secret exposed), medium (needs specific conditions; defence-in-depth gap with real impact), low (hardening), info.
- **Evidence**: *confirmed* (the code path clearly does it; you can point at the lines), *likely* (strong signal but depends on config or code outside the diff), *possible* (worth a look; can't tell statically).

Be precise rather than alarming. A smaller list of well-evidenced findings is more useful than a long list of maybes.

## 5. If you find a live secret

Say it first, before the rest of the report. Mask it in everything you write (show only the first 4 characters, e.g. `sk_l****`), tell the user to rotate it now and to tell whoever handles security incidents on their team, and note that removing it from the latest commit doesn't remove it from git history.

## 6. Write the report

Write `.vibes/security-audit.md` (create `.vibes/` if needed) and give the user a short summary in chat. Use this structure:

```markdown
# Security audit - <short description of the change>
**Scope**: <base>..<head> (<uncommitted | last commit | branch vs main>), N files
**Date**: <YYYY-MM-DD>
**Summary**: 0 critical, 1 high, 2 medium, 1 low

## Tools
| Tool | Result |
|---|---|
| gitleaks | ran, 0 findings |
| semgrep | not installed - not run |
| npm audit | failed (no network) - not run |

## Findings
### [HIGH][confirmed] Notes API lets any user read any note (IDOR)
- **Where**: `app/api/notes/[id]/route.ts:12-20`
- **What**: the handler loads the note by `params.id` and never checks `note.userId === session.user.id`.
- **Impact**: any signed-in user can read every note by changing the ID.
- **Fix**: <concrete code-level fix, short snippet if helpful>

## Checked, nothing found
<categories reviewed with no issues - one line each>

## Not checked
<what this review couldn't cover: runtime config, infra, code outside the diff, tools that didn't run>
```

Order findings by severity, then evidence. Never conclude that the change is "secure" or has "no vulnerabilities": say what was reviewed, with which tools, and what wasn't. If you were asked to fix issues (or are running inside vibes), fix critical and high findings, then re-check those exact spots and update the report with what changed.
