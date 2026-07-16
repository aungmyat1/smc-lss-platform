# Install / Connect

## Option A - Claude Code repo (recommended for this spec)
1. Copy this folder to your machine, e.g. `~/smc-lss-platform`.
2. `cd ~/smc-lss-platform && git init` (already initialized in the delivered zip).
3. Open in your IDE; Claude Code auto-loads `.claude/skills` and reads `.mcp.json`.
4. Fill DEMO credentials in `.mcp.json`.

## Option B - Cowork
1. Skills: install each `.claude/skills/<name>` via Settings -> Customize.
   (Cowork cannot write to the skills store from a session; import manually.)
2. Connect this folder to Cowork to use the src/, specs/, data/, reports/ files.

## Verify
- `python -m pytest -q` -> structure + config smoke tests pass.
