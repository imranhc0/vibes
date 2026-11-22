---
name: vibes
description: Master workflow for vibe coding a feature end to end - plan, design, build, simplify, security-audit and test - by calling specialist sub-skills in order. Use this whenever the user says "vibes", "vibe code", "build this feature", "ship this", "take this from idea to tested code", or asks for a new feature, page, endpoint or app where planning, UI, code quality, security and tests all matter, even if they don't name the workflow. Also use it to run a single phase ("vibes plan", "vibes audit", "vibes test").
---

# vibes

vibes is a conductor. It doesn't do the specialist work itself; it decides which phases a request needs, calls the right sub-skill for each, carries the results forward, and loops back when an audit or test finds a problem. The goal is that "build me X" ends with code that was planned, designed, written to good standards, simplified, audited and tested, with a short report saying what was and wasn't checked.

## The phases

| # | Phase | Calls | Output |
|---|---|---|---|
| 1 | Plan | `vibes-plan` skill | `.vibes/plan.md` |
| 2 | Design (UI work only) | `vibes-design` skill | design notes in `.vibes/plan.md`, UI code |
| 3 | Build | `vibes-react` skill (React/Next.js) or stack-idiomatic rules below | code changes |
| 4 | Simplify | `vibes-simplify` skill | cleaner code, same behaviour |
| 5 | Security audit | `vibes-security-audit` skill | `.vibes/security-audit.md` |
| 6 | Test | `vibes-test` skill | test files + `.vibes/test-report.md` |
| 7 | Fix loop | back to 3-6 as needed | - |
| 8 | Release readiness | `references/sdlc-checklist.md` | `.vibes/checklist.md` |
| 9 | Report | - | summary to the user |

Simplify runs before audit and test on purpose: the audit and the tests should look at the code that will actually ship, not a draft that gets rewritten afterwards.

## Step 0: Size the request and read the project

Before calling anything, spend a minute understanding what you're working in, because every phase depends on it:

- **Stack**: look for `package.json` (and whether it has `next`, `react`, `vue`, `svelte`, `express`, `fastify`, `hono`), `pyproject.toml` / `requirements.txt` (FastAPI, Django, Flask), `go.mod`, `Cargo.toml`, etc. Note the test tooling already present (`playwright.config.*`, `vitest`, `jest`, `pytest`).
- **Git state**: `git status` and the current branch. If there are unrelated uncommitted changes, mention it; the audit and tests scope themselves by diff, so mixing unrelated work in muddies them. Suggest committing or stashing first, but don't do it without asking.
- **Branch**: if the user is on the default branch (`main`/`master`), suggest a feature branch and create it if they agree (or if they said not to wait for answers). Work in small, reviewable steps. Don't commit or push unless asked; when asked, keep each commit to one logical change so it can be reverted on its own.
- **Project rules**: read `CLAUDE.md`, `CONTRIBUTING.md` and any PR template. Their rules (review requirements, commit format, forbidden areas) override the defaults here.
- **Size**: pick a track.
  - *Full* - a new feature, page, endpoint or app: all phases.
  - *Small* - a contained change to existing code (a bug fix, a new field): skip Plan's interview (write a 5-line plan yourself), skip Design unless the UI visibly changes, keep Build → Simplify → Audit → Test.
  - *Single phase* - the user asked for one ("vibes audit", "just test it"): run only that phase and its report.

Tell the user in one or two lines which track you picked and which phases will run, so they can redirect early.

Then read `references/sdlc-checklist.md`. It lists what each stage of the lifecycle must leave behind, and which items apply to each track. Keep it in mind through every phase; you fill it in at phase 8.

Create `.vibes/` at the repo root for phase outputs. If `.gitignore` exists and doesn't cover it, ask whether they want `.vibes/` committed (useful as a record) or ignored.

## Calling sub-skills

Invoke each specialist with the Skill tool by name. Give each one the context it needs: the plan, the stack, the files changed so far. Don't paste the whole conversation; point to `.vibes/plan.md` and the diff.

Every specialist ships in this bundle. The installed name depends on how the bundle was installed: plain (`vibes-plan`) when the skills were copied into a skills folder, namespaced (`vibes:vibes-plan`) when installed as a plugin. Check the available skills list for either form. If a specialist isn't installed (for example, only `vibes` was installed), don't stall: use the fallback for that phase below, and tell the user once, at the end, which skills were missing (see "Missing skills").

### 1. Plan → `vibes-plan`

The point of planning is to surface the decisions the user hasn't made yet before code locks them in. Call `vibes-plan` with the feature request and what you learned in Step 0. Let it interview the user; this is the one phase where back-and-forth is expected.

When it finishes, write `.vibes/plan.md`:

```markdown
# <Feature name>
## Goal
## Scope (in / out)
## Decisions made (and why)
## Data / API contracts
## UI (screens, states: loading, empty, error, success)
## Acceptance criteria   <- numbered, testable; vibes-test turns these into tests
## Risks / open questions
```

Acceptance criteria matter most: they are what the Test phase checks and what your final report measures against. Make each one observable ("POST /api/notes with an empty title returns 400").

