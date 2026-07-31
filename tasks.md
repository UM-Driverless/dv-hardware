<!-- read in full — kept under 150 lines -->

# Tasks

The repo's cross-board task board, and the index of every other task board in the repo. Update status as you go: `TODO → In Progress → Done`. Read before editing; claim by adding `[YYYY-MM-DD <name>]` and the section change.

## Task boards

Each board keeps its own task list inside its project folder, so a board folder is self-contained. This
root file is the only index — a task board that isn't linked from here doesn't exist as far as anyone is
concerned. Work that spans boards, or belongs to no board (purchasing, repo conventions, shared library,
fab process), stays on this file.

- [`projects/kart-medulla/tasks.md`](projects/kart-medulla/tasks.md) — the kart-medulla board:
  schematic finish, PCB layout, pre-fab checklist, connector audit, the V2 improvement work. Its
  durable requirements (what the board must do, as opposed to the work) are in
  [`projects/kart-medulla/requirements.md`](projects/kart-medulla/requirements.md).

## TODO

### Resolve contradictions left open on 2026-07-16 — read before trusting any doc below

Opened or found during the tasks.md consolidation (`history.md` 2026-07-16). Each needs a decision from
Rubén. **Until one is closed, the files listed disagree with each other — don't treat either side as
authoritative.** Numbering is kept stable because `history.md` refers to these items by number; the
board-specific ones now live in the kart-medulla task board and are left here as pointers only.

1. **`AGENTS.md` says "Newest entries first" for `history.md`; the file is oldest-first** (entries
   run 2026-05-03 → newest appended at the bottom, which is what global `~/.claude/CLAUDE.md`
   specifies). The instruction is wrong, not the file. Fix the instruction, or reverse the file.
2. **`.agents/tasks.md` no longer exists but is still named** in two `history.md` entries and one
   `.agents/error-log.md` entry. Left deliberately — dated append-only records that were accurate
   when written. Decide whether that's the standing policy for stale paths in logs; if so, write it
   into `AGENTS.md` so nobody "fixes" them later. The 2026-07-31 move described in item 3 leaves more
   of these, so this decision now covers a larger set of files.
3. ~~**Per-board `projects/<board>/tasks.md` vs this root `tasks.md`**~~ **RESOLVED 2026-07-31,
   reversing the 2026-07-16 decision.** The 2026-07-16 call was one `tasks.md` per repo at the root,
   with big clusters in `tasks/<name>.md` linked from it. Two weeks of use showed the split leaked:
   the root board declared itself cross-board-only while carrying four kart-medulla items, one of
   which ("flip CN3 and CN4") duplicated a task already in the board file. Rubén's call 2026-07-31:
   **each board's task list lives in its own project folder** as `projects/<board>/tasks.md`, and this
   root file is the cross-board board plus the index of them. `tasks/kart-medulla.md` →
   `projects/kart-medulla/tasks.md`; the `tasks/` folder is gone.
4. **L7805 linear vs LM2596SX-ADJ buck** — kart-medulla item, see "Contradiction 4" in
   [`projects/kart-medulla/tasks.md`](projects/kart-medulla/tasks.md).
5. **Compressor power path** — kart-medulla item, see "Contradiction 5" in
   [`projects/kart-medulla/tasks.md`](projects/kart-medulla/tasks.md).
6. **PRESSURE_3 repurpose vs the 3× pressure-sensor requirement** — kart-medulla item, see
   "Contradiction 6" in [`projects/kart-medulla/tasks.md`](projects/kart-medulla/tasks.md).
7. **A 4th copy of the PCB checklist lives outside this repo**, in the team Google Drive at
   `formula/formula_24-25-26/el/pcb-checklist.md` — stale (last modified 2024-12-04, heading still
   says "formula 23-24") and now superseded by `docs/pcb-checklist.md`. Not deleted: the `el/` folder
   belongs to the whole electronics section, not just DV, so removing it is not this repo's call.
   Decide whether to delete it or replace its contents with a pointer here.
8. **`medulla-v1` vs `medulla-v2` numbering is an assumption, not a confirmed fact** — kart-medulla
   item, see "Contradiction 8" in
   [`projects/kart-medulla/tasks.md`](projects/kart-medulla/tasks.md).

### Buy WAGO 2601 PCB terminal blocks (2-pole + 3-pole)

Stock only **`2601-3102` (2-pole)** and **`2601-3103` (3-pole)** — with {2, 3} you can compose every pole count ≥ 2 (2 and 3 are coprime, so no gaps from 2 upward). 1-pole isn't needed: power runs are always ≥ 2-wire. Per-pin price is flat across pole counts on DigiKey (1-off, 2026-05), so no saving from 4-pole+. Full sourcing rationale + datasheet/Bürklin mirror hashes in `history.md:629`. Standards entry: `~/repos/ruben/docs/writing/standards.md` under Electric > Electric connectors.

## In Progress

_(cross-board work only — per-board work lives on each board's own task list, linked above)_

## Done

_(cross-board work only)_
