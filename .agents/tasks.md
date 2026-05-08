<!-- read in full — kept under 150 lines -->

# Tasks

Shared task board for `kart-medulla` schematic cleanup. Update status as you go: `TODO → In Progress → Done`. Read before editing; claim by adding `[YYYY-MM-DD <name>]` and the section change.

## TODO

### PCB finishing pass (pre-fab)

Remaining PCB work before running DRC and exporting fab files. Order matters — do roughly top-to-bottom:

1. **Round the board outline + reposition mounting holes.** Snap the PCB edge to round mm values (e.g. 100.000 × 80.000, not 99.7 × 80.3). Place the 4 mounting holes at round, symmetric coordinates relative to the outline. Set a 1 mm grid and re-snap before measuring.
2. **Reserve the ESP32-S3 antenna keepout.** The on-module PCB antenna (ceramic chip / trace antenna on the ESP32-S3 WROOM module) needs clear board area underneath and around it: **no copper (no zone fill, no ground pour, no traces) and no metal (no components) within the keepout zone published in the WROOM datasheet — typically ~15 mm of clearance off the antenna end of the module, extending past the board edge if possible**. Add an explicit keepout zone (F.Cu + B.Cu + inner layers, "no copper pour") covering that area so the GND pour in step 3 doesn't fill into it. Also keep the antenna end overhanging the board edge if the module orientation allows.
3. **Create the GND polygon pours and refill.** Add a GND zone on F.Cu and another on B.Cu covering the full board outline (minus the antenna keepout from step 2). Set the zones to net `GND`, set thermal relief on connector pads, refill all zones (`B` in pcbnew). Verify visually that islands aren't isolated and that stitching vias tie top/bottom GND together near high-current paths (motor, 12V input, buck converter).
4. **Add AISLER sponsor logo placeholder** — see "Add AISLER sponsor logo placeholder to PCB" task below for the exact spec (4 individual lines, 0.08382 mm width, 4:1 ratio).
5. **Label signals on silkscreen.** Add silkscreen text next to each external connector pin documenting its net name (`12V`, `GND`, `MOTOR_HALL_1`, `SDA`, `SCL`, `+3V3`, etc.) so the bare board is self-documenting. Coordinate with the existing "Update PCB silkscreen legend" task below — the numbered legend may be redundant once per-pin labels are in place; consider removing it.
6. **Run DRC** (`Inspect → Design Rules Checker` in pcbnew — KiCad calls it DRC for the PCB; ERC is the schematic equivalent and was already run). Fix all errors. Triage warnings (courtyard overlaps, silk-on-pad) — fix or explicitly accept.
   - **Subtask: configure DRC constraints for the chosen fab.** Before running DRC, set the board constraints in `File → Board Setup → Design Rules → Constraints` and `Net Classes` to match the fab's process capability. Even though we'll fab at AISLER, configuring to **JLCPCB's standard 2-layer process** (more conservative) gives a safe baseline that AISLER will also accept. Key values for JLCPCB standard 2-layer 1 oz: min track/clearance 0.127 mm (5 mil) — use 0.2 mm for margin; min via 0.45 mm with 0.2 mm drill; min hole-to-hole 0.5 mm; min annular ring 0.13 mm; silkscreen min width 0.153 mm, min text height 1 mm. Save these into the project's DRC config so the check is meaningful.
7. **Re-verify after DRC fixes.** Refill zones again (DRC fixes may have moved tracks), re-run DRC until 0 errors. Then check: no unconnected nets in the ratsnest, all footprints have 3D models for the render, board edge is closed (no gaps), drill file matches mounting hole sizes.
8. **Export fab package.** Gerbers + drill + pick-and-place + BOM, per AISLER's submission spec. Generate the 3D render / STEP for a final visual check before uploading.

### Update PCB silkscreen legend to match new CN assignments

The 21-signal numbered legend at the top of the PCB silkscreen (the block starting `1 GND  2 12V  3 MOTOR_HALL_2_5V ...`) is from the pre-2026-05-08 CN layout and is now stale. Re-author it to match the final CN1–CN10 pin assignments documented in `projects/kart-medulla/docs/pinout-cn-connectors.md`. Defer until other PCB layout work settles — not blocking fab review since the per-CN pinout doc + schematic are the binding documents, but the silkscreen will mislead anyone reading the bare board.

### Add AISLER sponsor logo placeholder to PCB

AISLER does NOT provide a logo file — their fab pipeline auto-detects a placeholder rectangle on silkscreen and substitutes the real logo at manufacture time. Draw the placeholder per their spec:

- **Shape:** rectangle drawn as **4 individual lines** (do NOT use the rectangle tool — recognition fails on grouped shapes)
- **Line width:** 0.08382 mm (3.3 mil) — exact
- **Aspect ratio:** 4:1 long:short
- **Long side:** 30–60 mm (we'll use 30 × 7.5 mm)
- **Layer:** silkscreen (F.Silkscreen or B.Silkscreen — designer's choice)
- **Orientation:** horizontal or vertical
- **Placement:** any free spot, away from mounting holes/connectors

Reference: https://community.aisler.net/t/adding-our-logo-to-your-pcb/5382

### Design the buzzer circuit

Moved to `projects/kart-medulla/tasks.md` → "Wire ASSI/AS-emergency buzzer on the BUZZER GPIO" — has the concrete inventory parts (CPT-407-105-L60 ×5, RE46C100S8F ×10) and the FS-Rules SPL constraint worked out.

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
