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

### Settle the 4th copy of the PCB checklist, in the team Google Drive #ruben

The last of the eight contradictions opened on 2026-07-16 (`history.md` that date); the other seven
were closed on 2026-07-31 — see the `history.md` entry for that day, and the kart-medulla task board
for the four that were board-specific.

`docs/pcb-checklist.md` in this repo is the live checklist. A stale 4th copy sits in the team Google
Drive at `formula/formula_24-25-26/el/pcb-checklist.md` — last modified 2024-12-04, heading still says
"formula 23-24". Rubén wants exactly one copy and no duplicates, and rejected a symlink because Drive
does not handle them.

**No symlink is needed.** Replace that file's whole contents with a single line pointing at
<https://github.com/UM-Driverless/dv-hardware/blob/main/docs/pcb-checklist.md>. The repo is public, so
anyone on the team opens it without a GitHub account, and a one-line file is a pointer rather than a
second copy. Two things to settle before doing it:

1. The `el/` folder belongs to the whole electronics section, not just Driverless, so overwriting a
   file there is not this repo's call to make unilaterally. Rubén: check with whoever owns `el/`.
2. The Claude Drive integration can read and create but **cannot delete or overwrite**, so this is a
   manual edit in the Drive web UI, not something an agent can do.

### Buy WAGO 2601 PCB terminal blocks (2-pole + 3-pole)

Stock only **`2601-3102` (2-pole)** and **`2601-3103` (3-pole)** — with {2, 3} you can compose every pole count ≥ 2 (2 and 3 are coprime, so no gaps from 2 upward). 1-pole isn't needed: power runs are always ≥ 2-wire. Per-pin price is flat across pole counts on DigiKey (1-off, 2026-05), so no saving from 4-pole+. Full sourcing rationale + datasheet/Bürklin mirror hashes in `history.md:629`. Standards entry: `~/repos/ruben/docs/writing/standards.md` under Electric > Electric connectors.

## In Progress

_(cross-board work only — per-board work lives on each board's own task list, linked above)_

## Done

_(cross-board work only)_
