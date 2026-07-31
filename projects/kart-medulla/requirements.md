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

- **Rotate the push-in connectors** — wires exit outward, away from the board, and pin
  numbering runs co-directional with the CN numbering on each side
- **Compressor: control signal only, not motor power** — decided 2026-07-31. V2 routes the
  compressor's gate signal out to a terminal and nothing else; the MOSFET, its flyback diode and
  the bulk capacitance stay off-board at the compressor, because the board's `+12V` is a ~1 mA
  logic feed with copper sized for that. Bringing motor power on-board is wanted eventually but is
  a power-section redesign — see "Contradictions to resolve before V2" item 3 below for what it
  has to get right (copper sizing first, then a connector rated above the measured 6 A)
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
   motor power. It does not.**~~ — **RESOLVED 2026-07-31 (Rubén): signals only for now, power
   on-board later.** Raised 2026-07-16. `+12V` enters at CN1 pin 2 and only feeds the on-board
   regulator for the logic/analog rail — roughly **1 mA, 7 mW**. The compressor MOSFET switches
   low-side, so the motor's + terminal is fed from the battery externally and only the return would
   pass through the board.

   **The decision.** The next revision carries the compressor's *control signal* only, matching the
   board's existing precedent for the steering driver ("The PCB only routes signals
   (CMD_STEER_PWM, CMD_STEER_DIR) to the Cytron, not power" — `docs/pinout-esp32-s3.md`). The
   MOSFET, flyback diode and bulk capacitance stay off-board at the compressor. Motor power **is**
   intended to come on-board in a later revision, so that revision is a power-section redesign
   scoped as one job, not three improvement bullets bolted onto a signal board.

   **What that later revision must get right,** decided at the same time:
   - **Track and via sizing is the blocker, and it is the important part.** `+12V` and the motor
     return are drawn today for a ~1 mA logic supply. They must be re-drawn (or poured) for a
     stated design current, with the via count to match, and that current written down. No
     component addition fixes copper sized for a different job.
   - **The connector must be rated for the load.** The compressor measured **6 A running at 60 %
     duty** (bench, 2026-07-18). The Phoenix 1990012 push-in terminals fitted to CN1–CN10 are rated
     **2 A** — 3× under, so compressor current must not go through them. The **WAGO 2601-3103**
     the team already stocks is rated **17.5 A** and clears it comfortably. If a sealed harness
     connector is wanted instead, the team standard is the **Deutsch DT family** (DT size-16
     contacts 13 A; DTM size-20 contacts 7.5 A, which is tight for this load). Soldering the wire
     directly to the board is an accepted fallback. Ratings, sources and the worked example:
     [`../../docs/connectors.md`](../../docs/connectors.md).
   - **Measure locked-rotor inrush before designing it.** Only the running current is known. The
     stall peak is what sizes the MOSFET, the flyback path and the copper.

   Unrelated discrepancy found while checking this, now closed: the task list specified an **L7805
   linear** regulator (decision 2026-05-02) while the `docs/pinout-esp32-s3.md` power architecture
   showed an **LM2596SX-ADJ buck**. Settled 2026-07-31 against the schematic — `U19` is an
   **L7805CDT** in a DPAK, so the L7805 is what is fitted and the LM2596 was an alternative never
   taken. The pinout docs say so now.
