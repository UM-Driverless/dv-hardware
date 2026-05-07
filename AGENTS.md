# dv-hardware

KiCad hardware projects for the U-Motorsport Driverless section (URJC Formula Student). Pairs with [kart-medulla](https://github.com/UM-Driverless/kart-medulla) firmware.

## Layout
```
lib/                            shared symbols, footprints, 3D models (used by every project)
projects/<board>/               one folder per board
  ├── <board>.kicad_*           KiCad project files
  ├── <board>.pretty/           project-local footprint library
  ├── easyeda-source/           original .epro exports (audit trail, never edit)
  ├── datasheets/               PDFs for chips on this board (subset of vault catalog)
  ├── 3dmodels/                 .step files referenced by footprints (${KIPRJMOD}/3dmodels/)
  ├── parts.md                  per-part sourcing (where symbol/footprint/3D came from)
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
- Naming: kebab-case for repos, folders, and project files (`kart-medulla`, not `kart-medulla` or `KartMedulla`). Matches verbal team usage (`kart-brain`, `kart-medulla`).
- One project folder per board under `projects/`. Board name = folder name = `.kicad_pro` basename.
- EasyEDA source exports archived under `projects/<board>/easyeda-source/` for diff history. Never edit those — they're an audit trail.
- One person per board at a time. Coordinate in chat. KiCad files are text but not line-mergeable — concurrent edits to the same `.kicad_pcb` produce silently broken board files.

## Workflow
1. `git pull --rebase` before starting work.
2. Edit in KiCad 10.0.1+. Don't open files inside `easyeda-source/` — opening an `.epro` makes KiCad drop sibling stub files there (blocked by gitignore but still noise).
3. Validate before fab: `kicad-cli sch erc -o /tmp/x.rpt projects/<board>/<board>.kicad_sch` and `kicad-cli pcb drc -o /tmp/x.rpt projects/<board>/<board>.kicad_pcb`. **Always pass `-o`** — without it, kicad-cli drops reports in CWD.
4. Commit small, commit often.
5. Tag fab releases: `<board>-v<rev>` here, `<board>-v<rev>-fw` on the firmware repo, link both READMEs.

## KiCad UI menu names (macOS)

When telling the user where to click, use the actual KiCad menu names, not invented ones:
- **`KiCad → Settings…`** (not "Preferences"). The cross-app dialog is reached via "Settings", not "Preferences", even on macOS where most apps use "Preferences".
- Inside Settings, sections are e.g. **Mouse and Touchpad**, **PCB Editor**, **Schematic Editor**.
- View menu: **Draw Zone Outlines Only**, **Recalculate Ratsnest** — exact names, no paraphrasing.

If unsure of an exact label, say "the menu that does X" and ask the user to find it, rather than inventing a path.

## Editing KiCad files outside KiCad (agents)

When editing `.kicad_sch`, `.kicad_pcb`, or `.kicad_sym` from a script/agent (Edit tool, sed, anything that isn't KiCad itself):

1. **Don't mix kicad-mcp-pro writes with direct file edits in the same session.** The MCP server caches the schematic in memory after `kicad_set_project` and silently flushes its cache to disk on the next MCP write call (`sch_add_no_connect`, sometimes `run_erc` / `sch_reload`), wiping any direct file edits made between MCP calls. Pick one workflow per session — pure-MCP or pure-file-edit. KiCad open in the GUI is actually fine *if you only reload (File → Revert) and never save before the agent commits* — KiCad only writes on explicit save. Check before editing: `pgrep -fl kicad-mcp-pro; pgrep -i 'KiCad' -a`.
2. **`agent_full` MCP profile gaps.** No `sch_delete_label`, no `sch_add_text` — so "replace a label with a text annotation" cannot be done via MCP alone (must direct-edit). Placement tools (`sch_add_no_connect` etc.) default to 2.54 mm grid snap; dev-board header pins on official Espressif DevKitC-1 sit on 1.27 mm offsets (e.g. x=389.89), so pass `snap_to_grid=False` to avoid landing 1.27 mm off the pin.
3. **Run `kicad-cli sch erc -o /tmp/x.rpt …` (or `pcb drc`) immediately after editing** to confirm the file is still valid and the edit had the intended electrical effect.
4. **Commit immediately**, then `git diff HEAD -- <file>` to confirm the working tree matches the commit. If a diff shows up unprompted later, KiCad probably reopened and clobbered — use `git checkout HEAD -- <file>` to restore.
5. **For symbol fixes that affect ERC behavior** (electrical type changes on pins like `passive`/`no_connect`/`power_in`), re-run ERC after the change. A "cosmetic" symbol fix can surface real wiring bugs the broken symbol was masking — investigate any new violations rather than dismissing them.
6. **Two-copy rule for symbols.** Each symbol exists twice: the master in `<project>.kicad_sym` and a snapshot in the schematic's `lib_symbols` block. KiCad renders from the snapshot. When fixing a symbol bug, edit both copies, or fix the master and tell the user to run `Schematic → Tools → Update Symbols from Library`. Verify with `grep -A30 '(symbol "<lib>:<name>"' <board>_<sheet>.kicad_sch` to see the cached version.

## Knowledge files
- `.agents/tasks.md` — shared kanban (TODO / In Progress / Done). Read before starting work.
- `history.md` — append-only log: what was tried, what worked, what didn't, gotchas, references. Grep — don't read in full.
- `.agents/error-log.md` — mistakes made + prevention rules. Grep before working in a related area, especially after a correction.
- `projects/<board>/parts.md` — per-part sourcing (manufacturer URLs, SnapEDA/UltraLib download links, which file is from where, replacement notes). Add an entry whenever a new part is integrated.

## Pairing with firmware
Match-tagged. Hardware rev `medulla-v1.2` here pairs with firmware tag `medulla-v1.2-fw` in `kart-medulla`. Cross-link in both READMEs at release time.

## Sister repos — consult before asking the user about kart facts
- `~/dv/` — **team Google Drive mirror**, the active working knowledge base for the whole DV section. Has its own `AGENTS.md`, `tasks.md`, `onboarding.md`. Authoritative for: pinouts (`~/dv/kart/kart-medulla/pinout-esp32-s3.md`), per-board READMEs/history (`~/dv/kart/<board>/`), datasheet master catalog (`~/dv/datasheets/`), CAN DBCs (`~/dv/can/`), inventory (`~/dv/inventory/`), team/onboarding notes. **PCBs themselves live in this GitHub repo, firmware in the `kart-medulla` repo — but design notes, pinouts, decisions, and reference material live in `~/dv/`.** Grep here first before asking the user any "what pin / what part / what value / what was decided" question.
- `~/repos/kart-docs` — single source of truth for kart-level documentation: sensor part numbers, wiring conventions, voltage rails, mechanical dimensions, vendor links, datasheet pointers. **Look here first** for any "what part is X / what voltage does Y use / how is Z mounted" question instead of asking the user.
- `~/repos/kart-medulla` — firmware paired with this hardware. Pin assignments, I2C addresses, firmware logic.
