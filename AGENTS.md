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
