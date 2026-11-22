# Third-party notices

Four skills in this repo are adapted from other open-source projects. Each keeps its upstream license text inside its own folder, so the license travels with the skill however it is installed. Our changes are listed below and noted at the top of each changed `SKILL.md`.

| Skill | Upstream | Upstream commit | License |
|---|---|---|---|
| `vibes-plan` | [mattpocock/skills](https://github.com/mattpocock/skills): `skills/engineering/grill-with-docs`, `skills/productivity/grilling`, `skills/engineering/domain-modeling` | `abeeaf95660ba9e8b7c753eb38f441ca707a8823` | MIT, Copyright (c) 2026 Matt Pocock (`skills/vibes-plan/LICENSE`) |
| `vibes-design` | [anthropics/skills](https://github.com/anthropics/skills): `skills/frontend-design` | `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` | Apache-2.0 (`skills/vibes-design/LICENSE.txt`) |
| `vibes-react` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills): `skills/react-best-practices` | `5a37a6329fbad3666c3207392a6a7c0110e92efb` | MIT, as declared in the upstream SKILL.md and README (`skills/vibes-react/LICENSE`) |
| `vibes-simplify` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official): `plugins/code-simplifier` | `73c8cf3ea7e296057b467990f2f5d61b4c922260` | Apache-2.0 (`skills/vibes-simplify/LICENSE.txt`) |

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

These are copies, not live links, so upstream updates don't arrive on their own. To check for changes, compare the upstream path at its latest commit with the commit recorded above, apply what you want by hand, and update the commit in the table.
