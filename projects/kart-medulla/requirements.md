<!-- reference — read when scoping a board revision -->

# kart-medulla — requirements

What the board must do. Durable: survives revisions and task pruning.

- **This file** = the target (what the board must do, in every revision).
- **`tasks.md`** (next to this file) = the work for this board (pruned as items are done).
  The cross-board board is the repo root `tasks.md`, which indexes it.
- **`pinout-esp32-s3.md` / `pinout-cn-connectors.md`** = the as-built pin-by-pin reality.

Signals are named here, never pin-mapped — pin assignments live in the pinout docs only.

`[built]` means the assembled board already meets it and the next revision must not lose it.
`[v2]` means the next revision has work to do. Every requirement links to its entry in
[Notes](#notes), which carries the reasoning, the numbers and the traps — read that entry
before drawing the thing. Cite requirements elsewhere by ID, not by quoting the line, so
rewording here does not break the reference.

## Requirements

- **REQ-01 — Push-in terminal connectors, rated for what they carry.** No dupont. WAGO
  2601-31xx, wires exiting outward, pin numbering co-directional with CN numbering on each
  side. `[v2]` [Why](#req-01)
- **REQ-02 — Read 3 motor hall sensors.** 5 V digital, level-translated to 3.3 V. `[built]`
  [Why](#req-02)
- **REQ-03 — Read 3 Festo pressure sensors.** 0–10 V analog. `[v2]` [Why](#req-03)
- **REQ-04 — Write the kart accelerator command.** 5 V analog. `[built]` [Why](#req-04)
- **REQ-05 — Write the Festo brake-valve command, across its full 0–10 V range.** `[v2]`
  [Why](#req-05)
- **REQ-06 — Cut the shutdown circuit on command.** `[built]` [Why](#req-06)
- **REQ-07 — Give the steering sensor its own PWM-capable input.** GPIO 38, no divider and no
  filter capacitor. `[v2]` [Why](#req-07)
- **REQ-08 — Every output that can move the kart reaches its safe state through a component,
  not through code.** Pulldowns on `CMD_STEER_PWM` and `CMD_STEER_DIR`. `[v2]` [Why](#req-08)
- **REQ-09 — Separate power and signal ground.** Distinct net classes for Power GND
  (compressor, heavy actuators) and Signal GND (ESP32, logic). `[v2]` [Why](#req-09)
- **REQ-10 — Bring at least two spare GPIOs out to terminals.** Unassigned, PWM-capable,
  non-strap. `[v2]` [Why](#req-10)
- **REQ-11 — Switch the EBS compressor on the board, motor current included.** `[v2]`
  [Why](#req-11)

**Explicitly not a requirement:** an ASSI or AS-emergency buzzer. FS-Rules DV 4.5 applies to
the formula vehicle, not this kart — Rubén, 2026-07-18. The `BUZZER` net name on GPIO 3 /
CN8.2 is historical; that pin is the compressor's permanently.

<a id="notes"></a>

## Notes

<a id="req-01"></a>

### REQ-01 — Push-in terminal connectors, rated for what they carry

From the original brief: carry the ESP32 and make connections easier with wago-like push-in
connectors, not arduino-style dupont.

The fitted Phoenix 1990012 is rated 2 A and v2 carries the compressor's 6 A, so the connector
family changes to the team's WAGO standard (17.5 A, 3.5 mm pitch, top entry). This replaces an
earlier "rotate the push-in connectors" requirement: swapping the part makes rotating the old
one moot, and the two things that requirement wanted become placement rules for the new
footprints — **wires exit outward, away from the board, and pin numbering runs co-directional
with the CN numbering on each side.** Note the pitch change from 2.5 mm widens every connector
and affects the board outline.

<a id="req-02"></a>

### REQ-02 — Read 3 motor hall sensors

5 V digital, level-translated to 3.3 V. From the original brief; met by the assembled board.

<a id="req-03"></a>

### REQ-03 — Read 3 Festo pressure sensors

0–10 V analog, a voltage divider may suffice. **Still three. Confirmed 2026-07-31 by Rubén**,
overriding a 2026-07-18 reading that dropped it to two.

On the assembled board only two work: `PRESSURE_3` (GPIO 1, CN5.2) was repurposed to read the
steering sensor's PWM angle output. On v2 that pin goes back to `PRESSURE_3` and the steering
sensor moves to GPIO 38 — see [REQ-07](#req-07) and the v2 pin allocation in
`docs/pinout-esp32-s3.md`.

An earlier version of this said the opposite, that GPIO 1 was not coming back and the third
pressure channel needed a new pin. That is not possible: ADC1 is GPIO 1–10 and ADC2 is unusable
with WiFi on, so there are exactly ten analog-capable pins, and seven analog inputs plus the
compressor gate on GPIO 3 and I²C on GPIO 8/9 already fills them. Something non-analog has to
leave ADC1, and the steering PWM is the one that costs nothing to move.

<a id="req-04"></a>

### REQ-04 — Write the kart accelerator command

5 V analog. From the original brief; met by the assembled board.

<a id="req-05"></a>

### REQ-05 — Write the Festo brake-valve command, across its full 0–10 V range

The brake command chain is the MCP4922 DAC (0–3.3 V, since U13 moved to +3V3 on 2026-08-01) →
an LM358 ×3 non-inverting stage (U1, R19 2 kΩ / R20 1 kΩ) → the Festo VPPM proportional valve.
U1 is supplied from +12 V and the LM358 is not rail-to-rail: TI SLOS068AB §5.7 gives 3 V max
swing from the positive rail, so a worst-case part reaches only 9 V where the valve wants 10 V,
and the kart's unregulated 12 V sagging under load pushes that lower.

Accepted on the assembled board (the VPPM is ~1 bar per volt, so it costs the top ~1 bar of a
range the kart does not use) but the next revision should deliver the full range — either supply
U1 from 24 V, or fit a rail-to-rail-output op-amp in the same SOIC-8 footprint. Until it is
fixed, firmware must not treat DAC full scale as 10 bar: the achievable maximum varies between
boards, so any target above ~9 bar needs closed-loop control against a pressure sensor. Full
working and the trade-off between the two fixes: "Give the pressure-command amplifier full
0–10 V swing on the next board revision" in [`tasks.md`](tasks.md).

<a id="req-06"></a>

### REQ-06 — Cut the shutdown circuit on command

The original brief asked for a normally-open relay able to cut the shutdown circuit on
condition. The assembled board does it with a MOSFET instead of a relay (Q3, IRLZ44N, gate
pulled low by R23 so the chain sits open until firmware drives it) — the requirement is the
function, not the part.

<a id="req-07"></a>

### REQ-07 — Give the steering sensor its own PWM-capable input

Decided 2026-07-18. On the assembled board the steering sensor's PWM angle output is read on
GPIO 1, the pin silkscreened `PRES3` on CN5.2. That works, but every name still says "pressure
sensor 3", so the schematic, the netlist, the silkscreen and the firmware all describe something
the board does not do. For v2:

- **Rename the net and the silkscreen** to what it is — e.g. `STEER_SENS_PWM` — across the
  schematic, `pinout-esp32-s3.md`, `pinout-cn-connectors.md` and the firmware pin map.
- **Drop the ADC divider** on that input. It was drawn for an 0–10 V analog sensor; the steering
  sensor is a 3.3 V logic PWM output and does not want a divider in front of it.
- **Choose the pin deliberately** rather than inheriting it from a pressure channel. The sensor
  itself is not settled — AS5600, MT6701 and MA732 are all under evaluation (datasheets in the
  `kart-medulla` repo), and MT6701/MA732 offer SSI/SPI as well as PWM, so the pin choice should
  not foreclose that.
- **`STEER_SENS_PWM` moves to GPIO 38**, amended 2026-07-31 after the ADC1 count in
  [REQ-03](#req-03). GPIO 38 is unconstrained, is not a strap pin and is on neither ADC, so a PWM
  capture input wastes nothing there. `PRESSURE_3` returns to GPIO 1 with the divider it already
  has.
- **GPIO 38 must get no divider and no filter capacitor.** A 1/3 divider puts a 3.3 V logic high
  at 1.100 V against the ESP32's 2.475 V VIH, and 100 nF against that source impedance gives a
  239 Hz corner on a 994.4 Hz PWM frame. Both are correct for an analog pressure input and fatal
  for a logic-level one.

<a id="req-08"></a>

### REQ-08 — Every output that can move the kart reaches its safe state through a component

Raised 2026-08-08, after the steering swung to full lock and broke teeth off the steering gears
while the ESP32-S3 was being reflashed. The kart was in autonomous at the time and the motor was
live: the Cytron H-bridge is fed permanently from the 48 V traction pack, deliberately, so it is
powered whenever the kart is.

The board treats its actuators inconsistently, and steering is on the wrong side of the split:

- **Throttle is safe.** It passes through the MAX4660 mux (U14), whose `SELECT_THROTTLE` line
  carries a 10 kΩ pulldown (R32) to GND. An ESP32 that is unbooted, resetting, crashed or removed
  leaves the mux in manual passthrough — the driver's pedal — by physics.
- **The compressor is safe.** Its MOSFET gate has a 100 kΩ pulldown holding it off through boot.
- **Steering is not.** `CMD_STEER_PWM` and `CMD_STEER_DIR` run from the ESP32 to the Cytron with
  nothing in between and no pull resistors, so whenever the ESP32 is not actively driving them
  the motor's behaviour is whatever the floating lines happen to look like to the Cytron's
  inputs. The only thing that has ever held steering off is firmware writing zero — which does
  not exist during a reset, and a reset is part of every flash.

So: a pulldown to GND on `CMD_STEER_PWM` and on `CMD_STEER_DIR`, sized like R32 rather than
relying on the ESP32's internal pulls — the internal ones are ~45 kΩ and, more importantly, only
exist once firmware has configured them, which is exactly the window that broke the gears. Place
them at the Cytron end of each net so an unplugged connector is also covered.

Check when drawing it: the firmware drives the Cytron in sign-magnitude mode, PWM duty for
magnitude and a separate DIR pin for sign, so a low PWM line means the motor is off. **Verify the
Cytron's mode-select switches actually select that mode.** Under a locked-antiphase scheme a low
PWM line means full reverse, and the pulldown would cause the failure it is meant to prevent.

Ask the same question of every other output on the board before fab, not just this one: for each,
what does the kart do while the ESP32 is held in reset? Any answer other than "nothing" needs a
resistor.

Firmware has been changed alongside this (kart-medulla `2092130`) to drive both steering pins low
as the first action of `KM_GPIO_Init` and enable their internal pulldowns. That shortens the
undriven window to the earliest instant code can act, and does not close it — the bootloader
window remains, and only the external resistors cover it.

<a id="req-09"></a>

### REQ-09 — Separate power and signal ground

Distinct net classes for Power GND (compressor, heavy actuators) and Signal GND (ESP32, logic).

<a id="req-10"></a>

### REQ-10 — Bring at least two spare GPIOs out to terminals

Unassigned, PWM-capable, non-strap, on every revision. From 2026-07-10: *a spare pin you cannot
reach with a screwdriver is not a spare pin.* Concretely, route GPIO 38 → CN3.1 and GPIO 39 →
CN3.2; the first is the intended `CMD_COMPRESSOR_PWM`.

<a id="req-11"></a>

### REQ-11 — Switch the EBS compressor on the board, motor current included

Reconfirmed 2026-07-31: integrate it, the less wiring the better. V2 carries the MOSFET, its gate
drive, the flyback diode and the bulk capacitance, copying the already-validated module circuit
(bridge rectifier removed, 330 Ω optocoupler LED resistor for 3.3 V drive).

This is a power-section change before it is a component addition. The assembled board takes `+12V`
in at CN1 pin 2 and feeds only the on-board regulator for the logic/analog rail, roughly **1 mA,
7 mW**, with copper sized for that. The answer is to change the copper, not to keep the compressor
off the board: *the less wiring, the better*, and the kart currently runs two boxes that v2 is
meant to collapse into one.

**What makes it tractable is that the circuit already exists and is validated.** The compressor
MOSFET module in service has had its **bridge rectifier removed** and the **series resistor
feeding the optocoupler's LED changed to 330 Ω**, which makes its input work when driven from
3.3 V. It works, and more of the same modules are in stock. V2 copies that circuit onto the PCB
rather than designing a fresh gate-drive stage. The module has to be identified and its schematic
traced first — see the compressor task in [`tasks.md`](tasks.md).

**What v2 must get right:**

- **Track and via sizing.** `+12V` and the motor return are drawn today for a ~1 mA supply. They
  must be re-drawn (or poured) for a stated design current, with the via count to match, and that
  current written down. No component addition fixes copper sized for a different job — Rubén's
  emphasis: this is the important part.
- **A connector rated for the load**, which is what [REQ-01](#req-01) is for. The compressor
  measured **6 A running at 60 % duty** (bench, 2026-07-18). The Phoenix 1990012 terminals fitted
  as CN1–CN10 are rated **2 A** and cannot carry it. The **WAGO 2601-3103** already on the buy list
  is rated **17.5 A** and can. Deutsch **DT** (13 A per size-16 contact) is the team's harness
  standard if a sealed connector is wanted; **DTM** at 7.5 A is tight. Soldering the wire straight
  to the board is an accepted fallback. Ratings and sources:
  [`../../docs/connectors.md`](../../docs/connectors.md).
- **Nothing is gained by measuring locked-rotor inrush.** Decided 2026-07-31: the circuit is
  validated in service and over-sizing costs nothing when the parts are already in stock. Size
  generously from what is on the shelf instead of measuring the peak and designing to it.
