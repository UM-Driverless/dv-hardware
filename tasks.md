<!-- read in full — kept under 150 lines -->

# Tasks

The repo's task board — the only one. Update status as you go: `TODO → In Progress → Done`. Read before editing; claim by adding `[YYYY-MM-DD <name>]` and the section change. Big clusters get a `tasks/<name>.md`, always linked from the index below.

## Task files

Big task clusters live in `tasks/`, indexed here. This root board is the only index — a file under
`tasks/` that isn't linked from here doesn't exist as far as anyone is concerned.

- [`tasks/kart-medulla.md`](tasks/kart-medulla.md) — the kart-medulla board: schematic finish, PCB
  layout, buzzer circuit, pre-fab checklist, connector audit. Its durable requirements (what the
  board must do, as opposed to the work) are in `projects/kart-medulla/requirements.md`.

## TODO
flip CN3 and CN4

### Resolve contradictions left open on 2026-07-16 — read before trusting any doc below

Six known contradictions, opened or found during the tasks.md consolidation (`history.md`
2026-07-16). Each needs a decision from Rubén. **Until one is closed, the files listed disagree
with each other — don't treat either side as authoritative.**

1. **`AGENTS.md` says "Newest entries first" for `history.md`; the file is oldest-first** (entries
   run 2026-05-03 → newest appended at the bottom, which is what global `~/.claude/CLAUDE.md`
   specifies). The instruction is wrong, not the file. Fix the instruction, or reverse the file.
2. **`.agents/tasks.md` no longer exists but is still named** in two `history.md` entries and one
   `.agents/error-log.md` entry. Left deliberately — dated append-only records that were accurate
   when written. Decide whether that's the standing policy for stale paths in logs; if so, write it
   into `AGENTS.md` so nobody "fixes" them later.
3. ~~**Per-board `projects/<board>/tasks.md` vs this root `tasks.md`**~~ **RESOLVED 2026-07-16** —
   Rubén's call: exactly one `tasks.md` per repo, at the root, no exceptions; big clusters get a
   `tasks/<name>.md` linked from it. `projects/kart-medulla/tasks.md` → `tasks/kart-medulla.md`.
4. **L7805 linear vs LM2596SX-ADJ buck** — `tasks/kart-medulla.md` specifies an L7805
   (decision 2026-05-02); `projects/kart-medulla/docs/pinout-esp32-s3.md` power architecture shows
   an LM2596SX-ADJ. One is stale.
5. **Compressor power path** — three V2 items assume the board carries motor power; it doesn't
   (`+12V` is a ~1 mA logic feed and the tracks are sized for that). See
   `projects/kart-medulla/requirements.md`.
6. **BUZZER / PRESSURE_3 repurpose items contradict live requirements** (the rules-mandated ASSI
   buzzer; the 3× pressure-sensor requirement). Also in `projects/kart-medulla/requirements.md`.
7. **A 4th copy of the PCB checklist lives outside this repo**, in the team Google Drive at
   `formula/formula_24-25-26/el/pcb-checklist.md` — stale (last modified 2024-12-04, heading still
   says "formula 23-24") and now superseded by `docs/pcb-checklist.md`. Not deleted: the `el/` folder
   belongs to the whole electronics section, not just DV, so removing it is not this repo's call.
   Decide whether to delete it or replace its contents with a pointer here.
8. **`medulla-v1` vs `medulla-v2` numbering is an assumption, not a confirmed fact.** `docs/pcb-checklist.md`
   and the board task list now name the next revision `medulla-v2`, reading "V2 Hardware Improvements"
   as authoritative and treating the assembled EasyEDA-origin board as v1. But `fab/` is empty and the
   only tag is `medulla-v0.1-converted`, so nothing on disk confirms the assembled board is "v1".
   Rubén: confirm the mapping, then put the name on the silkscreen and the title block.

### Buy WAGO 2601 PCB terminal blocks (2-pole + 3-pole)

Stock only **`2601-3102` (2-pole)** and **`2601-3103` (3-pole)** — with {2, 3} you can compose every pole count ≥ 2 (2 and 3 are coprime, so no gaps from 2 upward). 1-pole isn't needed: power runs are always ≥ 2-wire. Per-pin price is flat across pole counts on DigiKey (1-off, 2026-05), so no saving from 4-pole+. Full sourcing rationale + datasheet/Bürklin mirror hashes in `history.md:629`. Standards entry: `~/repos/ruben/docs/writing/standards.md` under Electric > Electric connectors.

## In Progress

_(cross-board work only — kart-medulla items live in `tasks/kart-medulla.md`)_

## Done

_(cross-board work only)_
