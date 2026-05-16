<!-- read in full — kept under 150 lines -->

# kart-medulla — board-specific tasks

Per-board task list. Higher-level/cross-board work lives in `dv-hardware/.agents/tasks.md`. Update status: `TODO → In Progress → Done`. Claim by adding `[YYYY-MM-DD <name>]`.

## TODO

### Investigate routing the on-board ESP32-S3-DevKitC-1 RGB LED

The DevKitC-1 has an on-board WS2812 RGB LED tied to **GPIO38** (or GPIO48 on some revisions — confirm against the exact module rev used). It is **disconnected by default**: a solder-bridge jumper on the module needs to be closed to wire the LED data line to the GPIO. If we close that bridge, that GPIO becomes unavailable for anything else on the medulla side.

**Decide:**
1. Confirm which exact GPIO the on-board LED uses on our DevKitC-1 rev (check the user-provided silkscreen / Espressif schematic for that rev).
2. Audit the current medulla schematic — is that GPIO already routed to a sensor/peripheral?
3. **If unused on our side:** leave it unwired on the medulla side AND document that closing the module's solder jumper enables the LED (→ add to `docs/`).
4. **If we're already short on pins:** skip this — the LED is a nice-to-have, not worth losing a real I/O.

Outcome to commit: a 1-line note in `docs/pinout` (or wherever pinout lives) saying "GPIO## reserved for on-board LED, leave free, requires SJ## closed on module".

### Triple-check MAX4660 (U14) throttle-mux wiring

Current verified state (per netlist generated 2026-05-07): pin 1 COM=`CMD_ACC__0_5V`, pin 2 NC=`PEDAL_ACC__0_5V`, pin 3 GND=GND, pin 4 V+=`+5V_REG`, pin 5 NC=no-connect, pin 6 IN=`SELECT_THROTTLE`, pin 7 V−=GND, pin 8 NO=`CMD_ACC_ESP32__0_5V`, pin 9 EP=GND. ERC clean.

Outstanding doubts to resolve:
- **`SELECT_THROTTLE` driver — most important.** Audit (2026-05-07) of `~/repos/kart-medulla` firmware found **no GPIO drives this line**: manual/autonomous safety is currently done by zeroing the DAC output when `mission == MISSION_MANUAL` (`main/main.c:106`). User's intent is that `SELECT_THROTTLE` should come from one of the ESP32 GPIOs OR an output of the PCF8574 GPIO expander (U25). **Action:** trace `SELECT_THROTTLE` net on the schematic — find what other pin/connector currently terminates the net. If it's a dangling stub at U23/U24 (the ESP32 header) or U25 (PCF8574), that's the intended driver and firmware needs to drive that GPIO. If it's not connected to anything at all, decide which GPIO to assign and wire it.
- **Functional cross-check vs firmware:** once a driver is assigned, verify polarity — schematic intent: LOW = COM→NC = pedal sensor pass-through (default safe state), HIGH = COM→NO = ESP32 DAC takes over. Firmware should drive LOW for manual/autonomous-disabled, HIGH for autonomous-enabled. Confirm in `main.c` once the GPIO is wired.
- **Pin 9 EP overlap (cosmetic):** earlier the `GND` text label on the EP power symbol overlapped with the chip's "EP" pin name. Resolved 2026-05-07 by moving the GND symbol up.

### Learn: how the manual `#PWR` reference rename worked

User renamed `#PWR25ce01` → `#PWR042` and `#PWRdf4d01` → `#PWR043` via KiCad GUI (right-click GND symbol → Properties → Reference field). Done; ugly auto-refs gone. **But user did not understand what was happening conceptually.** Task: read up and write a short note in `docs/` (or a comment somewhere) covering:

