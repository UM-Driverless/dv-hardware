<!-- read in full — kept under 150 lines -->

# kart-medulla — board-specific tasks

Per-board task list. Higher-level/cross-board work lives in `dv-hardware/tasks.md` (repo root). Update status: `TODO → In Progress → Done`. Claim by adding `[YYYY-MM-DD <name>]`.

## TODO

### V2 Hardware Improvements (Kart Medulla PCB)

Moved to [`requirements.md`](requirements.md) on 2026-07-16 — requirements are durable, this list gets pruned as tasks complete. Scope a revision from that file; track the work here.

Two moved items **contradict** other requirements and are flagged there rather than actioned — do not implement either as written: "repurpose BUZZER for compressor PWM" (conflicts with the rules-mandated ASSI buzzer on GPIO 3, and looks superseded by the GPIO 38/39 routing task below) and "repurpose PRESSURE_3 for steering PWM" (conflicts with the 3× pressure-sensor requirement and with the ADC dividers called for in the schematic task).

The connector-rotation item also restates the "Flip all ten CN connectors 180°" task below — same change, two entries. Kept the task, moved the requirement.

### Design the compressor MOSFET drive on-board for medulla-v2 #ruben

Raised 2026-07-18 after the EBS compressor was bench-run for the first time. Rubén's directive for
this revision: **integrate it — fewer wires running between boxes and bolted-on PCBs.** So the
switching stage comes onto the medulla board rather than staying an external module.

**Why the current arrangement fails.** The compressor is switched by an **IRLZ44N** whose gate is
driven straight from a 3.3 V ESP32 pin. Measured on the bench (see `kart-medulla` repo `history.md`
2026-07-18): **6 A running at 60% duty, and the MOSFET reached ~100 C even after the duty was cut to
20%.** The IRLZ44N datasheet specifies Rds(on) at Vgs = 10 V / 5 V / 4 V and stops there, so at
3.3 V it never fully enhances. This is conduction loss, not switching loss — at 500 Hz conduction
dominates roughly 50x, so changing the PWM frequency cannot fix it.

**The fix is gate drive, not a different MOSFET.** Driven at 10 V the IRLZ44N is already a good part
(22 mOhm, ~0.5 W). A survey of ~150 datasheets found the industry floor for a *specified* Rds(on) is
Vgs = 4.5 V, because Vgs(th) max on power dice is 2.0-2.5 V and nothing can be guaranteed at 3.3 V.
There is no drop-in part that solves this; a driver stage does.

**Design for v2 — five parts plus the MOSFET:**

| Item | Choice | Why |
|---|---|---|
| Gate driver | **UCC27517A** (SOT-23-5), or TC4420 / MCP1407 (PDIP-8) | Fixed TTL input, VIH <= 2.4 V across VDD 4.5-18 V, so 3.3 V logic drives it with ~0.9 V margin. Non-inverting, so no firmware change. |
| Driver supply | **12 V rail** + 100 nF decoupler | Low-side switching, so no bootstrap needed. See the rail note below before choosing 5 V instead. |
| Input pulldown | 10 kOhm to GND | Holds the compressor OFF through ESP32 boot and reset |
| Series gate resistor | 10-47 Ohm | |
| Flyback diode | across the compressor terminals | The load is an inductive motor |
| MOSFET | see below | |

**Which rail feeds the driver — 5 V or 12 V?** All three drivers accept VDD = 4.5-18 V, so either
works electrically. The catch is that VDD *is* the gate voltage, so the rail choice and the MOSFET
choice are one decision, not two:

| | Gate at 5 V | Gate at 12 V |
|---|---|---|
| IRLZ44N | **0.025 Ohm — specified in the datasheet.** Acceptable. | 0.022 Ohm |
| HA210N06 | **Unspecified.** 1 V of overdrive against a 4 V worst-case threshold. Not acceptable. | 4 mOhm |

So **5 V is only safe if the MOSFET is specified at 5 V**. The IRLZ44N is; the HA210N06 harvested
from the HUABAN module is not, and neither is any part chosen for low Rds(on) at 10 V. Since the
point of adding a driver is to stop being constrained by gate voltage, **default to the 12 V rail** —
it costs nothing extra, keeps every MOSFET option open, and removes the failure mode where the
circuit looks correct and still runs hot. Only drop to 5 V if the 12 V rail is genuinely
unavailable at that point on the board, and then pin the MOSFET choice to a 5 V-specified part and
say so on the schematic.

