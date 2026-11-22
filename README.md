# vibes skills

Agent skills for vibe coding with a proper software lifecycle. You describe a feature, and Claude takes it through plan, design, build, simplify, security audit, tests and a release-readiness checklist, then reports what was and wasn't checked.

Everything the workflow needs is in this repo. There are no outside skills to install.

| Skill | What it does | Invoke |
|---|---|---|
| [`vibes`](skills/vibes/SKILL.md) | The main workflow. Sizes the request, runs each phase in order, loops back on failed audits or tests, and writes a final report. | `/vibes <what to build>` |
| [`vibes-plan`](skills/vibes-plan/SKILL.md) | Interviews you in rounds until every decision is settled, and records the domain glossary and ADRs as they come up. | `/vibes-plan` |
| [`vibes-design`](skills/vibes-design/SKILL.md) | Visual design direction: palette, typography, layout and copy that don't look templated. | `/vibes-design` |
| [`vibes-react`](skills/vibes-react/SKILL.md) | 70 React and Next.js performance rules, ranked by impact. | `/vibes-react` |
| [`vibes-simplify`](skills/vibes-simplify/SKILL.md) | Simplifies the code changed in this session without changing behaviour, then re-runs checks. | `/vibes-simplify` |
| [`vibes-security-audit`](skills/vibes-security-audit/SKILL.md) | Static security review of your latest changes (uncommitted work, last commit, or branch vs main). Findings are ranked by severity and evidence level. | `/vibes-security-audit` |
| [`vibes-test`](skills/vibes-test/SKILL.md) | Explores the running app, then writes and runs Playwright UI and API tests against the acceptance criteria. | `/vibes-test` |

Each specialist skill also works on its own, without the main workflow.

## Repository layout

```
vibes/
├── .claude-plugin/
│   ├── marketplace.json      # lets Claude Code install this repo as a plugin marketplace
│   └── plugin.json           # plugin name and version
├── skills/
│   ├── vibes/                # main workflow
│   │   ├── SKILL.md
│   │   └── references/sdlc-checklist.md
│   ├── vibes-plan/           # adapted from mattpocock/skills (MIT)
│   │   ├── SKILL.md
│   │   ├── LICENSE
│   │   └── references/       # ADR and glossary formats
│   ├── vibes-design/         # adapted from anthropics/skills (Apache-2.0)
│   │   ├── SKILL.md
│   │   └── LICENSE.txt
│   ├── vibes-react/          # adapted from vercel-labs/agent-skills (MIT)
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   ├── LICENSE
│   │   └── rules/            # one file per rule
│   ├── vibes-simplify/       # adapted from anthropics/claude-plugins-official (Apache-2.0)
│   │   ├── SKILL.md
│   │   └── LICENSE.txt
│   ├── vibes-security-audit/
│   │   └── SKILL.md
│   └── vibes-test/
│       └── SKILL.md
└── THIRD_PARTY_NOTICES.md    # upstream sources, commits, licenses and our changes
```

Each folder under `skills/` is a self-contained skill: a `SKILL.md` with `name` and `description` frontmatter, plus any reference files it reads.

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code) (2.1.275 or later for the one-step plugin install below)
- A git repository to work in. The audit and test skills scope themselves to the current diff.
- For `vibes-test`: Node.js (or Python with `pytest-playwright`). The skill asks before it installs Playwright.
- Optional: `gitleaks`, `semgrep`, `bandit`, `gosec`, `npm audit` / `pip-audit`. The audit uses whichever are installed and lists the ones that didn't run.

## Install

Pick one option. Don't combine them, or each skill will load twice.

### Option 1: Claude Code plugin (recommended)

Gives you all the skills and updates through Claude Code's plugin manager.

From GitHub:

```
/plugin install vibes --marketplace imranhc0/vibes
```

On Claude Code older than 2.1.275, add the marketplace first and then install:

```
/plugin marketplace add imranhc0/vibes
/plugin install vibes@vibes-skills
```

From a local clone (no GitHub needed):

```
/plugin marketplace add /path/to/vibes
/plugin install vibes@vibes-skills
```

The same commands work from a shell as `claude plugin marketplace add ...` and `claude plugin install ...`.

Restart Claude Code after installing. Plugin skills are namespaced, so you invoke them as `/vibes:vibes`, `/vibes:vibes-plan`, `/vibes:vibes-test` and so on. Claude also picks them up automatically when your request matches, for example "audit my changes" or "write e2e tests for this page".

### Option 2: npx (skills CLI)

