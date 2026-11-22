# vibes-react

React and Next.js performance rules, adapted from Vercel's React Best Practices (MIT). Originally created by [@shuding](https://x.com/shuding) at [Vercel](https://vercel.com). See `THIRD_PARTY_NOTICES.md` at the repo root.

## Structure

- `SKILL.md` - entry point: rule categories, priorities and a one-line index of every rule
- `rules/` - one file per rule, with an incorrect and a correct example
  - `_sections.md` - section titles, impact levels and descriptions
  - `_template.md` - template for a new rule

The `rules/` folder is the single source. Upstream also ships a compiled `AGENTS.md` built by its own tooling; it is not included here, so there is nothing to rebuild.

## Adding or changing a rule

1. Copy `rules/_template.md` to `rules/<prefix>-<description>.md`.
2. Use the prefix for its section:

   | Prefix | Section | Impact |
   |---|---|---|
   | `async-` | Eliminating Waterfalls | CRITICAL |
   | `bundle-` | Bundle Size Optimization | CRITICAL |
   | `server-` | Server-Side Performance | HIGH |
   | `client-` | Client-Side Data Fetching | MEDIUM-HIGH |
   | `rerender-` | Re-render Optimization | MEDIUM |
   | `rendering-` | Rendering Performance | MEDIUM |
   | `js-` | JavaScript Performance | LOW-MEDIUM |
   | `advanced-` | Advanced Patterns | LOW |

3. Fill in the frontmatter (`title`, `impact`, optional `impactDescription`, `tags`) and give a clear incorrect and correct example.
4. Add a one-line entry for the rule under its section in `SKILL.md`'s Quick Reference. That index is how Claude finds the rule.

Files starting with `_` are not rules.