1. **Why every symbol has a Reference (`R12`, `U14`, `#PWR042`, etc.).** It's the unique identifier KiCad uses to map schematic symbols to PCB footprints — the netlist sends `(comp (ref "U14") ...)` and the PCB looks up `U14` to know which footprint instance gets which net. Without a unique Reference, the PCB push fails.
2. **Why power symbols (GND, +3V3, +5V_REG…) get `#PWR…` instead of `R…` or `U…`.** They are virtual-only — they exist in the schematic to declare "this wire is on the GND net" but have no physical part on the PCB. KiCad still requires every symbol to have a unique reference, so power symbols get the `#`-prefix family (`#PWR042`, `#FLG01`, `#PWR_FLAG…`) which signals "exclude from BOM, exclude from PCB push." The number is just for uniqueness; the meaning of the symbol is in its Value field (`GND`, `+3V3`).
3. **Why the auto-IDs from kicad-mcp-pro were ugly (`#PWR25ce01`).** When the MCP added a power symbol via `sch_add_power_symbol`, it generated a random suffix to avoid colliding with existing refs, but it didn't assign a clean sequential number. KiCad's Annotate tool only renames symbols whose ref ends in `?` (the "needs annotation" sentinel) — it skipped these because they had a "complete-looking" ref already.
4. **The fix the user did:** open Properties dialog (`E` key or right-click → Properties) → change the Reference text field to `#PWR042` (next free number that no other power symbol uses) → OK. Same as renaming a variable. No electrical effect — Reference is just a label.

This is worth turning into a 5-line note in `docs/kicad-conventions.md` (or wherever board-level KiCad docs live) so future board work doesn't repeat the confusion.

### Wire ASSI/AS-emergency buzzer on the BUZZER GPIO

The schematic reserves GPIO 3 as `BUZZER` (digital out, debug-only) but no actual transducer or driver is wired. Resolve before fab.

**Inventory we already have** (Milwaukee components box, see Notion AI Inventory):
- **CPT-407-105-L60** (Same Sky, qty 5) — self-driving piezo, 14 VDC, **105 dB @ 10 cm**, wire-leaded with connector, continuous tone. No external driver IC needed; just gate kart 12 V through a low-side N-channel MOSFET (e.g. the BSS123 footprint already used elsewhere) controlled from GPIO 3.
- **RE46C100S8F** (Microchip, qty 10) — piezoelectric horn driver IC, used on the legacy Eagle ASSI board (2021–2022). Only useful with a non-self-oscillating piezo element; redundant for the CPT-407. Keep as fallback if we end up sourcing a louder bare-piezo transducer. Datasheet: `~/dv/datasheets/re46c100_microchip_datasheet.pdf`.

**FS-Rules concern (DV 4.5):** required SPL is **80–90 dB(A) @ 2 m**. CPT-407's 105 dB @ 10 cm projects to **~79 dB @ 2 m** (−26 dB over 20× distance for a point source) — right at or just below the minimum. **Bench-measure SPL at 2 m with a phone/Class-2 meter before committing the design.** If it falls short:
- Parallel two CPT-407s in phase (~+3 dB → ~82 dB @ 2 m).
- Source a louder transducer (≥110 dB @ 10 cm) and pair with the RE46C100S8F.
- Add a small horn/baffle (+3–6 dB cheap).

**Schematic action:** add the buzzer footprint + low-side MOSFET + flyback diode (CPT-407 is inductive-ish at switching) on the GPIO 3 net. Connector pin on a green push-in if the buzzer mounts off-board, or 2 solder pads on-board if mounted directly.

**Origin:** Telegram driverless chat msg 11568–11572 (2026-05-07). Original suggestion was to solder a generic Arduino buzzer to the GPIO — would not pass scrutineering.

### Switch DAC from MCP4922 → DAC7574 #gabriel #eduardo

DAC7574 (quad 12-bit I²C) is the closest match to what's in stock — 2 in stock at 17F06; MCP4922 is not in inventory.
- Interface reverts to I²C on GPIO 8/9 (shared with AS5600, no address conflict: AS5600 = 0x36, DAC7574 = 0x4C–0x4F).
- VDD = 5 V acts as reference → RC filter moves from VREF pin to VDD pin (use ferrite bead + 22 µF, or 10 Ω + 22 µF, to avoid DC drop from ~1 mA supply current).
- LDAC → GND (auto-latch on every I²C write).
- Free GPIO 14 back to `CS_SPARE`; update `docs/pinout-esp32-s3.md`, `history.md`, `README.md`, and the EasyEDA schematic.