[`skills`](https://github.com/vercel-labs/skills) is an open-source installer for agent skills. It works with Claude Code and many other coding agents. It needs Node.js 22.20 or later and no clone.

```bash
# All skills, for every project (~/.claude/skills/)
npx skills add imranhc0/vibes -g -a claude-code

# All skills, for the current project only (.claude/skills/)
npx skills add imranhc0/vibes -a claude-code

# Just one skill
npx skills add imranhc0/vibes --skill vibes-security-audit -a claude-code
```

Leave out `-a claude-code` to choose agents interactively. The CLI sends anonymous usage data unless you set `DISABLE_TELEMETRY=1`.

If you install only some skills, `vibes` still runs: it uses built-in fallback instructions for any phase whose skill is missing and says so in its report.

Start a new Claude Code session. Skills installed this way have no namespace: `/vibes`, `/vibes-plan`, `/vibes-test` and so on.

### Option 3: Copy into your skills folder

Copy the skills into one of these folders:

- All your projects: `~/.claude/skills/`
- One project only: `<repo>/.claude/skills/` (commit it so your team gets the skills too)

```bash
git clone https://github.com/imranhc0/vibes.git
mkdir -p ~/.claude/skills
cp -r vibes/skills/* ~/.claude/skills/
```

For a single project, swap `~/.claude/skills` for `<repo>/.claude/skills`.

Start a new Claude Code session. Skills installed this way have no namespace: `/vibes`, `/vibes-plan`, `/vibes-test` and so on.

### Option 4: Symlink a clone (for editing the skills)

Use this if you're changing the skills and want edits to take effect without copying again.

```bash
git clone https://github.com/imranhc0/vibes.git
cd vibes
mkdir -p ~/.claude/skills
for s in skills/*/; do
  s=$(basename "$s")
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s
done
```

Remove any earlier copies of these folders from `~/.claude/skills/` first. If a real folder with the same name is already there, `ln` puts the link inside it instead of replacing it.

### Claude.ai and Claude Desktop

These skills are written for Claude Code: they run git, local tools and a dev server. On Claude.ai or Claude Desktop you can upload them as custom skills, but the audit, simplify and test phases will only work where Claude has code execution and can see your repository.

To build the upload files:

```bash
mkdir -p dist
cd skills
for s in */; do
  s=${s%/}
  zip -r "../dist/$s.zip" "$s"
done
```

Then upload each zip from the Skills section of Claude's settings.

## Usage

```
/vibes add a notes page where signed-in users can create, edit and delete their own notes
```

vibes picks a track and tells you which phases it will run:

- **Full**: a new feature, page, endpoint or app. Runs every phase.
- **Small**: a contained change such as a bug fix or a new field. Writes a short plan itself and skips design unless the UI changes.
- **Single phase**: `vibes plan`, `vibes design`, `vibes audit`, `vibes simplify`, `vibes test` or `vibes checklist` runs only that phase.

It stops once to confirm the plan with you, then works through the rest. It never commits, pushes or deploys unless you ask, and it flags changes that need human review (auth, tenant isolation, secrets, billing, personal data, destructive migrations).

| # | Phase | Uses | Output |
|---|---|---|---|
| 1 | Plan | `vibes-plan` | `.vibes/plan.md`, `GLOSSARY.md`, `docs/adr/` when needed |
| 2 | Design (UI only) | `vibes-design` | design notes, UI code |
| 3 | Build | `vibes-react` (React / Next.js) or stack rules | code changes |
| 4 | Simplify | `vibes-simplify` | cleaner code, same behaviour |
| 5 | Security audit | `vibes-security-audit` | `.vibes/security-audit.md` |
| 6 | Test | `vibes-test` | test files, `.vibes/test-report.md` |
| 7 | Fix loop | phases 3 to 6, up to 3 rounds | |
| 8 | Release readiness | `references/sdlc-checklist.md` | `.vibes/checklist.md` |
| 9 | Report | | summary in chat |

## Adapted third-party skills

Four skills are our own copies of open-source skills, renamed with the `vibes-` prefix so they don't clash with the originals if you also have those installed. We change them freely here; upstream updates don't arrive automatically.

| Skill | Adapted from | License |
|---|---|---|
| `vibes-plan` | `grill-with-docs`, `grilling` and `domain-modeling` from [mattpocock/skills](https://github.com/mattpocock/skills) | MIT |
| `vibes-design` | `frontend-design` from [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 |
| `vibes-react` | `react-best-practices` from [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | MIT |
| `vibes-simplify` | the `code-simplifier` agent from [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Apache-2.0 |

[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) records the upstream commit each copy was taken from, what we changed, and how to pull later upstream changes.

## Outputs

Each run writes to `.vibes/` at the root of the repo you're working in:

| File | Written by |
|---|---|
| `plan.md` | Plan and design phases |
| `security-audit.md` | `vibes-security-audit` |
| `test-report.md` | `vibes-test` |
| `checklist.md` | Release-readiness phase |

vibes asks whether you want `.vibes/` committed as a record or added to `.gitignore`. The Plan phase may also create `GLOSSARY.md` and `docs/adr/` in your repo; those are meant to be committed.

## Update and uninstall

| Installed with | Update | Uninstall |
|---|---|---|
| Plugin | `claude plugin marketplace update vibes-skills`, then `claude plugin update vibes@vibes-skills` | `claude plugin uninstall vibes@vibes-skills` |
| npx | `npx skills update` | `npx skills remove vibes vibes-plan vibes-design vibes-react vibes-simplify vibes-security-audit vibes-test` (add `-g` if installed globally) |
| Copy | `git pull` in your clone, then copy the folders again | delete the `vibes*` folders from your skills directory |
| Symlink | `git pull` in your clone | delete the `vibes*` links from your skills directory |

Restart Claude Code after any of these.

## Contributing

To change a skill or add one:

1. Edit or add a folder under `skills/<skill-name>/` with a `SKILL.md`. The frontmatter needs `name` (matching the folder) and a `description` that says when Claude should use it.
2. If you change one of the adapted skills, add the change to [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and keep its license file in the folder.
3. Validate the repo:
   ```bash
   claude plugin validate --strict .
   ```
4. Bump `version` in `.claude-plugin/plugin.json`. Plugin users only receive changes when the version goes up.
5. Optionally tag the release, which also checks the plugin and marketplace manifests agree:
   ```bash
   claude plugin tag .
   ```

## License

No license has been added yet for this repo's own skills (`vibes`, `vibes-security-audit`, `vibes-test`), so default copyright applies. The four adapted skills stay under their upstream licenses (MIT or Apache-2.0); see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). A `LICENSE` file is also required before the plugin can be submitted to a plugin directory.
