<!-- reference — read when working on this board; too long to load every task -->

# kart-medulla — board-specific tasks

This board's task list, indexed from the repo root board at `dv-hardware/tasks.md`, which carries only
cross-board work. Update status: `TODO → In Progress → Done`. Claim by adding `[YYYY-MM-DD <name>]`.

## TODO

### medulla-v2: replace the throttle mux so manual mode survives an unpowered board #ruben

Raised 2026-08-08. Full evidence in `history.md`, entry "the throttle mux does NOT pass the pedal
through with the board unpowered".

Two faults with one fix:

1. **The board cannot tell whether the kart is in autonomous or manual mode.** No net carries the
   kart's mode-switch position. `SELECT_THROTTLE` (GPIO 15 → U14 pin 6) is an output; firmware knows
   only what it last wrote. If the driver flips to manual while firmware still believes it is
   autonomous, nothing detects the mismatch.
2. **U14 (MAX4660) does not pass the pedal through when the medulla is unpowered.** It is a CMOS
   switch: at V+ = 0 V both channel MOSFETs are off and only ESD diodes remain, so the pedal is
   disconnected from the motor electronics and instead backfeeds the dead `+5V_REG` rail. "Normally
   closed" in the datasheet means closed at logic 0 **with power applied**. The board was designed
   believing the opposite.

Related and unfixed: U14 runs from `+5V_REG` against a +9 V datasheet minimum (blocker in the
2026-07-31 audit item below). Both go away if the part goes away.

**Decided 2026-08-08, after Rubén described the kart-side wiring:** the panel switch is a **DPDT**
that already selects the throttle source reaching the ESC (pole 1) and breaks the Cytron-to-
steering-motor cable (pole 2), both on metal contacts, downstream of this board. So U14 is a
second selector in series doing a job that is already done, by a part that does it better —
the switch works with everything unpowered and no firmware can reach it.

**The fix is deletion, not replacement.** In v2:

- **Remove U14 (MAX4660)** and its supply. The medulla always outputs its autonomous throttle
  command on CN10.1; the panel switch decides whether anything listens. This also closes the
  "U14 supplied at 5 V against a 9 V minimum" blocker, and frees GPIO 15.
- **Add a mode-sense input.** One wire from a **third pole** on the panel switch, shorting to GND
  in autonomous against a pull-up on the medulla. Read-only by construction: firmware can see the
  mode but can never cause it, which is the property Rubén asked for. Needs the panel switch
  swapped for a 3PDT or one with an auxiliary contact — there is no other electrical difference
  between the modes to detect, since the Cytron's supply is permanently powered.

Feeds the v2 pin allocation item below: the sense line needs one input pin, and a free PCF8574
port is probably enough since it is a slow digital signal.

Kart-side wiring is documented in `kart-docs` (commits `bec7c20`, `c625d75`): the DPDT's second
pole is in `wiring.yaml` and the global diagram. Both questions that were open there are now
answered by Rubén (2026-08-08) — pole 2 breaks **M+**, and the Cytron is fed **directly from the
battery**, not the 12 V rail.

### Decide the medulla-v2 pinout as one allocation, not signal by signal #ruben

Raised 2026-07-31. There are now at least six separate claims on v2 pins, each already tracked as its
own item, and several of them want the same kind of GPIO. Deciding them one at a time is how two
signals end up on one pin — which is exactly what happened on v1, where `PRESSURE_3` and `BUZZER` both
got quietly repurposed (see "As-built pin use" in
[`docs/pinout-esp32-s3.md`](docs/pinout-esp32-s3.md)).

The competing claims, all of which must be satisfied by one table before v2 layout starts:

- **3× 0–10 V pressure inputs** — needs three non-strap ADC-capable GPIOs plus dividers and terminals.
  GPIO 1 is not coming back; see "Restore the third pressure channel on a new pin (V2)".
- **Steering angle sensor** — pin need depends on the interface, and the part is settled where v1 is
  concerned but not for v2: v1 runs the **MT6701 on PWM** (validated on the kart 2026-07-31). If v2
  keeps PWM it needs one capture-capable GPIO; SSI/SPI needs more. Decide the part and the interface
  before allocating.
- **Compressor MOSFET drive, on-board** — see "Design the compressor MOSFET drive on-board for
  medulla-v2". GPIO 3 carries it on v1 and keeps it on v2 — its reset state is what makes it safe
  (floats with no internal pull, so an external pulldown wins at boot). Allocate around it.
- ~~ASSI buzzer on GPIO 3~~ — **not a competing claim: closed 2026-07-18**, the kart carries no buzzer
  or ASSI (those are formula-vehicle only), so **GPIO 3 is the compressor's permanently** and the
  `BUZZER` net name is historical. `requirements.md` still flags this as an unresolved conflict — that
  flag is stale and should be cleared when v2 is scoped.
- **Throttle command path** — whether v2 keeps the MCP4922 SPI DAC, switches to the DAC7574, or
  keeps a filtered-PWM output as a designed-in fallback rather than a patch.
- **GPIO 38 + 39 reaching terminals** — see "Route GPIO 38 + GPIO 39 out to CN terminals"; today no
  spare GPIO is physically reachable, which is what forced the v1 repurposing in the first place.

**DONE 2026-07-31 — the table is in `docs/pinout-esp32-s3.md` under "medulla-v2 pin allocation".**
Every claim above is placed, no pin carries two signals, and no strap pin is used.

The constraint that decided it, which none of the individual claims had exposed: **ADC1 is full.**
ADC1 is GPIO 1–10 and ADC2 is unusable with WiFi on, so the board has exactly ten analog-capable
pins. v2 needs seven. All ten were occupied, four by non-analog signals — steering PWM on GPIO 1,
compressor gate on GPIO 3, I²C on 8 and 9 — so the third pressure channel could only come back by
evicting one. **`STEER_SENS_PWM` moves from GPIO 1 to GPIO 38** (unconstrained, no strap, not ADC),
returning GPIO 1 to `PRESSURE_3`. That is one firmware pin number and nothing else.

Also settled while building it: **GPIO 41/42 were already reserved for `CAN_RX`/`CAN_TX`**, so the
CAN question needed no pins freed at all.

What the table does **not** solve, because it is connector capacity rather than GPIO capacity:
CN4 gives the steering encoder its two bus lines but neither
power nor ground.

### Act on the 7 verified audit findings (2026-07-31) #ruben

Raised by the multi-agent audit and each one survived two independent refuters told to kill it.
Full evidence, consequence and proposed fix for every item is in `history.md`, entry
"audit workflow, capped rerun". Ordered by what blocks what.

1. **[BLOCKER] `U25` (PCF8574T, narrow SO16) is on a wide-body SOIC-16W land pattern** — leads land
   0.5 mm short of every pad. This is on the fabricated board. Decide which side is wrong, then
   either retarget to `Package_SO:SOIC-16_3.9x9.9mm_P1.27mm` or change the part.
2. **[major] MCP4922 `CS#`/`SCK`/`SDI` have no pull resistors**, the DAC sits on `+5V_REG` which is
   live without the ESP32, and `LDAC#` is tied low so there is no second latch. With the ESP32 in
   reset or being reflashed, noise can latch an arbitrary brake-pressure setpoint onto CN10.2 —
   `VOUTB` has no mux to fall back on, unlike the throttle. Add a 10 kΩ pull-up on `CS#` to
   `+5V_REG` and a 10 kΩ pulldown on `SCK`.
3. ~~**[major] `C13` and the `R8`/`R9`/`R10` divider sit on GPIO 1**~~ — **REFUTED 2026-07-31 for the
   built board.** `README.md`'s rework list records that **R10 is removed** on the physical board.
   R10 was the only shunt to ground, so with it gone there is no divider — just `R8` + `R9` as a
   20 kΩ series into a high-impedance digital input, which passes the full 3.3 V swing. That is
   exactly why the pin is decoded with the MCPWM capture peripheral instead of read as an analog
   voltage, and why the steering read works on the kart. `C13` is schematic-only and not fitted.
   The audit missed this because its agents were pointed at the schematic, PCB, docs, tasks,
   requirements and `history.md` — but **not at `README.md`, which is where board rework lives.**
   Workflow context fixed. What survives of the finding is already handled: on v2 GPIO 1 goes back
   to `PRESSURE_3` where the divider and cap are correct, and `requirements.md` now states that
   GPIO 38 must carry neither.