**Do NOT use UCC27518 or UCC27519** — their inputs are CMOS and scale with VDD (VIN_H = 70% of VDD),
so at 12 V the threshold is 8.4 V and a 3.3 V signal never registers. **Do NOT use a discrete
inverting level shifter** (small FET with a pull-up to 12 V): it inverts, so while the GPIO floats at
boot and reset the pull-up drags the gate high and the compressor runs full-on.

**MOSFET choice.** Once a driver is present the part is no longer constrained by what a GPIO can
swing, so prefer something in production: **IRLB8743, IPP034N03L or PSMN2R7-30PL**, all 3-4 mOhm.
The **HA210N06** harvested from the HUABAN module in inventory also works *provided the driver comes
with it* — that part is emphatically not logic-level (Vgs(th) 2/3/4 V min/typ/max, and Rds(on)
specified at exactly one point, Vgs = 10 V), so on its own it would be worse than what is fitted
today. Its Qg is 135 nC and Ciss 5800 pF, about 3x the IRLZ44N, which is a second reason a GPIO
cannot drive it directly.

**Current path — the part that is actually a board change.** `+12V` at CN1.2 and the motor return
are drawn today for the milliamp logic feed. Bringing the switch on-board needs:
- terminals and copper rated for **8 A continuous** (~3.5 mm on 1 oz external, or a pour) with via
  count to match, and the design current stated on the drawing;
- the **motor return taken straight back to the 12 V regulator**, meeting signal ground at exactly
  one star point. This is not cosmetic — see the pressure-sensor item below.
- Reference for sizing: the HUABAN carrier this replaces is rated **25 A** on a 60 x 50 mm board.

**Related: give the pressure sensor a clean supply and reference.** On the same bench run the tank
pressure reading sagged **~64%** while the compressor was running and recovered when it stopped.
Most likely a ratiometric sensor on a sagging rail, or ground bounce from the motor return — the
same mechanism behind the USB brownouts recorded in the `kart-medulla` repo. Whatever the cause, the
sensor's supply and reference must not share the motor's return path.

**Open, blocks nothing but worth settling:** whether the HUABAN module's control input accepts 3.3 V.
Believed yes by inference, unverified — see `history.md` 2026-07-18. If the module does boost the
gate from its own DC-IN rail, its `U2` stage is a working reference design to copy here.

### Route GPIO 38 + GPIO 39 out to CN terminals (no spare ESP32 GPIO is reachable today)

Found 2026-07-10 while trying to add the EBS compressor PWM driver without a soldering iron.

**The board has no spare ESP32 GPIO on any CN terminal.** Verified on a fresh netlist export:

  - CN pins that reach the ESP32 are all assigned: `SCL` (CN4.1), `SDA` (CN4.2), `BUZZER` (CN8.2),
    `CMD_STEER_DIR` (CN8.3), `CMD_STEER_PWM` (CN9.1).
  - The free CN pins — `EXP_P1`/`P2`/`P3` (CN3.1–3) and `EXP_P4` (CN5.3) — reach **U25, the PCF8574
    expander**, not the ESP32. They cannot generate PWM: I²C-rate edges, ~100 µA source current
    (cannot charge a MOSFET gate), and all ports released high at power-up.
  - The genuinely free GPIOs, **38 and 39**, exist only as pads under the dev module (U24 pads 13/14).

So any new PWM peripheral currently requires soldering a wire from under the module to a terminal.
That is the wrong trade for a team that wants to bolt something on at the bench.

**Do:** route **GPIO 38 → CN3 pin 1** and **GPIO 39 → CN3 pin 2**, relocating or dropping `EXP_P1`
and `EXP_P2`. Keep at least one `EXP_Px` on a terminal for slow on/off use. Suggested net name for
the first: `CMD_COMPRESSOR_PWM`. Coordinate with the connector-flip task below — both touch CN3.

**Principle worth writing into the board README:** a spare pin you cannot reach with a screwdriver is
not a spare pin. Bring at least two unassigned, PWM-capable, non-strap GPIOs to terminals on every
revision.

### Flip all ten CN connectors 180° (wires outward, pin order in sequence)

Raised by Rubén 2026-07-10 after handling the assembled board. Two complaints, one root cause:
the wire entry of every CN faces **inward**, toward the middle of the PCB, and within each
connector the pin numbers run *against* the direction the CNs advance.

Verified against `kart-medulla.kicad_pcb`:

