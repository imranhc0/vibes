# vibes

Agent skills for vibe coding with a proper software lifecycle. Describe a feature, and Claude takes it through plan, design, build, simplify, security audit, tests and a release-readiness checklist, then tells you what was and wasn't checked.

```
/plugin install vibes --marketplace imranhc0/vibes
```

Then, in a new Claude Code session:

```
/vibes:vibes add a notes page where signed-in users can create, edit and delete their own notes
```

## Skills

| Skill | What it does |
|---|---|
| [`vibes`](skills/vibes/SKILL.md) | The main workflow. Sizes the request, runs each phase in order, loops back on failed audits or tests, and writes a final report. |
| [`vibes-plan`](skills/vibes-plan/SKILL.md) | Interviews you in rounds until every decision is settled, and records the domain glossary and decision records as they come up. |
| [`vibes-design`](skills/vibes-design/SKILL.md) | Visual design direction: palette, typography, layout and copy that don't look templated. |
| [`vibes-react`](skills/vibes-react/SKILL.md) | 70 React and Next.js performance rules, ranked by impact. |
| [`vibes-simplify`](skills/vibes-simplify/SKILL.md) | Simplifies the code changed in this session without changing behaviour, then re-runs your checks. |
| [`vibes-security-audit`](skills/vibes-security-audit/SKILL.md) | Static security review of your latest changes, with findings ranked by severity and evidence. |
| [`vibes-test`](skills/vibes-test/SKILL.md) | Explores the running app, then writes and runs Playwright UI and API tests. |

Every skill also works on its own. Everything the workflow needs is in this repo; there's nothing else to install.

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code) 2.1.275 or later for the one-line plugin install
- A git repository to work in
- For `vibes-test`: Node.js, or Python with `pytest-playwright`. The skill asks before installing Playwright.
- Optional security tools: `gitleaks`, `semgrep`, `bandit`, `gosec`, `npm audit`, `pip-audit`. The audit uses whichever are installed and lists the ones it couldn't run.

## Install

Pick one method. Installing the same skills two ways makes each one load twice.

### Claude Code plugin (recommended)

```
/plugin install vibes --marketplace imranhc0/vibes
```

On Claude Code older than 2.1.275:

```
/plugin marketplace add imranhc0/vibes
/plugin install vibes@vibes-skills
```

Restart Claude Code afterwards. Plugin skills are namespaced: `/vibes:vibes`, `/vibes:vibes-plan`, `/vibes:vibes-test` and so on.

### npx

Uses the open-source [`skills`](https://github.com/vercel-labs/skills) installer. Needs Node.js 22.20 or later.

```bash
# All skills, for every project (~/.claude/skills/)
npx skills add imranhc0/vibes -g -a claude-code

# All skills, for the current project only (.claude/skills/)
npx skills add imranhc0/vibes -a claude-code

# One skill
npx skills add imranhc0/vibes --skill vibes-security-audit -a claude-code
```

Leave out `-a claude-code` to pick agents interactively. Set `DISABLE_TELEMETRY=1` to turn off the installer's anonymous usage data.

### Manual copy

```bash
git clone https://github.com/imranhc0/vibes.git
mkdir -p ~/.claude/skills
cp -r vibes/skills/* ~/.claude/skills/
```

Use `<your-repo>/.claude/skills/` instead of `~/.claude/skills/` to install for one project only, and commit it so your team gets the skills too.

With npx or a manual copy, skills have no namespace: `/vibes`, `/vibes-plan`, `/vibes-test` and so on. Start a new Claude Code session to load them.

### Claude.ai (your personal account)

Skills you upload to claude.ai are private to your account. They also load in Claude Code when you're signed in with the same account (Claude Code 2.1.273 or later). If you use claude.ai skills, don't also install the plugin or npx copy, or the skills will load twice.

1. Build one zip per skill. Each zip holds the skill's folder:
   ```bash
   git clone https://github.com/imranhc0/vibes.git && cd vibes
   mkdir -p dist && cd skills
   for s in */; do s=${s%/}; zip -r "../dist/$s.zip" "$s"; done
   ```
2. On claude.ai, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Go to **Customize → Skills**, click **+**, then **Create skill → Upload a skill**, and choose a zip from `dist/`. Repeat for each skill.
4. Make sure each skill's toggle is on.

To update a skill, delete the old one (open it, turn off its toggle, then **… → Delete**) and upload the new zip. On a personal plan, skills can't be shared with other people; Team and Enterprise plans can share them across the organization.

The audit, simplify and test skills need to see your code and run commands, so they work best in Claude Code.

## Usage

```
/vibes <what you want built>
```

vibes picks a track and tells you which phases it will run:

- **Full**: a new feature, page, endpoint or app. Runs every phase.
- **Small**: a bug fix or a contained change. Writes a short plan itself and skips design unless the UI changes.
- **Single phase**: `vibes plan`, `vibes design`, `vibes audit`, `vibes simplify`, `vibes test` or `vibes checklist`.

It stops once to confirm the plan with you, then works through the rest. It never commits, pushes or deploys unless you ask, and it flags changes that need a human reviewer: auth, tenant isolation, secrets, billing, personal data and destructive migrations.

| # | Phase | Skill | Output |
|---|---|---|---|
| 1 | Plan | `vibes-plan` | `.vibes/plan.md`, plus `GLOSSARY.md` and `docs/adr/` when needed |
| 2 | Design (UI only) | `vibes-design` | design notes, UI code |
| 3 | Build | `vibes-react` for React / Next.js, stack rules otherwise | code changes |
| 4 | Simplify | `vibes-simplify` | cleaner code, same behaviour |
| 5 | Security audit | `vibes-security-audit` | `.vibes/security-audit.md` |
| 6 | Test | `vibes-test` | test files, `.vibes/test-report.md` |
| 7 | Fix loop | phases 3 to 6, up to 3 rounds | |
| 8 | Release readiness | built-in checklist | `.vibes/checklist.md` |
| 9 | Report | | summary in chat |

vibes asks whether you want `.vibes/` committed as a record or added to `.gitignore`.

## Update and uninstall

| Installed with | Update | Uninstall |
|---|---|---|
| Plugin | `claude plugin marketplace update vibes-skills`, then `claude plugin update vibes@vibes-skills` | `claude plugin uninstall vibes@vibes-skills` |
| npx | `npx skills update` | `npx skills remove vibes vibes-plan vibes-design vibes-react vibes-simplify vibes-security-audit vibes-test` (add `-g` if installed globally) |
| Manual copy | `git pull` in your clone, then copy again | delete the `vibes*` folders from your skills directory |
| Claude.ai | delete and re-upload | **Customize → Skills**, open the skill, **… → Delete** |

Restart Claude Code after any of these.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Some skills include their own license file in their folder.