4. **[major] MCP4922 digital inputs are driven below their guaranteed threshold** — VIH is
   0.7·VDD = 3.5 V on the 5 V rail and the ESP32 drives 3.3 V, with no level shifter in the path.
   Works at room temperature, guaranteed by nothing. Either buffer through a 5 V HCT part or move
   U13 to 3.3 V and gain up after the DAC.
5. **[major] The v2 pin table and `requirements.md` contradict each other** on returning
   `PRESSURE_3` to GPIO 1. Pick one and edit the other in the same commit.
6. **[major] No footprint declares an SMD or through-hole attribute** — the pick-and-place export
   contains 1 of 41 SMD parts. Add `(attr smd)` / `(attr through_hole)` in `kart-medulla.pretty`.
7. **[major] `U1` (LM358) has an empty Footprint field** in the schematic; the SOIC-8 exists only
   as a PCB-side override, so the BOM is wrong. Set it on both units and re-export.

### Patch the fabricated board for the CN10.2 brake fix #ruben

Filed 2026-07-31. The design fix landed in `f68cc1f` and is marked DONE under "Fix the
proportional-valve command path" below — but the board that exists was fabbed from `84d6dd0`, one
commit earlier, so **the fault is still physically in the hardware**. Fixing the design does not fix
the artifact, and nothing tracked that gap until now.

On the assembled board: CN10.2 sits on the unamplified `CMD_BRAKE__0_5V` node instead of the LM358's
×2 output, so the proportional valve is commanded over 0-5 V where it expects 0-10 V; and the
U13.10 → U1.3 copper (MCP4922 channel B into the amplifier's non-inverting input) is unrouted,
because six of that net's seven segments had been ripped up in KiCad.

Needs a cut-and-jumper on the assembled board, not a respin. Rubén said 2026-07-31 this will be
patched physically while the PCB is fixed. Record what was actually cut and jumpered in the rework
list in [`README.md`](README.md) — a patched board no longer matches the hash printed on it, and that
list is the only thing that will say so.

### Consider a flyback diode on the PCB, at the compressor MOSFET's output #ruben

Raised 2026-07-31 by Rubén. The compressor motor is inductive, so its switching MOSFET needs a
freewheel path. Today that diode lives at the compressor. Putting a footprint for it **on the medulla
itself**, across the MOSFET's output terminals, means a different compressor can be swapped in later
without soldering a diode onto loose wiring — his reasoning: it fits better on a PCB than lying
around in the harness.

Depends on the on-board compressor stage landing first (see the compressor task above), since the
diode sits across that MOSFET.

To decide when drawing it:
- **Rating.** The motor drew 6 A running at 60 % duty on the bench. The diode carries the freewheel
  current, so size it for that plus the unmeasured stall peak, with the margin-from-stock policy
  already agreed for this load. A Schottky of 3 A+ was the earlier suggestion; 6 A running argues for
  more.
- **Placement.** The loop the diode closes has to be short and tight against the MOSFET, or the
  inductive spike takes the long way round anyway. This constrains the layout, not just the BOM.
- **Whether to fit it by default or leave the footprint unpopulated**, given that most modules
  already carry their own.

### Consider putting CAN on the board #ruben

Raised 2026-07-31 by Rubén: is there pin budget for CAN, and could the GPIO expander free some up?

**The GPIOs are already reserved — this was answered before the question was asked.**
`docs/pinout-esp32-s3.md` holds **GPIO 41 for `CAN_RX` and GPIO 42 for `CAN_TX`**, marked
*"Held for future CAN … medulla has no transceiver in this rev"*. Neither is ADC-capable and neither
is a strap pin, so they cost nothing else. **No pins need freeing and the expander is not involved.**

What CAN actually still needs is on the board and the edge, not the pin table:
- **A 3.3 V transceiver** — SN65HVD230 or TCAN332 class. New part, new footprint. `CAN_TX`/`CAN_RX`
  only have to reach it, and it is on-board, so they never need terminals.
- **Two terminal pins** for CANH/CANL, which is the real cost — the board has no spare, and
  CN4's steering encoder is already competing for them. (`CN8.2` frees up on v2 and
  `EXP_P1`–`EXP_P4` are reshufflable.)
- **A termination decision**: 120 Ω fitted if the medulla is an end node, omitted if it is a stub.

(Superseded analysis, kept because the facts in it are still true and useful elsewhere: TWAI needs
two GPIOs; `MISO` on GPIO 13 is unused because the MCP4922 is write-only; `SELECT_THROTTLE` on
GPIO 15 could move to the expander if a slow signal ever needs displacing — with the caveat that a
PCF8574 output powers up weak-high and HIGH on that net hands the throttle to the DAC, so the 10 kΩ
pulldown would have to keep winning.)

**Superseded — the two GPIOs were already reserved:**
`EXP_P5`, `EXP_P6` and `EXP_P7` are unconnected on `U25` (pins 10, 11, 12; `INT#` on 13 is free too),
so there are three expander slots waiting with no new hardware. Checked against the netlist
2026-07-31, the ESP32's 22 signals give:

- **`MISO` (GPIO 13) is already free.** Its net reaches `U23.37`/`U23.38` and nothing else — the
  MCP4922 is a write-only device with no data output, so nothing is on the other end. That is one
  TWAI pin at zero cost, no expander involved.
- **`SELECT_THROTTLE` (GPIO 15) is the clean move.** It drives the MAX4660 throttle mux and changes a
  handful of times per run, so I²C latency is irrelevant. **One catch that must be designed around:**
  a PCF8574 output powers up in the weak-high state, and HIGH on this net means COM→NO, the ESP32 DAC
  taking the throttle. The existing 10 kΩ pulldown makes the power-on default pedal pass-through,
  which is the safe state. Moving the signal to the expander must keep that default — the PCF8574's
  pull-up is only ~100 µA, so a 10 kΩ pulldown holds the pin near 1 V and should still read LOW at
  the MAX4660, but that has to be checked against the MAX4660's input threshold rather than assumed.
- **`CMD_STEER_DIR` (GPIO 17) is arguable** — a direction bit that only changes at reversals, but it
  is a motor-control signal and an I²C write puts a few hundred microseconds in front of every
  change. Only move it if a second pin is genuinely needed.
- **Nothing else can move.** The rest is analog inputs, PWM, SPI, I²C, hall inputs and the
  safety-chain read — none tolerates being behind a bus transaction. `SDC_NOT_EMERGENCY` in
  particular should stay on a real pin.

So the realistic answer is `MISO` plus `SELECT_THROTTLE`, which costs one expander slot and leaves
two spare.

The rest of the cost:
- **A 3.3 V CAN transceiver** — SN65HVD230 or TCAN332 class. New part, new footprint.
- **Two terminal pins** for CANH/CANL, competing with CN4's
  steering encoder (no power, no ground) for the board's scarce connector capacity.
- **A termination decision**: 120 Ω fitted if the medulla is an end node, omitted if it is a stub.

**Worth answering first:** what would CAN carry that the existing Orin link does not? The team keeps
DBCs in `~/dv/can/`, so something in the wider vehicle speaks it — but if nothing on *this* kart does
yet, this is capacity for later, which changes whether it earns two of the few free pins.

### Restore the third pressure channel on a new pin (V2) #ruben

Decided 2026-07-31. Three 0–10 V pressure inputs stay a requirement, overriding the 2026-07-18
reading that dropped it to two. On the as-built board `PRESSURE_3` (GPIO 1, CN5.2) was repurposed to
read the steering sensor's PWM angle output, and that repurpose stands — so the third pressure
channel needs a **new** home, not GPIO 1 back.

Needs, all three together: an ADC-capable GPIO that isn't a strap pin, a 0–10 V divider in front of
it, and a terminal pin to reach it. Scope it alongside the steering sensor's own pin choice (see the
V2 item in [`requirements.md`](requirements.md)) so the two don't end up competing for the same GPIO
— the steering sensor may want SSI/SPI rather than PWM depending on which part is chosen
(AS5600 / MT6701 / MA732 are all still under evaluation).

### Put `kart-medulla-v1` on the assembled board, and name the next one `kart-medulla-v2` #ruben