### Add L7805 on-board linear regulator (12 V → 5 V) #ruben

Decision 2026-05-02 (see `history.md`): split-rail design.
- **L7805 from kart 12 V** powers analog only: MCP4922 VDD/VREF + MAX4660 V+ (×2). ~1 mA total → 7 mW heat. Trivial.
- **USB VBUS from Orin** powers the ESP32 dev board only (via its onboard 3.3 V LDO). Not connected to the L7805 rail.
- Only GND is shared between the two rails.

BOM (all in stock): 1× L7805CDT-TR (DPAK) + 1× 0.33 µF input cap + 1× 0.1 µF output cap.

Schematic wiring rule: ESP32 5 V pin and medulla USB-C VBUS net stay separate from the L7805 5 V rail. D+/D−/GND go from medulla USB-C to ESP32 GPIOs 19/20 + GND. VBUS goes from medulla USB-C to ESP32 5 V pin (or onboard USB-C VBUS net), nothing else.

Existing RC on MCP4922 VREF (100 Ω + 10 µF) stays — overkill for the linear but harmless and keeps the design swap-ready. Update `docs/pinout-esp32-s3.md` power architecture diagram to reflect the split-rail topology.

### Finish medulla schematic — verify every signal is wired and labeled correctly #ruben

- Title: change `ESP32-S3-DevkitC-1` → `ESP32-S3-DevKitC-1` (capital K).
- ESP32 header pin labels match the canonical names committed 2026-05-03: MOSI / CLK / CMD_DAC_CS (not OUT_SDI/SDK/CS).
- Pin 13 signal labeled `SDC_NOT_EMERGENCY__3V3` everywhere (matching the schematic; the doc was updated to match).
- All ESP32 SPARE / RESERVED pins have NC flags or `SPARE` text labels (Pins 8, 10, 11, 12, 16, 17, 36 — see `docs/pinout-esp32-s3.md`). DRC should report no unconnected-pin warnings.
- ADC voltage dividers in place for: PEDAL_ACC (0–5 V → ~0–2.5 V), PEDAL_BRAKE (0–5 V), PRESSURE_1/2/3 (0–10 V → ~0–2.5 V), HYDRAULIC_1/2 (0–5 V). Each input also gets a small filter cap (100 nF) at the ADC pin.
- Verify where the 5 V supply for the motor hall sensors comes from (`MOTOR_HALL_*__5V` nets on CN6/CN7). If it's external, the medulla connector just passes it through. If it's medulla-supplied, decide whether to feed from the on-board L7805 rail or add a separate 5 V source.

### Add REVERSE_WIRE + needed signals to the green push-in connectors #ruben

- Add `REVERSE_WIRE` (output of the BSS123 Q4 drain) to a connector pin. Empty CN8 is the natural choice. Confirm whether the manual reverse button is wired through the medulla too (would need a second pin + GND); if the button goes directly to the kart electronics box, just one pin suffices.
- Rename `STEER_SDA__I2C` → `SDA__I2C` and `STEER_SCL__I2C` → `SCL__I2C` on CN4 (I²C bus is now shared with the PCF8574, not just the AS5600). [partially done 2026-05-04 — confirm and finish]
- Verify every signal in `docs/pinout-esp32-s3.md` that needs to leave the medulla actually has a connector pin. Cross-check: PEDAL_ACC, PEDAL_BRAKE, PRESSURE_1/2/3, HYDRAULIC_1/2, motor halls (×3), CMD_ACC, CMD_BRAKE, CMD_STEER_PWM, CMD_STEER_DIR, SDA, SCL, REVERSE_WIRE, manual reverse button (if needed), 12 V, GND.

### Lay out the medulla PCB (post-schematic, blocked on schematic finish) #ruben

