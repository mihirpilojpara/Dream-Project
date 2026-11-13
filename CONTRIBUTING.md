# How we work

## Branches

| Branch | Purpose | Who writes to it |
|---|---|---|
| `production` | Final, release-ready code. The default branch. | Only merges from `qa` |
| `qa` | Quality testing and demos | Only merges from `development` |
| `development` | Integration ("stage"). All features land here first. | Only merges from `feature/*`, `fix/*` |
| `feature/<short-name>` | One new piece of work | You, directly |
| `fix/<short-name>` | A bug fix | You, directly |
| `main` | Legacy starting point. Not used. | Nobody |

**Never commit directly to `production`, `qa`, `development` or `main`.**

## Flow

```bash
git checkout development && git pull
git checkout -b feature/scene-phone-mockup
# ...work...
git add -A && git commit -m "feat(scenes): add phone mockup scene"
git push -u origin feature/scene-phone-mockup
# open a Pull Request: feature/scene-phone-mockup -> development
```

Promotion (when ready): PR `development -> qa`, test it, then PR `qa -> production`.

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org):

```
<type>(<area>): <what changed, in present tense>
```

| Type | Use for |
|---|---|
| `feat` | New feature (a scene type, a format, a command) |
| `fix` | Bug fix |
| `content` | New or edited episode scripts in `content/` |
| `docs` | README / guides |
| `chore` | Config, tooling, dependencies |
| `ci` | GitHub Actions |
| `refactor` | Code change with no behaviour change |

Examples: `feat(studio): add chat scene`, `content(ep02): add COD episode`, `fix(reel): keep text out of Instagram UI area`.

## Content rule

Until something is live, content never points people to a website, sign-up or "link in bio".
The studio enforces this (`rules: no_links` in `brand.yaml`).