Confirmed 2026-07-31 (Rubén): the assembled EasyEDA-origin board **is** `medulla-v1`, so the next
revision is `medulla-v2` — which is what `../../docs/pcb-checklist.md` and this task list already
assume. Nothing on disk backs it today: `fab/` is empty and the only tag is
`medulla-v0.1-converted`.

To close it: put the revision name on the silkscreen and in the schematic title block, and tag the
next fab release `medulla-v2` (with `medulla-v2-fw` on the firmware repo, per `AGENTS.md`).

**Silkscreen done 2026-07-31** (`b4fe1e2`): the board carries the revision name, `Design ID`, a
9.45 mm QR and the digits `1604 0948 4608 5574`, right of CN5. DRC clean; the QR decodes from the
plotted silkscreen. Still open: the KiCad title block, and the tag at fab time.

**Spelling settled 2026-07-31 (Rubén): the full name, `kart-medulla-v2`.** The silkscreen already
said that while `docs/pcb-checklist.md` gave its examples as `medulla-v1` / `medulla-v2`; the full
form wins because the folder, the firmware repo and the docs pages all use it. The checklist and
`AGENTS.md` now say so, and the four places the name appears — silkscreen, title block, git tag,
`fab/` folder — must all use it. The pre-convention tag `medulla-v0.1-converted` keeps its name;
bare `medulla-vN` in older notes means the same board.

**Also settled: the number tracks compatibility.** A whole-number bump is earned by changes the
previous revision is not compatible with; a change that leaves the board a drop-in replacement —
heavier copper, a part substitution, a silkscreen fix — takes a decimal instead. So `kart-medulla-v2`
is right for the next revision because its connector and pinout work breaks compatibility, and
`v1.1` would have been right for a copper-weight respin of the same design. Written into
`docs/pcb-checklist.md` under "Revision naming".

### V2 Hardware Improvements (Kart Medulla PCB)

Moved to [`requirements.md`](requirements.md) on 2026-07-16 — requirements are durable, this list gets pruned as tasks complete. Scope a revision from that file; track the work here.

Two moved items **contradict** other requirements and are flagged there rather than actioned — do not implement either as written: "repurpose BUZZER (old name) for compressor PWM" (conflicts with the rules-mandated ASSI buzzer on GPIO 3, and looks superseded by the GPIO 38/39 routing task below) and "repurpose PRESSURE_3 for steering PWM" (conflicts with the 3× pressure-sensor requirement and with the ADC dividers called for in the schematic task).

The connector-rotation item also restates the "Flip all ten CN connectors 180°" task below — same change, two entries. Kept the task, moved the requirement.

### Design the compressor MOSFET drive on-board for medulla-v2 #ruben

Raised 2026-07-18 after the EBS compressor was bench-run for the first time. Rubén's directive, given
then and **reconfirmed 2026-07-31**: *integrate it — fewer wires running between boxes and bolted-on
PCBs. The less wiring, the better.* So the switching stage, and the compressor current with it, comes
onto the medulla board for v2. The kart runs two boxes today; v2 is meant to collapse that.

**Copy the module that already works, don't invent one.** Rubén, 2026-07-31: the compressor MOSFET
module in service has been modified and validated —

- its **bridge rectifier is removed**, and
- the **series resistor feeding the optocoupler's LED is changed to 330 Ω** so the input works when
  driven from 3.3 V.

That combination is a proven 3.3 V-driven switch for this load, and he has more of the same modules
at home, so the parts already exist. The v2 job is to put that circuit on the PCB rather than design
a fresh gate-drive stage.

**The input stage**, from a photograph taken **before the resistor change**
([`docs/images/compressor-module-U2-PC817.png`](docs/images/compressor-module-U2-PC817.png)):

- **`U2` is a Sharp `PC817`** — a 4-pin phototransistor optocoupler, lot code `CW831`.
  Datasheet: <https://www.sharpsde.com/fileadmin/products/Optoelectronics/Optocouplers/Specs/PC817X_Series_Datasheet.pdf>
- **`R2`, `R3` and `R4` read 10 kΩ** (marked `1002`) — the as-shipped values.

This settles the question left open on 2026-07-18, which had guessed `U2` was a transistor
level-shifter and treated its package as a clue. It is not: the module is **opto-isolated**, so the
ESP32 pin drives an LED and the MOSFET gate is driven on the far side from the module's own DC-IN
rail. That is why a 3.3 V pin works here when it cannot drive a power gate directly.

**Why 330 Ω is the right value.** The PC817's LED drops about 1.2 V, so the series resistor sets the
LED current directly:

| Series resistor | Drive voltage | LED current |
|---|---|---|
| 10 kΩ as shipped | 12 V | (12 − 1.2) / 10 k = **1.1 mA** |
| 10 kΩ as shipped | 3.3 V | (3.3 − 1.2) / 10 k = **0.21 mA** — dead |
| **330 Ω fitted** | **3.3 V** | (3.3 − 1.2) / 330 = **6.4 mA** |

The as-shipped 10 kΩ was sized for a 12 V control input. Driven from 3.3 V it gives a fifth of a
milliamp, far below the IF = 5 mA point where the PC817's current-transfer ratio is specified
(80–160 % for the rank-A part), so the phototransistor barely conducts. 330 Ω puts 6.4 mA through the
LED — just above the characterised point, with CTR giving roughly 5–10 mA of collector current — and
6.4 mA is nothing for an ESP32-S3 pin rated 28 mA. That is the whole modification.

**Still to trace before v2 can be drawn:**

1. **The output side.** What loads the phototransistor's collector, what rail feeds it, and what
   drives the gate. If a 10 kΩ is the only pull-up on a gate the size of the HA210N06's
   (Qg = 135 nC, Ciss = 5800 pF), the RC is tens of microseconds and the device spends a long time
   in linear operation on every edge — survivable at 500 Hz, but worth replacing with a real driver
   when the circuit moves onto the PCB rather than copying as-is.
2. **The MOSFET and flyback arrangement**, and whether this carrier is the HUABAN HA210N06 board
   described further down (the `U2` reference designator matches).
3. **File it.** Datasheets to `datasheets/`, the traced schematic to `docs/`, sourcing to
   `parts.md`, so v2 is drawn from documents rather than from the physical board.

Opto-isolated input also changes the framing of the problem below: the ESP32 pin drives an LED at
330 Ω, not a power MOSFET gate, so the 3.3 V gate-drive analysis in the rest of this task describes
the *unmodified* arrangement and the alternative if the module circuit is not copied.

Read [`../../docs/connectors.md`](../../docs/connectors.md) before laying it out: the compressor
draws **6 A running**, the Phoenix 1990012 terminals fitted to CN1–CN10 are rated **2 A** and cannot
carry it, and the WAGO 2601-3103 on the buy list is rated 17.5 A. Locked-rotor inrush will not be
measured — Rubén, 2026-07-31: the circuit is validated in service and over-sizing from stock costs
nothing. Size the copper generously; **the traces being properly sized is the important part.**

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

**Related, and now root-caused: the motor return must leave the signal ground alone.** On the same
bench run the tank pressure reading sagged **~64%** while the compressor ran, recovering the instant
it stopped. Initially suspected as a ratiometric sensor on a sagging rail — **that is ruled out**:
Rubén confirmed the pressure sensors run from a 24 V regulator that feeds nothing else. It is ground
IR drop, and the arithmetic closes:

| | |
|---|---|
| Observed shift | 1041 ADC counts = **0.84 V** |
| Resistance needed at 8 A | **~105 mOhm** |
| A 0.25 mm x 50 mm 1 oz trace | **96 mOhm → 0.77 V at 8 A** |

The compressor MOSFET switches low-side **on this board**, so the full ~8 A return crosses ground
copper drawn for a ~1 mA logic feed (see [`requirements.md`](requirements.md)).
That lifts the ESP32's ground relative to the sensor's reference, and since the ADC reads
`sensor_out − esp32_gnd`, the reading falls. Same mechanism as the USB brownouts.

**This makes the star-ground item a functional requirement, not housekeeping.** A working
pressure reading during pump-up depends on it, and so does the EBS logic that uses that reading.
Confirmable before any redesign: measure DC volts between the 24 V regulator GND and the ESP32 GND
while the compressor runs — expect 0.5-1 V where a shared ground should read ~0 mV.

