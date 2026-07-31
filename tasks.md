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

### Collapse the PCB checklist to one copy — there are five, not two #ruben

**[2026-07-31] Claimed — another agent session is doing this. Don't start it here.** Left in place
with its findings so the work isn't repeated or lost if that session stops early.

The last of the eight contradictions opened on 2026-07-16 (`history.md` that date); the other seven
were closed on 2026-07-31.

`docs/pcb-checklist.md` in this repo is the live checklist and stays the single source. The item was
filed as "a 4th copy exists in the team Drive". A search on 2026-07-31 found **four checklist copies
plus a backup** in Drive, all owned by `ruben.jimenezmejias@gmail.com`, so this is Rubén's cleanup to
do and not blocked on the `el/` folder's owner after all:

| File | Size | Last modified | Link |
|---|---|---|---|
| `pcb-checklist.md` — the `el/` copy, heading still says "formula 23-24" | 5014 B | 2026-04-12 | [open](https://drive.google.com/file/d/1PHIJccg5II7XtpXAjtRninKK2DPvlvcl/view) |
| `pcb_checklist.md` | 5014 B | 2026-06-05 | [open](https://drive.google.com/file/d/1DhO2Or8D2ThQcZpfv9QldPdRuQ2dkbXw/view) |
| `pcb_checklist.md` | 5016 B | 2024-04-22 | [open](https://drive.google.com/file/d/1T5ezNKGtI7q40F1n8cWXP9NeM1yFvgeN/view) |
| `PCB CHECKLIST.md` | 4519 B | 2023-08-12 | [open](https://drive.google.com/file/d/1iYyxn4AP7VqBQQxLEFsYpG6ef-844gTx/view) |
| `pcb-checklist-md.backup20240202` | 4721 B | 2026-04-12 | [open](https://drive.google.com/file/d/1eXi9UZvN0_YgFEPPhBR3ltjxFK_RWwf_/view) |

**No symlink is needed** — Drive not handling them is not a blocker. Replace each file's entire
contents with the single line

```
https://github.com/UM-Driverless/dv-hardware/blob/main/docs/pcb-checklist.md
```

A file holding a URL is a pointer, not a second copy, and this repo is public so nobody needs a
GitHub account to follow it. Delete the backup outright.

**Manual work, in the Drive web UI.** The Drive integration available to an agent here can read and
create but cannot overwrite or delete, so an agent can find these files and read them but cannot
carry out the edit.

### Buy WAGO 2601 PCB terminal blocks (2-pole + 3-pole)

Stock only **`2601-3102` (2-pole)** and **`2601-3103` (3-pole)** — with {2, 3} you can compose every pole count ≥ 2 (2 and 3 are coprime, so no gaps from 2 upward). 1-pole isn't needed: power runs are always ≥ 2-wire. Per-pin price is flat across pole counts on DigiKey (1-off, 2026-05), so no saving from 4-pole+. Full sourcing rationale + datasheet/Bürklin mirror hashes in `history.md:629`. Standards entry: `~/repos/ruben/docs/writing/standards.md` under Electric > Electric connectors.

## In Progress

_(cross-board work only — per-board work lives on each board's own task list, linked above)_

## Done

_(cross-board work only)_
