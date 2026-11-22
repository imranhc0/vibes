# Contributing

## Layout

```
.claude-plugin/          plugin and marketplace manifests (Claude Code plugin install)
skills/<name>/SKILL.md   one folder per skill, plus any reference files it reads
upstream.json            pinned upstream commits for the adapted skills
scripts/                 maintenance scripts
.github/workflows/       weekly upstream check
```

## Working on the skills locally

Symlink your clone into Claude Code's skills folder so edits take effect in the next session without copying. Remove any installed copies of these skills first (plugin, npx or copied folders), or they will load twice.

```bash
mkdir -p ~/.claude/skills
for s in skills/*/; do
  s=$(basename "$s")
  ln -sfn "$PWD/skills/$s" ~/.claude/skills/$s
done
```

If a real folder with the same name is already in `~/.claude/skills/`, `ln` puts the link inside it instead of replacing it.

## Changing or adding a skill

1. Edit or add `skills/<name>/SKILL.md`. The frontmatter needs `name` (matching the folder, lowercase letters, digits and hyphens, up to 64 characters) and a `description` (up to 1,024 characters) that says when Claude should use it. The only other keys claude.ai accepts are `license`, `allowed-tools`, `metadata` and `compatibility`.
2. Validate:
   ```bash
   claude plugin validate --strict .
   ```
3. Bump `version` in `.claude-plugin/plugin.json`. Plugin users only receive changes when the version goes up.
4. Optionally tag the release, which also checks that the plugin and marketplace manifests agree:
   ```bash
   claude plugin tag .
   ```

## Adapted skills

`vibes-plan`, `vibes-design`, `vibes-react` and `vibes-simplify` are adapted from other open-source skills. Keep the license file in each of those folders. When you change one, add a line to [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Pulling upstream changes

Our copies are customised, so upstream changes are ported by hand, never copied over.

1. Check for changes. A weekly GitHub Actions run does this and opens an issue titled "Upstream skill updates available". To run it locally:
   ```bash
   python3 scripts/check_upstream.py
   ```
   Exit code 0 means no changes, 1 means changes (listed with a diff link), and 2 means the check itself failed. Set `GITHUB_TOKEN` if you hit the GitHub API rate limit.
2. Read the diff and port what you want into the skill.
3. Set that skill's `commit` in `upstream.json` to the commit the report gives.
4. Validate, bump the version and close the issue.