**Open, blocks nothing but worth settling:** whether the HUABAN module's control input accepts 3.3 V.
Believed yes by inference, unverified — see `history.md` 2026-07-18. If the module does boost the
gate from its own DC-IN rail, its `U2` stage is a working reference design to copy here.

### Two ground terminals, not one — give the switched loads their own `PWR_GND` pin #ruben

**Scope settled 2026-07-31 (Rubén): `PWR_GND` exists for the compressor MOSFET and nothing else.**
The medulla will supply ground on one pin of the compressor motor's connector, with +12 V on the
other. That return carries the motor current, so it is the noisy one. Every other signal leaving the
board is just a signal, and stays on the ordinary `GND`. So this is one dedicated return pin for one
load, not a general power/signal ground split across the board.


Rubén's directive for medulla-v2 (2026-07-19). The board currently exposes only one kind of ground
(CN1.3 / CN9.3 / CN10.3), so every return leaves on the same conductor and the switched current is
forced through copper the ADC uses as its 0 V reference. That is the mechanism behind the 0.84 V
shift documented in the compressor item above. No amount of copper fixes it: at 8 A, holding the
error under one ADC count (0.8 mV at 12-bit over 3.3 V) needs the shared resistance below 0.1 mΩ,
which no board trace or pour achieves. The current has to not be there at all.

**The change is a pinout change.** Add a `PWR_GND` terminal alongside the existing signal ground.
Internally it is its own pour, tied to signal ground at one point (or not at all on-board — see the
open question below). Externally it lands on the rear ground Wago block, which is the kart's ground
star point; the harness side of this is documented in the kart-docs wiring page under
"Why two grounds", where the two returns are the nets `GND` and `GND_SIG`.

**Both low-side switches go on it — there are two, not one:**

| Switch | Drives | Why it belongs on `PWR_GND` |
|---|---|---|
| `compressor_fet` (gate on CN8.2) | EBS air compressor, ~8 A PWM | The measured offender |
| `Q3` (IRLZ44N, pulls `SDC_5` / CN8.1 low) | SDC relay coil | Low-side by necessity, not choice: N-channel needs its source at ground to be driven from a positive gate. Coil current plus inductive kickback, and nothing on this path is measured, so it has no reason to share the clean reference. Confirmed by Rubén 2026-07-19. |

They can share `PWR_GND` with each other freely — neither is a measurement, so noise between them
costs nothing. The separation that matters is between this pair and the ADC reference.

**What stays on signal ground:** ESP32, the ADC dividers and clamps, the pressure-sensor terminals,
the MCP4922 / LM358 / MAX4660 analog chain, and the I²C bus.

**Decided 2026-07-19 (Rubén): the two grounds do NOT connect on the board.** They stay separate all
the way to the rear Wago and meet only there — no on-board tie, so no second path and no loop.
Place a `0 Ω` jumper footprint between them anyway and **leave it unpopulated**: behaviour is
identical to no link at all, and it turns a possible future need (ESD, a floating input found at
bring-up) into a resistor rather than a respin.

**Consequence — where the gate driver's ground goes.** Vgs is gate minus *source*, and the source
sits on `PWR_GND`, so the driver's reference is now a real choice:

- Referenced to **signal ground**: the logic input is clean, but the gate-drive current (amps, into
  5800 pF, in tens of ns) must return from the driver to the source — and with no on-board tie that
  loop leaves the board, crosses the kart and comes back. Largest loop area on the fastest edges in
  the design. Do not do this.
- Referenced to **`PWR_GND` at the MOSFET source (Kelvin connection)**: gate loop stays a few
  millimetres, which is the requirement. Cost is that the driver's logic threshold floats with
  `PWR_GND`, so the ESP32's 3.3 V input arrives offset by the ground difference.

**Take the Kelvin option.** UCC27517A VIH <= 2.4 V against 3.3 V logic leaves ~0.9 V margin, and the
residual offset is tens of mV. **This margin depends on `PWR_GND` being properly sized** — state the
8 A rating on the drawing next to the driver, because thinning that copper later re-creates the
original fault through a different route.

**Expected residual offset, and why the 0.84 V figure does not apply after the fix.** The measured
0.84 V comes from ~105 mOhm of return path, i.e. a 0.25 mm trace drawn for a 1 mA logic feed. With
`PWR_GND` copper sized for 8 A the resistance is a few mOhm, so expect **tens of mV** between the
grounds under load. Quote 0.84 V only when describing the present fault, never as the post-redesign
expectation.

**Failure mode to guard.** With no on-board tie, if the `PWR_GND` wire is left off the Wago the
compressor return does not stop — it finds the signal-ground wire, and the board is back to today's
0.84 V shift. It keeps working, which is why nobody notices. Make the terminal mechanically obvious
or key the connector; the one-meter check below catches it either way.

**Worth adding on top, once the terminal exists:** measure the pressure sensors differentially. The
SDE5's 0–10 V output is referenced to its own 0 V at the 24 V regulator, so bringing that 0 V back
as a sense line and taking the difference (four matched 0.1% resistors around the existing LM358, or
an MCP3421 on the I²C bus) turns any residual ground offset into a common-mode signal the ADC
rejects. Belt-and-braces on top of the terminal split, not a substitute for it.

**Cheap firmware mitigation, independent of hardware:** at 500 Hz PWM there is a compressor-off
window every 2 ms with genuinely zero current. Sampling the ADC inside it reads a clean ground.
Costs a timer alignment; shrinks as duty rises, so it does not replace the layout work.

**Verify before redesigning:** DC volts between the 24 V regulator GND and the ESP32 GND while the
compressor runs. On the present board expect 0.5–1 V; a healthy ground reads a few mV. If it reads
clean, the diagnosis above is wrong and this task is aimed at the wrong target. Repeat the same
measurement on v2 as the acceptance check — it should then read a few tens of mV at worst.

### Route GPIO 38 + GPIO 39 out to CN terminals (no spare ESP32 GPIO is reachable today)

Found 2026-07-10 while trying to add the EBS compressor PWM driver without a soldering iron.

**The board has no spare ESP32 GPIO on any CN terminal.** Verified on a fresh netlist export:

  - CN pins that reach the ESP32 are all assigned: `SCL` (CN4.1), `SDA` (CN4.2), `BUZZER` (CN8.2, old name),
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

### Switch CN1–CN10 to WAGO 2601-31xx on v2 #ruben

Decided 2026-07-31. Replaces the connector-rotation task below, which only existed because the
Phoenix parts were already placed the wrong way round — swapping the part makes rotating the old one
pointless. Place the new footprints correctly from the start instead.

**Why swap at all.** The fitted Phoenix Contact 1990012 (PTSA 0,5/3-2,5-Z) is rated **2 A**. v2
carries the compressor's **6 A** on-board, so at least that path needs a different connector, and
using one family across the board beats mixing two. The WAGO **2601-3103** (3-pole) and
**2601-3102** (2-pole) are rated **17.5 A**, are the team's chosen standard, and are top entry —
wire in from above, levers on the front face. Ratings and sources:
[`../../docs/connectors.md`](../../docs/connectors.md).

**What changes on the board, and it is not a drop-in:**

- **Pitch goes 2.5 mm → 3.5 mm**, so every connector footprint gets wider and the board outline and
  component keep-outs along both edges have to be re-checked. Ten 3-pole connectors gain 10 × 2 mm
  of edge length between them.
- ~~**New footprints and 3D models.**~~ **Nothing to draw — KiCad 10 already ships both**, checked
  2026-07-31. Use `TerminalBlock_WAGO:TerminalBlock_WAGO_2601-3103_1x03_P3.50mm_Vertical` and
  `..._2601-3102_1x02_P3.50mm_Vertical`. The `TerminalBlock_WAGO` library is reachable with no
  setup: the global `fp-lib-table` nests KiCad's stock table, which registers it. (KiCad calls the
  top-entry parts `_Vertical` and the side-entry `-11xx` ones `_Horizontal` — a second, independent
  confirmation of which variant is which.)
