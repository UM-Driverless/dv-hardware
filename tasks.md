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

### 3D-model placement values (re-apply if peers' PCB edits clobber them)

Empirically tuned 2026-05-09 by visual verification in the 3D viewer. Peers editing the PCB may re-import footprints, change footprint properties, or re-link models — which can wipe these per-instance offsets/rotations. After any such peer edit, re-run the values below by either (a) editing `kart-medulla.kicad_pcb` directly via the Python snippet committed in `kart-medulla.kicad_pcb.bak.20260509*` history, or (b) opening Footprint Properties → 3D Models tab on a representative instance and copying the values to siblings.

**Note on sign convention:** KiCad's Footprint Properties dialog displays rotation values with **opposite sign** from what gets written to the .kicad_pcb file. Dialog X=+90 ↔ File X=−90, Dialog Z=−90 ↔ File Z=+90, etc. The values below are documented in **both** forms.

| Component | Footprint name | 3D model | Rotation (file / dialog) | Offset (file = dialog, mm) |
|---|---|---|---|---|
| CN1–CN10 (Phoenix PTSA push-in 3p) | `kart-medulla:CONN-TH_3P-P2.50-S5.00_1990012` | `${KIPRJMOD}/3dmodels/1990012_PTSA_3p_2.5mm.step` | `(xyz -90 0 0)` / dialog `(90, 0, 0)` | `(-0.75, -1.2, 0)` |
| Q3 (IRLZ44N TO-220) | `kart-medulla:TO-220-3_L10.0-W4.5-P2.54-T` | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_THT.3dshapes/TO-220-3_Vertical.step` | `(xyz 0 0 90)` / dialog `(0, 0, -90)` | `(0, 2.54, 0)` |
| U24 (1×22 pin socket, SSW-122-…-S) | `kart-medulla:HDR-TH_ESQ-122-23-G-S` | `${KICAD10_3DMODEL_DIR}/Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x22_P2.54mm_Vertical.step` | `(xyz 0 0 90)` / dialog `(0, 0, -90)` | `(26.6, 0, 0)` |
| U23 (2×22 pin socket, SSW-122-…-D) | `kart-medulla:HDR-TH_ESQ-122-59-G-D` | `${KICAD10_3DMODEL_DIR}/Connector_PinSocket_2.54mm.3dshapes/PinSocket_2x22_P2.54mm_Vertical.step` | `(xyz 0 0 90)` / dialog `(0, 0, -90)` | `(26.6, -1.5, 0)` |

All other footprints with bulk-injected KiCad-bundled .step models (R0603, C0603, SOIC-8/14/16, MSOP-8, SOT-23, TO-252) currently use defaults: `rotate (xyz 0 0 0)`, `offset (xyz 0 0 0)`. **Verify visually** — TO-252 L7805 (U19) DPAK orientation and MSOP-8 SN74LVC3G17 (U5) pin-1 dot are likely candidates if anything still looks off after peer edits.

**Standalone pads** (`standalone_pad_0001..4`) intentionally have no 3D model — they're fiducials/markers.

**Backups:** `kart-medulla.kicad_pcb.bak.20260509` (pre-injection), `…20260509b` (post-CN STEP add), `…20260509c/d/e/f` (rotation/offset iteration snapshots).

### Update PCB silkscreen legend to match new CN assignments

The 21-signal numbered legend at the top of the PCB silkscreen (the block starting `1 GND  2 12V  3 MOTOR_HALL_2_5V ...`) is from the pre-2026-05-08 CN layout and is now stale. Re-author it to match the final CN1–CN10 pin assignments documented in `projects/kart-medulla/docs/pinout-cn-connectors.md`. Defer until other PCB layout work settles — not blocking fab review since the per-CN pinout doc + schematic are the binding documents, but the silkscreen will mislead anyone reading the bare board.

### Add AISLER sponsor logo placeholder to PCB

AISLER does NOT provide a logo file — their fab pipeline auto-detects a placeholder rectangle on silkscreen and substitutes the real logo at manufacture time. Draw the placeholder per their spec:

- **Shape:** rectangle drawn as **4 individual lines** (do NOT use the rectangle tool — recognition fails on grouped shapes)
- **Line width:** 0.08382 mm (3.3 mil) — exact
- **Aspect ratio:** 4:1 long:short
- **Long side:** 30–60 mm (we'll use 30 × 7.5 mm)
- **Layer:** silkscreen. AISLER's doc says "Draw a rectangle placeholder on the desired silkscreen layer" and "Place as many placeholders as you want — each will be replaced with the logo." It does **not** say you have to pick only one side — placing one on F.Silkscreen *and* one on B.Silkscreen is allowed (or at worst the second one stays as a near-invisible 0.08 mm outline). Default plan: place on both.
- **Orientation:** horizontal or vertical
- **Placement:** any free spot, away from mounting holes/connectors

Reference: https://community.aisler.net/t/adding-our-logo-to-your-pcb/5382

### Design the buzzer circuit

Moved to `tasks/kart-medulla.md` → "Wire ASSI/AS-emergency buzzer on the BUZZER GPIO" — has the concrete inventory parts (CPT-407-105-L60 ×5, RE46C100S8F ×10) and the FS-Rules SPL constraint worked out.

### External-connector audit (CN1–CN10) — missing / suspect signals

Audited the 10× green push-in 3-pin connectors against the schematic and pinout doc on 2026-05-08.

**Definitely missing — must be added/decided before fab:**

- **`SDC_ENABLE`** (ESP32 GPIO 39, drives the external SDC enable relay/contactor). Currently only a free-text annotation on the schematic ("SDC_ENABLE — orphan, expected from external module" near U24 pin 14). No wire, no label, no exit on any connector. Decide:
  - Wire GPIO 39 to a label, route to a free pin on an existing 3-pin push-in (CN8 / CN9 / CN10 have free slots if EXP_P* are reshuffled), OR add a CN11.
  - Or: drop `SDC_ENABLE` entirely if the SDC relay is now driven from elsewhere (Orin? external module?). If dropped, also remove the row from `docs/pinout-esp32-s3.md` and the GPIO 39 assignment.

**Verify (probably fine, but confirm with the schematic before fab):**

- **CN4 (I²C bus to AS5600 steering encoder) has no GND.** Pins are SDA / SCL / +3V3. The AS5600 module needs 4 wires (VCC, GND, SCL, SDA). If GND is supplied via a separate cable / chassis return, document it. Cleaner: reshuffle so CN4 carries SDA / SCL / +3V3 / GND on a 4-pin connector, or split power onto a sibling connector and keep CN4 as 3-pin signal-only.
- **`SDC_IN_LOW_SIDE` (on CN5) vs `SDC_NOT_EMERGENCY__3V3` (internal)** — confirm they're the same physical SDC sense signal at different voltage levels with a divider/level-shift in between. If they're separate nets that aren't bridged, the SDC readback path is broken.
- **`MANUAL_THR` passthrough** — the manual throttle path requires `PEDAL_ACC__0_5V` (from CN5) to branch internally to (a) the ESP32 ADC divider and (b) the U14 MAX4660 NC pin. Confirm the schematic actually has both branches connected on the same net (earlier ERC audit suggests yes, but reverify after current PCB-layout work).

**Defer / informational:**

- **`EXP_P1`–`EXP_P7`** (PCF8574 outputs on CN8 / CN9 / CN10) currently have no documented kart-side function. Decide what each will drive (relays, indicators, valves, …) before final cable harness build, and document in `docs/pinout-esp32-s3.md`.
- **External buzzer** — if the buzzer (currently dangling label, see "Design the buzzer circuit" task above) lives off-board, it needs a connector pin. If it's on-board, no connector entry needed.
- **5V power input** — the medulla currently takes +12V on CN6 and (presumably) derives +5V on-board via the LM2596SX-ADJ buck. Confirm the LM2596 instance is actually placed and routed (not just stocked) before fab.

## In Progress

- [2026-05-07] **PCB layout** — peer working on it.

## Done

- LM358 U1B tied back (pin 7→6 follower, pin 5→GND) — replaces NC flags.
- Annotate schematic + ERC cleanup (wire endpoints, isolated single-pin labels, U14 MAX4660 NC pin etype). Schematic clean.
- Status LED decision resolved.
- 2026-05-04 — Schematic ERC: 313 → 32 (0 errors). Major cleanups: extracted EasyEDA-cached symbols into project lib + registered sym-lib-table; set pin electrical types on all chips; added PWR_FLAGs on +3V3/+5V_USB/+12V/GND rails; split LM358DR into proper multi-unit symbol; converted text annotations to real labels; wired ESP32 header pin-pair shorting on U23; renamed CN4 I2C labels (`STEER_SDA__I2C` → `SDA__I2C`, same for SCL — was a real bus-rename orphan that would have left steering sensor unwired); promoted/demoted labels for consistent local-vs-global scope; replaced misnamed `SPARE__3V3` with proper +3V3 power symbol on the connector; documented strap pins (U23 27/28 + U24 8) with NC + text annotation. See `history.md` for the lessons learned (KiCad no_connect semantics, isolated_pin_label false-confidence trap, mid-wire labels vs wire endpoints).

## Notes for the next person

- `~/repos/kart-docs` is the source-of-truth for kart facts (sensor parts, voltage rails, mechanical). Grep there before asking.
- `history.md` has a running log of decisions/gotchas (grep, don't read in full).
- `.agents/error-log.md` has prevention rules from past mistakes — **especially the rule that `no_connect` markers mean "designer chose not to wire, on this board" and not "pin doesn't exist on silicon", and the rule to grep each `isolated_pin_label` before classifying it as "legitimate"**.
- The schematic is on a single sheet (`kart-medulla_P1.kicad_sch`). Hierarchical labels are not used; if you split into multiple sheets later, convert the relevant globals to hierarchical labels and add sheet pins.
