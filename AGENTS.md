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
  ├── requirements.md           what the board must do (durable; outlives the task list)
  ├── tasks.md                  this board's task board (linked from the root tasks.md)
  └── docs/                     board-specific notes (pinout, mechanical, app notes)
tasks.md                        cross-board task board + index of every per-board task board
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
- `dv-hardware/docs/` (shared) = applies to every board: **`pcb-checklist.md`** (the standing bar every revision must clear, plus the `<board>-v<N>` revision-naming rule), fab vendor process (JLCPCB checklist), naming conventions, KiCad setup/onboarding, library standards. Never copy checklist items into a task list — a board's task list carries one task, "pass the checklist for `<board>-vN`", linking it.
- `projects/<board>/docs/` (per-board) = pinout, mechanical drawings, design-decision notes, board-revision changelog, app notes specific to this design's use of a part.
- Rule of thumb: *would another board's designer read this?* → shared. *Only meaningful for this PCB?* → project folder.

## Reporting: separate the decisions from the work

Every report on this board ends with a **`Your call:`** block listing only what genuinely needs a
human decision, each with the context needed to answer it in one line. **Anything not in that block
is the agent's to finish** — do not describe your own next steps in a way that reads like a question.

The failure this prevents, 2026-07-31: a report explained that a PCF8574 output powers up weak-high
and that the existing pulldown "wants checking against the MAX4660's input threshold". That was the
agent's own to-do, but it read as a decision, and Rubén had to ask which it was. A finding stated
without saying who owns it costs a round trip every time.

Rule of thumb for what belongs in `Your call:` — it needs a fact only the human has (what the vehicle
must do, what is in a box at home, what a teammate agreed), or it commits money, an order, or an
irreversible change. Datasheet lookups, arithmetic, threshold checks, netlist verification and
consistency sweeps are never decisions.

## Tooling
- **KiCad 10.0.1+** on macOS. Confirmed — don't ask again or assume an older version. UI labels and menu paths follow KiCad 10 (e.g. Grids live in `KiCad → Settings… → PCB Editor → Grids`, not under the View menu).

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

**See `.agents/kicad-workflow.md` for the full workflow** — the two modes (read-only MCP vs. direct-edit-with-KiCad-closed), tool selection cheat-sheet, and rationale. Default to Mode A (read-only MCP). Run `scripts/guard-kicad-write.sh` before any direct edit.

