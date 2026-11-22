# Third-party notices

Four skills in this repo are adapted from other open-source projects. Each keeps its upstream license text inside its own folder, so the license travels with the skill however it is installed. Our changes are listed below and noted at the top of each changed `SKILL.md`. The upstream commit each copy was taken from is pinned in [`upstream.json`](upstream.json).

| Skill | Upstream | License |
|---|---|---|
| `vibes-plan` | [mattpocock/skills](https://github.com/mattpocock/skills): `skills/engineering/grill-with-docs`, `skills/productivity/grilling`, `skills/engineering/domain-modeling` | MIT, Copyright (c) 2026 Matt Pocock (`skills/vibes-plan/LICENSE`) |
| `vibes-design` | [anthropics/skills](https://github.com/anthropics/skills): `skills/frontend-design` | Apache-2.0 (`skills/vibes-design/LICENSE.txt`) |
| `vibes-react` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills): `skills/react-best-practices` | MIT, as declared in the upstream SKILL.md and README (`skills/vibes-react/LICENSE`) |
| `vibes-simplify` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official): `plugins/code-simplifier` | Apache-2.0 (`skills/vibes-simplify/LICENSE.txt`) |

## Changes from upstream

**vibes-plan**
- Merged three skills into one. `grill-with-docs` only called `grilling` and `domain-modeling`, so their content now lives in one `SKILL.md`.
- Removed `disable-model-invocation: true`, so the vibes workflow can call it.
- Moved `ADR-FORMAT.md` and `GLOSSARY-FORMAT.md` into `references/`, unchanged.
- Dropped the OpenAI/Codex `agents/openai.yaml` files.

**vibes-design**
- Renamed from `frontend-design` and extended the description. The body is unchanged.

**vibes-react**
- Renamed from `vercel-react-best-practices` and extended the description.
- `rules/` (70 rules plus `_sections.md` and `_template.md`) is unchanged.
- Removed the compiled `AGENTS.md` and its build files, so `rules/` is the single source, and removed the `AGENTS.md` pointer from `SKILL.md`.
- Replaced the upstream README with one that describes editing rules without the build tooling.

**vibes-simplify**
- Converted from a Claude Code agent (`agents/code-simplifier.md`) to a skill, so every install method includes it.
- Replaced the fixed list of coding standards with the project's own rules (`CLAUDE.md`, linter config, existing code).
- Added an explicit scope (files changed in the session) and a verification step (type check, lint, tests; revert what breaks).
- Removed the agent-only `model` field and the "operate autonomously and proactively" paragraph.

## Pulling upstream changes

These are copies, not live links. `scripts/check_upstream.py` compares each copied path at its pinned commit with upstream's latest version, and a weekly GitHub Actions run (`.github/workflows/upstream-check.yml`) opens an issue when something changed. Port what you want by hand, then update the commit in `upstream.json`. See [CONTRIBUTING.md](CONTRIBUTING.md).
