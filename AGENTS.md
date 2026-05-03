# dv-hardware

KiCad hardware projects for the U-Motorsport Driverless section (URJC Formula Student). Pairs with [kart_medulla](https://github.com/UM-Driverless/kart_medulla) firmware.

## Layout
```
lib/                 shared symbols, footprints, 3D models (referenced by every project)
projects/<board>/    one folder per board (KiCad project + EasyEDA source archive)
fab/<board>/<rev>/   released Gerbers, BOM, pick-and-place, JLC zip
docs/                cross-board notes
.agents/             agent-readable knowledge base
```

## Conventions
- Naming: kebab-case for repos, folders, and project files (`kart-medulla`, not `kart_medulla` or `KartMedulla`). Matches verbal team usage (`kart-brain`, `kart-medulla`).
- One project folder per board under `projects/`. Board name = folder name = `.kicad_pro` basename.
- EasyEDA source exports archived under `projects/<board>/easyeda-source/` for diff history. Never edit those — they're an audit trail.
- One person per board at a time. Coordinate in chat. KiCad files are text but not line-mergeable — concurrent edits to the same `.kicad_pcb` produce silently broken board files.

## Workflow
1. `git pull --rebase` before starting work.
2. Edit in KiCad 10.0.1+. Don't open files inside `easyeda-source/` — opening an `.epro` makes KiCad drop sibling stub files there (blocked by gitignore but still noise).
3. Validate before fab: `kicad-cli sch erc -o /tmp/x.rpt projects/<board>/<board>.kicad_sch` and `kicad-cli pcb drc -o /tmp/x.rpt projects/<board>/<board>.kicad_pcb`. **Always pass `-o`** — without it, kicad-cli drops reports in CWD.
4. Commit small, commit often.
5. Tag fab releases: `<board>-v<rev>` here, `<board>-v<rev>-fw` on the firmware repo, link both READMEs.

## Knowledge files
- `.agents/history.md` — append-only log: what was tried, what worked, what didn't, gotchas, references. Grep — don't read in full.

## Pairing with firmware
Match-tagged. Hardware rev `medulla-v1.2` here pairs with firmware tag `medulla-v1.2-fw` in `kart_medulla`. Cross-link in both READMEs at release time.
