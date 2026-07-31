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
6. **PRESSURE_3 repurpose item contradicts a live requirement** (the 3× pressure-sensor
   requirement). Also in `projects/kart-medulla/requirements.md`.
   **The BUZZER half of this item is RESOLVED 2026-07-18** — Rubén: the kart carries no buzzer or
   ASSI, those are formula-vehicle only. So repurposing that net for the compressor conflicts with
   nothing, and GPIO 3 / CN8.2 is the compressor's permanently. The PRESSURE_3 half still stands.
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

### Patch the fabricated board for the CN10.2 brake fix #ruben

Filed 2026-07-31. The design fix landed in `f68cc1f` and is marked DONE under "Fix the
proportional-valve command path" in [`tasks/kart-medulla.md`](tasks/kart-medulla.md) — but the board
that exists was fabbed from `84d6dd0`, one commit earlier, so **the fault is still physically in the
hardware**. Fixing the design does not fix the artifact, and nothing tracked that gap until now.

On the assembled board: CN10.2 sits on the unamplified `CMD_BRAKE__0_5V` node instead of the LM358's
×2 output, so the proportional valve is commanded over 0-5 V where it expects 0-10 V; and the
U13.10 → U1.3 copper (MCP4922 channel B into the amplifier's non-inverting input) is unrouted,
because six of that net's seven segments had been ripped up in KiCad.

Needs a cut-and-jumper on the assembled board, not a respin. Rubén said 2026-07-31 this will be
patched physically while the PCB is fixed. Record what was actually cut and jumpered in the rework
list in [`projects/kart-medulla/README.md`](projects/kart-medulla/README.md) — a patched board no
longer matches the hash printed on it, and that list is the only thing that will say so.

### Buy WAGO 2601 PCB terminal blocks (2-pole + 3-pole)

Stock only **`2601-3102` (2-pole)** and **`2601-3103` (3-pole)** — with {2, 3} you can compose every pole count ≥ 2 (2 and 3 are coprime, so no gaps from 2 upward). 1-pole isn't needed: power runs are always ≥ 2-wire. Per-pin price is flat across pole counts on DigiKey (1-off, 2026-05), so no saving from 4-pole+. Full sourcing rationale + datasheet/Bürklin mirror hashes in `history.md:629`. Standards entry: `~/repos/ruben/docs/writing/standards.md` under Electric > Electric connectors.

## In Progress

_(cross-board work only — kart-medulla items live in `tasks/kart-medulla.md`)_

## Done

_(cross-board work only)_
