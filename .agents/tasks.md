<!-- read in full — kept under 150 lines -->

# Tasks

Shared task board for `kart-medulla` schematic cleanup. Update status as you go: `TODO → In Progress → Done`. Read before editing; claim by adding `[YYYY-MM-DD <name>]` and the section change.

## TODO

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

`BUZZER` net (ESP32 GPIO3) is currently a dangling label — only one endpoint, no driver, no transducer. ERC doesn't flag it (single-pin nets with labels pass). Decide and implement:

- **Pick the buzzer part.** Active (built-in oscillator, just needs DC) vs passive (needs PWM tone from MCU). Voltage (3.3 V vs 5 V vs 12 V). Through-hole vs SMD. Loudness/frequency for kart use (cabin noise — likely needs >85 dB @ 10 cm). Add the chosen part to the BOM.
- **Design the drive circuit.** GPIO3 can't sink/source enough for a typical buzzer. Use an NPN/N-MOSFET low-side switch (e.g. BSS138, MMBT2222) with base/gate resistor + flyback diode if the buzzer is inductive. Note GPIO3 is a strap pin (JTAG src select, default high) — buzzer must be idle-LOW-safe at boot, OR the transistor stage must invert so high-at-boot ≠ buzzing. Confirm this against the chosen part's drive polarity.
- **Power rail.** Pick from existing rails (+3V3, +5V_USB, +12V) — most likely +5V_USB or +12V depending on buzzer.
- **Placement.** On-board (footprint on the medulla PCB) or external on a 2-pin connector? If external, add to one of the green screw terminals.
- **Update** `docs/pinout-esp32-s3.md` line 178 BUZZER row with the final polarity / idle-state behavior, and remove the "for debugging" framing if it's now a real feature.

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
