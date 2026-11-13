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

# Stealth: we teach the problem, never show the product we are building.
REVEAL_PATTERNS = [
    (r"(\bi['’]m|\bi am|\bwe['’]re|\bwe are)\b.{0,25}\b(building|creating|making|launching|developing)\b", '"I\'m building / launching"'),
    (r"\b(main|hum)\b.{0,40}\b(bana raha|bana rahe|bana rahi|launch kar)", '"main/hum ... bana raha hoon"'),
    (r"\bour (tool|app|product|platform|software|solution|startup)\b", '"our tool / app / product"'),
    (r"\b(my|mera|meri) (tool|app|product|platform|software|startup)\b", '"my tool / app"'),
    (r"\b(checker|scanner|beta|early access|coming soon|pre-?launch|launching|prototype|MVP)\b", "a product word"),
    (r"\bagentready (tool|app|platform|software|score|scan|checker|product)\b", '"AgentReady <product>"'),
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


def check_no_links(script, patterns=LINK_PATTERNS):
    """Return a list of (where, what, text) problems. Audio/file path fields are ignored."""
    problems = []
    for where, text in _walk(script):
        if where.split(".")[-1] in ("music", "slug") or ".voiceover" in where or "._voice" in where:
            continue
        clean = HANDLE_RE.sub("", text)
        for pattern, label in patterns:
            if re.search(pattern, clean, re.IGNORECASE):
                problems.append((where, label, text.strip().splitlines()[0][:80]))
                break
    return problems


def check_no_reveal(script):
    return check_no_links(script, REVEAL_PATTERNS)


def enforce(brand, script):
    rules = brand.rules or {}
    sections = []
    if rules.get("no_links", True):
        p = check_no_links(script)
        if p:
            sections.append(("no_links", "nothing is live yet, so don't send people anywhere",
                             "use 'Follow', 'Comment', 'Save this' instead", p))
    if rules.get("no_product_reveal", True):
        p = check_no_reveal(script)
        if p:
            sections.append(("no_product_reveal", "we're in stealth: teach the problem, never describe what we're building",
                             "talk about the seller's problem and free fixes, not a tool or launch", p))
    if not sections:
        return
    lines = [""]
    for name, why, fix, problems in sections:
        lines += [f"Content rule '{name}' failed: {why}.", f"Rewrite these lines ({fix}):", ""]
        lines += [f"  - {w}: contains {label}  ->  {text}" for w, label, text in problems]
        lines.append("")
    lines += ["Turn a rule off in brand.yaml (rules:) only when it no longer applies.", ""]
    raise SystemExit("\n".join(lines))