When editing `.kicad_sch`, `.kicad_pcb`, or `.kicad_sym` from a script/agent (Edit tool, sed, anything that isn't KiCad itself):

1. **Don't mix kicad-mcp-pro writes with direct file edits in the same session.** The MCP server caches the schematic in memory after `kicad_set_project` and silently flushes its cache to disk on the next MCP write call (`sch_add_no_connect`, sometimes `run_erc` / `sch_reload`), wiping any direct file edits made between MCP calls. Pick one workflow per session — pure-MCP or pure-file-edit. KiCad open in the GUI is actually fine *if you only reload (File → Revert) and never save before the agent commits* — KiCad only writes on explicit save. Check before editing: `pgrep -fl kicad-mcp-pro; pgrep -i 'KiCad' -a`.
2. **`agent_full` MCP profile gaps.** No `sch_delete_label`, no `sch_add_text` — so "replace a label with a text annotation" cannot be done via MCP alone (must direct-edit). Placement tools (`sch_add_no_connect` etc.) default to 2.54 mm grid snap; dev-board header pins on official Espressif DevKitC-1 sit on 1.27 mm offsets (e.g. x=389.89), so pass `snap_to_grid=False` to avoid landing 1.27 mm off the pin.
3. **Run `kicad-cli sch erc -o /tmp/x.rpt …` (or `pcb drc`) immediately after editing** to confirm the file is still valid and the edit had the intended electrical effect.
4. **Commit immediately**, then `git diff HEAD -- <file>` to confirm the working tree matches the commit. If a diff shows up unprompted later, KiCad probably reopened and clobbered — use `git checkout HEAD -- <file>` to restore.
5. **For symbol fixes that affect ERC behavior** (electrical type changes on pins like `passive`/`no_connect`/`power_in`), re-run ERC after the change. A "cosmetic" symbol fix can surface real wiring bugs the broken symbol was masking — investigate any new violations rather than dismissing them.
6. **Two-copy rule for symbols.** Each symbol exists twice: the master in `<project>.kicad_sym` and a snapshot in the schematic's `lib_symbols` block. KiCad renders from the snapshot. When fixing a symbol bug, edit both copies, or fix the master and tell the user to run `Schematic → Tools → Update Symbols from Library`. Verify with `grep -A30 '(symbol "<lib>:<name>"' <board>_<sheet>.kicad_sch` to see the cached version.

## Logging empirical findings — do this without being asked

When you discover **non-obvious config values, gotchas, sign conventions, or workflow lessons** through trial and error (e.g. 3D-model offsets/rotations, undocumented KiCad behavior, dialog-vs-file mismatches, footprint-import quirks), log them **automatically**, no prompting needed:

1. **`history.md`** — append a dated section covering: what triggered the work, what was tried (including failed attempts so they're not repeated), what worked, surprising findings, and the **final empirically-validated values in a table**. Append to the end — oldest entry first, newest last. Failed iterations belong here too — they're future-you's most valuable signal.
2. **`tasks.md`** — if the values are *re-applicable config* (e.g. per-component 3D-model offsets that peers' edits could clobber), drop a reference table in a clearly-labeled section ("3D-model placement values", "DRC overrides", etc.) so they can be re-applied as a one-shot. `history.md` is the narrative; `tasks.md` is the cookbook.
3. **`error-log.md`** — if the lesson is "don't do X again", add a one-line prevention rule with a back-link to the history.md entry.

Apply this even mid-task — pause, write the log, continue. The user shouldn't have to remember to ask. If you're unsure whether something qualifies, err on logging it: a duplicated note is cheaper than a re-discovered gotcha.

## Knowledge files
- `tasks.md` (repo root) — the cross-board task board (TODO / In Progress / Done), and the index of every other task board in the repo. Read before starting work. **Each board keeps its own `projects/<board>/tasks.md`** so a board folder is self-contained, and every one of them **must** be linked from the root board — an unlinked task board is invisible. Work spanning boards, or belonging to none (purchasing, repo conventions, shared library, fab process), stays on the root file. There is no `.agents/tasks.md`. Decided 2026-07-31, reversing the 2026-07-16 one-file-per-repo rule, which leaked: the root board declared itself cross-board-only while carrying four kart-medulla items, one of them a duplicate.
- `.agents/kicad10-ui.md` — verified KiCad 10 UI cheat-sheet (menus, panels, hotkeys). Grep before describing any KiCad UI element.
- `.agents/kicad-workflow.md` — the two modes for KiCad work (read-only MCP vs direct-edit), tool cheat-sheet. Read when touching `.kicad_*` files.
- `history.md` — append-only log: what was tried, what worked, what didn't, gotchas, references. Grep — don't read in full. **Dated entries are never edited to match later reality.** A path, filename or decision named in an old entry was accurate on its date; if it later moved or was reversed, the newer entry says so and the old one stays as written. Don't "fix" stale paths in here or in `.agents/error-log.md` — that is what a history is (Rubén, 2026-07-31).
- `.agents/error-log.md` — mistakes made + prevention rules. Grep before working in a related area, especially after a correction.
- `projects/<board>/parts.md` — per-part sourcing (manufacturer URLs, SnapEDA/UltraLib download links, which file is from where, replacement notes). Add an entry whenever a new part is integrated.
- `scripts/guard-kicad-write.sh` — preflight check before any agent-driven edit to KiCad project files. Run it; if it fails, do not write.

## Pairing with firmware
Match-tagged. Hardware rev `kart-medulla-v1.2` here pairs with firmware tag `kart-medulla-v1.2-fw` in `kart-medulla`. Cross-link in both READMEs at release time. A new whole number means the board is no longer a drop-in replacement; a decimal means it is — see `docs/pcb-checklist.md`, "Revision naming".

## Sister repos — consult before asking the user about kart facts
- `~/dv/` — **team Google Drive mirror**, the active working knowledge base for the whole DV section. Has its own `AGENTS.md`, `tasks.md`, `onboarding.md`. Authoritative for: datasheet master catalog (`~/dv/datasheets/`), CAN DBCs (`~/dv/can/`), inventory (`~/dv/inventory/`), team/onboarding notes, cross-system mechanical/pneumatic/brake docs (`~/dv/kart/<subsystem>/`). **Hardware-specific docs (pinouts, board READMEs, per-board history, decision notes) live in this GitHub repo under `projects/<board>/docs/`** so the schematic and its documentation move together; `~/dv/` is for everything that is not tied to a single PCB. Grep `~/dv/` before asking the user any "what part / what value / what does the team standard say" question.
- `~/repos/kart-docs` — single source of truth for kart-level documentation: sensor part numbers, wiring conventions, voltage rails, mechanical dimensions, vendor links, datasheet pointers. **Look here first** for any "what part is X / what voltage does Y use / how is Z mounted" question instead of asking the user.
- `~/repos/kart-medulla` — firmware paired with this hardware. Pin assignments, I2C addresses, firmware logic.
