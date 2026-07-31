<!-- reference — read when scoping a board revision -->

# kart-medulla — requirements

What the board must do. Durable: survives revisions and task pruning.

- **This file** = the target (what the board must do, what the next revision must add).
- **`tasks.md`** (next to this file) = the work for this board (pruned as items are done).
  The cross-board board is the repo root `tasks.md`, which indexes it.
- **`pinout-esp32-s3.md` / `pinout-cn-connectors.md`** = the as-built pin-by-pin reality.

Signals are named here, never pin-mapped — pin assignments live in the pinout docs only.

## Functional requirements (V1, as-built)

Original brief, posted in the Driverless Telegram chat 2025-12-13 as "Apuntes de la pcb",
attributed there to Eduardo. Recovered 2026-07-16 from the chat export; it had never been
committed anywhere. The export flattens its HTML, so the attribution is what the export shows
and is not independently confirmed. The board built from this brief exists and is assembled.

- Carry the ESP32 and make connections easier with wago-like push-in connectors, not
  arduino-style dupont
- Read 3× 5 V digital from the motor hall sensors, level-translated to 3.3 V
- Read 3× 0–10 V analog from the Festo pressure sensors (voltage divider may suffice)
  — **still three. Confirmed 2026-07-31 by Rubén**, overriding the 2026-07-18 reading that dropped
  it to two. On the as-built board only two work: `PRESSURE_3` (GPIO 1, CN5.2) was repurposed to
  read the steering sensor's PWM angle output. That repurpose stands, so V2 must find the third
  pressure channel a *new* GPIO, ADC divider and connector pin rather than take GPIO 1 back.
- Write 5 V analog for the kart accelerator
- Write the signal for the Festo actuators / servo braking
- Hold a normally-open relay able to cut the shutdown circuit on condition

## Mandatory (rules)

- ~~**ASSI / AS-emergency buzzer** — FS-Rules DV 4.5~~ — **NOT A REQUIREMENT FOR THIS BOARD.**
  Rubén, 2026-07-18: *the kart will not carry a buzzer or ASSI; those are for the formula vehicle
  only.* So this section has no mandatory items for kart-medulla.

  Two consequences, both of which unblock things that were previously flagged as conflicts:
  - **GPIO 3 / CN8.2 belongs to the compressor permanently**, not on loan. The `BUZZER` name on
    that net is purely historical, and nothing needs to be found a new home before fab.
  - The buzzer parts already in inventory (CPT-407-105-L60 x5, RE46C100S8F x10) and the SPL
    bench-measurement work belong to the **formula vehicle**, not here. Kept in
    `tasks.md` marked not-applicable rather than deleted, so the research is not lost
    if that vehicle needs it.

## V2 target — next revision

Moved here from the board's task list on 2026-07-16 so it outlives it.

- **Switch CN1–CN10 to WAGO 2601-31xx, placed correctly** — the fitted Phoenix 1990012 is rated
  2 A and v2 carries the compressor's 6 A, so the connector family changes to the team's WAGO
  standard (17.5 A, 3.5 mm pitch, top entry). This replaces the earlier "rotate the push-in
  connectors" requirement: swapping the part makes rotating the old one moot, and the two things
  that requirement wanted become placement rules for the new footprints — **wires exit outward,
  away from the board, and pin numbering runs co-directional with the CN numbering on each side.**
  Note the pitch change from 2.5 mm widens every connector and affects the board outline
- **On-board compressor switching, motor current included** — reconfirmed 2026-07-31: integrate
  it, the less wiring the better. V2 carries the MOSFET, its gate drive, the flyback diode and the
  bulk capacitance, copying the already-validated module circuit (bridge rectifier removed, 330 Ω
  optocoupler LED resistor for 3.3 V drive). This is a power-section change before it is a
  component addition: `+12V` and the motor return must be re-sized from the ~1 mA they carry today,
  and CN1–CN10's 2 A Phoenix terminals replaced on that path — see "Contradictions to resolve
  before V2" item 3 below and [`../../docs/connectors.md`](../../docs/connectors.md)
- **Separate power/signal GND** — distinct net classes for Power GND (compressor, heavy
  actuators) and Signal GND (ESP32, logic)
- **Reachable spare GPIOs** — bring at least two unassigned, PWM-capable, non-strap GPIOs out
  to terminals on every revision. From 2026-07-10: *a spare pin you cannot reach with a
  screwdriver is not a spare pin.* Concretely, route GPIO 38 → CN3.1 and GPIO 39 → CN3.2; the
  first is the intended `CMD_COMPRESSOR_PWM`
- **Full 0–10 V swing on the pressure-command amplifier** — the brake command chain is the
  MCP4922 DAC (0–5 V) → an LM358 ×2 non-inverting stage (U1) → the Festo VPPM proportional
  valve. U1 is supplied from +12 V and the LM358 is not rail-to-rail: TI SLOS068AB §5.7 gives
  3 V max swing from the positive rail, so a worst-case part reaches only 9 V where the valve
  wants 10 V, and the kart's unregulated 12 V sagging under load pushes that lower. Accepted on
  the as-built board (the VPPM is ~1 bar per volt, so it costs the top ~1 bar of a range the kart
  does not use) but the next revision should deliver the full range — either supply U1 from 24 V,
  or fit a rail-to-rail-output op-amp in the same SOIC-8 footprint. Until it is fixed, firmware
  must not treat DAC full scale as 10 bar: the achievable maximum varies between boards, so any
  target above ~9 bar needs closed-loop control against a pressure sensor. Full working and the
  trade-off between the two fixes: "Give the pressure-command amplifier full 0–10 V swing on the
  next board revision" in [`tasks.md`](tasks.md).