- Place ESP32-S3-DevKitC-1 in the center, footprint matching `~/dv/kart/kart-medulla/resources/esp32-s3-devkitc-1/` (verified 22.86 mm row spacing).
- Place L7805 (U19) with its caps near the +12 V input edge, copper pour on the GND tab for thermal dissipation.
- Place MCP4922 (U13) close to the ESP32 SPI pins (MOSI/CLK/CMD_DAC_CS, Pins 39/40/42).
- Place MAX4660 ×1 (U14, throttle mux) near the throttle command path between MCP4922 VOUTA and CN7 pin 3.
- Place the LM358 amp (U4) near MCP4922 VOUTB on the brake path before CN5 pin 3 (`CMD_BRAKE__0_10V`).
- Place PCF8574 (U25) on the I²C bus near the AS5600 connector (CN4); break P1–P7 to a small future-expansion header.
- Place BSS123 (Q4) near the CMD_REVERSE path between PCF8574 P0 and the REVERSE_WIRE connector pin.
- Place the medulla USB-C connector at the edge facing the Orin; route only D+/D−/GND/VBUS, with VBUS going only to the ESP32 5 V pin.
- Place the green push-in connectors (CN1–CN8) along the kart-facing edge.
- Continuous GND plane on at least one inner layer; star/loop GND for analog vs digital noise separation if comfortable doing so.
- Mounting holes (M3 × 4) at corners, isolated from any nets.
- Check footprint sizes against actual parts (DPAK for L7805, SOIC-16 for PCF8574, µMAX-8 for MAX4660, SOT-23 for BSS123, SOIC-14 for MCP4922).

### PCB checklist — pre-fab review and validation #ruben

- Run **DRC** until 0 errors / 0 unexpected warnings. Suppress only the SPARE/NC pin warnings explicitly.
- Run **ERC** on the schematic. 0 errors. Investigate every warning.
- Visually inspect: every net label has a counterpart on the other end (no dangling labels). Every component has a value and a footprint. Every connector pin has a net or NC flag.
- Export the **BOM** and verify DNP parts (4k7 I²C pull-ups, optional bulk caps) are excluded. Verify quantities match what's actually in stock — no surprise purchases.
- Export **gerbers** and view in a separate gerber viewer (e.g. JLCPCB previewer). Check copper layers, silkscreen readability, drill alignment.
- Print a 1:1 paper copy of the PCB outline + footprints. Place the actual ESP32 dev board on top — confirm every pin lands on its pad. Same for the connectors and the MOSFET / regulator footprints.
- Final manual review: walk through `docs/pinout-esp32-s3.md` row by row and confirm every Pin's listed signal is correctly wired in the schematic.
- Tag the EasyEDA project with a version number before fabrication, and commit a snapshot to `~/dv/kart/kart-medulla/project-backups/`.

## In Progress

- [ ] **New kart-medulla PCB version for ESP32-S3-N16R8** #gabriel #eduardo — overall board revision tracking the schematic + layout work above
- [ ] **Wire reverse gear to ESP32 + remote joystick control** #eduardo #gabriel — hardware side (BSS123 + REVERSE_WIRE connector pin); firmware side tracked in `~/repos/kart-medulla` (firmware repo)

## Done

- [2026-05-09] **Bind 3D models at library level (not instance level)**: edited 12 footprints in `kart-medulla.pretty/` (C0603, R0603, SOIC-{8,14,16}, SOP65P400X130-8N, SOT-23, TO-{220-3,252-2}, the two Samtec ESQ-122 headers, PTSA 3P) to carry `(model …)` blocks at library level, matching the existing pattern in `SOP65P490X110-9N` (which already had its MAX4660 binding). Per-footprint `offset` / `rotate` (e.g. PTSA's `xyz -90 0 0`) preserved exactly from the values in the `.kicad_pcb`. Future "Update Footprints from Library" or re-imports will now rebuild the 3D bindings automatically; the regression that needed `kart-medulla.kicad_pcb.bak.20260509f` recovery in commits `9596513` / surgical-merge cannot reoccur from the library side.
