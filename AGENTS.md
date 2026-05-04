# dv-hardware

KiCad hardware projects for the U-Motorsport Driverless section (URJC Formula Student). Pairs with [kart_medulla](https://github.com/UM-Driverless/kart_medulla) firmware.

## Layout
```
lib/                            shared symbols, footprints, 3D models (used by every project)
projects/<board>/               one folder per board
  ├── <board>.kicad_*           KiCad project files
  ├── <board>.pretty/           project-local footprint library
  ├── easyeda-source/           original .epro exports (audit trail, never edit)
  ├── datasheets/               PDFs for chips on this board (subset of vault catalog)
  └── docs/                     board-specific notes (pinout, mechanical, app notes)
fab/<board>/<rev>/              released Gerbers, BOM, pick-and-place, JLC zip
docs/                           cross-board notes (fab process, KiCad setup, library standards)
.agents/                        agent-readable knowledge base
```

## Where things live (the splits that matter)

**Datasheets**
- Vault `~/dv/datasheets/` = master catalog of every chip the team has ever touched. Stays as-is.
- `projects/<board>/datasheets/` = subset actually placed on this board. Copy in when a part is designed onto the PCB. Small duplication is fine; lookup pain isn't. Self-contained `git clone` is the goal.
- Don't symlink `~/dv/datasheets` → repo as a team policy (works on macOS+Drive only, breaks on Linux dev boxes). Personal symlinks are fine, gitignored.

**Docs**
- `dv-hardware/docs/` (shared) = applies to every board: fab vendor process (JLCPCB checklist), naming conventions, KiCad setup/onboarding, library standards.
- `projects/<board>/docs/` (per-board) = pinout, mechanical drawings, design-decision notes, board-revision changelog, app notes specific to this design's use of a part.
- Rule of thumb: *would another board's designer read this?* → shared. *Only meaningful for this PCB?* → project folder.

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
- `.agents/tasks.md` — shared kanban (TODO / In Progress / Done). Read before starting work.
- `.agents/history.md` — append-only log: what was tried, what worked, what didn't, gotchas, references. Grep — don't read in full.
- `.agents/error-log.md` — mistakes made + prevention rules. Grep before working in a related area, especially after a correction.

## Pairing with firmware
Match-tagged. Hardware rev `medulla-v1.2` here pairs with firmware tag `medulla-v1.2-fw` in `kart_medulla`. Cross-link in both READMEs at release time.

## Sister repos — consult before asking the user about kart facts
- `~/repos/kart-docs` — single source of truth for kart-level documentation: sensor part numbers, wiring conventions, voltage rails, mechanical dimensions, vendor links, datasheet pointers. **Look here first** for any "what part is X / what voltage does Y use / how is Z mounted" question instead of asking the user.
- `~/repos/kart_medulla` — firmware paired with this hardware. Pin assignments, I2C addresses, firmware logic.
