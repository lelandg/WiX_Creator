@AGENTS.md

# CLAUDE.md — Claude Code specifics

All rules live in `AGENTS.md`. Claude Code only: use the `update-code-map` skill when `Docs/CodeMap.md` is stale (>7 days). The skill has no script another CLI can run; any other CLI reading this file updates `Docs/CodeMap.md` by hand instead.
