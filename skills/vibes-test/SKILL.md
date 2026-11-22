---
name: vibes-test
description: Frontend and API testing for a web app with Playwright - explores the running app with a browser agent, then writes and runs Playwright end-to-end UI tests and API tests (via Playwright's request context) for the latest changes or a plan's acceptance criteria, and reports what passed, failed and wasn't covered. Use this whenever the user asks to test, QA, smoke-test, write e2e/integration/API tests, "check the page works", "test my endpoints", or "make sure this feature works", or when the vibes workflow reaches its test phase, even if Playwright isn't mentioned.
---

# vibes-test

Test the feature the way a user and a client would use it: click through the UI in a real browser and call the API over HTTP. Playwright does both in one runner (`page` for the browser, `request` for HTTP), so UI and API tests share config, base URL, auth setup and reports.

The deliverable is two things: **test files committed to the repo** (so the checks keep running after this session) and **a report** of what was run and what happened.

## Safety boundaries

Test only the user's own app: localhost, a dev container, or a staging environment they say is theirs. Never point tests at production or third-party services, and never run load, fuzzing or brute-force style tests. API tests that create or delete data run against a local or disposable database, and clean up after themselves. If the only target available is shared or production, stop and ask.

## 1. Work out what to test

Gather, in this order:

1. **Acceptance criteria** from `.vibes/plan.md` if it exists (the vibes workflow writes it). Each criterion should map to at least one test.
2. **The change**: `git diff HEAD --name-only` (or vs the main branch) to find touched pages, components, routes and handlers. Read them to learn the URLs, form fields, API paths, request/response shapes and auth requirements.
3. **Existing tests and config**: `playwright.config.*`, `tests/`, `e2e/`, plus other runners (vitest, jest, pytest). Extend what's there: same folder layout, naming, fixtures and helpers. Don't create a parallel setup.

Write a short test plan (bullets, not prose): for each criterion, the UI checks and the API checks. Cover the happy path plus the cases that usually break: empty/invalid input, unauthenticated and wrong-user access, not-found, empty states, error states, and anything the plan lists as an edge case.

## 2. Set up Playwright

If Playwright isn't in the project:

- Node/TS projects: `npm i -D @playwright/test` (or the project's package manager), then `npx playwright install chromium` if browsers aren't present. Add a minimal `playwright.config.ts`.
- Python projects: `pip install pytest-playwright` and `playwright install chromium`; write the tests with pytest's `page` and `playwright.request` fixtures instead. The principles below are the same.

Ask before adding dependencies if the user hasn't already approved test setup (inside the vibes workflow, it's approved).

A config that fits most apps:

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }], ['json', { outputFile: 'test-results/results.json' }]],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    // Separate testDir per project. A testMatch regex like /api\/.*\.spec/ is matched against the
    // absolute path, so a parent folder containing "api/" would pull UI tests into the API project.
    { name: 'api', testDir: './tests/api' },
    { name: 'ui', testDir: './tests/e2e', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',          // use the project's real dev/start command
    url: 'http://localhost:3000',    // and its real port
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

Find the real dev command and port from `package.json` scripts, framework defaults (Next 3000, Vite 5173, FastAPI 8000) or the README. If the app needs env vars or a database, look for `.env.example` / docker-compose and set up a local instance; don't copy real secrets into tests or config.

## 3. Explore with a browser agent first

Before writing assertions, look at the actual app. This catches the things a spec can't tell you: real selectors, labels, loading behaviour, console errors, broken layouts.

- If browser tools are available in this session (a Playwright MCP server such as `browser_navigate` / `browser_snapshot` / `browser_click`, or a Chrome-controlling extension), use them to walk each flow in the plan: navigate, read the accessibility snapshot, fill forms, submit, watch for console errors and failed network requests.
- Otherwise, drive a headless browser with a short throwaway script: open each page, take a screenshot (look at it), record `console` errors and responses with status ≥ 400, and print the accessible roles/names of the interactive elements.

Note any bugs you see now; they become failing tests or report items. Keep exploration notes brief; their value is in the tests they inform.

## 4. Write the tests

Put UI tests in `tests/e2e/` and API tests in `tests/api/` (or follow the existing layout). One spec file per feature.

**UI tests (`page`)**
- Locate by what users see: `getByRole`, `getByLabel`, `getByText`, `getByPlaceholder`. Fall back to `getByTestId` only when there's no accessible handle (and consider adding a label instead).
- Use web-first assertions that wait: `await expect(locator).toBeVisible()`, `toHaveText`, `toHaveURL`. Never `waitForTimeout` - fixed sleeps make tests slow and flaky.
- Each test sets up its own state (via the API or a fixture) so tests run in any order and in parallel.
- Assert outcomes the user cares about (the note appears in the list, the error message shows), not implementation details.
- Fail on unexpected console errors for key flows:
  ```ts
  const errors: string[] = [];
  page.on('console', m => m.type() === 'error' && errors.push(m.text()));
  // ... flow ...
  expect(errors).toEqual([]);
  ```
- If `@axe-core/playwright` is present, add an accessibility check on new pages.

**API tests (`request`)**
```ts
import { test, expect } from '@playwright/test';

test.describe('POST /api/notes', () => {
  test('creates a note for a signed-in user', async ({ request }) => {
    const res = await request.post('/api/notes', { data: { title: 'Hello', body: 'World' } });
    expect(res.status()).toBe(201);
    const note = await res.json();
    expect(note).toMatchObject({ title: 'Hello', body: 'World' });
    expect(note.id).toBeTruthy();
  });

  test('rejects an empty title with 400', async ({ request }) => {
    const res = await request.post('/api/notes', { data: { title: '' } });
    expect(res.status()).toBe(400);
  });
});
```
For each endpoint cover: success status and response shape; validation errors (400/422) for missing, wrong-type and out-of-range fields; 401 without auth; 403/404 when a user touches another user's resource; 404 for unknown IDs; and pagination or limits if the endpoint lists things. Check the response doesn't leak fields it shouldn't (password hashes, internal IDs, other users' data).