| | Footprint rotation | Pin order top→bottom | CN order |
|---|---|---|---|
| CN1–CN5 (right) | −90° | 1, 2, 3 | ascends bottom→top |
| CN6–CN10 (left) | +90° | 3, 2, 1 | ascends top→bottom |

Rotating every CN by 180° fixes both at once: wires exit outward, away from the board, and the
pin numbering becomes co-directional with the CN numbering on each side, so you can read
`CN1.1, CN1.2, CN1.3, CN2.1, …` straight down (or up) the edge.

**Not a free rotation.** The footprint is `CONN-TH_3P-P2.50-S5.00_1990012` — staggered pads,
pins 1 and 3 in one row and pin 2 in a row 5.00 mm across. A 180° flip swaps which side pin 2's
row sits on, so all copper under the connectors must be re-routed, and board-outline clearance
on the outward side must be re-checked (wires now need room to leave).

**Steps:**
1. Rotate each CN footprint 180° in the PCB (right side −90° → +90°, left side +90° → −90°).
2. Re-route; expect the pin-2 nets to change side under every connector.
3. Re-check edge clearance and any mounting-hole / standoff conflicts on the outward side.
4. Update the silkscreen legend and `docs/pinout-cn-connectors.md` (the pin-order table there).
5. Confirm the signal↔pin-number assignment table is unchanged — we rotate footprints, we do
   **not** renumber pads. Any harness already crimped keeps its signal mapping; only the
   physical position of pin 1 moves.

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
- **`SELECT_THROTTLE` driver — RESOLVED on the schematic side 2026-07-10; firmware side still open.**
  Traced on a fresh netlist export (`kicad-cli sch export netlist`). The net terminates at exactly
  three places: **U23 pins 15/16 → ESP32 module Pin 30 → GPIO 15**, `U14` (MAX4660) pin 6, and `R32`
  (10 kΩ pulldown). So the intended driver is **ESP32 GPIO 15**, already wired — no PCF8574 involved,
  nothing to assign. The 10 kΩ pulldown means the power-on default is LOW = COM→NC = pedal
  pass-through, the safe state.
  **Remaining action is firmware only:** nothing in `~/repos/kart-medulla` drives GPIO 15 (confirmed
  by grep, 2026-07-10). Manual/autonomous safety is still done by zeroing the DAC output when
  `mission == MISSION_MANUAL` (`main/main.c:106`). Firmware must drive GPIO 15 HIGH to hand throttle
  to the DAC, LOW otherwise. Verify polarity against the MAX4660 datasheet once implemented.
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

### Pass the PCB checklist for `medulla-v2` #ruben

One finishable task: walk [`docs/pcb-checklist.md`](../docs/pcb-checklist.md) end to end against
`medulla-v2` and tick every box. Done = every item passes, the board is tagged `medulla-v2`, and the
fab package is committed under `fab/kart-medulla/v2/`.

The checklist items are deliberately **not** copied here — copying is what produced four divergent
copies of it (`history.md` 2026-07-16). Fix the checklist in `docs/` if an item is wrong; don't fork it.

Board-specific additions for this revision, on top of the generic checklist:
- Walk `projects/kart-medulla/docs/pinout-esp32-s3.md` row by row against the schematic
- Commit a project snapshot to `~/dv/kart/kart-medulla/project-backups/`
- Confirm `projects/kart-medulla/requirements.md` is satisfied — including the ASSI buzzer, which is
  a rules requirement (FS-Rules DV 4.5), not a nice-to-have

### Pre-fab finishing — board-specific remainder

Moved here from the root board 2026-07-16: these are kart-medulla items, not cross-board work. Most
of what was here has been folded into [`docs/pcb-checklist.md`](../docs/pcb-checklist.md) — the
generic parts (DRC/ERC, parity, 3D check, DFM preview, gerber export, easter eggs, GND pour, outline
rounding, antenna keepout, DRC constraints) are now checklist items, ticked once via "Pass the PCB
checklist for `medulla-v2`" above rather than tracked as separate tasks.

**Stale:** the section below is dated *"Tomorrow (2026-05-10)"* and was written two months before this
move. Kept verbatim rather than pruned — Rubén should delete what the checklist now covers and keep
only what's genuinely board-specific (the AISLER logo spec, the CN legend note). Flagged, not guessed.

<details>
<summary>Original text as moved (2026-05-10 / pre-fab finishing pass)</summary>

### Tomorrow (2026-05-10): pre-fab finishing