### V2 — make the steering-sensor input a first-class signal, not a repurposed one

Decided 2026-07-18. On the built board the steering sensor's PWM angle output is read on GPIO 1,
the pin silkscreened `PRES3` on CN5.2. That works, but every name still says "pressure sensor 3",
so the schematic, the netlist, the silkscreen and the firmware all describe something the board
does not do. For V2:

- **Rename the net and the silkscreen** to what it is — e.g. `STEER_SENS_PWM` — across the
  schematic, `pinout-esp32-s3.md`, `pinout-cn-connectors.md` and the firmware pin map.
- **Drop the ADC divider** on that input. It was drawn for an 0–10 V analog sensor; the steering
  sensor is a 3.3 V logic PWM output and does not want a divider in front of it.
- **Provision a proper PWM-capable input for the steering sensor**, chosen deliberately rather
  than inherited from a pressure channel. Note the sensor itself is not settled — AS5600, MT6701
  and MA732 are all under evaluation (datasheets in the `kart-medulla` repo), and MT6701/MA732
  offer SSI/SPI as well as PWM, so the pin choice should not foreclose that.
- **Restore the third pressure channel on a new pin.** Decided 2026-07-31: three pressure inputs
  remain a requirement, and GPIO 1 is not coming back, so V2 needs a different ADC-capable GPIO for
  `PRESSURE_3`, its own 0–10 V divider, and a connector pin. Scope this alongside the steering
  sensor's pin choice so the two don't compete for the same GPIO.

### Contradictions to resolve before V2 — do not action either item as written

Both were written 2025-12/2026-07 and conflict with requirements above. Flagged 2026-07-16;
Rubén decides.

1. ~~**"Repurpose BUZZER for compressor PWM"**~~ — **RESOLVED 2026-07-18.** Not a conflict: the
   kart carries no buzzer or ASSI (formula vehicle only), so nothing was displaced. GPIO 3 /
   CN8.2 is the compressor's permanently and the `BUZZER` name on that net is historical.
2. ~~**"Repurpose PRESSURE_3 for steering PWM"**~~ — **RESOLVED 2026-07-31**, refining the
   2026-07-18 answer. The repurpose itself is not a conflict: it is *already done on the built
   board*, deliberately, and GPIO 1 / CN5.2 reads the steering sensor's PWM angle output. What the
   2026-07-18 note got wrong was concluding the third pressure sensor is dropped. Rubén 2026-07-31:
   **three pressure channels stay a requirement.** So V2 keeps the steering sensor on its own pin
   *and* provisions a new GPIO, divider and terminal for `PRESSURE_3`. Both V2 items above are
   written accordingly.

3. ~~**The three compressor items (MOSFET, flyback diode, bulk caps) assume the board carries
   motor power. It does not.**~~ — **RESOLVED 2026-07-31 (Rubén): v2 integrates the compressor
   switching stage, motor current and all.** The observation that raised this on 2026-07-16 was
   correct about the board as built — `+12V` enters at CN1 pin 2 and feeds only the on-board
   regulator for the logic/analog rail, roughly **1 mA, 7 mW**, with copper sized for that. The
   answer is to change the copper, not to keep the compressor off the board: *the less wiring, the
   better*, and the kart currently runs two boxes that v2 is meant to collapse into one.

   **What makes it tractable is that the circuit already exists and is validated.** The compressor
   MOSFET module in service has had its **bridge rectifier removed** and the **series resistor
   feeding the optocoupler's LED changed to 330 Ω**, which makes its input work when driven from
   3.3 V. It works, and more of the same modules are in stock. v2 copies that circuit onto the PCB
   rather than designing a fresh gate-drive stage. The module has to be identified and its schematic
   traced first — see the compressor task in `tasks.md`.

   **What v2 must get right:**
   - **Track and via sizing.** `+12V` and the motor return are drawn today for a ~1 mA supply. They
     must be re-drawn (or poured) for a stated design current, with the via count to match, and that
     current written down. No component addition fixes copper sized for a different job — Rubén's
     emphasis: this is the important part.
   - **A connector rated for the load.** The compressor measured **6 A running at 60 % duty**
     (bench, 2026-07-18). The Phoenix 1990012 terminals fitted as CN1–CN10 are rated **2 A** and
     cannot carry it. The **WAGO 2601-3103** already on the buy list is rated **17.5 A** and can.
     Deutsch **DT** (13 A per size-16 contact) is the team's harness standard if a sealed connector
     is wanted; **DTM** at 7.5 A is tight. Soldering the wire straight to the board is an accepted
     fallback. Ratings and sources: [`../../docs/connectors.md`](../../docs/connectors.md).
   - **Nothing is gained by measuring locked-rotor inrush.** Decided 2026-07-31: the circuit is
     validated in service and over-sizing costs nothing when the parts are already in stock. Size
     generously from what is on the shelf instead of measuring the peak and designing to it.

   Unrelated discrepancy found while checking this, now closed: the task list specified an **L7805
   linear** regulator (decision 2026-05-02) while the `docs/pinout-esp32-s3.md` power architecture
   showed an **LM2596SX-ADJ buck**. Settled 2026-07-31 against the schematic — `U19` is an
   **L7805CDT** in a DPAK, so the L7805 is what is fitted and the LM2596 was an alternative never
   taken. The pinout docs say so now.