**Auth**: log in once in a setup project and reuse `storageState`, or create a request context with a token from a test-only user. Test credentials come from env vars or seeded fixtures, never real accounts.

## 5. Run, triage, re-run

Run `npx playwright test` (or `pytest`). For each failure, open the trace or screenshot and decide:

- **App bug** → it's a real finding. Report it (or fix it, if you're inside the vibes workflow or were asked to), then re-run.
- **Test bug** (wrong selector, bad assumption, missing setup) → fix the test.
- **Flaky** (passes on retry) → find the cause (usually a missing wait-for or shared state) and fix it; don't hide it with retries or longer timeouts.

Never change an assertion just to make it match buggy behaviour, and never delete or `skip` a failing test to get a green run. If a test can't run at all (the app won't start, browsers can't install, a dependency is missing), that is a failed check: say so plainly.

## 6. Report

Write `.vibes/test-report.md` (create `.vibes/` if needed) and summarise in chat:

```markdown
# Test report - <feature>
**Date**: <YYYY-MM-DD>   **Target**: http://localhost:3000 (dev server)   **Browser**: Chromium
**Result**: 12 passed, 1 failed, 0 skipped (9 UI, 4 API)

## Acceptance criteria
| # | Criterion | Tests | Status |
|---|---|---|---|
| 1 | Signed-in user can create a note | e2e/notes.spec.ts "creates a note"; api/notes.spec.ts "creates a note" | pass |
| 2 | Empty title is rejected | api/notes.spec.ts "rejects empty title" | FAIL - API returns 500 |

## Failures
### api/notes.spec.ts > rejects an empty title with 400
Expected 400, got 500. Cause: no validation before insert (`app/api/notes/route.ts:8`). Trace: test-results/...

## Bugs found while exploring
## Not covered
<browsers, devices, flows or criteria with no test, and why; anything that couldn't run>

## How to run
npx playwright test            # all
npx playwright test --project=api
npx playwright show-report
```

Report exactly what ran. "Not run" and "failed to run" are never reported as passing, and a green run means "these checks passed", not "the app has no bugs".
