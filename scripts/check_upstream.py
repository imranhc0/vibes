#!/usr/bin/env python3
"""Check whether the upstream sources of the adapted skills have changed.

Reads upstream.json at the repo root. For each adapted skill it compares every
copied path at the pinned commit with the same path on the upstream branch, and
lists the upstream commits that touched a changed path.

Exit codes: 0 no upstream changes, 1 upstream changes found, 2 the check failed.
Set GITHUB_TOKEN to raise the GitHub API rate limit.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
MANIFEST = Path(__file__).resolve().parent.parent / "upstream.json"


def get(path, params=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "vibes-upstream-check",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def path_sha(repo, ref, path):
    """Git object SHA of a file or folder at ref, or None if it doesn't exist there."""
    parent, _, name = path.rstrip("/").rpartition("/")
    try:
        listing = get(f"/repos/{repo}/contents/{urllib.parse.quote(parent)}", {"ref": ref})
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    return next((item["sha"] for item in listing if item["name"] == name), None)


def inline_code(text):
    # Code spans keep upstream text from rendering as markdown or @-mentions in the issue.
    return "`" + text.replace("`", "'") + "`"


def check(skill, source):
    """Markdown section describing upstream changes for one skill, or None if unchanged."""
    repo, branch, pinned = source["repo"], source["branch"], source["commit"]
    # Validate every path before any shortcut, so a wrong manifest fails instead of reading as "no changes".
    pinned_shas = {}
    for path in source["paths"]:
        pinned_shas[path] = path_sha(repo, pinned, path)
        if pinned_shas[path] is None:
            raise ValueError(f"{path} not found in {repo} at pinned commit {pinned[:7]}")

    head = get(f"/repos/{repo}/commits/{urllib.parse.quote(branch)}")["sha"]
    if head == pinned:
        return None

    changed = []
    for path, before in pinned_shas.items():
        after = path_sha(repo, head, path)
        if before != after:
            changed.append((path, after is None))
    if not changed:
        return None

    since = get(f"/repos/{repo}/commits/{pinned}")["commit"]["committer"]["date"]
    commits = {}
    for path, _ in changed:
        params = {"sha": head, "path": path, "since": since, "per_page": 100}
        for commit in get(f"/repos/{repo}/commits", params):
            if commit["sha"] != pinned:
                commits[commit["sha"]] = commit

    lines = [f"## {skill} ({repo})", ""]
    for path, removed in changed:
        lines.append(f"- {inline_code(path)} {'was removed upstream' if removed else 'changed'}")
    lines.append(f"- Diff: https://github.com/{repo}/compare/{pinned[:12]}...{head[:12]}")
    ordered = sorted(commits.values(), key=lambda c: c["commit"]["committer"]["date"], reverse=True)
    for commit in ordered:
        date = commit["commit"]["committer"]["date"][:10]
        title = commit["commit"]["message"].splitlines()[0]
        lines.append(f"  - {commit['sha'][:7]} {date} {inline_code(title)}")
    lines.append(f"- After porting what you want, set `commit` to `{head}` in upstream.json")
    return "\n".join(lines)


def main():
    sources = json.loads(MANIFEST.read_text())
    sections, failures = [], []
    for skill, source in sources.items():
        try:
            section = check(skill, source)
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as error:
            failures.append(f"- {skill}: {error}")
            continue
        if section:
            sections.append(section)

    if failures:
        print("# Upstream check failed\n")
        print("These skills could not be checked, so their upstream status is unknown:\n")
        print("\n".join(failures))
        if sections:
            print("\n" + "\n\n".join(sections))
        return 2
    if not sections:
        print(f"No upstream changes since the pinned commits ({len(sources)} skills checked).")
        return 0
    print("# Upstream skill updates\n")
    print(f"{len(sections)} of {len(sources)} adapted skills have upstream changes. "
          "Our copies are customised, so port what you want by hand instead of overwriting them.\n")
    print("\n\n".join(sections))
    return 1


if __name__ == "__main__":
    sys.exit(main())
