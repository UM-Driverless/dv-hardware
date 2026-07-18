<!-- reference — read when scoping a board revision -->

# kart-medulla — requirements

What the board must do. Durable: survives revisions and task pruning.

- **This file** = the target (what the board must do, what the next revision must add).
- **`../../../tasks/kart-medulla.md`** = the work for this board (pruned as items are done).
  The repo-wide board is the root `tasks.md`, which indexes it.
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
- Write 5 V analog for the kart accelerator
- Write the signal for the Festo actuators / servo braking
- Hold a normally-open relay able to cut the shutdown circuit on condition

## Mandatory (rules)

- **ASSI / AS-emergency buzzer** — FS-Rules **DV 4.5**: 80–90 dB(A) @ 2 m. Not optional; a
  fab without it fails scrutineering. GPIO 3 is reserved as `BUZZER` (old name — now `CMD_COMPRESSOR_PWM`,
  the EBS compressor MOSFET gate) but no transducer or driver is wired yet. See `tasks/kart-medulla.md` (repo root) for the candidate parts and the SPL bench-measurement
  the CPT-407 needs (it projects to ~79 dB @ 2 m — at or just under the minimum).

## V2 target — next revision

Moved here from the board's task list on 2026-07-16 so it outlives it.

- **Rotate the push-in connectors** — wires exit outward, away from the board, and pin
  numbering runs co-directional with the CN numbering on each side
- **On-board compressor MOSFET & cooling** — a second dedicated power MOSFET on the PCB to
  drive the compressor, with a footprint that takes a heatsink
- **Built-in flyback diode** — 3 A+ Schottky across the compressor motor output terminals, to
  protect the MOSFET from the inductive spikes when disconnecting the motor
- **Bulk capacitance on the 12 V rail** — large bulk electrolytics in the design (e.g. 2×
  4700 µF 35 V in parallel) beside the compressor MOSFET, to stabilise 12 V and absorb
  locked-rotor inrush
- **Separate power/signal GND** — distinct net classes for Power GND (compressor, heavy
  actuators) and Signal GND (ESP32, logic)
- **Reachable spare GPIOs** — bring at least two unassigned, PWM-capable, non-strap GPIOs out
  to terminals on every revision. From 2026-07-10: *a spare pin you cannot reach with a
  screwdriver is not a spare pin.* Concretely, route GPIO 38 → CN3.1 and GPIO 39 → CN3.2; the
  first is the intended `CMD_COMPRESSOR_PWM`

### Contradictions to resolve before V2 — do not action either item as written

Both were written 2025-12/2026-07 and conflict with requirements above. Flagged 2026-07-16;
Rubén decides.

1. **"Repurpose BUZZER (old name) for compressor PWM (skip GPIO 3)"** conflicts with the rules-mandated
   buzzer. It also appears obsolete: routing GPIO 38/39 to terminals (2026-07-10, above) gives
   a PWM pin without stealing GPIO 3, and names `CMD_COMPRESSOR_PWM` for it. Likely just
   delete the repurpose idea — but confirm the compressor PWM lands on GPIO 38 first.
2. **"Repurpose PRESSURE_3 for steering PWM (skip GPIO 1)"** conflicts with the V1 requirement
   to read 3× Festo pressure sensors, and with the schematic task that still calls for ADC
   dividers on PRESSURE_1/2/3. Decide whether the third pressure sensor is actually dropped —
   if so, amend the V1 requirement above rather than leaving both to contradict each other.

3. **The three compressor items (MOSFET, flyback diode, bulk caps) assume the board carries
   motor power. It does not.** Raised by Rubén 2026-07-16. `+12V` enters at CN1 pin 2 and only
   feeds the on-board regulator for the logic/analog rail — roughly **1 mA, 7 mW**. The
   compressor MOSFET switches low-side, so the motor's + terminal is fed from the battery
   externally and only the return passes through the board. Consequences:
   - Bulk caps on the board's `+12V` would sit across a milliamp logic rail, outside the
     inrush loop (battery → motor → MOSFET → GND → battery). They cannot absorb locked-rotor
     inrush from there.
   - A low-side flyback diode returns to the motor's +12 V, so placing it on-board puts amps of
     freewheel current through a net sized for milliamps.
   - **Track width is the concrete blocker.** `+12V` and the motor-return copper are drawn today
     for a ~1 mA logic supply. Compressor current — and especially locked-rotor inrush — needs
     tracks (or pours) sized for it, plus the via count to match. No amount of adding components
     fixes a net whose copper is sized for a different job: any on-board compressor power path
     starts with re-sizing `+12V`, the motor return, and their vias, and stating the design
     current those are sized for.

   **The decision this forces: does the compressor power path come on-board at all?**
   - *Signals only* — matches the board's own precedent for the steering driver: "The PCB only
     routes signals (CMD_STEER_PWM, CMD_STEER_DIR) to the Cytron, not power" (see
     `docs/pinout-esp32-s3.md`, power architecture). Flyback and bulk caps live at the
     compressor. The three items collapse into the GPIO 38/39 routing task, already scoped.
   - *Power on-board* — needs a high-current 12 V input terminal, heavy copper for `+12V` and
     the motor return, a heatsinked MOSFET, then the flyback and bulk caps make sense. This is
     a power-section redesign and should be scoped as one, not as improvement bullets.

   Unrelated discrepancy found while checking this: `tasks/kart-medulla.md` specifies an **L7805 linear**
   regulator (decision 2026-05-02) while `docs/pinout-esp32-s3.md` power architecture shows an
   **LM2596SX-ADJ buck**. One of the two is stale — worth settling while the power section is
   open.