Confirm the plan with the user before building. This is the main checkpoint; after it, work through the remaining phases without stopping unless something blocks you.

*Fallback*: interview the user yourself, at most 5 sharp questions focused on scope, data, edge cases and who can access what, reading any docs in the repo (`README`, `docs/`, ADRs) first so you don't ask what's already written down. Then write the same plan file.

### 2. Design → `vibes-design`

Only when the work has a UI. Call `vibes-design` with the plan's UI section and the existing design system (look for Tailwind config, CSS variables, a component library, existing pages to match). Matching the existing product beats inventing a new look; ask for a distinctive direction only for greenfield work. Append a short "Design notes" section to the plan: layout, components, tokens, every state.

*Fallback*: match existing components and tokens; design all states (loading, empty, error, success); keep it accessible (semantic HTML, labels, focus states, contrast, keyboard paths); make it responsive.

### 3. Build → best practices

For React or Next.js, load `vibes-react` before writing code and follow it. For other stacks, follow the fallback rules. Either way:

- Build in small vertical slices and run the app or a type check as you go, rather than writing everything then debugging at the end.
- Validate input at every trust boundary (API handlers, server actions, form posts), on the server.
- Keep secrets in environment variables or a secrets manager; never in code, logs or client bundles.
- Handle errors explicitly; don't leak stack traces to clients.
- Reuse what the codebase already has before adding dependencies. If a new dependency is needed, say why.

*Fallback (any stack)*: follow the project's existing patterns and linter; strict typing where the language allows; small focused functions; no dead code; avoid N+1 queries and unbounded lists (paginate); parallelise independent async work; avoid shipping server-only code to the client.

### 4. Simplify → `vibes-simplify`

Call `vibes-simplify` on the files changed in this session. It preserves behaviour exactly, then runs the type check, linter and existing tests, and reverts any simplification that breaks them.

*Fallback*: do a pass yourself: remove duplication, unnecessary abstraction, dead code and nested conditionals; clarify names; keep behaviour identical.

### 5. Security audit → `vibes-security-audit`

Call `vibes-security-audit` on this session's changes. It writes `.vibes/security-audit.md` with findings by severity and evidence level.

### 6. Test → `vibes-test`

Call `vibes-test` with the plan's acceptance criteria. It writes Playwright UI and API tests, runs them against the local app, and writes `.vibes/test-report.md`.

### 7. Fix loop

Fix, in this order: critical/high security findings, failing tests that reveal real bugs, then medium findings. After fixes, re-run only what's affected: the audit on the new diff, the failing tests. Cap it at 3 rounds; if things still fail, stop and report clearly rather than thrashing. Never "fix" a test by weakening its assertion to match buggy behaviour, and never mark a security finding resolved without changing the code or explaining why it's a false positive.

### 8. Release readiness → SDLC checklist

Passing tests isn't the same as being ready to merge. Copy the checklist from `references/sdlc-checklist.md` to `.vibes/checklist.md` and mark every item that applies to your track as **done** (with where the evidence is), **n/a** (with a reason), **not done** (with a reason) or **needs human**. Do the cheap outstanding items now (update the README, add the new env var to `.env.example`, write the rollback note) rather than listing them as gaps.

Some changes need a person to review them before merge no matter how green everything is, because a mistake there is expensive and hard to see in tests: authentication and access control, tenant isolation, secrets handling, payments/billing/plan tiers, consent and personal data, destructive data migrations, and anything the project's own rules name. If the diff touches one of these, say so at the top of the final report and name what the reviewer should look at.

## 9. Final report

Keep it short and scannable:

```markdown
## vibes report: <feature>
**Track**: full | small | single phase    **Phases run**: ...
**Acceptance criteria**: 7/8 met (list any unmet and why)
**Security**: 0 critical, 0 high, 2 medium (1 fixed, 1 accepted: reason) - see .vibes/security-audit.md
**Tests**: 14 written (9 UI, 5 API), 14 passing - see .vibes/test-report.md
**SDLC checklist**: 21/24 done, 2 n/a, 1 needs human - see .vibes/checklist.md
**Needs human review**: (only if the diff touches a sensitive area) what and why
**Rollback**: how to undo this change (revert commit X; migration Y is reversible / is not)
**Not checked**: what was out of scope or couldn't run (e.g. no browser available, production config)
**Missing skills**: (only if any)
**Next steps**: 1-3 items
```

Be honest about gaps. A phase that couldn't run (no dev server, tool missing, test runner crashed) is reported as "not run", never as "passed" or "no findings". Don't describe the result as "secure" or "bug-free"; say what was checked.

## Missing skills

If a specialist was unavailable, list it in the report so the user can install it. All of them are part of this vibes bundle (github.com/imranhc0/vibes): `vibes-plan`, `vibes-design`, `vibes-react`, `vibes-simplify`, `vibes-security-audit`, `vibes-test`.

## Running one phase

"vibes plan", "vibes design", "vibes audit", "vibes simplify", "vibes test", "vibes checklist": do Step 0's stack and git check, then run just that phase (with its fallback if needed) and its part of the report.
