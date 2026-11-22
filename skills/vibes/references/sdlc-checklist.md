# SDLC checklist

What each stage of the software lifecycle should leave behind before a change is called done. vibes copies this to `.vibes/checklist.md` in phase 8 and marks each item:

- `[x]` done - say where the evidence is (file, test name, report section)
- `[-]` n/a - one-line reason
- `[ ]` not done - one-line reason; it goes in the final report's next steps
- `[!]` needs human - a decision or review only a person can give

Items marked ★ are the core set. The *small* track checks only ★ items; the *full* track checks everything. An item is never ticked on trust: if you didn't verify it in this session, it is not done.

## 1. Requirements
- [ ] ★ The goal is written in one or two sentences a non-engineer would understand
- [ ] ★ Acceptance criteria are numbered and each is observable (a test could check it)
- [ ] Scope is explicit: what is in, and what is deliberately out
- [ ] Who can use the feature and who must not (roles, tenants, anonymous users) is stated
- [ ] Open questions are either answered or listed as risks

## 2. Design
- [ ] ★ API and data contracts are written down (routes, request/response shapes, status codes, schema changes)
- [ ] Every UI state is designed: loading, empty, error, success
- [ ] Accessibility is considered: labels, keyboard path, focus, contrast
- [ ] Failure modes are considered: what happens when a dependency is slow or down, on bad input, on double submit
- [ ] Data changes are backward compatible, or there is a migration plan
- [ ] New dependencies are justified (why not what's already there)

## 3. Implementation
- [ ] ★ Follows the project's existing patterns, linter and formatter; lint and type check pass
- [ ] ★ Input is validated on the server at every new trust boundary
- [ ] ★ No secrets in code, config, logs, tests or commits; new settings come from env vars or a secrets manager
- [ ] ★ Errors are handled; clients never see stack traces or internal details
- [ ] No dead code, debug output, commented-out blocks or stray TODOs without an owner
- [ ] Lists are bounded (pagination or limits); no obvious N+1 queries
- [ ] Logging is useful for debugging and contains no personal data or credentials

## 4. Code review
- [ ] ★ The diff contains only this change (no unrelated edits or reformatting)
- [ ] ★ A simplify pass ran, and behaviour was re-verified afterwards
- [ ] The change is small enough to review; if not, it is split or the split is proposed
- [ ] ★ Sensitive areas are flagged for human review: auth and access control, tenant isolation, secrets handling, payments/billing/tiers, consent and personal data, destructive migrations, anything the project's rules name
- [ ] Commit messages / PR description explain what changed and why

## 5. Security
- [ ] ★ A security audit of the diff ran (`.vibes/security-audit.md`)
- [ ] ★ Critical and high findings are fixed, or explicitly accepted by a person with the reason recorded
- [ ] ★ Tools that could not run are listed as "not run", never as clean
- [ ] Dependency audit ran if manifests changed
- [ ] New endpoints check both authentication and authorisation for the specific resource

## 6. Testing
- [ ] ★ Every acceptance criterion maps to at least one automated test
- [ ] ★ All tests pass, with no skipped or weakened tests (`.vibes/test-report.md`)
- [ ] ★ Existing tests still pass (no regressions)
- [ ] Both layers are covered where they exist: UI in a real browser and the API over HTTP
- [ ] Negative cases are covered: invalid input, unauthenticated, wrong user, not found
- [ ] Tests are independent and repeatable (no order dependence, no fixed sleeps, they clean up their data)
- [ ] What was not tested is written down (browsers, devices, load, integrations)

## 7. Release readiness
- [ ] ★ Rollback is written down: how to undo the change, and whether any migration is reversible
- [ ] ★ Docs are updated where behaviour changed: README, API docs, `.env.example`, changelog
- [ ] New config, env vars, migrations and manual steps are listed for whoever deploys
- [ ] Risky or user-visible changes can be switched off (feature flag) or are released gradually
- [ ] CI is expected to pass: the new tests run in the project's existing CI command
- [ ] Nothing was committed, pushed, merged or deployed without the user asking

## 8. After release (hand-over notes; vibes doesn't deploy)
- [ ] How to tell it works in production: the log line, metric or page to check
- [ ] What to watch for the first day (error rate, slow queries, support tickets)
- [ ] Follow-ups that were deliberately left out are listed with enough context to pick up later
