# ESP32-S3 (WROOM-1-N16R8) — current PCB

> **Authoritative source: the schematic in this same project folder (`../kart-medulla.kicad_sch`).** This document mirrors the pin assignments for human reading and adds rationale/strap-pin/firmware-mode notes that the schematic doesn't carry. **PCB layout is in progress — pin assignments may shift as routing constraints surface.** When this doc and the schematic disagree, the schematic wins; fix this file. Re-verify before each fab release.

Status legend (refreshed 2026-05-08):
  BLOCKED       — physically off-limits. Hardware constraint, never reclaim.
                  Examples: dev-board USB-UART bridge owns GPIO 43/44; dev-board
                  on-board RGB LED on GPIO 48; USB_D+/- pins not wired on this
                  PCB.
  HOLD          — pin works, currently unassigned, kept free for future
                  expansion. Includes octal-PSRAM-shared pins on N8R8 (GPIO
                  33-37 — usable on N8R2 but held free for module-variant
                  compatibility), conditional-strap pins (usable post-boot if
                  signal's idle-state matches the strap default), and pins
                  parked for known-but-not-yet-wired functions like CAN.
                  Don't grab without team agreement.
  NC            — pin physically not wired on this PCB rev. ERC silenced via
                  no-connect symbol.
  (signal)      — assigned, in use.

Older labels in git history: RESERVED ≈ today's BLOCKED, SPARE ≈ today's HOLD.

Each row's Notes column gives a brief reason for SPARE / RESERVED / SPARE/<sig>.

Column meanings:
  Pin        — physical-position index for the module, treated like an IC:
               bottom-right pin is **1**, count counter-clockwise around the
               ESP32-S3 dev board (component side, USB-C at the top).
                 Pins 1–22  = right edge, bottom (Pin 1) to top (Pin 22).
                 Pins 23–44 = left edge, top (Pin 23) to bottom (Pin 44).
               This is the canonical way to refer to a contact in
               conversation, on a multimeter probe, or in assembly notes.
               **Always use Pin (1–44).** Never use the schematic-symbol pin
               numbers from EasyEDA's connector parts — those are different
               (see "Schematic-symbol pin mapping" below for translation).
  Silkscreen — what's printed on the dev board next to that pin. Espressif
               labels GPIOs by their bare GPIO number (e.g. `4`, `15`, `46`)
               and adds short labels for special pins (`GND`, `3V3`, `5V`,
               `EN`, `TX`, `RX`). Useful when probing or hand-soldering.
  GPIO       — Espressif GPIO number (the one you use in firmware). Some
               pins are pure power/reset and have no GPIO.
  Signal     — net name on the schematic (see "Net Name Nomenclature" in README.md).
  Type       — peripheral / electrical role (ADC1_CHx, SPI, UART, Power, etc.).

Three references for the same physical contact:
  - "Where is it on the dev board physically?" → Pin
  - "What's printed on the board next to it?"  → Silkscreen
  - "What do I write in code?"                 → GPIO

## Schematic-symbol pin mapping

The medulla schematic uses two connector symbols:

- **RIGHT_HEADER** (on the right of the schematic, single row, 22 pins):
  the symbol's pin numbers map 1:1 to our Pin numbering. Symbol pin N = Pin N
  (for N = 1..22).
- **LEFT_HEADER** (on the left of the schematic, dual-row stacked, 44 contact
  pads but only 22 unique nets — each row is shorted between its two physical
  pads for daughterboard pass-through): symbol pins (1, 2) carry one signal,
  (3, 4) the next, etc. Each row maps to one Pin: row k → Pin (22 + k).
  - Symbol pin 1 (and 2) → Pin 23
  - Symbol pin 3 (and 4) → Pin 24
  - …
  - Symbol pin 43 (and 44) → Pin 44

(The PCB-header numbering H1.x / H2.x existed in earlier revisions of this
doc but was removed on 2026-05-02 — see `history.md`.)

Note on octal PSRAM pins (GPIO 33-37): a quad-PSRAM module (N8R2) leaves
these pins available externally. An octal-PSRAM module (N8R8 / N16R8) wires
them to the in-package PSRAM die, so they are internally reserved. The board
is laid out so it accepts either module — GPIO 35-37 are kept as SPARE on the
headers, no signal is routed to them. See history.md (2026-04-29) for rationale.

**The module actually fitted is an N16R8 (octal PSRAM)** — the supplier shipped
it instead of the ordered N8R2; verified on hardware 2026-07-10 (see
`history.md`). So on this board GPIO 33-37 are *not* reclaimable in practice:
treat them as BLOCKED, not HOLD, unless the module is swapped for a quad-PSRAM
part. The variant-agnostic layout means no signal has to move.

## Dev-board compatibility checklist (when buying a non-Espressif S3 board)

The pinout above targets the bare ESP32-S3-WROOM-1 module. Generic dev
boards (AliExpress clones, etc.) usually carry the same module on a
breakout PCB, but a few details vary between vendors and must be checked
before assuming this pinout works:

1. **Module variant.** Confirm whether the board carries an N8R2 (quad
   PSRAM, GPIO 33-37 free) or an N*R8 like N8R8 / N16R8 (octal PSRAM, GPIO
   33-37 reserved internally). The pinout is laid out to be safe with
   either — GPIO 35-37 are SPARE, GPIO 33-34 are unused, and signals that
   used to live on octal-PSRAM pins were moved (BUZZER (old name) 36→3, MOTOR_HALL_1
   37→16, CMD_STEER_DIR 35→0). So **either variant works**, but if you
   end up with an octal-PSRAM module **do not assign anything to GPIO
   33-37 in firmware**, ever.

2. **Native USB-OTG routing.** The pinout uses GPIO 19/20 as USB D-/D+ to
   the Orin. On the official Espressif DevKitC-1, two USB-C ports are
   provided: one wired to GPIO 19/20 (native USB), one to a UART bridge
   on GPIO 43/44. Generic clones vary — some wire their single USB-C only
   to a UART bridge (no native USB at all), some wire it to GPIO 19/20
   directly, some have both ports like the official board. **Verify with
   a multimeter on arrival**: continuity from the dev-board USB-C D+ pad
   to GPIO 20 and D- pad to GPIO 19. If GPIO 19/20 are not reachable
   through the on-board USB connector, the board still works for the
   medulla *only* if those GPIOs are exposed on the pin headers (so the
   medulla PCB can route them to its own USB-C connector toward the
   Orin). If 19/20 aren't broken out at all, the board is unsuitable.

3. **Physical footprint.** The medulla PCB headers (H1.1-22, H2.1-22)
   assume the Espressif **ESP32-S3-DevKitC-1** outline:
   - Board outline:           **25.40 mm × ~62.7 mm** (1000 mil × 2470 mil)
   - Pin pitch within a row:  **2.54 mm** (0.1 ″ / 100 mil)
   - Pins per row:            **22** (44 total)
   - Row-to-row centerline:   **22.86 mm** (0.9 ″ / 900 mil) —
                              pin holes sit **1.27 mm inside each PCB edge**,
                              so centerline spacing = PCB width − 2 × 1.27.
                              This is the standard Espressif DevKitC
                              footprint, kept consistent between the classic
                              ESP32-DevKitC and the S3-DevKitC-1.
   - USB-C connectors protrude ~8.00 mm past the bottom edge.

   **Confirmed by physical measurement on a teammate's official Espressif
   ESP32-S3-DevKitC-1 (2026-05-02):** caliper-imprecise centerline-to-
   centerline ≈ 24 mm, and the photo clearly shows pin centerlines inset
   from the PCB outline. 22.86 mm matches; 25.40 mm does not.

   Source documents (mirrored locally in `resources/esp32-s3-devkitc-1/`):
   - Espressif official mechanical drawing
     (`DXF_ESP32-S3-DevKitC-1_V1.1_20220429.pdf`) — board outline 25.40 mm
     and pin pitch 2.54 mm. The two `1.27 mm` callouts at the top of the
     drawing are most likely the edge-to-pin-row-centerline offsets,
     giving the 22.86 mm row spacing. The drawing is ambiguous enough
     that this was misread twice in 2026-05-01 → see `history.md` for
     the incident; trust the physical measurement and the 0.9 ″ DevKitC
     convention over any single PDF callout.
   - Espressif official schematic
     (`SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf`) — for USB / RGB / button
     wiring; not for mechanical dimensions.

   ⚠ **Do NOT trust the UIOPAL clone vendor drawing in `resources/`** for
   this measurement. It shows `1000 mil` and `1100 mil` callouts that
   were misinterpreted as PCB-vs-outer-envelope on 2026-05-01. The
   physical measurement on the official board contradicts that reading.
   The clone may have a different layout, or the labels were misread.

   Clones (AliExpress, etc.) mostly match the official 22.86 mm footprint
   but not always — row count, board length, and row spacing have all
   been seen to differ on no-name boards. Before committing to
   manufacturing the medulla PCB, place the actual dev board on a printed
   1:1 paper copy of the footprint and confirm every pin lands on its
   pad. Photos in listings are not reliable for this.



| Pin | Silkscreen | GPIO | Signal | Type | Notes |
|---|---|---|---|---|---|
| 1 | GND | - | GND | Power | Ground (bottom of right edge / RIGHT_HEADER pin 1) |
| 2 | GND | - | GND | Power | Ground |
| 3 | 19 | 19 | NC | - | No USB-C connector on the medulla PCB. GPIO 19 is brought to the header but unwired in this rev (Orin USB link goes elsewhere). Marked NC in schematic. |
| 4 | 20 | 20 | NC | - | Same as Pin 3 — no USB connector on this board, GPIO 20 unwired. |
| 5 | 21 | 21 | MOTOR_HALL_3 | Digital In | Motor hall sensor 3 |
| 6 | 47 | 47 | MOTOR_HALL_2 | Digital In | Motor hall sensor 2 |
| 7 | 48 | 48 | BLOCKED | - | Dev-module's on-board RGB LED. No external LED on the medulla PCB. NC in schematic, BLOCKED label. |
| 8 | 45 | 45 | HOLD | - | Strap pin (VDD_SPI voltage select, flash/boot risk). Reclaimable post-boot if signal's idle state matches the strap default (LOW for 3.3V flash). |
| 9 | 0 | 0 | HOLD | - | BOOT-mode strap pin (must be HIGH at boot for normal boot). Was previously assigned to `CMD_STEER_DIR` (signal moved to GPIO 17 on 2026-05-08 to remove the strap-pin risk from real signals). Reclaimable for any signal that is HIGH or high-Z at power-on. |
| 10 | 35 | 35 | HOLD | - | Octal-PSRAM pin. Internally reserved on the fitted N16R8 — unusable in practice. Kept as HOLD (not BLOCKED) because the layout also accepts a quad-PSRAM N8R2, where it would be free. |
| 11 | 36 | 36 | HOLD | - | Octal-PSRAM pin on N8R8 — same as Pin 10. (Was briefly assigned to CMD_REVERSE on 2026-05-02; moved to PCF8574 P0 on 2026-05-03 to restore N8R8 compatibility.) |
| 12 | 37 | 37 | HOLD | - | Octal-PSRAM pin on N8R8 — same as Pin 10. |
| 13 | 38 | 38 | HOLD | - | Unconstrained GPIO. Was `SDC_NOT_EMERGENCY` until 2026-05-08; signal moved to GPIO 18 (Pin 33) so Q3's gate driver could sit on the left side of the PCB next to the MOSFET. Currently free. |
| 14 | 39 | 39 | HOLD | - | Unconstrained GPIO. Earlier doc revisions described `SDC_ENABLE` here — that signal never existed in the schematic; the ESP32's contribution to the SDC chain is the GPIO driving Q3 directly (see Pin 33 / GPIO 18). |
| 15 | 40 | 40 | CMD_STEER_PWM | LEDC PWM | Steering motor PWM (Cytron H-bridge). |
| 16 | 41 | 41 | HOLD | - | Held for future CAN_RX (CAN currently moved to Orin carrier; medulla has no transceiver in this rev). |
| 17 | 42 | 42 | HOLD | - | Held for future CAN_TX (same as Pin 16). |
| 18 | 2 | 2 | HYDRAULIC_2 | ADC1_CH1 | Hydraulic pressure sensor 2 (input only) |
| 19 | 1 | 1 | PRESSURE_3 | ADC1_CH0 | Pressure sensor 3 (input only) |
| 20 | RX | 44 | BLOCKED | - | Owned by the dev-module's USB-UART bridge (UART0 RX0). Not reclaimable — the bridge IC drives this pin from the USB-C port of the DevKitC-1. |
| 21 | TX | 43 | BLOCKED | - | Same as Pin 20 — UART0 TX0, owned by the dev-module USB-UART bridge. |
| 22 | GND | - | GND | Power | Ground (top of right edge / RIGHT_HEADER pin 22) |
| 23 | 3V3 | - | 3V3 | Power | 3.3V supply (generated by S3 module LDO from 5V input) — top of left edge / LEFT_HEADER row 1 |
| 24 | 3V3 | - | 3V3 | Power | 3.3V supply |
| 25 | EN | - | RST | Reset | Reset (Espressif silkscreens this as `EN` for chip enable) |
| 26 | 4 | 4 | PEDAL_ACC | ADC1_CH3 | Accelerator pedal (input only) |
| 27 | 5 | 5 | PEDAL_BRAKE | ADC1_CH4 | Brake pedal |
| 28 | 6 | 6 | PRESSURE_1 | ADC1_CH5 | Pressure sensor 1 (input only) |
| 29 | 7 | 7 | PRESSURE_2 | ADC1_CH6 | Pressure sensor 2 (input only) |
| 30 | 15 | 15 | HOLD | - | Free and unassigned since 2026-08-08. It drove `SELECT_THROTTLE`, the SELECT pin of the U14 MAX4660 throttle mux; U14 was deleted from the schematic because a CMOS analog switch passes nothing while the board is unpowered (both channel MOSFETs are off), and because the kart's panel DPDT switch already selects the throttle source downstream on metal contacts that work unpowered. R32, the 10 kΩ pulldown on `SELECT_THROTTLE`, was deleted with it. No new function has been assigned to this pin. |
| 31 | 16 | 16 | MOTOR_HALL_1 | Digital In | Motor hall sensor 1 (moved from GPIO 37 for N8R8 compatibility) |
| 32 | 17 | 17 | CMD_STEER_DIR__3V3 | Digital Out | Steering motor direction (Cytron H-bridge). Moved here from GPIO 0 on 2026-05-08 to remove the BOOT-strap risk; now sits on the left side of the ESP32 alongside SDC_NOT_EMERGENCY. (UART1 TX default — but UART pins are remappable on ESP32-S3.) |
| 33 | 18 | 18 | SDC_NOT_EMERGENCY__3V3 | Digital Out | Drives the gate of Q3 (IRLZ44N) through R22 (100 Ω). When HIGH, Q3 conducts and pulls `SDC_IN_LOW_SIDE` to GND, completing the kart's SDC chain return path → no emergency. When LOW, Q3 is off and the SDC chain is broken → emergency. R23 (100 kΩ) gate-pulldown ensures Q3 is OFF (= emergency) at boot until firmware drives it HIGH. The signal name reads as the *intent* the ESP32 is asserting, not the chain's electrical state. Moved here from GPIO 38 on 2026-05-08 so the gate driver sits on the left side of the PCB next to the MOSFET. (UART1 RX default — remappable.) |
| 34 | 8 | 8 | SDA | I2C | I²C data — AS5600 steering angle sensor + PCF8574 I/O expander share this bus |
| 35 | 3 | 3 | BUZZER (old name) | Digital Out | Buzzer for debugging. Moved from GPIO 36 for octal-PSRAM compatibility. **Correction 2026-07-10:** this row used to claim "strap pin: JTAG src select, default high". Both halves are wrong on our hardware. (a) `STRAP_JTAG_SEL` eFuse is **not burned** (read from the chip), so GPIO 3 is never sampled as a strap. (b) GPIO 3 has **no internal pull at reset** — measured `IO_MUX_GPIO3 = 0x0a02` (neither FUN_WPU bit 8 nor FUN_WPD bit 7), against controls GPIO 0 = `0x0b02` (pull-up) and GPIO 45/46 = `0x0a82` (pull-down). It floats, so an external pulldown wins at boot. That makes GPIO 3 safe to drive a MOSFET gate — see the compressor reassignment in `history.md` 2026-07-10. |
| 36 | 46 | 46 | HOLD | - | Strap pin (ROM-print enable, flash/boot risk). Default LOW = no boot-message print, which is what we want. Reclaimable post-boot if signal's idle state is LOW at power-on. |
| 37 | 9 | 9 | SCL | I2C | I²C clock — same bus as SDA |
| 38 | 10 | 10 | HYDRAULIC_1 | ADC1_CH9 | Hydraulic pressure sensor 1 (input only) |
| 39 | 11 | 11 | MOSI | SPI | SPI data out (→ MCP4922 SDI). Also referred to as `OUT_SDI` in some parts of the schematic. |
| 40 | 12 | 12 | CLK | SPI | SPI clock (→ MCP4922 SCK). Also `OUT_SCK` in some schematic labels. |
| 41 | 13 | 13 | MISO | SPI | SPI data in. Unused by MCP4922 (write-only DAC); available for future SPI peripheral. |
| 42 | 14 | 14 | CMD_DAC_CS | SPI | MCP4922 chip select (active low). Also `OUT_CS` in some schematic labels. |
| 43 | 5V | - | +5V_USB | Power | 5V from USB VBUS via the medulla USB-C connector — powers the ESP32 dev board only (split-rail design, see history.md 2026-05-02). NOT connected to the L7805 +5V_REG rail. |
| 44 | GND | - | GND | Power | Ground (bottom of left edge / LEFT_HEADER row 22) |

## medulla-v2 pin allocation — decided 2026-07-31, as one table

Decided together rather than signal by signal, which is what let `PRESSURE_3` and `BUZZER` get
quietly repurposed on v1. Inputs to it: MT6701 stays on PWM, the MCP4922 stays as the throttle DAC,
and the op-amp keeps its 12 V rail (all Rubén, 2026-07-31).

**The constraint that drives the whole table: ADC1 is full.** On the ESP32-S3, ADC1 is GPIO 1–10 and
ADC2 is GPIO 11–20 — and ADC2 is unusable whenever WiFi is on, so in practice this board has exactly
**ten analog-capable pins**. v2 needs **seven** of them (`PEDAL_ACC`, `PEDAL_BRAKE`, `PRESSURE_1`,
`PRESSURE_2`, `PRESSURE_3`, `HYDRAULIC_1`, `HYDRAULIC_2`). All ten are currently occupied, four by
signals that are not analog at all: the steering-sensor PWM on GPIO 1, the compressor gate on GPIO 3,
and I²C on GPIO 8 and 9. Six analog + four squatters = ten, so restoring the third pressure channel
means evicting one squatter.

**Evict the steering sensor, not I²C.** Moving `STEER_SENS_PWM` from GPIO 1 to **GPIO 38** costs
nothing: GPIO 38 is an unconstrained HOLD today, is not a strap pin, is not on either ADC, and a PWM
capture input does not care which pin it sits on. That returns GPIO 1 to `PRESSURE_3`, its originally
designed use, and it is what `requirements.md` already asks for — the steering sensor gets a pin
chosen for it rather than inherited from a pressure channel. Moving I²C instead would work but
touches two pins and the firmware bus setup for no extra gain.

| GPIO | v2 signal | Why this pin |
|---|---|---|
| 1 | `PRESSURE_3` | ADC1_CH0. Returns to its designed use. |
| 2 | `HYDRAULIC_2` | ADC1_CH1, unchanged |
| 3 | `CMD_COMPRESSOR_PWM` | Unchanged, and deliberately: GPIO 3 floats at reset with no internal pull, so an external pulldown wins at boot. That is what makes it safe on a MOSFET gate. |
| 4 | `PEDAL_ACC` | ADC1_CH3, unchanged |
| 5 | `PEDAL_BRAKE` | ADC1_CH4, unchanged |
| 6 | `PRESSURE_1` | ADC1_CH5, unchanged |
| 7 | `PRESSURE_2` | ADC1_CH6, unchanged |
| 8 | `SDA` | I²C, unchanged. Costs an ADC1 pin but moving it buys nothing once the steering sensor has left. |
| 9 | `SCL` | I²C, unchanged |
| 10 | `HYDRAULIC_1` | ADC1_CH9, unchanged |
| 11 | `MOSI` | SPI to MCP4922, unchanged |
| 12 | `CLK` | SPI, unchanged |
| 13 | `MISO` | Unused — MCP4922 is write-only. Free pin, left as a spare. |
| 14 | `CMD_DAC_CS` | SPI chip select, unchanged |
| 15 | *free, unassigned* | Held `SELECT_THROTTLE` for the MAX4660 throttle mux until that mux (U14) was deleted from the schematic on 2026-08-08, together with its 10 kΩ pulldown R32. No replacement function is assigned. |
| 16 | `MOTOR_HALL_1` | unchanged |
| 17 | `CMD_STEER_DIR` | unchanged |
| 18 | `SDC_NOT_EMERGENCY` | Drives Q3's gate. Stays on a real pin — a safety read must not sit behind a bus transaction. |
| 21 | `MOTOR_HALL_3` | unchanged |
| 38 | **`STEER_SENS_PWM`** | **New.** MT6701 PWM angle capture, moved off GPIO 1. Unconstrained, no strap, not ADC. |
| 39 | *spare, reachable* | The remaining unconstrained GPIO, and genuinely unclaimed. `SDC_ENABLE` held a claim on it in earlier revisions; dropped 2026-08-01 — the shutdown loop is closed by Q3 off GPIO 18, and `SDC_ENABLE` was never a net. |
| 40 | `CMD_STEER_PWM` | unchanged |
| 41 | `CAN_RX` | Already reserved for CAN. Not ADC, not a strap pin. |
| 42 | `CAN_TX` | Already reserved for CAN. |
| 47 | `MOTOR_HALL_2` | unchanged |
| 0, 45, 46 | strap pins — leave HOLD | boot behaviour risk |
| 35, 36, 37 | unusable | octal PSRAM on the fitted N16R8 |
| 48 | BLOCKED | module's own RGB LED |
| 19, 20 | NC | USB pins, no connector on this board |

**No pin carries two signals, every strap pin is left alone, and the two ADC-capable pins spent on
non-analog signals (3 and 8/9) are spent deliberately.**

Two things this table does *not* solve, because they are connector capacity rather than GPIO
capacity: `SDC_ENABLE` still has no terminal to leave through, and CN4 gives the steering encoder its
two bus lines but neither power nor ground. See the connector audit in `tasks.md`.

**Firmware impact:** one pin number changes, `STEER_SENS_PWM` from GPIO 1 to GPIO 38. Everything else
keeps its current assignment.

## As-built pin use — board `84d6dd0`

**The table above is the *design*. This section is the *board that exists*, and it lists only the pins
whose real use differs.** Everything not listed here is used as the table says. Exceptions-only is
deliberate: a second full table would drift out of sync with the first one within a revision.

Physical modifications (cut traces, patch wires) are **not** here — they live in the per-board rework
list in [`../README.md`](../README.md), keyed to the same hash. This section is firmware-side pin
assignment; that one is copper. A person holding the board needs both.

| Pin | GPIO | Designed signal | Actual use on `84d6dd0` | Status |
|---|---|---|---|---|
| 19 | 1 | `PRESSURE_3` (ADC1_CH0) | **Reads the MT6701 steering-angle sensor's PWM output.** | Decided 2026-07-31 (Rubén). Pressure sensor 3 is not fitted on this board. |
| 35 | 3 | `BUZZER` (Digital Out) | **Drives the compressor MOSFET gate.** | Reassigned 2026-07-10 (see `../../../history.md`); and **permanent** — the kart carries no buzzer or ASSI at all (closed 2026-07-18; those are formula-vehicle only), so the `BUZZER` net name is historical. GPIO 3 floats at reset with no internal pull, so an external pulldown wins at boot — which is what makes it safe on a gate. |
| 13 | 38 | `HOLD` (unassigned) | **Planned:** raw ESP32 PWM → RC low-pass → U14 pin 8, as the throttle command, bypassing the SPI/MCP4922 path. | **Not done, and now obsolete.** It targeted the MAX4660 mux U14, which is fitted on this fabricated board but was deleted from the schematic on 2026-08-08 (a CMOS switch passes nothing unpowered, and the kart's panel DPDT switch already selects the throttle source downstream). The throttle command now leaves the board through the LM358 U1B gain stage instead. The 66 % shortfall this was meant to work around no longer exists: U1B now scales the DAC's 0–3.3 V up to 4.99 V before it leaves the board. |

Neither the pressure-3 sensor nor the buzzer is populated on this board, so both reassignments are
free — no signal was displaced. Record any further deviation here the day it is decided, not the day
the firmware is written; the point of this section is that someone probing the board can trust it.

## MCP4922 (dual 12-bit SPI DAC) — external chip connections on the PCB

| Pin | Signal | Connects to |
|---|---|---|
| VDD | +3V3 | 3.3 V rail. Moved from 5 V on 2026-08-01 (commit `16a35fb`): the MCP4922 datasheet DS22250A p7 sets VIH min = 0.7 × VDD, so a 5 V supply demanded 3.5 V on the SPI pins, which a 3.3 V ESP32 cannot reach. |
| VSS | GND | Ground |
| SHDN | +3V3 | Tied high (DAC always enabled) |
| LDAC | GND | Tied low → every SPI write latches to output immediately |
| CS | → ESP32 GPIO14 (CMD_DAC_CS) | |
| SCK | → ESP32 GPIO12 (CLK) | |
| SDI | → ESP32 GPIO11 (MOSI) | |
| VREFA | +3V3 via RC filter | 100 Ω series + 10 µF ceramic to GND, placed next to chip. Full scale on VOUTA is therefore 3.3 V. |
| VREFB | +3V3 via RC filter | 100 Ω series + 10 µF ceramic to GND (can share filter node). Full scale on VOUTB is therefore 3.3 V. |
| VOUTA | `CMD_ACC_ESP32__0_3V3` | Accelerator analog command, **0–3.3 V** at the DAC pin (U13 pin 14). It is amplified before leaving the board: U13 pin 14 → U1 pin 5 (LM358 U1B, +IN2), a non-inverting stage of gain 1.51 set by R37 5.1 kΩ and R38 10 kΩ, so full scale is **4.99 V** on U1 pin 7, which is the net `CMD_ACC__0_5V` and goes straight to CN10.1. This closes the earlier shortfall where a 3.3 V command reached only ~66 % of the motor controller's 0–5 V input range. |
| VOUTB | `CMD_PRES_DAC__0_3V3` | Pressure command, **0–3.3 V at the DAC pin**. It does not leave the board at that level: U1A (LM358) amplifies it ×3 (R19 2 kΩ / R20 1 kΩ) and CN10.2 exports **0–9.9 V** to the Festo VPPM proportional regulator. |

RC filter purpose: attenuates ~150 kHz switching ripple from the XW-1224 buck
by ~60 dB at the DAC reference pins. DAC VREF draws <100 µA so the 100 Ω
series resistor drops <10 mV (negligible vs 5V).

## Power architecture

```
Kart 12V battery ─┬─→ XW-1224 buck (external, 5A) ──→ 5V kart-wide rail
                  │                                   │
                  │                                   ├→ Medulla PCB 5V (H1.21)
                  │                                   │   │
                  │                                   │   ├→ ESP32-S3 module VIN ─→ module LDO ─→ 3.3V
                  │                                   │   └→ other on-board 3.3 V loads, including
                  │                                   │      MCP4922 VDD and its VREFA/VREFB filter
                  │                                   │
                  │                                   └→ other kart 5V loads
                  │
                  ├─→ L7805CDT linear regulator (U19, DPAK) ──→ the on-board +5V_REG rail.
                  │   THIS IS WHAT IS FITTED. Since the MAX4660 throttle mux U14 was deleted
                  │   from the schematic on 2026-08-08, this rail reaches only CN2 pin 3, plus
                  │   its own decoupling C3 (0.1 µF) and C4 (4.7 µF) — U14 was its only other
                  │   consumer. The MCP4922 (U13) moved to +3V3 on 2026-08-01 (commit 16a35fb).
                  │   The load is about 1 mA, 7 mW of heat, so a linear part is fine here. An
                  │   LM2596SX-ADJ buck (qty 8 in stock) was the alternative and was NOT taken;
                  │   settled 2026-07-31 against the schematic, where U19 = L7805CDT.
                  │
                  └─→ Cytron H-bridge 12V (steering driver) — permanently powered, NOT gated by
                      the manual/autonomous mode switch. Decision 2026-05-01: routing the Cytron
                      through the mode switch caused inrush brownouts on the Orin every time the
                      kart was switched to autonomous. See history.md (2026-05-01) for details.
                      The PCB only routes signals (CMD_STEER_PWM, CMD_STEER_DIR) to the Cytron,
                      not power. Firmware also commands PWM = 0 in manual — but that is a courtesy,
                      not the safety measure: the mode switch's second pole physically breaks the
                      cable from the Cytron to the steering motor in manual, so the motor is
                      disconnected regardless of what firmware does. Clarified 2026-08-08; the
                      earlier wording implied firmware was the only thing holding steering off.
```

## Manual/autonomous signal selection (throttle mux deleted 2026-08-08; I²C-driven reverse, decision 2026-05-01 / refined 2026-05-02 / brake-mux dropped 2026-05-08 / reverse moved to PCF8574 2026-05-03)

> **The MAX4660 throttle mux (U14) has been deleted from the schematic, on 2026-08-08.** Deleted with
> it: R32, the 10 kΩ pulldown on `SELECT_THROTTLE`, and C5, U14's local 100 nF decoupling capacitor.
> The part is still fitted on the fabricated v1 board. Two reasons for the removal:
>
> 1. **It is redundant.** The kart's panel DPDT mode switch already selects the throttle source
>    downstream of this board — the pedal or the medulla's `CMD_ACC__0_5V` on CN10.1 — so U14 was a
>    second selector in series doing the same job.
> 2. **It does not do what it was believed to do.** The design assumed U14 passed the pedal through
>    when the medulla was unpowered. It does not: it is a CMOS switch, so at V+ = 0 V both channel
>    MOSFETs are off and only ESD diodes remain, so the pedal is disconnected and instead backfeeds
>    the dead `+5V_REG` rail. "Normally closed" in the datasheet means closed at logic 0 **with power
>    applied**. The panel switch, with real metal contacts, is what actually provides the unpowered
>    manual path.
>
> The removal also resolves the open blocker that U14 ran from `+5V_REG` against a +9 V datasheet
> minimum, and it frees GPIO 15. The medulla now always outputs its autonomous throttle command and
> the panel switch decides whether anything listens. Full evidence in `history.md`, 2026-08-08.

The throttle analog signal is no longer muxed on this board: the path is MCP4922 U13 pin 14 (VOUTA,
0–3.3 V) → U1 pin 5 (LM358 U1B, +IN2), a non-inverting stage of gain 1.51 set by R37 5.1 kΩ and R38
10 kΩ giving 4.99 V full scale → U1 pin 7, the net `CMD_ACC__0_5V`, straight to CN10.1
(net `CMD_ACC__0_5V`). Brake is **not** muxed either — manual mode does not need brake control routed
through the ESP32, so the brake signal goes straight from the MCP4922 to the motor
electronics with no switch. The digital reverse signal does not use an analog switch
either — it is driven by **U25 PCF8574T port P0** (I²C GPIO expander, pin 4)
wired in parallel with the manual reverse button (wired-OR via the motor
controller's existing pull-up). The PCF8574's quasi-bidirectional outputs are
natively open-drain with a weak internal pull-up, so the wired-OR is electrically
correct without any extra components. Steering is NOT muxed (ESP32 drives the
Cytron directly; PWM = 0 in manual mode).

See `~/dv/kart/kart-medulla/history.md` for the full design history — entries
`2026-05-01` (initial PCB-mux design), `2026-05-02` (reverse refinement to
open-drain on a direct ESP32 GPIO), `2026-05-03` (reverse moved off the ESP32
onto PCF8574 P0 to free GPIO 36 and gain N8R8 compatibility), `2026-05-08`
(brake mux dropped).

| Chip / signal | Type | Manual source | Autonomous source | Output |
|---|---|---|---|---|
| **LM358 U1B, ×1.51 non-inverting (throttle)** | analog 0–3.3 V in, 0–4.99 V out | (n/a — the pedal reaches the motor electronics through the kart's panel DPDT switch, not through this board) | MCP4922 VOUTA (U13 pin 14) = `CMD_ACC_ESP32__0_3V3` | U1 pin 5 → U1 pin 7 (**R37 5.1 kΩ / R38 10 kΩ, gain 1.51**) → CN10.1 (`CMD_ACC__0_5V`). **No mux on the PCB** since U14 was deleted on 2026-08-08; the panel switch chooses between this output and the pedal. |
| **LM358 U1A, ×3 non-inverting (pressure)** | analog 0–3.3 V in, 0–9.9 V out | (n/a — manual brake bypasses ESP32) | MCP4922 VOUTB = `CMD_PRES_DAC__0_3V3` | LM358 U1A (**R19 2 kΩ / R20 1 kΩ, gain 3** as of 2026-08-01, because U13 now runs from +3V3) → `CMD_PRES__0_10V` → CN10.2 → Festo VPPM. **No mux on the PCB** — the DAC always owns the command and the only way to release it is to write zero. |
| **U25 PCF8574T pin 4 / P0** | digital | Manual reverse button (in parallel) | I²C-controlled `CMD_REVERSE` (open-drain via PCF8574) | → kart-electronics-box REVERSE wire |

No ESP32 GPIO selects the throttle source any more. GPIO 15 drove the deleted
MAX4660's SELECT pin through the net `SELECT_THROTTLE`, and is now free.

`CMD_REVERSE` is asserted by writing to PCF8574 port P0 over I²C (same bus as
`SDA__I2C` / `SCL__I2C` on ESP32 GPIO 8 / 9, shared with the AS5600 steering
sensor). The PCF8574 P0 output is in parallel with the manual reverse button.
The motor controller's REVERSE input already has its own pull-up to 5 V (that
is why the button works by pulling the line LOW). Both the button and P0 can
only sink to GND, never push HIGH actively → wired-OR with no electrical
conflict. Fail-safe property: ESP32 or I²C bus dead → P0 stays high-Z (or in
its power-on default state, all outputs high) → only the button controls the
line (identical to the current manual-only setup).

**Firmware note**: `CMD_REVERSE` is set/cleared by writing the PCF8574 output
register over I²C. The PCF8574 is quasi-bidirectional, so writing `1` releases
the line (high-Z + weak pull-up), writing `0` pulls it LOW. No special "open-drain"
mode flag needed — the chip is built that way. There is no longer a direct ESP32
GPIO-mode constraint for CMD_REVERSE.

### GPIO assignments (current schematic)

Module variant in use: **WROOM-1-N16R8** (16 MB flash, 8 MB octal PSRAM) —
verified on hardware 2026-07-10. The ESP32 GPIOs involved in manual/autonomous source selection:

| Signal | GPIO | Notes |
|---|---|---|
| *none* | 15 | Free and unassigned. It drove `SELECT_THROTTLE` into the MAX4660 (U14) SELECT pin until U14 and its 10 kΩ pulldown R32 were deleted from the schematic on 2026-08-08. |
| `SDA__I2C` / `SCL__I2C` | 8 / 9 | I²C bus shared by AS5600 (steering angle) and PCF8574 (GPIO expander, drives `CMD_REVERSE` and EXP_P1..P7). |

`CMD_REVERSE` no longer consumes an ESP32 GPIO directly. With the PCF8574
indirection the design is fully N8R8-compatible — no signal depends on the
quad-PSRAM-only GPIOs (33-37).

Other signals related to this design:
- `PEDAL_ACC__0_5V` (entering at CN6.2 — CN6.1 is `PEDAL_BRAKE__0_5V`) is read by the ESP32 via ADC and nothing else on this board. It used to branch inside the schematic to the NC pin of the MAX4660 mux U14 as the manual throttle source, but U14 was deleted on 2026-08-08 and the pedal now reaches the motor electronics only through the kart's panel DPDT switch, outside this board. There is no separate `MANUAL_THR` / `PEDAL_THR` signal. Same pattern for `MANUAL_BRK`: the brake mux was dropped 2026-05-08, so manual brake never enters the medulla; the manual brake source goes directly to the brake valve driver on the kart side.
- `CMD_STEER_PWM` (GPIO 40) and `CMD_STEER_DIR` (GPIO 0) — unchanged, feed the Cytron directly with no switch in between.
- `U12` (PC357N1J000F opto with planned BSS123 swap) for driving the kart REVERSE wire is now redundant — the ESP32 GPIO open-drain output drives the line directly. **TODO**: decide whether to remove U12 from the schematic or keep it as an inline buffer. Default plan: remove for simplicity.

### Datasheet references

Datasheets live in the shared `dv/datasheets/` folder (one canonical copy per part, indexed in `dv/datasheets/README.md`). Per-board project folders hold integration-specific docs only (e.g. `kart/kart-medulla/resources/esp32-s3-devkitc-1/` keeps mechanical drawings + the local clone-vendor PDF, not the chip datasheet itself).

- **MAX4660EUA+T** (U14, the throttle mux — deleted from the schematic 2026-08-08, still fitted on the fabricated v1 board): `dv/datasheets/max4660_analogdevices_datasheet.pdf` (mirrored 2026-05-02; canonical URL <https://www.analog.com/media/en/technical-documentation/data-sheets/MAX4659-MAX4660.pdf>).
- **L7805CDT** (U19, the fitted 12 V → 5 V regulator): <https://item.szlcsc.com/datasheet/L7805CDT/21968527.html>.
- **LM2596SX-ADJ** (evaluated, not fitted): `dv/datasheets/lm2596_ti_datasheet.pdf` (mirrored 2026-05-02).

---

# Legacy: classic ESP32 (previous board, kept for reference)

| Pin | Header | GPIO | Signal | Type | Notes |
|---|---|---|---|---|---|
| 1 | H1.1 | 6 | RESERVED | - | FLASH/SDIO |
| 2 | H1.2 | 7 | RESERVED | - | FLASH/SDIO |
| 3 | H1.3 | 8 | RESERVED | - | FLASH/SDIO |
| 4 | H1.4 | 15 | RESERVED | - | STRAP pin (boot config risk) |
| 5 | H1.5 | 2 | STATUS_LED | Digital Out | Onboard LED (strap pin, keep LOW at boot) |
| 6 | H1.6 | 0 | RESERVED | - | STRAP pin (BOOT mode) |
| 7 | H1.7 | 4 | RESERVED | - | STRAP pin (boot config risk) |
| 8 | H1.8 | 16 | MOTOR_HALL_3 | Digital In | Motor hall sensor 3 (also UART2 RX) |
| 9 | H1.9 | 17 | MOTOR_HALL_1 | Digital In | Motor hall sensor 1 (also UART2 TX) |
| 10 | H1.10 | 5 | RESERVED | - | STRAP pin (boot config risk) |
| 11 | H1.11 | 18 | CMD_STEER_PWM | LEDC PWM | Steering motor PWM (Cytron H-bridge) |
| 12 | H1.12 | 19 | CMD_STEER_DIR | Digital Out | Steering motor direction (Cytron H-bridge) |
| 13 | H1.13 | - | GND | Power | Ground |
| 14 | H1.14 | 21 | I2C_SDA | I2C | AS5600 steering angle sensor data |
| 15 | H1.15 | 3 | USB_UART_RX | UART0 RX | Reserved (binary protocol from Orin) |
| 16 | H1.16 | 1 | USB_UART_TX | UART0 TX | Reserved (binary protocol to Orin) |
| 17 | H1.17 | 22 | I2C_SCL | I2C | AS5600 steering angle sensor clock |
| 18 | H1.18 | 23 | SPARE | - | Available |
| 19 | H1.19 | - | GND | Power | Ground |
| 20 | H2.1 | - | 3V3 | Power | 3.3V supply |
| 21 | H2.2 | - | EN | Reset | Active-low reset |
| 22 | H2.3 | 36 (VP) | PRESSURE_1 | ADC1_CH0 | Pressure sensor 1 (input only) |
| 23 | H2.4 | 39 (VN) | PRESSURE_2 | ADC1_CH3 | Pressure sensor 2 (input only) |
| 24 | H2.5 | 34 | PRESSURE_3 | ADC1_CH6 | Pressure sensor 3 (input only) |
| 25 | H2.6 | 35 | PEDAL_ACC | ADC1_CH7 | Accelerator pedal (input only) |
| 26 | H2.7 | 32 | PEDAL_BRAKE | ADC1_CH4 | Brake pedal |
| 27 | H2.8 | 33 | MOTOR_HALL_2 | Digital In | Motor hall sensor 2 |
| 28 | H2.9 | 25 | CMD_ACC | DAC1 | Throttle analog output (0-255) |
| 29 | H2.10 | 26 | CMD_BRAKE | DAC2 | Brake analog output (0-255) |
| 30 | H2.11 | 27 | HYDRAULIC_1 | ADC2_CH7 | Hydraulic pressure sensor 1 |
| 31 | H2.12 | 14 | HYDRAULIC_2 | ADC2_CH6 | Hydraulic pressure sensor 2 |
| 32 | H2.13 | 12 | RESERVED | - | STRAP pin (flash/boot risk) |
| 33 | H2.14 | - | GND | Power | Ground |
| 34 | H2.15 | 13 | SDC_NOT_EMERGENCY | Digital In | Shutdown circuit emergency status |
| 35 | H2.16 | 9 | RESERVED | - | FLASH/SDIO |
| 36 | H2.17 | 10 | RESERVED | - | FLASH/SDIO |
| 37 | H2.18 | 11 | RESERVED | - | FLASH/SDIO |
| 38 | H2.19 | - | 5V | Power | 5V supply |
