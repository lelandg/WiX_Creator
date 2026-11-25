# Security scanning: SHA-pinned actions and the zizmor pin check

Moved word for word from the "Scanning & review" section of `AGENTS.md` on
2026-11-25; `AGENTS.md` keeps a one-line pointer. This text is as binding as
that file. Read it before editing `.github/workflows/security.yml` or
`.github/dependabot.yml`.

SHA-pinned actions get **no Dependabot alerts**: GitHub generates them only
for actions on semantic versions (docs: "About Dependabot alerts"). So no
security-update PR can ever fire for a pinned action, an
`applies-to: security-updates` group over github-actions is dead config, and
the weekly version update is their only automatic remediation -- which is why
the github-actions block carries no semver-major ignore. DETECTION comes
from the `zizmor` job in `security.yml`: it maps each SHA pin to its
release tag and fails on a known-vulnerable, impostor or unpinned action.
osv-scanner's `github/actions` plugin only lists the pinned actions: with
osv-scanner 2.7.0 it did not flag `tj-actions/changed-files`
(GHSA-mrrh-fwg8-r2c3) at a vulnerable SHA or tag. zizmor looks up a SHA
pin by one tag: for a root action (owner/repo@sha) the longest tag
without a `/`, for a sub-action the longest tag under its path or its
last directory (else the longest of all). The job fails unless that tag, and any tag tied
with it, is a plain release version (v1, v1.2.3): an untagged commit,
a non-version tag or a path-prefixed tag matches no advisory. Pin
released versions.
