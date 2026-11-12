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

Policy lives in `~/.config/agents/AGENTS.md` -> "Dependency, code, and secret
scanning" and "Model delegation & cross-provider review". It is not restated
here; read it there. What is specific to this repo:

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
- SHA-pinned actions get **no Dependabot alerts**: GitHub generates them only
  for actions on semantic versions (docs: "About Dependabot alerts"). So no
  security-update PR can ever fire for a pinned action, an
  `applies-to: security-updates` group over github-actions is dead config, and
  the weekly version update is their only automatic remediation -- which is why
  the github-actions block carries no semver-major ignore. DETECTION comes
  from the `zizmor` job in `security.yml`: it maps each SHA pin to its
  release tag and fails on a known-vulnerable, impostor or unpinned action.
  osv-scanner's `github/actions` plugin only lists the pinned actions: with
  osv-scanner 2.7.0 it did not flag `tj-actions/changed-files`
  (GHSA-mrrh-fwg8-r2c3) at a vulnerable SHA or tag. A SHA that no tag of
  the action's repository points at would match no advisory, so the zizmor
  job also fails on such a pin: pin released versions.
- Alerts and automatic security **updates** are two switches, not one. Alerts
  only report; the half that opens PRs is `automated-security-fixes`, left OFF
  here deliberately.
- PR reviewers configured for this repo: **Codex** (run locally against the
  committed branch before opening the PR) and **CodeRabbit**
  (`coderabbitai[bot]`). How to read their checks -- which one re-reviews a
  push, why a green check does not mean "no findings", and which label skips
  which bot -- is in the global policy cited above and is deliberately not
  repeated here.
