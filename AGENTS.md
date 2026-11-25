# WiX Creator — agent guide

`wix_creator.py` is a single-file Python 3 CLI. It scans a published application directory and writes a WiX v6 installer project (`.wxs`, `.wixproj`, license `.rtf`). Global house rules apply; this file adds only repo-specific facts.

## Hard rules

- Keep `wix_creator.py` standard-library only. Do not add pip dependencies. Users download the one script and run it.

## Gotchas

- Build the generated installer on native Windows. WiX Toolset v6 and `dotnet build` of a `.wixproj` do not run in WSL.
- Config recall changes prompt behaviour. With no arguments the script loads `last_project.json` and asks to confirm. With a `PUBLISH_DIR` argument and an existing `<ProductName>.json`, the script loads that file and skips all prompts.
- `last_project.json` and `<ProductName>.json` in the repo root are local test state. `.gitignore` excludes them, `Installer/`, and the MSI outputs. Do not commit them.
- `test_publish/` is a tracked fixture for manual runs. Do not delete it.

## Conventions

- Keep the single-file design. New behaviour goes into `wix_creator.py`.
- Component GUIDs come from `uuid.uuid4()` for `.exe` files and `*` (auto) for the rest. Keep that split; per-machine and per-user scope both depend on it.

## Build / test

- Run: `python wix_creator.py [PUBLISH_DIR] [-o OUTPUT_DIR]` (Windows) or `python3 ...` (WSL, generation only).
- Build the installer: `dotnet build ./Installer/<ProductName>.wixproj`, or `wix build -ext WixToolset.UI.wixext -ext WixToolset.Util.wixext ./Installer/<ProductName>.wxs`. Both `-ext` flags are required.
- No test suite and no lint config exist.

## Pointers

- Code map: `Docs/CodeMap.md`
- User docs and WiX install steps: `ReadMe.md`

## Scanning & review

Policy lives in `~/.config/agents/AGENTS.md` -> "Dependencies, advisories, and
scanning" (full text: `~/.claude/instructions/security-scanning.md`) and
"Model delegation & cross-provider review". It is not restated here; read it
there. What is specific to this repo:

- CI runs `gitleaks`, `osv-scanner`, `zizmor` and the two npm jobs on every PR,
  every push to `main`, and weekly (`.github/workflows/security.yml`). The repo
  has no dependency manifests, so osv-scanner reads only the workflows' action
  references and the npm jobs skip with a notice (they run only when a
  `package-lock.json` exists at the repo root). Adding a manifest means adding
  its package ecosystem to `dependabot.yml`; the scan jobs already exist.
- Dependabot: `github-actions` only (`.github/dependabot.yml`), which keeps the
  workflow's pinned action SHAs current. No package ecosystem, because there is
  no dependency manifest to watch. Advisories against the actions themselves
  still need alerts switched on, which a config file does not do.
- SHA-pinned actions get no Dependabot alerts; `zizmor` in `.github/workflows/security.yml` is the detector, so pin released versions (v1, v1.2.3). Detail: `Docs/Security-Scanning.md`.
- Alerts and automatic security **updates** are two switches, not one. Alerts
  only report; the half that opens PRs is `automated-security-fixes`, left OFF
  here deliberately.
- **PR reviewers.** The review council in the global rules applies here; its
  members are whatever `~/.config/agents/council.toml` seats, and the runner
  and commands are in `~/.claude/instructions/model-delegation.md`. This repo
  adds **CodeRabbit** (`coderabbitai[bot]`, config `.coderabbit.yaml`): it
  reviews every non-draft PR automatically and re-reviews every push, skips
  PRs authored by `dependabot[bot]` and `renovate[bot]`, and is skipped by the
  `no-ai-review` label when the label is on the PR at the moment the review
  fires: open the PR already carrying it, or open it as a draft, add the
  label, then mark it ready. A label added after the review has started is
  too late (the label has to exist in the repo first; the `gh label create`
  command is in `.coderabbit.yaml`). The list is additive, not closed: nothing
  named here replaces a council member. A green CodeRabbit check does not mean a review
  ran or that it found nothing: read the check's output title and the inline
  comments. How: the comments in `.coderabbit.yaml` and
  `~/.claude/instructions/pr-review-automation.md`.
