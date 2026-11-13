"""Content rules checked before anything is rendered.

`no_links` (brand.yaml -> rules): nothing is live yet, so a script must not send
people to a website, a sign-up page or a "link in bio". The studio refuses to
render until those lines are rewritten.
"""

import re

LINK_PATTERNS = [
    (r"https?://", "a web address"),
    (r"\bwww\.", "a web address"),
    (r"\b[a-z0-9-]+\.(com|in|io|ai|co|app|org|net|shop|store)\b(?!\w)", "a website domain"),
    (r"\blink in (the )?bio\b", '"link in bio"'),
    (r"\bvisit\b", '"visit"'),
    (r"\bclick (here|the link|below)\b", '"click here / the link"'),
    (r"\bsign ?up\b", '"sign up"'),
    (r"\bwait ?list\b", '"waitlist"'),
    (r"\bbuy now\b", '"buy now"'),
    (r"\bshop now\b", '"shop now"'),
    (r"\bdownload (the|our) app\b", '"download our app"'),
]

# Instagram/LinkedIn handles like @agentready.in are fine; strip them before checking.
HANDLE_RE = re.compile(r"@[\w.]+")


def _walk(node, path="script"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def check_no_links(script):
    """Return a list of (where, what, text) problems. Audio/file path fields are ignored."""
    problems = []
    for where, text in _walk(script):
        if where.split(".")[-1] in ("music", "slug") or ".voiceover" in where or "._voice" in where:
            continue
        clean = HANDLE_RE.sub("", text)
        for pattern, label in LINK_PATTERNS:
            if re.search(pattern, clean, re.IGNORECASE):
                problems.append((where, label, text.strip().splitlines()[0][:80]))
                break
    return problems


def enforce(brand, script):
    if not (brand.rules or {}).get("no_links", True):
        return
    problems = check_no_links(script)
    if problems:
        lines = ["", "Content rule 'no_links' failed: nothing is live yet, so don't send people anywhere.",
                 "Rewrite these lines (use 'Follow', 'Comment', 'Save this' instead):", ""]
        for where, label, text in problems:
            lines.append(f"  - {where}: contains {label}  ->  {text}")
        lines += ["", "When something is live, set `rules: no_links: false` in brand.yaml.", ""]
        raise SystemExit("\n".join(lines))