DRC reached **0 errors / 0 unconnected** on 2026-05-09 (commit `cfdf158`). Items still open before fab:

1. **Schematic Parity (5 issues)** — DRC dialog shows 5 mismatches between PCB and schematic when "Test for parity between PCB and schematic" is enabled. Likely net-name renames or footprint changes that didn't push back. Open the Schematic Parity tab, screenshot/list each, fix in the appropriate file (schematic vs PCB), re-sync.
2. **Run ERC** on the schematic (Inspect → Electrical Rules Checker) to confirm the schematic side is also clean.
3. **3D viewer sanity check** (Alt+3) — verify nothing collides: connector heights, header sockets U23/U24, TO-220 Q3 orientation, USB if present.
4. **AISLER DFM preview** — upload Gerbers to AISLER's online preview, or run their plugin if installed, for fab-side validation.
5. **Drill / Gerber test export** to a temp dir to confirm KiCad doesn't barf during output (no zero-drill vias, no missing layers).
6. **Easter eggs on silkscreen** — add personal/team easter eggs (e.g. UM Driverless logo, team initials, in-joke art, hidden text) to a free area on F.Silkscreen or B.Silkscreen. Avoid the AISLER logo placeholder area, mounting holes, antenna keepout, and the connector legend block. Decide whether to draw vector or use bitmap import (Image → Place Bitmap…).
7. **Final commit + push** before fab submission.

Ignored Tests in DRC are mostly fine to keep ignored (courtyard-related, tuning-profile, footprint-filter mismatches) — none critical for this prototype.



### PCB finishing pass (pre-fab)

Remaining PCB work before running DRC and exporting fab files. Order matters — do roughly top-to-bottom:

1. **Round the board outline + reposition mounting holes.** Snap the PCB edge to round mm values (e.g. 100.000 × 80.000, not 99.7 × 80.3). Place the 4 mounting holes at round, symmetric coordinates relative to the outline. Set a 1 mm grid and re-snap before measuring.
2. **Reserve the ESP32-S3 antenna keepout.** The on-module PCB antenna (ceramic chip / trace antenna on the ESP32-S3 WROOM module) needs clear board area underneath and around it: **no copper (no zone fill, no ground pour, no traces) and no metal (no components) within the keepout zone published in the WROOM datasheet — typically ~15 mm of clearance off the antenna end of the module, extending past the board edge if possible**. Add an explicit keepout zone (F.Cu + B.Cu + inner layers, "no copper pour") covering that area so the GND pour in step 3 doesn't fill into it. Also keep the antenna end overhanging the board edge if the module orientation allows.
3. **Create the GND polygon pours and refill.** Add a GND zone on F.Cu and another on B.Cu covering the full board outline (minus the antenna keepout from step 2). Set the zones to net `GND`, set thermal relief on connector pads, refill all zones (`B` in pcbnew). Verify visually that islands aren't isolated and that stitching vias tie top/bottom GND together near high-current paths (motor, 12V input, buck converter).
4. **Add AISLER sponsor logo placeholder** — see "Add AISLER sponsor logo placeholder to PCB" task below for the exact spec (4 individual lines, 0.08382 mm width, 4:1 ratio).
5. ~~**Label signals on silkscreen.**~~ **Done 2026-05-09** — per-pin labels added next to all 10 CN connectors using DejaVu Sans Mono (tab-aligned blocks). Pinout doc updated to match the latest schematic (CN5↔CN9 EXP_P4/GND swap + intra-CN reorderings). Per-pin labels supersede the old numbered legend; the "Update PCB silkscreen legend" task below is now obsolete and can be deleted along with the legend itself.
6. **Run DRC** (`Inspect → Design Rules Checker` in pcbnew — KiCad calls it DRC for the PCB; ERC is the schematic equivalent and was already run). Fix all errors. Triage warnings (courtyard overlaps, silk-on-pad) — fix or explicitly accept.
   - **Subtask: configure DRC constraints for the chosen fab.** Before running DRC, set the board constraints in `File → Board Setup → Design Rules → Constraints` and `Net Classes` to match the fab's process capability. Even though we'll fab at AISLER, configuring to **JLCPCB's standard 2-layer process** (more conservative) gives a safe baseline that AISLER will also accept. Key values for JLCPCB standard 2-layer 1 oz: min track/clearance 0.127 mm (5 mil) — use 0.2 mm for margin; min via 0.45 mm with 0.2 mm drill; min hole-to-hole 0.5 mm; min annular ring 0.13 mm; silkscreen min width 0.153 mm, min text height 1 mm. Save these into the project's DRC config so the check is meaningful.
