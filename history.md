<!-- consult selectively — grep, never read in full -->

# History

Append-only log. Newest first.

## 2026-05-09 — U19 (L7805) PCB-vs-AI-Inventory cross-check

PCB U19 uses footprint `kart-medulla:TO-252-2_L6.6-W6.1-P4.57-LS9.9-BR-CW`, value `L7805CDT_C20611927` (LCSC C20611927) — DPAK / TO-252-2, ST.

Notion AI Inventory (data_source `34a78747-3143-81da-85fb-000b14e5f8d8`) holds three rows for `L7805CDT-TR` (ST, Mouser 511-L7805CDT-TR), qty 10 + 5 + 15 = 30 in the Milwaukee components box. PCB part **matches** stock. Also one row of `LM7805CT/NOPB` (TI, qty 3) — TO-220 through-hole, **not** a footprint substitute.

Two cleanups worth doing in Notion (not yet done):
- All four 7805 rows have an empty `Package` field — should be `TO-252-2` for the STs and `TO-220` for the TI.
- The three ST rows look like schema-merge duplicates (same MPN, same Mouser PN, same location); consider consolidating into one row with qty 30.

## 2026-05-09 — Bulk-injecting 3D models into EasyEDA-imported footprints (kart-medulla)

**Trigger:** kart-medulla PCB had 58 of 59 footprints with no 3D model attached because the EasyEDA import doesn't ship `(model ...)` clauses for cached footprints. 3D viewer was nearly empty.

**Approach that worked:** scripted regex injection of `(model "${KICAD10_3DMODEL_DIR}/<lib>.3dshapes/<name>.step" (offset/scale/rotate ...))` blocks into each `(footprint ...)` block in `kart-medulla.kicad_pcb`, keyed on footprint name. **44 of 58 succeeded** on first pass (R0603, C0603, SOIC-8/14/16W, MSOP-8, SOT-23, TO-220-3, TO-252, PinSocket 1×22 + 2×22). Parens balanced afterward — no syntax damage.

**KiCad 10 env-var name:** `${KICAD10_3DMODEL_DIR}` (verified by grepping a stock `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod`). Earlier KiCad versions used `KICAD9_3DMODEL_DIR`, `KICAD8_3DMODEL_DIR`, etc. — the version number tracks the major release. Default base path on macOS: `/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels/`.

**Phoenix PTSA series not bundled.** KiCad ships `Connector_Phoenix_MC*`, `MSTB`, `GMSTB`, `SPT` 3dshapes — but **not** PTSA. For the 10× CN1–CN10 (`1990012`, PTSA 0,5/3-2,5-Z), downloaded STEP from SnapMagic (snapeda.com/parts/1990012/) and dropped at `projects/kart-medulla/3dmodels/1990012_PTSA_3p_2.5mm.step`. Referenced via `${KIPRJMOD}/3dmodels/...` so the project stays portable.

**Surprising finding — KiCad rotation sign convention differs between dialog and file.** The Footprint Properties → 3D Models dialog displays rotation values with **opposite sign** from what's stored in the .kicad_pcb. Verified empirically:
- File `(rotate (xyz -90 0 0))` → dialog shows `(90, 0, 0)`.
- Setting file to `(xyz 90 0 0)` (matching what dialog showed) flipped all 10 connectors upside down. Reverting to `(xyz -90 0 0)` restored correct upright orientation.
- Same pattern on Z: dialog `(0, 0, -90)` ↔ file `(xyz 0 0 90)`.
- Offsets and scale do **not** sign-flip — those are direct.

**Implication:** when a user reports values from the GUI, negate the rotation entries before writing to the file (or vice versa when reading the file to discuss with the user). Document both forms in any reference table.

**Failed iterations (good to remember so we don't redo them):**
- Asked user to nudge in Footprint Editor — wrong tool. Footprint Editor edits the *library* footprint, not the per-instance model offset. Per-instance offset only lives in pcbnew → click footprint → press `E` (Properties) → 3D Models tab. From the 3D Viewer (Alt+3) you can't edit anything; double-click does nothing.
- Tried inferring connector offset by guessing world-space displacement direction (`-1.41, 1.41, 0` then flipped X to `+1.41, 1.13, 0`). Both wrong, because the model offset is in the model's own (post-rotation, pre-yaw) frame and we don't know SnapEDA's authoring origin a priori. **Lesson: always ask the user to nudge ONE instance in the GUI and report exact numbers — then batch the rest. Don't guess offsets through coordinate-frame algebra; SnapEDA STEPs have arbitrary internal origins.**

**Final empirically-tuned values (verified visually in 3D viewer 2026-05-09):**

| Component | Footprint | 3D model | File rotation | File offset (mm) |
|---|---|---|---|---|
| CN1–CN10 (Phoenix PTSA 3p, 1990012) | `kart-medulla:CONN-TH_3P-P2.50-S5.00_1990012` | `${KIPRJMOD}/3dmodels/1990012_PTSA_3p_2.5mm.step` | `(xyz -90 0 0)` | `(-0.75, -1.2, 0)` |
| Q3 (IRLZ44N TO-220) | `kart-medulla:TO-220-3_L10.0-W4.5-P2.54-T` | `Package_TO_SOT_THT/TO-220-3_Vertical.step` | `(xyz 0 0 90)` | `(0, 2.54, 0)` |
| U24 (1×22 socket) | `kart-medulla:HDR-TH_ESQ-122-23-G-S` | `Connector_PinSocket_2.54mm/PinSocket_1x22_P2.54mm_Vertical.step` | `(xyz 0 0 90)` | `(26.6, 0, 0)` |
| U23 (2×22 socket) | `kart-medulla:HDR-TH_ESQ-122-59-G-D` | `Connector_PinSocket_2.54mm/PinSocket_2x22_P2.54mm_Vertical.step` | `(xyz 0 0 90)` | `(26.6, -1.5, 0)` |

Also re-recorded in `tasks.md` "3D-model placement values" section so peers' PCB edits don't silently regress them.

**Footprint name = body dimensions, not pin pitch alone.** EasyEDA's footprint names encode body L×W (e.g. `SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL`), which doesn't always match KiCad's stock body (`SOIC-8_3.9x4.9mm_P1.27mm`). The 3D model still looks right because pin pitch matches; the body's a few tenths of a mm off but visually fine. Don't waste time hunting for an exact-body-size match unless the visual error is obvious.

**Phoenix Contact 1990012 logged to vault inventory:** `~/vault/inventory/phoenix-contact-1990012-ptsa-0_5-3-2_5-z-3pin-25mm-push-in-terminal-block.md`. Status `Noted`, `units_to_buy: 10`, source Mouser.

## 2026-05-09 — EasyEDA footprint name "9N" includes exposed pad (false alarm on U14)

While auditing 3D-model coverage on kart-medulla, flagged U14 (MAX4660EUA+T) as having a "wrong" footprint: schematic and chip suggest 10 pins (μMAX-10), but EasyEDA-cached footprint `kart-medulla:SOP65P490X110-9N` has 9 pads. Initially diagnosed as a real footprint bug.

**It wasn't.** The footprint is 8 SMD leads + 1 exposed thermal pad (EPAD) underneath. EasyEDA's naming convention treats the EP as a numbered pad — hence "9N" = 8 leads + 1 EP, **not** 9 leads. The schematic agrees: pins 1–8 are real leads (with pin 5 marked NC), pin 9 is `EP` tied to GND. The 3D model rendering "only 8 pins" is correct because that's exactly what the chip looks like; the 9th pad is invisible from above.

**Lesson:** before claiming an EasyEDA footprint name like `<package>-<N>N` is wrong, count the SMD perimeter pads vs the body-center pad. Bottom EPAD doesn't appear in the chip's pin count but does appear in the footprint's pad count — almost universally for thermal-pad packages (DPAK, QFN, μMAX-EP, SOIC-EP). Don't assume `Nn` in the footprint name = chip pin count.

**Time cost:** ~10 minutes of misdirected investigation + a script run trying to re-attach a model that was already attached. Cheap, but worth not repeating on the next thermal-pad part.

## 2026-05-08 (later) — CN cluster reshuffle: U25 moved to right side, all PCF8574-related signals re-clustered

User decided to physically place U25 (PCF8574 GPIO expander) on the right side of the PCB near CN3, and asked to cluster all U25-related signals (I²C bus + expander outputs + reverse) on the right-side CNs to minimize routing length. Six labels swapped (none of the wire/footprint geometry changed; only the net names on the CN-side labels):

  - CN3.1: `CMD_STEER_DIR__3V3` → `EXP_P3`
  - CN4.2: `SDC_IN_LOW_SIDE` → `SDA__I2C`
  - CN4.3: `CMD_STEER__PWM_3V3` → `SCL__I2C`
  - CN8.1: `SDA__I2C` → `SDC_IN_LOW_SIDE`
  - CN8.3: `EXP_P3` → `CMD_STEER_DIR__3V3`
  - CN9.1: `SCL__I2C` → `CMD_STEER__PWM_3V3`

After: CN3 = pure EXP cluster (P1/P2/P3); CN4 = REVERSE_WIRE + SDA + SCL (all U25-facing); displaced ESP32 signals (CMD_STEER_DIR, SDC_IN_LOW_SIDE, CMD_STEER_PWM) land on left-side CNs (CN8/CN9) — their ESP32 GPIOs span both sides of the module, so route length is similar; the AS5600 I²C cable now exits through CN4 closest to U25.

Pre-existing naming inconsistency surfaced during this work: `CMD_STEER__PWM_3V3` uses double-underscore between `STEER` and `PWM` (parses as signal=`CMD_STEER`, level=`PWM_3V3`) while the matching `CMD_STEER_DIR__3V3` uses single underscore between signal-internal words and double before voltage. Should arguably be `CMD_STEER_PWM__3V3`. Not fixed in this pass to avoid net-rename churn before fab; tracked as a future cleanup.

## 2026-05-08 — Stacked-symbol confusion: Reference field vs parent symbol in KiCad GUI

While cleaning up a stray `U02` reference, the user found the symbol via Cmd+F (with hidden-fields search) but couldn't select-and-delete it. Two compounding causes:

1. **Two GND symbols stacked at exactly the same coordinate** `(125.73, 311.15)` — a legacy `kart-medulla:GND` (rotated 270°, with the bogus `Reference: U02`) buried under a standard `power:GND` (rotated 90°). Clicking the GND triangle selects only the top one. Grep for the coordinate (`grep "at <x> <y>" *.kicad_sch`) reveals stacks instantly.
2. **Cmd+F selects the matched property/field, not the parent symbol.** When the match is on a hidden Reference field, the side Properties panel shows `Field` with `Text = U02` and a `Visible` checkbox — that's the reference text, not the symbol. Pressing Delete from there would (try to) delete a reference field, not the symbol. The user's intuition "I thought it was part of the symbol" is right — references *are* parts of symbols — but in the GUI they're a separately-selectable child of the symbol, and selecting the field doesn't promote selection to the parent.

**How to actually delete a buried symbol via its hidden field in KiCad 10:**
- Trick that worked: in the Properties panel, tick **Visible** on the field. The reference text now shows on the canvas, anchored to the parent symbol's origin. You can see *where* the symbol lives (even if its body is overlapped by another symbol's body). Then click the symbol body at that location and Tab-cycle through stacked items, or just delete the now-visible reference's parent.
- Alternative when GUI fights you: close KiCad, surgically delete the symbol block from the .kicad_sch (Mode B per `kicad-workflow.md`).