- **Pad geometry changes more than the pitch does.** Measured from the two footprint files:

  | | Phoenix `CONN-TH_3P-P2.50-S5.00_1990012` | WAGO `2601-3103_1x03_P3.50mm_Vertical` |
  |---|---|---|
  | Holes per 3-pole | 3 | **6** — two per pole, rows 5 mm apart |
  | Pin pitch | 2.5 mm | 3.5 mm |
  | Pin-1→pin-3 span | 5.0 mm | 7.0 mm |
  | Drill | 1.0 mm | **1.2 mm** |
  | Pad | 1.66 mm round | 1.5 × 2.3 mm |
  | Arrangement | staggered — pins 1 & 3 one row, pin 2 offset 5 mm | regular grid, both rows aligned |

  Doubling the hole count per pole is the part that matters for routing: twelve extra holes appear
  along each board edge, all on existing nets. The staggered pin-2 row disappears, which is what made
  the old rotation task expensive — so the swap actually *simplifies* the copper under each
  connector even as it widens it.
- **Placement requirements, replacing the rotation task:** wires must exit **outward**, away from
  the board, and pin numbering must run **co-directional** with the CN numbering on each side, so
  `CN1.1, CN1.2, CN1.3, CN2.1, …` reads straight down the edge. Both were the point of the old task.
- **Silkscreen legend and `docs/pinout-cn-connectors.md`** need updating for the new pin order.
- **Decide whether all ten swap or only the high-current path.** All ten is the tidier answer and the
  one assumed here; confirm before ordering, since it changes the quantity to buy.
- **The pin budget improves in v2, it does not just move.** `CN8.2` currently carries the net still
  named `BUZZER`, which drives the external compressor MOSFET's gate. v2 brings that MOSFET
  on-board, so the gate signal never leaves the PCB and **`CN8.2` frees up** (Rubén, 2026-07-31 —
  and no buzzer is coming back to claim it, the kart carries none). That is one genuinely free pin
  on top of the four reshufflable `EXP_P*` pins, and the first claim on it should be settled here
  rather than discovered later: CN4's encoder has neither power
  nor ground.

Buy-list entry and per-variant notes: `~/vault/inventory/wago-2601-pcb-terminal-blocks.md`. Nothing
is in stock yet.

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

**Obsolete as a rotation job — superseded 2026-07-31.** Rubén confirmed it was all ten and not a
subset (a bare "flip CN3 and CN4" line had been sitting on the root board since `280a379` with no
context; it meant this task and is now deleted rather than tracked twice). But then: *obsolete if we
use WAGO*. He is right. v2 replaces the Phoenix 1990012 with WAGO 2601-31xx parts, which is a
different footprint at a different pitch — so there is nothing to rotate. The new footprints simply
get **placed** correctly the first time, and the two complaints above become placement requirements
rather than a rework task. See "Switch CN1–CN10 to WAGO 2601-31xx on v2" below. Everything from here
down is kept because it states what "correct" means and what the pin-2 stagger costs; it is no longer
work in its own right.

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

**Schematic side is done — re-verified 2026-07-31 on a fresh netlist export and unchanged since 2026-05-07:** pin 1 COM=`CMD_ACC__0_5V`, pin 2 NC=`PEDAL_ACC__0_5V`, pin 3 GND=GND, pin 4 V+=`+5V_REG`, pin 5 NC=unconnected, pin 6 IN=`SELECT_THROTTLE`, pin 7 V−=GND, pin 8 NO=`CMD_ACC_ESP32__0_5V`, pin 9 EP=GND. ERC 0 violations. **Nothing further to check in this repo; what remains is firmware.**

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

### NOT APPLICABLE TO THE KART — ASSI/AS-emergency buzzer (kept for the formula vehicle)

**Closed 2026-07-18.** Rubén: *the kart will not carry a buzzer or ASSI; those are for the formula
vehicle only.* So there is nothing to resolve before fab on this board, and **GPIO 3 / CN8.2 is the
compressor's permanently** — the `BUZZER` name on that net is historical only.

Kept rather than deleted because the parts survey and the SPL arithmetic below are real work that
the formula vehicle will need. Move this section to that vehicle's board when one exists.

*(Superseded text follows.)* The schematic reserves GPIO 3 as `BUZZER` (old name — now `CMD_COMPRESSOR_PWM`, the EBS compressor MOSFET gate) but no actual transducer or driver is wired.

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

### Fix the proportional-valve command path — CN10.2 is on the wrong side of the LM358 #ruben

Found 2026-07-30 by parsing the board file. Full analysis and the verified net map are in
`history.md` (entry "2026-07-30 — The brake / proportional-valve command leaves the board at 0–5 V").
Four separate items, all on the same signal chain. A fifth finding — the LM358 cannot guarantee a
full 10 V from the +12 V rail — was **judged not to matter for the kart** and is tracked as a separate
polish task below rather than as part of this fix.