7. **Re-verify after DRC fixes.** Refill zones again (DRC fixes may have moved tracks), re-run DRC until 0 errors. Then check: no unconnected nets in the ratsnest, all footprints have 3D models for the render, board edge is closed (no gaps), drill file matches mounting hole sizes.
8. **Export fab package.** Gerbers + drill + pick-and-place + BOM, per AISLER's submission spec. Generate the 3D render / STEP for a final visual check before uploading.
9. **Pass the personal PCB design-review checklist.** Rubén has a markdown checklist of things to verify before fab (location TBD — qmd-search and repo grep on 2026-05-09 didn't surface a dedicated PCB-checklist file; only `vault/other/sax-concert-checklist.md` turned up). Locate that file, link it here, and walk through every item before submitting fab files. Items typically include: silkscreen readability, decoupling cap placement, test points, fiducials, polarity marks, fab-house specific quirks, etc.


</details>

## In Progress

- [ ] **New kart-medulla PCB version for ESP32-S3-N16R8** #gabriel #eduardo — overall board revision tracking the schematic + layout work above
- [ ] **Wire reverse gear to ESP32 + remote joystick control** #eduardo #gabriel — hardware side (BSS123 + REVERSE_WIRE connector pin); firmware side tracked in `~/repos/kart-medulla` (firmware repo)

## Done

- [2026-05-09] **Bind 3D models at library level (not instance level)**: edited 12 footprints in `kart-medulla.pretty/` (C0603, R0603, SOIC-{8,14,16}, SOP65P400X130-8N, SOT-23, TO-{220-3,252-2}, the two Samtec ESQ-122 headers, PTSA 3P) to carry `(model …)` blocks at library level, matching the existing pattern in `SOP65P490X110-9N` (which already had its MAX4660 binding). Per-footprint `offset` / `rotate` (e.g. PTSA's `xyz -90 0 0`) preserved exactly from the values in the `.kicad_pcb`. Future "Update Footprints from Library" or re-imports will now rebuild the 3D bindings automatically; the regression that needed `kart-medulla.kicad_pcb.bak.20260509f` recovery in commits `9596513` / surgical-merge cannot reoccur from the library side.

---

## Moved from the root board 2026-07-16

All kart-medulla work, so it never belonged on a cross-board list. Verbatim; statuses preserved.

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

### In Progress (as moved)

- [2026-05-07] **PCB layout** — peer working on it.

### Done (as moved)

- LM358 U1B tied back (pin 7→6 follower, pin 5→GND) — replaces NC flags.
- Annotate schematic + ERC cleanup (wire endpoints, isolated single-pin labels, U14 MAX4660 NC pin etype). Schematic clean.
- Status LED decision resolved.
- 2026-05-04 — Schematic ERC: 313 → 32 (0 errors). Major cleanups: extracted EasyEDA-cached symbols into project lib + registered sym-lib-table; set pin electrical types on all chips; added PWR_FLAGs on +3V3/+5V_USB/+12V/GND rails; split LM358DR into proper multi-unit symbol; converted text annotations to real labels; wired ESP32 header pin-pair shorting on U23; renamed CN4 I2C labels (`STEER_SDA__I2C` → `SDA__I2C`, same for SCL — was a real bus-rename orphan that would have left steering sensor unwired); promoted/demoted labels for consistent local-vs-global scope; replaced misnamed `SPARE__3V3` with proper +3V3 power symbol on the connector; documented strap pins (U23 27/28 + U24 8) with NC + text annotation. See `history.md` for the lessons learned (KiCad no_connect semantics, isolated_pin_label false-confidence trap, mid-wire labels vs wire endpoints).

### Notes for the next person (as moved)

- `~/repos/kart-docs` is the source-of-truth for kart facts (sensor parts, voltage rails, mechanical). Grep there before asking.
- `history.md` has a running log of decisions/gotchas (grep, don't read in full).
- `.agents/error-log.md` has prevention rules from past mistakes — **especially the rule that `no_connect` markers mean "designer chose not to wire, on this board" and not "pin doesn't exist on silicon", and the rule to grep each `isolated_pin_label` before classifying it as "legitimate"**.
- The schematic is on a single sheet (`kart-medulla_P1.kicad_sch`). Hierarchical labels are not used; if you split into multiple sheets later, convert the relevant globals to hierarchical labels and add sheet pins.