**Confirmed safe-to-delete signal for stacked GNDs:** if `grep "at <x> <y>"` shows two power symbols + a junction at the same point, deleting one is a no-op for connectivity — the remaining symbol + junction keep the net intact. Verify with `kicad-cli sch erc` after deletion (no new violations at that coordinate).

In this case the deletion landed cleanly on disk: U02 gone, coord-occurrence count at (125.73, 311.15) dropped 9 → 4 (one full symbol's worth of property positions removed), ERC has 0 new violations at that point.

## 2026-05-08 — kart-medulla CN1–CN10 pin assignments locked to ESP32 geometry

User asked: with CN1–CN5 going up the right side of the PCB and CN6–CN10 going down the left side (mirroring the ESP32 module's "chip" pinout convention), what's the best signal-to-CN-pin assignment so jumper wires from each ESP32 pin to its CN pin stay short?

**Result — agreed assignment (CN pin 1 / 2 / 3):**

Right side (bottom→top):
- CN1: GND / +12V_IN / GND  — battery input
- CN2: MOTOR_HALL_3 (5V) / MOTOR_HALL_2 (5V) / +5V  — halls (2 of 3)
- CN3: CMD_STEER_DIR (3V3) / EXP_P1 / EXP_P2
- CN4: REVERSE_WIRE / SDC_IN_LOW_SIDE / CMD_STEER_PWM (3V3) — final, after two corrections during the session: (a) `SDC_NOT_EMERGENCY` removed from CN4.1 (it's an internal ESP32→Q3-gate net, must not be on a CN), and (b) the `MANUAL_THR`/`PEDAL_THR` placeholder I briefly proposed for the freed pin was wrong — the manual-throttle source is the same net as `PEDAL_ACC__0_5V` (CN6.1), branched internally to the MAX4660 NC pin; no second external pedal wire exists. CN4.1 ended up as `REVERSE_WIRE` (the genuinely missing external output that I had clobbered when renaming CN8.1).
- CN5: HYDRAULIC_2 (0–5V) / PRESSURE_3 (0–10V) / GND

Left side (top→bottom):
- CN6: PEDAL_ACC (0–5V) / PEDAL_BRAKE (0–5V) / +3V3
- CN7: PRESSURE_1 (0–10V) / PRESSURE_2 (0–10V) / MOTOR_HALL_1 (5V)
- CN8: SDA (I²C) / BUZZER / EXP_P3
- CN9: SCL (I²C) / HYDRAULIC_1 (0–5V) / EXP_P4
- CN10: CMD_ACC (DAC, 0–5V) / CMD_BRAKE (DAC, 0–5V) / GND

**Rejected: swap MH1 ↔ CMD_STEER_DIR on the ESP32 to cluster all three halls on one side.** Tempting because halls then live on CN2 alone, but GPIO 0 is a strap pin (must be HIGH at boot for normal boot mode). The hall level shifter U5 (SN74LVC3G17) is push-pull, so:
1. A pull-up to 3V3 on the MH1 net can't override U5 actively driving LOW at boot — if the rotor leaves the hall LOW at power-on, ESP32 enters ROM bootloader and the kart won't run until manually rolled and reset.
2. If firmware ever mis-configures the GPIO as output, two push-pull drivers fight, risking damage to U5 or the ESP32 pad.

Keeping CMD_STEER_DIR on GPIO 0 is safe because firmware actively drives it HIGH and the SDC keeps the Cytron disabled at boot regardless. So the swap stays NOT done; MH1 stays on GPIO 16 and rides on the left-side CN7 alongside the pressure sensors. Cable layout is fine because wires terminate in independent Wago slots — per-CN cable grouping doesn't have to match standard sensor pinouts.

**Aside on GPIO 45 / Pin 8:** user spotted "VSPI" on a third-party pinout image and asked if the pin is reclaimable. The label is misleading — on ESP32-S3 it's the **VDD_SPI voltage select strap** (not the classic ESP32 "VSPI" peripheral). Internal pulldown at boot selects 3.3V flash (correct for our N8R2). The pin is usable as a regular GPIO after boot, provided nothing externally pulls it HIGH at boot. Same rule applies to GPIO 46 (Pin 36). Both still listed as RESERVED in `pinout-esp32-s3.md` out of caution; can be promoted to SPARE-usable if a future need arises. Not needed for this assignment.

## 2026-05-08 — Open question: tasks.md is getting long for human peers, three options on the table

**Problem:** `.agents/tasks.md` was written agent-first per `AGENTS.md` ("shared kanban for agents to read and update"). Long-form rationale per task is good for AI continuity but bad for human peers skimming the file. User flagged this and asked for alternatives. No decision yet — leaving the file as-is until we pick.

**Options considered:**

1. **Folder-per-task (`.agents/tasks/<slug>.md`, with `tasks.md` as a one-line-per-task index).** Best fit if individual tasks start growing real discussion threads — each gets its own git history, can be assigned by filename prefix, and humans only see the index. Cost: a tiny bit of indirection for agents (extra file open per task).
2. **GitHub Issues for humans, lean `tasks.md` for agents.** If the team is already on GitHub, peers look at issues anyway. `tasks.md` becomes a short list of refs (`#42 — SDC_ENABLE wiring`). Cost: requires the project to be on GitHub with issues enabled, and adds a sync responsibility (close-issue ↔ move-to-Done).
3. **Just compress.** Keep one file, each entry becomes one short line ("SDC_ENABLE missing — wire GPIO 39 to a connector, see history.md 2026-05-08"). Rationale lives in `history.md` (which is what `history.md` was designed for). Cheapest to do, matches the existing "history.md as the explainer, tasks.md as the to-do" split.

**My recommendation if/when this is picked up:** option 3 first (one-pass cleanup, no structural change). Move to option 1 later if individual tasks start sprouting discussion. Option 2 only if the team is already living in GitHub Issues.

## 2026-05-08 — Source-of-truth flip + design clarifications (manual/auto mux, connector audit)

This session resolved several long-standing inconsistencies between the schematic, the pinout doc that lived in `~/dv/`, and what was actually built. Documenting the decisions here so we don't keep re-deriving them.

### Source of truth: dv-hardware (this repo) is canonical for chips and wiring

User's framing: "this is the pcb, can't be wrong." The schematic IS the physical artifact — derived docs can drift, the schematic cannot. So:

- `dv-hardware/projects/<board>/` is canonical for chip choices, nets, header pin assignments, decoupling, footprints. Anything that asks "what is on the board" → look at `kart-medulla.kicad_sch`.
- `~/dv/kart/<board>/` and `~/repos/kart-medulla` (firmware) defer. They carry firmware-specific overlays only: GPIO mode flags (open-drain etc.), idle-at-boot constraints, ISR notes, driver config.
- The pinout doc was moved from `~/dv/kart/kart-medulla/pinout-esp32-s3.md` to `dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md`. The `~/dv/` copy is now a 7-line tombstone pointing here.
- Don't write "this repo is the source of truth" inside the source-of-truth repo itself — that's circular. The pointer goes in the deferring repo. (User caught me trying to do this in `dv-hardware/AGENTS.md`; reverted.)

**Why this matters going forward:** disagreements between the schematic and any doc → fix the doc, not the schematic. PCB layout is in progress, so pin assignments will keep shifting; the doc has a header note saying re-verify before each fab release.

### Brake mux dropped — one MAX4660 is enough

Original 2026-05-01 design had two MAX4660s muxing throttle and brake separately between manual and autonomous modes. User clarified 2026-05-08: brake doesn't need autonomous-vs-manual muxing because manual mode doesn't route brake through the ESP32 at all (the manual brake is mechanical/hydraulic, not electrical). So:

- U14 MAX4660 (throttle) — kept.
- U17 MAX4660 (brake) — was never placed on the schematic. Don't add it. The brake autonomous command (`CMD_BRAKE__0_10V` on CN5) goes directly from the MCP4922 (via the 0–5 V → 0–10 V op-amp gain stage) to the brake valve driver, no switch.
- `SELECT_THROTTLE` (ESP32 GPIO 15) drives U14 SELECT only. The "drives both MAX4660 SELECT pins" wording in the old doc is wrong and has been fixed.

### CMD_REVERSE moved off ESP32 GPIO onto PCF8574 P0 (decision was 2026-05-03, but the pinout doc was still claiming the old design)

Original 2026-05-02 plan: ESP32 GPIO 36 in `OUTPUT_OPEN_DRAIN` mode, wired in parallel with the manual reverse button (wired-OR through the motor controller's existing 5 V pull-up). 2026-05-03 it moved onto U25 PCF8574T port P0 (pin 4) instead. Reasons:

- Frees GPIO 36, which was the only N8R2-only-safe GPIO assignment we had — design is now fully N8R8-compatible (no signal depends on the quad-PSRAM-only GPIOs 33–37).
- PCF8574 quasi-bidirectional outputs are natively open-drain with weak internal pull-ups, so the wired-OR architecture works the same way without needing an `OUTPUT_OPEN_DRAIN` flag in firmware.
- Firmware change: `CMD_REVERSE` is now an I²C write to the PCF8574 output register (writing 0 pulls REVERSE_WIRE LOW, writing 1 releases it to high-Z). No special pin-mode config.

**Fail-safe property preserved:** ESP32 dead or I²C bus down → P0 stays in its power-on-default state (all outputs high = high-Z) → only the manual button controls the line. Identical behavior to manual-only operation.

### Schematic-vs-doc discrepancies on the ESP32 header (7 pins)

The pinout doc still said these pins were active when the schematic actually has NC markers. All fixed in `docs/pinout-esp32-s3.md`:

| Pin | GPIO | Doc said | Schematic shows | Reason it's NC |
|---|---|---|---|---|
| 3 | 19 | USB_D- (USB-OTG to Orin) | NC | No USB-C connector on the medulla PCB this rev |
| 4 | 20 | USB_D+ | NC | Same |
| 7 | 48 | LED (status RGB) | NC | Using the dev-module's onboard LED, not an external one |
| 20 | 44 | RX0 (UART0) | NC | Dev-board's onboard USB-UART bridge already owns GPIO 43/44 |
| 21 | 43 | TX0 (UART0) | NC | Same |
| 32 | 17 | TX1 (UART1) | NC / SPARE | UART1 unused — the only UART link off-board uses UART0 via dev-module USB-C |
| 33 | 18 | RX1 (UART1) | NC / SPARE | Same |

Lesson: when a pinout doc lives in a different repo from the schematic, it drifts. With the source-of-truth flip + the doc now next to the schematic, this should stay aligned.

### SELECT_THROTTLE wiring traced clean (no action needed, just for the record)

User asked to confirm `SELECT_THROTTLE` is correctly wired. It is:

- U23 (LEFT_HEADER, SSW-122-01-T-D dual-row) symbol pins 15 & 16 (paired = LEFT_HEADER row 8 = physical Pin 30 = silkscreen `15` = ESP32 GPIO 15) → wire (313.69, 63.5)–(370.84, 63.5) → label `SELECT_THROTTLE`.
- U14 MAX4660 pin 6 (IN, the SELECT input) at (405.13, 219.71) → wire (405.13, 219.71)–(410.21, 219.71) → label `SELECT_THROTTLE`.
- R32 = 10 kΩ at (410.21, 224.79) on the same node → matches the spec'd hardware-default-manual pulldown.
- Both labels are local on a single sheet, so they form one net by name. ERC: 0 violations.

Earlier `mcp__kicad__sch_trace_net` reported "labels=2 pins=0" — that's misleading; it doesn't count pins reached via wire+label, only direct pin-to-name matches. Don't use it as a "no pins on this net" indicator.

### External-connector audit (CN1–CN10) — captured in tasks.md

Crossed every signal on the 10× green push-in connectors (CN1–CN10) against the schematic netlist. One signal definitely missing from the connectors: **`SDC_ENABLE`** (GPIO 39 — meant to drive the external SDC enable relay). The schematic only has a free-text annotation "SDC_ENABLE — orphan, expected from external module" near U24 pin 14; no actual label, no wire, no connector exit. Action item logged in `.agents/tasks.md` under "External-connector audit".

Also flagged for verification (not necessarily wrong, just worth confirming before fab): CN4 has no GND for the AS5600 (3 pins: SDA/SCL/+3V3 only); `SDC_IN_LOW_SIDE` (CN5) vs `SDC_NOT_EMERGENCY__3V3` (internal) need to be confirmed as bridged via a divider; the manual-throttle passthrough relies on `PEDAL_ACC__0_5V` branching internally to both the ADC divider and U14 NC pin.

## 2026-05-07 — Investigated KiCad-AI workflow problems; added workflow doc + guard; tested kicad-sch-api

**Trigger:** Recurring failures in error log (MCP cache clobbering edits, KiCad GUI auto-saving over agent commits, hand-rolled netlist parsers, screenshots-instead-of-MCP loops). User asked for a real fix.

**Root structural finding:** KiCad has no official IPC API for the **schematic editor** as of KiCad 10. PCB has `kicad-python` (works with running KiCad), schematic does not. Every schematic-editing MCP server (kicad-mcp-pro, Seeed-Studio, lamaalrajih, circuit-synth) is doing raw S-expression manipulation. That is the source of all our caching/conflict pain — these are not bugs in any one server, they're a structural limit until KiCad ships schematic IPC (KiCad 11+).

Seeed-Studio docs put it explicitly: *"KiCad must be closed and reopened to see file changes (no hot-reload). Use KiCad GUI for design work. Use this MCP server for analysis, validation, and code generation."* Adopted as our default.

**What was added:**
- `kicad-workflow.md` — codifies two modes: (A) read-only MCP, KiCad GUI may be open, default 90% of the time; (B) direct-edit, KiCad closed, no MCP writes that session. With tool-selection cheat-sheet.
- `scripts/guard-kicad-write.sh` — `pgrep -i kicad` and `pgrep -fl kicad-mcp-pro` preflight. Exits non-zero if unsafe. Dry-run confirmed.
- AGENTS.md "Editing KiCad files outside KiCad" updated with pointer to the workflow doc.

**kicad-sch-api evaluation (`circuit-synth/kicad-sch-api` v0.5.6):**
- **Read works.** `load_schematic('kart-medulla_P1.kicad_sch')` → 105 components, 141 wires, parses cleanly. Useful as a Python read API.
- **Write does NOT preserve format.** Round-trip test (`/tmp/kicad-sch-api-test/roundtrip.py`) produced large diff: drops `(thickness 0.1524)` from text effects, reorders properties, fills empty `Description ""` fields with library text, etc. Despite claims of "exact format preservation".
- **Reference validator is wrong.** Rejects KiCad-valid power-flag references containing `+` and `_` (`#FLG_+12V01`, `#FLG_+5V_USB01`, `#FLG_+3V3`) as "Invalid reference format". Need to call internal `_file_io_manager.save_schematic(sch._data, path)` to bypass — but the format-preservation issue is separate and worse.
- **Verdict: skip the library entirely.** Writes are broken (format reformat + buggy validator). Reads work, but reads are already covered by `kicad-mcp-pro` (`sch_get_symbols`, `sch_trace_net`, `sch_get_connectivity_graph`, `run_erc`, `export_netlist`) and `kicad-cli sch export netlist` — both already in our toolbox, neither has the MCP-write cache problem since we'd only call read tools. `kicad-sch-api` adds zero value to us. Edit-tool surgical regex remains the only direct-write path (preserves format exactly when changes are tiny). Re-evaluate when KiCad 11 ships schematic IPC.

**PCB side, when we get there:** use `kicad-python` (the official KiCad IPC API). Works with running KiCad GUI, no cache war. Enable in `KiCad → Settings… → Plugins → API server`. https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/

## 2026-05-07 — Parallel work on a single KiCad PCB: not really viable

Question: can two+ people work on different regions of the same `.kicad_pcb` in parallel without merge conflicts?

**Short answer: no, not on a shared `.kicad_pcb`.** Reasons:
- `.kicad_pcb` is one monolithic S-expression file. Footprints, tracks, vias, zones are flat lists.
- KiCad's save serialization is **not order-deterministic** between sessions, so even non-overlapping spatial edits can produce diff hunks git can't auto-merge cleanly.
- Global state (net classes, design rules, stackup, board outline) is shared — any edit there forces a manual merge.

**What works:**
- **Schematic ↔ PCB split** (different files). What we're doing now — Rubén on schematic + docs, peer on PCB. Trivially parallel.
- **Multi-board projects** — split logically into separate KiCad projects (e.g. main board + sensor adapter). Each is its own file set.
- **Time-sliced single-writer** via the `tasks.md` claim pattern. Boring but reliable.

**What sort-of works:** spatial division + serialized merges (A: top quadrant, B: bottom). Second person rebases and copies changes manually. Painful at >2 people.

**What doesn't exist in stock KiCad:** real-time multi-user editing or per-region locking. (Altium 365 / OrCAD X have it; KiCad doesn't.)

**Recommendation for this team:** keep the schematic/PCB split. Third person → give them a separate sub-board as its own project, not a chunk of medulla.

## 2026-05-07 — Git workflow: rebase-on-pull when both sides made identical changes to the same file

Situation: peer pushed commit `d0f64d1 "pcb update"` (touched `.kicad_pcb` + 1 line of `.kicad_pro`). Local had uncommitted edits including the **same 1-line change** to `.kicad_pro` (KiCad GUI clears `used_designators` automatically) plus schematic + agent-doc edits.

**Resolution path that worked cleanly:**
1. Commit local work first (split into logical commits) — gives a checkpoint to return to if anything goes wrong.
2. `git pull --rebase` — replays local commits on top of peer's. Identical `.kicad_pro` change auto-resolved with no prompt.
3. Push.

**Why `--rebase` over plain `git pull`:** plain pull creates a merge commit for trivial 1-commit divergences (noisy). Rebase produces linear history `peer → you`. Local commits get new SHAs (parent changed) — safe because they weren't pushed yet. Never rebase already-pushed commits.

**Recovery levers if rebase goes wrong:** `git rebase --abort`, `git reflog` + `git reset --hard <sha>`. Commits are nearly impossible to lose once made.

## 2026-05-07 — Decision: stay on KiCad long-term (vs EasyEDA)

Revisited tool choice after MCP-related friction. Decision: **KiCad**, long-term.

Reasoning:
- Open format, local files, git-tracked — work is owned, not hosted on a vendor's servers.
- No vendor lock-in; portable across fabs (not tied to JLCPCB pipeline).
- Scriptable; MCP tooling is improving and recent ERC issues were all resolved within KiCad.
- EasyEDA is fine for quick JLC-bound boards but wrong foundation for hardware meant to live for years.

## 2026-05-07 — KiCad ERC: "Input pin not driven" on GND net (kart-medulla GPIO expander U25 A0)

### Problem
ERC error: `Symbol U25 Pin 1 [A0, Input, Line] — Input pin not driven by any Output pins`. A0 of the PCF8574T (I2C address pin) was tied to GND for address 0, but ERC kept failing. Took many iterations to diagnose because of multiple overlapping KiCad concepts that all *look* the same to a human.

### Root causes (compound)
1. The "GND" on A0 was a **global label** (the arrow shape, `Ctrl+L`), not a **GND power symbol** (the triangle, `P`). They share the name "GND" but live on **separate nets**. ERC does not auto-merge them.
2. Even after using the correct GND **power symbol**, ERC still complained because the **GND power symbol's pin is type Power Input**, not Power Output. A net with only Power Input pins has no driver → ERC error.
3. Fix for #2 is **PWR_FLAG** — a special symbol whose pin is type Power Output, exists exclusively to tell ERC "this rail is actually driven." Need exactly **one** PWR_FLAG per power net **across the entire design** (one for GND, one for +3V3, etc.). Two PWR_FLAGs on the same net = "Power output and Power output connected" error.

### Key facts to never re-derive
- **Global label "GND" ≠ GND power net.** Labels are just net names. Power symbols carry power-net semantics.
- **Power symbols all named "GND"** (the triangles) **share one global net** across all sheets, regardless of where placed. So one PWR_FLAG drives every GND triangle in the project.
- **Global Label "Shape" property** (Input/Output/Bidirectional/Tri-state/Passive) is **purely cosmetic** — only changes the arrow shape. Does not affect ERC electrical type. ERC drive checks look at *symbol pin types* and PWR_FLAG, never at label shapes.
- **Pin types that DRIVE a net for ERC purposes:** Power Output, Output, PWR_FLAG. Power Input does not drive (this is why GND/+3V3 power symbols alone don't satisfy ERC).
- KiCad shortcuts: `L` = local label (sheet-scoped), `H` = hierarchical label, `Ctrl+L` = global label (the arrow), `P` = power symbol (the triangles, GND/+3V3/etc.).

### Recipe to make a power net pass ERC
1. Place GND power symbol (`P` → GND) on every GND-bound wire. Make sure the pin tip lands on the wire endpoint with a green junction dot.
2. Place exactly **one** PWR_FLAG (`P` → PWR_FLAG) somewhere on the GND net. Conceptually next to the actual power source (e.g., ESP32's GND pin) is fine, but electrically it doesn't matter.
3. Repeat (#2 only) for +3V3, +5V, etc.

### Confusion to avoid next time
- Do not suggest "the wire is floating" or "no junction" without verifying — the user can see the schematic and that gaslights them. The error is almost always a **net semantics** issue (label vs. power symbol vs. missing PWR_FLAG), not a literal disconnection.
- Trust the user when they say "I already placed the power symbol" — verify by checking PWR_FLAG count and pin-to-wire snap, not by re-explaining the difference between symbols.
- The KiCad GND power symbol can appear rotated (pointing left, right, down) — it is still the same symbol. Don't mistake a rotated GND triangle for an arrow-shaped global label.

### Resolution
User fixed it by placing **three separate GND power symbols, one per pin (A0, A1, A2)**, instead of wiring all three pins together to a single shared GND symbol. ERC then passed (0 violations).

### Why three-symbols-works when one-symbol-wired-to-all-three didn't (NOT FULLY EXPLAINED)
Electrically these should be identical: all three pins on the global GND net via the PWR_FLAG elsewhere. Power symbols with the same name (`GND`) merge into one global net regardless of how many copies are placed. **No confirmed root cause** for why the single-symbol version failed ERC on A0 specifically.

Most likely candidate (unverified): a hidden wire-connectivity issue where A0's pin or one wire segment was off-grid / not actually joined to the rest. ERC's "Input pin not driven" fires when a net has only Input-type pins and no driver — *including* the case where the "net" is just one pin with nothing else on it (a one-node net counts as undriven). That would explain why A0 alone failed while A1/A2 passed. But the user did not visually confirm a misalignment, so this remains a hypothesis.

### Lesson for future ERC drive errors
If ERC says "Input not driven" on **one specific pin** when adjacent pins on what looks like the same wire are fine: try dropping a power symbol directly on the offending pin (bypass the wire). If that fixes ERC, the wire connectivity was the issue. If not, there's something else going on — inspect the .kicad_sch file via MCP rather than guessing.

### Final final
- One PWR_FLAG per power net across the whole design (not per sheet, not per symbol). On disk this project has `#FLG01` (GND), `#FLG_+3V3`, `#FLG_+5V_USB01`, `#FLG_+12V01`. Don't add more.
- The kicad MCP (`mcp__kicad__run_erc`, `grep PWR_FLAG <sch>`) reads disk and is far faster than iterating from screenshots.

## 2026-05-07 — Idea: agent works in a separate git worktree so user can keep KiCad open

**Problem context:** Twice today the agent's edits to `kart-medulla_P1.kicad_sch` were silently clobbered — once by KiCad's stale-buffer save, once by interleaving direct file edits with kicad-mcp-pro writes. Root cause is that the agent and the user's KiCad are racing for the same on-disk file.

**Idea (not yet implemented; user said note it, don't set up):** add a sibling worktree just for agent work.

```
~/repos/dv-hardware/         user's main worktree, KiCad stays open
~/repos/dv-hardware-agent/   agent's worktree, on branch agent/<topic>
```

Setup is `git worktree add ../dv-hardware-agent agent-work`. Agent points the MCP at the worktree's project path with `kicad_set_project /Users/rubenayla/repos/dv-hardware-agent/projects/<board>` and edits there. KiCad's `${KIPRJMOD}` resolves relative to the worktree's `.kicad_pro`, so symbol libs (`*.kicad_sym`), footprint pretties (`*.pretty/*.kicad_mod`), and 3D models (`3dmodels/*.step`) all work without re-pathing. Agent commits + pushes on its branch; user pulls into their worktree when ready and runs `File → Revert` in KiCad to pick up the changes.

**Trade-offs to remember if/when this gets set up:**
- KiCad files are text but not line-mergeable. Concurrent edits to the *same* `.kicad_sch` or `.kicad_pcb` in both worktrees → ugly manual merge (KiCad re-formats huge sections on save, so even small logical changes can collide on hundreds of lines). Coordinate by topic — agent on one feature branch per task, user avoids touching the same file.
- The MCP is a single process. `kicad_set_project` per session is enough; no reconfig of the MCP itself.
- Could be wrapped in `~/.claude/skills/dv-worktree/SKILL.md` so the agent can spin one up on demand.

## 2026-05-07 — kicad-mcp-pro installed; pins 20/21 (UART0 TX0/RX0) NC'd on kart-medulla

**Tooling change:**
- `kicad-cli` symlinked to `/opt/homebrew/bin/kicad-cli` (was buried inside `/Applications/KiCad/KiCad.app/Contents/MacOS/`). Reports KiCad 10.0.1.
- `kicad-mcp-pro` v3.1.8 installed via `pipx --python /opt/homebrew/bin/python3.14` (the package needs Python ≥3.12; the user's default `python3` is 3.11 from a platformio venv). Registered in Claude Code at user scope: `claude mcp add kicad -s user -- /Users/rubenayla/.local/bin/kicad-mcp-pro --transport stdio --profile agent_full`. MIT-licensed despite the "Pro" name. Other contenders considered: `lamaalrajih/kicad-mcp` (lighter, KiCad 7+), `Seeed-Studio/kicad-mcp-server` (39 tools, targets KiCad 9), `mixelpixx/KiCAD-MCP-Server`. Picked the Pro one because it's the only one that explicitly supports KiCad 10.

**Design change applied:**
- Header pins 20/21 of the ESP32-S3-DevKitC-1 footprint on `kart-medulla_P1.kicad_sch` are GPIO 44/43 = RX0/TX0 = UART0. Previously rendered as global labels `TX0` / `RX0` with single-pin wires going nowhere. Confirmed via grep that nothing on the medulla PCB or in `~/dv/kart/kart-medulla` firmware references these nets. They are nonetheless reserved by the dev board's on-board CP210x USB-UART bridge (which physically drives those module pins whenever the UART USB-C is plugged in) — so they must not be reassigned on the medulla side either. Fix: removed the global labels + their wires, added `(no_connect)` markers at the pin endpoints (389.89, 48.26 / 50.8), and added `(text)` annotations explaining the reservation. Commit `b07c56f`.

**Gotchas hit (now also rules in AGENTS.md):**
- **kicad-mcp-pro caches the schematic in memory** between calls. After `kicad_set_project`, the next MCP write call (`sch_add_no_connect`, etc.) flushes the cached copy to disk, silently overwriting any direct-file edits made between MCP calls. Symptom: `git status` shows zero changes after multiple "successful" Edit calls. Fix: pick one workflow per session — pure-MCP or pure-file-edit, never interleave. KiCad open in the GUI is *fine* if you only reload (File → Revert) and never save before the agent commits; KiCad itself only writes on explicit save.
- **`agent_full` MCP profile** is missing `sch_delete_label` and `sch_add_text`. So "replace a global label with a text annotation" must be done by direct file edit. Filed mentally as a feature gap.
- **`sch_add_no_connect` snaps to 2.54 mm by default.** Header pins on the official ESP32-S3-DevKitC-1 sit on 1.27 mm offsets (x=389.89). Marker landed 1.27 mm off; fix: pass `snap_to_grid=False`.

## 2026-05-07 — MAX4660 (U14) integration: SnapEDA footprint+3D adopted, hidden wire-disconnect bug found and fixed

**Symbol correctness summary (the part that confused things):**
- SnapEDA-downloaded symbol (`MAX4660EUA_T.kicad_sym` from the zip): **correct**.
- Project library symbol (entry inside `projects/kart-medulla/kart-medulla.kicad_sym`): **also already correct** (pin 2 = passive, pin 5 = no_connect).
- Cached copy inside the schematic file (`lib_symbols` block in `kart-medulla_P1.kicad_sch`): **wrong** — pin 2 = no_connect (a stale snapshot from an earlier broken symbol version).

KiCad renders symbols from the schematic's cached copy, not the library — so the symbol editor showed the broken cache, even though the library was fine. Running `Tools → Update Symbols from Library` would have fixed it. **SnapEDA was not needed to fix the symbol** — the library already had the right one. SnapEDA's actual contribution to this integration was the verified **footprint** (`SOP65P490X110-9N.kicad_mod`) and **3D model** (`MAX4660EUA_T.step`), plus confirmation that the existing pin map was correct.

After confirming the original symbol's pin numbers were correct (matched SnapEDA), did a full SnapEDA integration for U14 (MAX4660 throttle mux). Workflow:

1. User downloaded `MAX4660EUA_T.zip` from SnapEDA without needing an account (so the SnapEDA login wall reported earlier wasn't actually blocking — should have tried first).
2. Extracted: symbol `MAX4660EUA_T.kicad_sym`, footprint `SOP65P490X110-9N.kicad_mod`, 3D model `MAX4660EUA_T.step`.
3. Copied footprint into `projects/kart-medulla/kart-medulla.pretty/`.
4. Created `projects/kart-medulla/3dmodels/` and put `MAX4660EUA_T.step` there. (First 3D model in the project — no prior convention; chose `${KIPRJMOD}/3dmodels/` as the standard location.)
5. Added `(model "${KIPRJMOD}/3dmodels/MAX4660EUA_T.step" ...)` to the new footprint.
6. Updated `kart-medulla.kicad_sym` U14 symbol's default Footprint property → `kart-medulla:SOP65P490X110-9N`, Datasheet → analog.com.
7. Updated U14 instance in `kart-medulla_P1.kicad_sch` (Footprint + Datasheet override).
8. **Critical fix:** the cached `lib_symbols` copy of `MAX4660EUA_T` in `kart-medulla_P1.kicad_sch` had pin 2 (NC) marked as electrical type `no_connect` — wrong; the library copy in `kart-medulla.kicad_sym` correctly had `passive`. The cache had drifted from the library, and KiCad uses the cache, so the schematic editor was rendering pin 2 with the no-connect-X marker. Patched the cache to `passive`.
9. **Real bug uncovered:** with pin 2 fixed, ERC immediately fired `pin_not_connected` on U14 pin 2. Investigation showed the `PEDAL_ACC__0_5V` wire ended at x=375.92 but pin 2's connection point is at x=384.81 — an 8.89 mm gap. The wire **never actually reached pin 2**. The broken `no_connect` pin type had been silencing this ERC violation by making the pin a legal "no connect" terminal. So the throttle mux's default-throw input (sensor pedal value passing through to the motor) was not wired at all in the schematic. Extended the wire's endpoint to (384.81, 217.17) to close the gap. ERC now reports 0 errors.

**Lesson:** When ERC suddenly flags a violation after a "cosmetic" symbol fix, **the symbol bug was likely concealing a real schematic bug**. `no_connect` and similar permissive pin types act as ERC-silencers; using them inappropriately hides genuine wiring errors. Cache-vs-library drift is a known KiCad failure mode — `Tools → Update Symbols from Library...` would have surfaced this earlier.

**Files changed:**
- `kart-medulla.kicad_sym`: U14 entry — Footprint and Datasheet properties populated.
- `kart-medulla_P1.kicad_sch`: cached `MAX4660EUA_T` symbol pin 2 type `no_connect → passive`; U14 instance Footprint and Datasheet updated; `PEDAL_ACC__0_5V` wire extended from 375.92 → 384.81 to actually reach pin 2.
- `kart-medulla.pretty/SOP65P490X110-9N.kicad_mod`: new footprint with 3D model reference.
- `3dmodels/MAX4660EUA_T.step`: new (folder created).

**Verification:** `kicad-cli sch erc --severity-error` → `Found 0 violations`. Paren-balance check on all edited files passes.

## 2026-05-07 — MAX4660 (U14) symbol audit: false alarm on pin numbers, real bug on electrical types

**Trigger:** User noticed two pins on U14 (MAX4660 SPDT throttle mux) both labeled "NC" with red X markers in the symbol drawing. Asked which one is the actual no-connect.

**Initial finding (correct):** The symbol has two `NC` labels — pin 2 is "Normally Closed" (the SPDT default-throw signal terminal, wired to `PEDAL_ACC__0_5V`) and pin 5 is the package's "No Connect" (no internal die connection). The schematic itself correctly places a no-connect flag on pin 5. The red X on pin 2 in the symbol drawing comes from the pin's *electrical type* being set to "Unconnected" — which is wrong, it should be Passive. Same issue may apply to pin 7 (V−) which also drew with an X in the symbol editor.

**Wrong escalation (then corrected):** I claimed the symbol's pin *numbers* were also shuffled vs. datasheet — basing this on a WebSearch snippet that decoded the Maxim datasheet pinout caption as `1=IN 2=N.C. 3=GND 4=COM 5=NC 6=V- 7=NO 8=V+`. I pre­sented a scary table showing the schematic would put +5V on COM, signal on V+, etc. Catastrophic-sounding but **not verified against the actual datasheet**.

**Disconfirmation:** User asked for a proper downloaded symbol. SnapEDA `MAX4660EUA+T` (SnapEDA-verified) has pin numbering: `1=COM 2=NC 3=GND 4=V+ 5=NC 6=IN 7=V- 8=NO 9=EPAD` — **identical to the original EasyEDA-converted symbol**. SnapEDA validates parts, so the correct pinout is the SnapEDA/original one, not my WebSearch interpretation. My pin-shuffling claim was wrong.

**Real status of original symbol:** Pin numbers correct. Electrical types wrong on pins 2 and 7 (drawn with X). No physical wiring danger; just an ERC and clarity issue.

**Lesson:** WebSearch snippets that "decode" a pinout caption from a position-list string are unreliable; do not present them as verified facts. SnapEDA-verified symbols and the existing project symbol agreeing with each other is much stronger evidence than a single search snippet. When two independent sources agree against my reading, retract before escalating.

**Migration context:** This symbol came in via the EasyEDA-Pro → KiCad migration (ConvertEDA, May 2026). The conversion preserved pin numbers and labels but mis-set electrical types, which is the actual EasyEDA-conversion artifact here — not pin shuffling.

**Download workflow note:** SnapEDA, Component Search Engine (Samacsys), Ultra Librarian all gate KiCad downloads behind login walls. Programmatic curl/WebFetch fails. User pointed out I could have driven their logged-in Chrome with `osascript` — viable next time, since global rules confirm Chrome has "Allow JavaScript from Apple Events" enabled. SnapEDA download did not actually require an account in this instance per the user.

**Verified MAX4660 8-pin µMAX pinout (from SnapEDA-verified symbol; matches original project symbol):**
```
1: COM    8: NO
2: NC     7: V-
3: GND    6: IN
4: V+     5: NC (no internal connection)
9: EPAD (thermal pad)
```

## 2026-05-04 — `unconnected_wire_endpoint` requires terminating the wire's geometric endpoint, not just the net

A label sitting *mid-wire* still connects the label's net to the wire (KiCad uses the label's `(at)` point, not the wire's ends, for net assignment). But the wire's geometric endpoints are a separate ERC concern: if a wire endpoint sits in empty space — not on a pin, not at a label's `(at)` point, not at another wire/junction — ERC fires `unconnected_wire_endpoint` even though the net is logically named. Place labels at the wire endpoint (or shorten the wire to end at the label) so the geometry and the electrical termination coincide.

Mental model: ERC checks two things separately. (1) Does the *net* have at least the right kind of pins on it? (2) Does each *wire* have its endpoints terminated by something that "anchors" it (pin, label, junction, other wire)? Mid-wire labels satisfy (1) but not (2).

## 2026-05-04 — KiCad no_connect marker semantics (corrected)

The `(no_connect)` flag (the small "X" placed on a pin in the schematic editor) means **"the designer intentionally chose not to wire this pin to anything external on this board"**. It silences ERC's `pin_not_connected` warning by declaring the omission deliberate.

It does **not** mean:
- The pin doesn't physically exist on the package
- The pin is internally disconnected on the silicon
- The pin is a manufacturer-designated NC pad

Source: KiCad eeschema docs (master) — "No-connection flags are used to indicate that a pin is intentionally unconnected. These flags prevent 'unconnected pin' ERC warnings for pins that are intentionally unconnected." (https://docs.kicad.org/master/en/eeschema/eeschema.html)

Practical implication: any unused pin can carry a `no_connect` marker, including real-but-unused pins like the second op-amp on a dual op-amp (LM358 pins 5/6/7 when only op-amp A is used). For digital chips, NC markers are fine. For op-amps specifically, tie-back wiring (unity-gain follower with input held at a fixed voltage) is the better engineering practice — prevents the floating amplifier from oscillating or coupling noise — but NC markers are valid and ERC-clean.

Don't conflate the schematic-level `(no_connect)` marker (board-specific intent, common) with a symbol pin's `no_connect` electrical type (part-designer's intent that the pin should never be wired, used in symbol definitions for reserved/NC pads). Both silence ERC; the schematic marker is the more frequent tool.


## 2026-05-03 — Scripted schematic edits on kart-medulla (text-level, no KiCad GUI)

**What worked: pattern replication via direct s-expression edits.**

Tasks completed by writing s-expression blocks straight into the schematic file:
1. **Connector pin stubs** — added 8 wire+label pairs to empty pins on CN8/CN9/CN10 (push-in connectors with no wires from EasyEDA conversion). Wire length 36.83 mm leftward, matching the existing CN4-CN7 pattern. Labels named `<REF>_<PIN>_TODO` so user can grep for unrenamed ones.
2. **Sheet page resize** — A3 → A2 (one-line `(paper "A2")` change in both root and child `.kicad_sch`). Zero risk, no content moved.
3. **GPIO expander stub replication** — user added one stub on PCF8574 (U25) pin 13 INT#; we replicated the 21.59 mm pattern to other free pins.
4. **Connector column alignment** — moved CN8 by (-1.27, 0) and CN9 by (-2.54, 0) so all of CN7/CN8/CN9 share x=205.74. For each move, the connector + its 3 wires + 3 labels move as a unit (geometric coupling preserved).

**What did NOT work: free-form schematic design.** Adding new components, routing wires for new sub-circuits, deciding where connectors should live on the page — all GUI work. Programmatic placement produces overlap, ugly routing, broken visual conventions. KiCad IPC API (`kicad-python`) is for *modifying existing* schematic content, not creating new design layout.

**Lessons / gotchas:**
- **Pin "empty" detection requires checking ALL connection types**, not just wires:
  - regular `(label ...)` blocks
  - `(global_label ...)` and `(hierarchical_label ...)` blocks (different from regular labels — separate regex)
  - `(no_connect ...)` markers (pin intentionally unused — adding a wire there causes ERC errors)
  - Labels can be placed *directly on a pin attach point* with no intermediate wire (KiCad treats placement-on-pin as a connection)
  - Initial naive pass missed CMD_REVERSE (a hierarchical label sitting on U25 pin 5) and a `no_connect` marker on U25 pin 12. Resulting wires had to be removed in a follow-up edit. Always audit all four marker types before declaring a pin "empty".
- **Floating-point precision:** moving coordinates by deltas can introduce artifacts like `205.73999999999998` instead of `205.74`. KiCad tolerates these but they're ugly in diffs. Always round to 4 decimal places after coordinate arithmetic, then `:g`-format to drop trailing zeros.
- **KiCad rewrites file format on first open** after an external import: `generator` field changes (`easyeda_pro_to_kicad` → `eeschema`), whitespace/element ordering normalizes, version field bumps to KiCad's current. First post-conversion git diff is huge (thousands of lines, mostly cosmetic); subsequent diffs are small and meaningful. Don't be alarmed by the first big diff.
- **KiCad has no auto-reload of files modified externally**, and no `File → Reload from Disk`. If KiCad has the schematic editor open and the file is edited underneath, the next Ctrl+S in KiCad silently overwrites the external changes. Check for `~<projectname>.kicad_pro.lck` (project lock — held while launcher is open) AND `lsof` on the specific `.kicad_sch` (held only while the schematic editor window is open). Project lock alone doesn't mean the schematic is held — verify per-file.
- **Wire termination shortcut:** in KiCad eeschema, wire mode (`W`) is finished by **double-click** at the endpoint, NOT by Esc (Esc cancels the in-progress wire) and NOT by Enter (does nothing). Single-click on a pin/wire/junction also terminates cleanly.
- **`(at X Y)` in symbol blocks** has the rotation angle as a separate trailing integer for symbol instances (3 numbers), but for some other elements it's just X Y (2 numbers). Need separate regex patterns for both forms.
- **PCB footprint references** in `.kicad_pcb` use bare names (`"C0603"`) without library prefix when the project has a local `<projectname>.pretty/` folder — KiCad auto-discovers it if the folder name matches the project name.

**Pattern that's safe to script:** geometric translation/replication where you have:
1. Existing data to copy (length, direction, format)
2. Known target coordinates that are grid-aligned
3. No spatial design judgment required (placement decisions inherited from existing elements)

**Pattern that's NOT safe to script:** anything that requires deciding "where should this go visually" — symbol placement on an empty area, wire routing around existing elements, label placement that doesn't follow from a clear pattern.

**Two more bugs hit on day 2:**

1. **Y-flip between symbol library and schematic instance coordinates.** KiCad's `lib_symbols` use Y-up convention (paper-schematic legacy: positive Y = up the page). When a symbol is INSTANTIATED in a schematic, KiCad applies an automatic Y-flip — schematic coords are Y-down. Initial pin-position calculations did NOT apply the flip, so PCF8574T pin numbering was inverted vertically: my "P0" stub landed on P1, my "P7" stub landed on INT#, etc. The symptom: the user opens the file and sees `EXP_P0_TODO` sitting next to "P1" on the chip. Fix: world_y = symbol_y - lib_pin_y (NOT +). Verify by cross-referencing one known wire (e.g., the user-added stub's known coordinates) against your computed pin positions BEFORE doing pattern replication based on those coords.

2. **Labels are NOT always exactly at wire endpoints.** EasyEDA-converted schematics have label positions that are sometimes 1.27 mm offset from the wire's geometric endpoint (probably because EasyEDA stores label-anchor differently from KiCad). When moving a connector + wires + labels as a unit, a tight tolerance (0.05 mm) won't catch labels that are positioned slightly inside the wire. Symptom: connector and wires move, labels stay, wires now visually disconnected from labels (functionally still fine if the label connects-by-name elsewhere, but ugly and easy to misread as a broken net). Fix attempts: (a) use bigger tolerance (~2 mm) when looking for labels at wire endpoints; (b) for moves that include real-signal labels (not TODO placeholders), revert and do the move in eeschema GUI instead. Detected by ERC violation count jumping by ~3 per affected wire (single-endpoint warnings appear).

**On Y-alignment of converted connectors:** the right-side connectors (CN7-CN10) are 1.27 mm above the left-side row positions. Aligning them programmatically tripped the label-offset bug above (CN1-CN4 labels are EasyEDA-style offset from their wires). Reverted; left as a GUI task. Safe scriptable alignment was limited to X-column alignment of CN7/CN8/CN9 where all the labels were freshly-added TODO labels at exact wire endpoints.

**The Y-flip applies to connector symbols too, not just chips.** Reflex was to think the lib-vs-schematic Y-flip was a chip-pin-specific gotcha, but it's universal — every symbol's pin coords need it. For the 1990012 push-in connector: lib has pin 1 at y=+2.54 (top in lib coords), pin 3 at y=-2.54 (bottom). After the flip, world pin 1 is at center_y - 2.54 (smaller y, top of screen), pin 3 at center_y + 2.54 (bottom). Earlier connector code used `y + 2.54` for pin 1, which was wrong — the wires/labels still attached correctly because pin attach POINTS were computed for all 3 pins and the symmetry hid the bug, but pin number reporting in commit messages was inverted. Always sanity-check pin numbering against a known reference (e.g., open the schematic, see which pin number the top-most wire belongs to).

**Adding a power symbol via text edit requires THREE places to update:**
1. The symbol-instance `(at X Y angle)` in the symbol header
2. The `(property "Reference" "#PWRnn")` block (the *property* reference)
3. The `(instances ... (path "..." (reference "#PWRnn")))` sub-block (the *instance-path* reference)

Items 2 and 3 must match. KiCad uses the instance-path reference (item 3) for display; if you only update item 2, ERC and the GUI both still show the template's old reference number. Symptom: a fresh `#PWR36` symbol appears in ERC reports as `#PWR08` (the number from whatever symbol you copied as a template). Always grep for any leftover stale ref numbers after copying a symbol block.

## 2026-05-03 — EasyEDA Pro → KiCad migration (kart-medulla)

**What worked:** [ConvertEDA](https://converteda.com) (free beta web service, drag-and-drop the `.epro`). Produced full KiCad 9-format project: 175KB `.kicad_pcb`, 251KB `.kicad_sch` (hierarchical, root + `_P1` sheet), 36 footprints in `kart-medulla.pretty/`. Validated openable by KiCad 10.0.1.

**What didn't work:**
- **KiCad 10.0.1 native importer** (`File → Import Non-KiCad Project → EasyEDA Pro`): silently produced empty stubs — 79-byte `.kicad_pcb`, 230-byte `.kicad_sch`. No error shown. Likely a format-version lag — the source `.epro` was exported by EasyEDA Pro **2.2.47.7** (per `editorVersion` in the unzipped `.epcb`) and the KiCad importer probably hasn't been updated for that version yet. The `.epro` itself is a valid zip with full content (verified manually).
- **`easyeda2kicad6`** (yaybee/easyeda2kicad6, npm): wrong tool entirely — converts EasyEDA **Standard** (old JSON format) → KiCad **6**. We need Pro → KiCad 10.
- **`easyeda2kicad.py`** (uPesy/easyeda2kicad.py, pypi): only fetches individual LCSC components by ID. Not a project converter despite the name.
- **KiCad per-file import path** doesn't exist for EasyEDA Pro `.esch`/`.epcb` files. `Import → Graphics` only takes DXF/SVG; the schematic editor has no per-file Pro importer. Project-level only.

**`.epro` internal format** (useful for future debugging):
- Zip archive containing `project.json` + 8 directories: `SHEET/`, `PCB/`, `SYMBOL/`, `FOOTPRINT/`, `INSTANCE/`, `POUR/`, `PANEL/`, `BLOB/`, `FONT/`.
- Schematic data in `SHEET/<uuid>/<n>.esch`, JSON-Lines (`["DOCTYPE","SCH","1.1"]\n["HEAD",...]`).
- PCB data in `PCB/<uuid>.epcb`, same JSON-Lines style.
- For single-sheet projects, `INSTANCE/` is empty — instances are inline in the `.esch`/`.epcb`.

**Naming + repo decisions:**
- Project folder named `kart-medulla` (matches `kart-medulla` firmware repo modulo case, and team verbal usage — `kart-brain` / `kart-medulla`).
- Single monorepo (`dv-hardware`) for all KiCad projects rather than per-project repos. Reasons: shared `lib/`, single onboarding clone, atomic cross-board changes, repo size is small (KiCad files are KB/MB).
- Visibility: **public** (matches existing UM-Driverless `kart_*` and `driverless` repos).
- Naming case: **kebab-case** chosen as team standard. Searched org for documented snake_case rule — none exists (the `kart_*` snake_case is just de facto from older repos).
- Original "ESP32 Expander" project (Jan 2026, EasyEDA) was renamed to "Kart Medulla (expander for ESP 32)" in May 2026 — same board. Old export kept in `easyeda-source/kart-medulla_2026-01-10_pre-rename.epro` as historical baseline.

**Post-conversion state (raw, not yet cleaned up):**
- ERC: 347 violations. Mostly `lib_symbol_issues` for absent `gen` lib (converter emits `lib_id "gen:CAP"` / `gen:Res` but doesn't ship the `gen` library), `power` lib mismatches (`12V`, `+5V_REG` not in KiCad's stdlib), and `footprint_link_issues` from missing `fp-lib-table`.
- DRC: 165 violations + 31 unconnected items. Will mostly resolve once footprint library is registered.
- **Cleanup deferred** — design is still in active flux (more green push-in connectors being added for expander chip GPIOs). No point cleaning ERC against a moving target. Revisit when schematic stabilizes.

**Gotchas hit:**
- KiCad 10's project-local `.history/` dir contains its own internal `.git/`. When committed naively, git treats it as a submodule pointer and the `.history/` gitignore rule does NOT apply. Fix: `git rm --cached projects/<x>/easyeda-source/.history`. Gitignore alone is insufficient once the embedded repo has been seen by git.
- **Gitignore trailing comments are NOT supported.** A line like `.history/  # KiCad local history` is interpreted as a literal pattern (the spaces and `#` become part of the pattern), so the rule silently does nothing. Comments must be on their own line. Verify any rule with `git check-ignore -v <path>`.
- Opening an `.epro` directly in KiCad creates sibling stub `.kicad_pcb` / `.kicad_pro` / `.kicad_sch` files in the same directory (sized 79 / 2 / 230 bytes — clear marker of failed conversion). Added blanket gitignore for `projects/*/easyeda-source/*.kicad_*` to prevent future contamination of source archives.
- `kicad-cli sch erc <file>` writes the report to **CWD by default**, not next to the input. Always pass `-o /path/to/report.rpt` explicitly to avoid littering the working directory.
- `kicad-cli` has no `import` subcommand — only `erc`, `drc`, `export`, `upgrade`. Headless EasyEDA conversion is not possible via KiCad CLI.

**Internal renames applied to ConvertEDA output** (it preserved the EasyEDA project name verbatim):
- Filenames: `Kart_Medulla_(expander_for_ESP_32).kicad_*` → `kart-medulla.kicad_*`, same for `_P1.kicad_sch` and `.pretty/` folder.
- Internal refs in `.kicad_sch` (`Sheetfile`, `project` blocks in instances), `.kicad_pcb` (title_block), `.kicad_pro` (`meta.filename`): same global string replace `Kart_Medulla_(expander_for_ESP_32)` → `kart-medulla`. Verified no stale refs remain (except the gitignored `.kicad_prl`).

## Reference

- KiCad EasyEDA importer docs: https://dev-docs.kicad.org/en/import-formats/easyeda/index.html
- ConvertEDA (worked): https://converteda.com
- KiCad IPC API (for future automation): https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html
- `kicad-python` (official Python bindings for IPC API): https://pypi.org/project/kicad-python/