**Root cause, found 2026-07-30:** commit `e8881f1` (2026-05-08, "assign CN1–CN10 pins to match ESP32
geometry") renamed the label on what became CN10 pin 2 from `EXP_P7` to `CMD_BRAKE__0_5V`, and
overwrote the label that had carried `CMD_BRAKE__0_10V` with `GND`. The EasyEDA design this project
was migrated from had the connector on the amplified net, so this is a regression introduced in the
KiCad cleanup, not an original design error. Details and the diff in `history.md` (2026-07-30, second
entry); why the commit's own verification and ERC both missed it is in `.agents/error-log.md`.

1. **DONE 2026-07-30 — connector pin moved to the amplifier output.** As built: schematic label at
   (218.44, 48.26) renamed to `CMD_BRAKE__0_10V`; CN10 pad 2's net changed to match; CN10.2 routed to
   the 0–10 V net on **F.Cu** — (74.5, 90.9999) at 45° to (81.0727, 97.5726), then east to
   (87.0, 97.5726), then a 0.6/0.3 mm via down onto the existing B.Cu stub between U1.1 and R19.2.
   F.Cu was empty in that corridor, which avoids the congested B.Cu side entirely; the track clears
   CN10.1's through-hole pad by ~0.81 mm. Zones refilled. Verified: ERC 0 violations, DRC 0 violations,
   0 unconnected items, netlist shows `CMD_BRAKE__0_5V` = U13.10 + U1.3 and `CMD_BRAKE__0_10V` =
   CN10.2 + R19.2 + U1.1. The 5 remaining schematic-parity warnings (U1 footprint-field mismatch, the
   four `PAD1`–`PAD4` mechanical pads) are byte-identical to those at the previous commit — pre-existing
   and unrelated.

   Also restored in the same commit: the **U13.10 → U1.3** copper (DAC output to amplifier input). Six
   of the seven `CMD_BRAKE__0_5V` segments had been ripped up in KiCad, leaving that connection
   unrouted — DRC reported it as a missing connection between U1 pad 3 and U13 pad 10. The original
   geometry was put back (via (84.582, 91.44) → (83.566, 92.456) → (83.566, 99.8826) →
   (84.6484, 100.965)), since it was the routing the layout was designed around.

   Original problem statement, kept for context: `CN10.2` sat on `/P1/CMD_BRAKE__0_5V`, the MCP4922
   VOUTB node.
   `/P1/CMD_BRAKE__0_10V` (LM358 U1 pin 1, the ×2 output) reaches only R19 pin 2 and never leaves the
   PCB, so the board sends 0–5 V to a valve whose setpoint input is 0–10 V and full DAC scale commands
   about half the pressure range. ERC/DRC stayed silent because a two-pad net is electrically legal —
   nothing checks that a net has an exit point.

   Every connection in this chain is made by a label on a short wire stub, not by a drawn wire, so:

   - **Schematic:** change the label at **(218.44, 48.26)** — CN10 pin 2's stub — from
     `CMD_BRAKE__0_5V` to `CMD_BRAKE__0_10V`. That is the entire schematic edit. Afterwards
     `CMD_BRAKE__0_5V` = U13.10 + U1.3 (DAC to amplifier input, intact) and `CMD_BRAKE__0_10V` =
     U1.1 + R19.2 + CN10.2.
   - **PCB:** Update PCB from Schematic, then delete the two B.Cu segments that reach out to CN10.2 —
     (74.5, 91.0)→(82.110, 91.0) and (82.110, 91.0)→(83.566, 92.456). The remaining five segments
     still join U13.10 to U1.3 through the junction at (83.566, 92.456), so the DAC→amplifier path is
     untouched. Then route CN10.2 (74.5, 91.0) to the `CMD_BRAKE__0_10V` net: 13.07 mm to U1.1
     (85.255, 98.425) or 14.88 mm to R19.2 (87.845, 97.573). **Prefer R19.2 or the existing stub at
     (86.108, 97.573)** — U1's pins 1–4 are a vertical column at x = 85.255 and pin 3 is on the 0–5 V
     net, so approaching pin 1 from below threads past two pins on a foreign net. Existing 0–10 V
     track width is 0.25 mm. Refill zones and re-run DRC.
   - **Not yet checked:** whether the corridor between (74.5, 91) and (86, 97.5) on B.Cu is clear of
     other copper. Check before committing to the route.

   Note the older wording elsewhere in this file named **CN5.3** as the amplifier's exit; CN5.3 carries
   `EXP_P4` today and the brake command exits on CN10.2. Use CN10.2 and make the docs match.
2. **DONE — the same change removed an over-voltage path into the DAC, and the number is now known.**
   With `CN10.2` on the DAC node, anything the harness presented at that terminal landed directly on
   MCP4922 VOUTB with no series resistor, clamp or buffer. Datasheet filed 2026-07-31: any input or
   output referred to VSS has an **absolute maximum of −0.3 V to VDD + 0.3 V**, so **−0.3 V to
   +5.3 V** here, with output-pin current capped at ±25 mA. The **VPPM-8L proportional regulator** on
   the far end of CN10.2 is supplied from 24 V — that is its supply, not its 0–10 V setpoint, and it
   is a different device from the 12 V EBS electrovalve, which no medulla pin touches — so a fault at
   that terminal was about **19 V over the absolute maximum**, straight onto a CMOS analog output.
   CN10.2 now sits on the op-amp output instead, which survives a harness fault far better.
3. **DONE 2026-07-31 — nets renamed.** `CMD_BRAKE__0_5V` → **`CMD_PRES_DAC__0_5V`** and
   `CMD_BRAKE__0_10V` → **`CMD_PRES__0_10V`**, applied to the schematic (4 occurrences), the PCB
   (15 occurrences, so the two stay in parity) and the two pinout docs. ERC 0 violations, DRC
   0 violations and 0 unconnected items afterwards. Original reasoning: One name, `CMD_BRAKE__0_5V`, is
   currently shared by the DAC output, the amplifier input, and the connector pin — which is how a
   0–5 V net ended up on a 0–10 V pin without looking wrong. Follow the throttle channel's pattern
   (`CMD_ACC_ESP32__0_5V` internal → `CMD_ACC__0_5V` exported): `CMD_BRAKE__0_5V` →
   `CMD_PRES_DAC__0_5V`, `CMD_BRAKE__0_10V` → `CMD_PRES__0_10V`. `CMD_PRES` because the signal is a
   pressure setpoint for a proportional regulator, not a brake-force command. Silkscreen shows
   `CMD_BRK` with no voltage, so a rename does not invalidate the board as built; update the legend
   to `CMD_PRES` at the next revision.
4. **DONE 2026-07-31 — datasheet filed and the limit measured. It is not the binding constraint.**
   `datasheets/MCP4922_Microchip_datasheet.pdf` (DS22250A). Output swing is **0.01 V to VDD − 0.04 V
   typical**, so on this board's 5.0 V rail full scale is about **4.96 V** — 0.8 % short. Doubled by
   the LM358 that is **9.92 V instead of 10.00 V**, roughly 0.08 bar on a valve regulating about
   1 bar per volt. Negligible beside the op-amp's own 1–2 V of lost headroom, which remains the real
   limit on this chain. One caveat for calibration: accuracy is guaranteed better than 1 LSb only
   between 10 mV and VDD − 40 mV, so the extreme codes are out of spec.

   **Two firmware constraints follow from how VREF is wired** (Register 5-1, datasheet page 24), and
   both are set in the same 16-bit write word:
   - **`GA` = 1**, selecting 1×. `GA` = 0 selects 2× and asks a 5 V-supplied part for 10 V, which
     clips at ~4.96 V.
   - **`BUF` = 0**, unbuffered VREF. Buffered mode accepts VREF only over 0.040 V to VDD − 0.040 V,
     and VREF here *is* VDD, outside that window. Unbuffered accepts 0 to VDD at 165 kΩ.

   Neither is checked in firmware yet — `~/repos/kart-medulla` has no MCP4922 write implemented at
   all, which is the separate "throttle has no working output" item in the board README.

### Give the pressure-command amplifier full 0–10 V swing on the next board revision #ruben

Polish, not a blocker. Do it when the analog front end is next touched; do **not** hold a revision for
it and do not rework the built board for it.

**Decision, 2026-07-30 (Rubén):** not a problem for the kart — **9 bar of brake pressure is enough.**
So the board ships as-is on this point.

**The finding.** U1 (LM358DR) is the ×2 stage that turns the DAC's 0–5 V into the valve's 0–10 V
setpoint, and it is supplied from +12 V. Per TI SLOS068AB rev. Oct 2024 §5.7 — the plain-LM358 table,
not the LM358B one — swing from the positive rail is 2 V typ / **3 V max** at RL ≥ 10 kΩ
(`datasheets/LM358_TI_datasheet.pdf`). On a 12 V rail that is a 10 V typical ceiling and a **9 V
guaranteed** ceiling, so a worst-case device tops out at 9 V instead of 10 V. The kart's +12 V is an
unregulated battery rail that sags under load, which pushes the real ceiling lower still.

**Why it does not matter here.** The Festo VPPM-8L (571293) regulates 0.1–10 bar across a 0–10 V
setpoint, roughly 1 bar per volt (datasheet: "Pressure regulation range 0.01 MPa…1 MPa / 0.1 bar…10
bar", "Signal range analogue input 0 – 10 V"). A 9 V ceiling therefore costs the top ~1 bar of an
unused part of the range. What it does mean, and what firmware should not assume: **commanding DAC
full scale does not reliably produce 10 bar** — the achievable maximum is somewhere between about
9 bar and 10 bar depending on the individual op-amp and the instantaneous battery voltage, and it is
not repeatable between boards. Any pressure target above ~9 bar has to come from closed-loop control
against a pressure sensor, never from an open-loop DAC code.

**What to change when the time comes,** in order of preference:

1. **Supply U1 from 24 V instead of +12 V.** The kart already carries a 24 V rail for the valve (a
   UENPO 9–36 V → 24 V / 5 A buck-boost, bought 2026-05-30 — see
   `~/dv/kart/pneumatics/history.md`). 24 − 3 = 21 V of guaranteed swing, so the 10 V target stops
   being anywhere near the limit. The LM358's absolute-maximum supply is 32 V, so 24 V is comfortable.
   Cost: routing that rail onto the medulla, which it does not have today.
2. **Keep +12 V and fit a rail-to-rail-output op-amp** in the same SOIC-8 footprint. No new rail, but
   a part change and a stock check.

Either way, re-check the combined budget afterwards against item 4 of the fix task above (the DAC's
own full-scale limit is a second, smaller shortfall on the same signal, and the two add).

### Check whether the assembled medulla-v1 board has the valve-command bug too #ruben

Raised 2026-07-30. Two minutes with a multimeter; do it before assuming the kart's brake command is
fine or that it needs rework. The bug above was introduced in the KiCad cleanup on 2026-05-08, *after*
the EasyEDA export that the assembled board descends from — and the EasyEDA design had the connector on
the amplified net. So the built board is **probably** correct, but that is an inference, and the
connector numbering differs between the two designs (EasyEDA had CN1–CN8, KiCad has CN1–CN10) so it
does not even say which physical terminal carries the valve command.

With the board unpowered, buzz the terminal wired to the Festo VPPM against U1 (LM358) pin 1 and
against U1 pin 3:

- **Continuity to pin 1** (op-amp output) — built board is correct, only the KiCad design needs fixing.
- **Continuity to pin 3** (op-amp input / DAC output) — built board has the bug. Rework: cut the track
  leaving that terminal, run a wire from the terminal to U1 pin 1.
- **Also confirm U1 is actually populated.** If the amplifier was never fitted, the real chain differs
  from what either design file says and this whole analysis needs redoing against the hardware.

Record the result in `history.md` either way — right now nothing on disk says which design was
fabricated, which is the same gap already flagged as contradictions 7–8 in the root `tasks.md`.

### Correct the brake-command documentation (it describes the as-built 0–5 V path as intended) #ruben

Raised 2026-07-30 alongside the task above. Do these together with the net rename so the docs and the
board change in one step:

- `docs/pinout-cn-connectors.md` line 66 — says CN10's two commands go "to the motor controller". The
  brake/pressure command does not: braking on this kart is pneumatic and the command goes to the
  Festo VPPM proportional regulator. Only `CMD_ACC` goes to the motor controller.
- `docs/pinout-esp32-s3.md` line 217 — "VOUTB | CMD_BRAKE | Brake analog command (0-5V) → brake
  valve driver" states 0–5 V as the delivered range. It should be the DAC-side range, with the
  exported range given as 0–10 V.
- `docs/pinout-esp32-s3.md` line 273 — "No chip — direct DAC output … → brake valve driver (no mux on
  PCB)" describes the DAC output as going straight out and does not mention that an LM358 ×2 stage
  exists. The "no mux" half is correct and worth keeping: unlike the throttle, the brake/pressure
  channel has no MAX4660, so the DAC always owns it and the only way to release the command is to
  write zero.
- Document the valve's supply/ground relationship in the harness notes: the VPPM runs on a separate
  24 V supply, so its 0 V must be common with the medulla's GND for the setpoint to mean anything.
  `CN10.3` is GND and is presumably that return, but nothing says so. A ground offset between the two
  supplies shifts the commanded pressure directly.
- ~~Find the VPPM setpoint input's impedance.~~ **Dropped 2026-07-31 (Rubén): not a problem.** It is a signal input and the op-amp holds the voltage.

### Fix two stale connector references in the external-connector audit

Noticed 2026-07-30 while dumping the as-built connector map (the full map is in the `history.md`
entry for that date). In the "External-connector audit (CN1–CN10)" section below:

- It says "`SDC_IN_LOW_SIDE` (on **CN5**)". As built it is on **CN8.1**. CN5 carries
  `HYDRAULIC_2__0_5V` / `PRESSURE_3__0_10V` / `EXP_P4`.
- It says "CN8 / CN9 / CN10 have free slots if EXP_P* are reshuffled". **CN10 has no `EXP_P*` pin**
  and no free slot — its three pins are `CMD_ACC__0_5V`, `CMD_BRAKE__0_5V`, `GND`, all in use. CN9
  pin 3 is GND, also in use. Only the `EXP_P*` pins on CN3 and CN5.3 are genuinely reshufflable.

### Finish medulla schematic — verify every signal is wired and labeled correctly #ruben

- ~~Title: change `ESP32-S3-DevkitC-1` → `ESP32-S3-DevKitC-1` (capital K).~~ **Done** — verified 2026-07-31, the schematic already carries the capital K and no lowercase variant remains.
- ESP32 header pin labels match the canonical names committed 2026-05-03: MOSI / CLK / CMD_DAC_CS (not OUT_SDI/SDK/CS).
- Pin 13 signal labeled `SDC_NOT_EMERGENCY__3V3` everywhere (matching the schematic; the doc was updated to match).
- ~~All ESP32 SPARE / RESERVED pins have NC flags or `SPARE` text labels.~~ **Done** — verified 2026-07-31: 24 unconnected pins across the design, all flagged, ERC reports 0 violations. Breakdown: `U24` 14 (the second ESP32 socket row), `U25` 4, `U13` 3, `U23` 2, `U14` 1.
- **`EXP_P5`, `EXP_P6`, `EXP_P7` exist on the chip and are free** — `U25` (PCF8574) pins 10, 11, 12 are unconnected, as is `INT#` on pin 13. They are cheap extra capacity for anything that only needs a slow on/off line. They are **not** usable for the encoder's supply, for PWM, or for anything analog: they are I²C-driven expander outputs, so a write costs a bus transaction and they cannot be timed.
- ~~**Filter caps missing on all seven analog inputs.**~~ **Done 2026-07-31 — `C7`–`C13`, 100 nF each.** Verified against the netlist 2026-07-31. Each 0–5 V input has a two-resistor divider (`PEDAL_ACC` R14/R15, `PEDAL_BRAKE` R16/R17, `HYDRAULIC_1` R24/R25, `HYDRAULIC_2` R26/R27) and each 0–10 V input a three-resistor chain (`PRESSURE_1` R11/R12/R13, `PRESSURE_2` R4/R6/R7, `PRESSURE_3` R8/R9/R10). But the whole board contains only **six capacitors, C1–C6, and every one is on a power rail** — none sits on an ADC node. Added 2026-07-31: `C7` `PEDAL_ACC__3V3`, `C8` `PEDAL_BRAKE__3V3`, `C9` `HYDRAULIC_1__0_3V3`, `C10` `HYDRAULIC_2__0_3V3`, `C11` `PRESSURE_1__0_3V3`, `C12` `PRESSURE_2__0_3V3`, `C13` `PRESSURE_3__0_3V3` — each 100 nF, `kart-medulla:C0603`, one pin on the divider node and one on GND. ERC 0 violations, every one confirmed on its intended net in a fresh netlist export. **Still to do on the PCB:** each cap must sit physically at the ESP32's ADC pin, not near its divider — a decoupling cap at the wrong end of a trace does nothing.
- ~~Verify where the 5 V supply for the motor hall sensors comes from~~ — **answered 2026-07-31 from the netlist. It is medulla-supplied.** `CN2.3` carries the `+5V_REG` net, which is the output of `U19` (L7805CDT) fed from `+12V` on `CN1.2`. The halls themselves sit on `CN2.1`, `CN2.2` and `CN7.3`, so CN2 hands out both the supply and two of the three sense lines. Same net can instead take an external 5 V rail from outside — that is by design, not an accident. What remains is a load check: three hall sensors on a linear regulator whose budget was written up as ~1 mA for the analog chips alone.

### Add REVERSE_WIRE + needed signals to the green push-in connectors #ruben

- ~~Add `REVERSE_WIRE` to a connector pin~~ — **done, verified 2026-07-31: it is on `CN4.3`**, not CN8 as this task proposed. Still open: whether the manual reverse button is also wired through the medulla (that would need a second pin plus GND, and there is no free pin — see the connector audit). If the button goes straight to the kart electronics box, `CN4.3` alone is enough.
- ~~Rename `STEER_SDA__I2C` → `SDA__I2C` and `STEER_SCL__I2C` → `SCL__I2C`~~ — **done, verified 2026-07-31**: the netlist carries `SDA__I2C` and `SCL__I2C` with no `STEER_` prefix anywhere.
- Verify every signal in `docs/pinout-esp32-s3.md` that needs to leave the medulla actually has a connector pin. Cross-check: PEDAL_ACC, PEDAL_BRAKE, PRESSURE_1/2/3, HYDRAULIC_1/2, motor halls (×3), CMD_ACC, CMD_BRAKE, CMD_STEER_PWM, CMD_STEER_DIR, SDA, SCL, REVERSE_WIRE, manual reverse button (if needed), 12 V, GND.

### Re-lay out the medulla PCB from scratch for v2 — do not edit the v1 copper #ruben

**Decision 2026-07-31 (Rubén): enough has changed that the board is worth redoing rather than
patched.** Rip up the existing routing and start the layout again once the v2 schematic is settled.
This replaces the incremental placement list this task used to be.

**The arithmetic behind it,** measured 2026-07-31. The board today carries **332 track segments,
14 vias, 8 zones and 60 footprints**. The connector swap alone invalidates most of it: **27 of the
82 nets reach a CN connector, and 201 of the 332 track segments — 60 % — sit on one of those nets.**
All of those have to move, because every connector footprint changes pitch and hole pattern. On top
of that, v2 adds a power section that does not exist yet (compressor MOSFET, gate drive, flyback,
bulk capacitance), resizes `+12V` and the motor return from ~1 mA copper to something carrying 6 A,
splits `PWR_GND` off the signal ground, and adds a third pressure channel. Preserving the remaining
40 % is not worth routing around.

**Order of work: the schematic lands first.** Routing before the v2 schematic is settled just makes
copper that gets deleted again. The rip-up is one operation and is reversible through git, so it
belongs at the moment the schematic is done — not before.

**Placement notes, corrected 2026-07-31 against the netlist.** The previous version of this list had
three wrong references: it called the op-amp "U4" (it is `U1`), said "CN1–CN8" when there are ten,
and put the throttle and pressure commands on CN7.3 and CN5.3 when both are on CN10.

- Place ESP32-S3-DevKitC-1 in the center, footprint matching `~/dv/kart/kart-medulla/resources/esp32-s3-devkitc-1/` (verified 22.86 mm row spacing).
- Place L7805 (U19) with its caps near the +12 V input edge (`CN1.2`), copper pour on the GND tab for thermal dissipation.
- Place MCP4922 (U13) close to the ESP32 SPI pins (MOSI/CLK/CMD_DAC_CS, Pins 39/40/42).
- Place MAX4660 (U14, throttle mux) on the throttle path between MCP4922 VOUTA and **`CN10.1`**.
- Place the LM358 (**U1**, not U4) near MCP4922 VOUTB on the pressure-command path before **`CN10.2`** (`CMD_BRAKE__0_10V`).
- Place the compressor switching stage — MOSFET, gate drive, flyback, bulk caps — as its own block with its own heavy copper, kept away from the analog chain.
- Place PCF8574 (U25) on the I²C bus near the steering-encoder connector (CN4); break the unused expander outputs to a small future-expansion header.
- Place BSS123 (Q4) near the CMD_REVERSE path between PCF8574 P0 and `REVERSE_WIRE` (**`CN4.3`**).
- Place the medulla USB-C connector at the edge facing the Orin; route only D+/D−/GND/VBUS, with VBUS going only to the ESP32 5 V pin.
- Place the WAGO push-in connectors (**CN1–CN10**, plus CN11 if the pin count grows) along the kart-facing edge, wires exiting **outward** and pin numbering co-directional with the CN numbering.
- **Bring out a separate `PWR_GND` terminal** — see "Two ground terminals, not one" below. This is a
  **functional requirement, not an optional refinement**: the measured 0.84 V ground shift that
  killed the pressure reading is what it fixes.
- Continuous GND plane on at least one inner layer for the signal side.
- Mounting holes (M3 × 4) at corners, isolated from any nets.
- Check footprint sizes against actual parts (DPAK for L7805, SOIC-16 for PCF8574, µMAX-8 for MAX4660, SOT-23 for BSS123, SOIC-14 for MCP4922).

### Pass the PCB checklist for `medulla-v2` #ruben

One finishable task: walk [`docs/pcb-checklist.md`](../../docs/pcb-checklist.md) end to end against
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
of what was here has been folded into [`docs/pcb-checklist.md`](../../docs/pcb-checklist.md) — the
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

Moved to this file → "Wire ASSI/AS-emergency buzzer on the BUZZER GPIO (old name)" — has the concrete inventory parts (CPT-407-105-L60 ×5, RE46C100S8F ×10) and the FS-Rules SPL constraint worked out.

### External-connector audit (CN1–CN10) — missing / suspect signals

Audited the 10× green push-in 3-pin connectors against the schematic and pinout doc on 2026-05-08.

**As-built map, re-exported from the netlist 2026-07-31 — this is the authority for the corrections
below.** All thirty pins are assigned; there is no free slot anywhere.

| | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| CN1 | `+3V3` | `+12V` | `GND` |
| CN2 | `MOTOR_HALL_3__5V` | `MOTOR_HALL_2__5V` | `+5V_REG` |
| CN3 | `EXP_P1` | `EXP_P2` | `EXP_P3` |
| CN4 | `SCL__I2C` | `SDA__I2C` | `REVERSE_WIRE` |
| CN5 | `HYDRAULIC_2__0_5V` | `PRESSURE_3__0_10V` | `EXP_P4` |
| CN6 | `PEDAL_BRAKE__0_5V` | `PEDAL_ACC__0_5V` | `+3V3` |
| CN7 | `PRESSURE_1__0_10V` | `PRESSURE_2__0_10V` | `MOTOR_HALL_1__5V` |
| CN8 | `SDC_IN_LOW_SIDE` | `BUZZER` (= compressor gate) | `CMD_STEER_DIR__3V3` |
| CN9 | `CMD_STEER__PWM_3V3` | `HYDRAULIC_1__0_5V` | `GND` |
| CN10 | `CMD_ACC__0_5V` | `CMD_BRAKE__0_10V` | `GND` |

**Definitely missing — must be added/decided before fab:**

- ~~**`SDC_ENABLE`** (ESP32 GPIO 39, external SDC enable relay/contactor)~~ — **DROPPED 2026-08-01
  (Rubén): the signal is not wanted and never existed.** *"why would i want SDC_ENABLE? we have a
  mosfet that ends the shutdown loop to gnd when everything ok."* That is what the board does today
  and it is complete: GPIO 18 (`SDC_NOT_EMERGENCY__3V3`) drives Q3's gate through R22, and Q3's drain
  pulls `SDC_IN_LOW_SIDE` — CN8.1 — to ground when the chain should be closed. Verified on the
  netlist: `SDC_IN_LOW_SIDE` = `CN8.1` + `Q3.2`, `SDC_NOT_EMERGENCY__3V3` = `R22.2` + the ESP32
  socket. Nothing else is needed to close the loop.

  `SDC_ENABLE` was never a net. It existed as a free-text annotation near U24 pin 14 and in older
  revisions of `docs/pinout-esp32-s3.md`, describing an external enable relay the design does not
  use. It has been carried as an open connector-capacity item since 2026-05-08 and treated as a
  competing claim on the board's few spare pins — including in the v2 pin table, which gave GPIO 39's
  first claim to it. **It is not a claim. GPIO 39 is simply free.**

**Verify (probably fine, but confirm with the schematic before fab):**

- **CN4 has neither GND nor power** — worse than this audit originally recorded. Re-checked 2026-07-31: its pins are `SCL__I2C` / `SDA__I2C` / **`REVERSE_WIRE`**, not SDA / SCL / +3V3. So the steering encoder (AS5600 or MT6701, still being chosen) gets *only* its two bus lines here and must take VCC and GND from somewhere else entirely, which nothing documents. Decide before the harness is built: a 4-pin or 5-pin connector for the encoder, or a sibling connector carrying +3V3 and GND. Note that fixing this collides with the WAGO swap — settle the pole count while that footprint change is being made, not after.
- **`SDC_IN_LOW_SIDE` (on CN8.1, not CN5) vs `SDC_NOT_EMERGENCY__3V3` (internal)** — confirm they're the same physical SDC sense signal at different voltage levels with a divider/level-shift in between. If they're separate nets that aren't bridged, the SDC readback path is broken. (Connector corrected 2026-07-31 against the netlist: CN5 carries `HYDRAULIC_2__0_5V` / `PRESSURE_3__0_10V` / `EXP_P4`.)
- **`MANUAL_THR` passthrough** — the manual throttle path requires `PEDAL_ACC__0_5V` (from CN5) to branch internally to (a) the ESP32 ADC divider and (b) the U14 MAX4660 NC pin. Confirm the schematic actually has both branches connected on the same net (earlier ERC audit suggests yes, but reverify after current PCB-layout work).

**Defer / informational:**

- **`EXP_P1`–`EXP_P4`** (PCF8574 outputs on **CN3.1/2/3 and CN5.3**, not CN8/CN9/CN10) have no documented kart-side function. Only four of the expander's eight outputs reach a connector — `EXP_P5`–`EXP_P7` are not nets in the schematic at all. Decide what each of the four will drive before the harness is built, and document it in `docs/pinout-esp32-s3.md`. These four pins are also the only spare capacity on the whole board, so anything else that needs to get out (the encoder's power and ground) competes for them.
- **External buzzer** — if the buzzer (currently dangling label, see "Design the buzzer circuit" task above) lives off-board, it needs a connector pin. If it's on-board, no connector entry needed.
- ~~**5V power input**~~ — **settled 2026-07-31 against the netlist.** `+12V` comes in on **CN1.2**, not CN6. It feeds `U19`, an **L7805CDT** linear regulator (not the LM2596SX-ADJ buck, which was evaluated and never fitted), whose output is the `+5V_REG` net. That rail is exported on **CN2.3**, which is where the motor hall sensors get their 5 V — so the hall supply is medulla-supplied, not a pass-through. The same pin can instead accept an external 5 V rail tied onto `+5V_REG`; the net is shared by design.

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
