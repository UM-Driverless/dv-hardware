<!-- reference — read when designing or fabbing any board -->

# PCB checklist

Applies to **every** board in this repo. Not a task list: it's the standing bar a revision has to
clear. A board's `projects/<board>/tasks.md` carries **one** finishable task — "pass this checklist for
`<board>-vN`" — instead of copying these items out. Copying them into a task list is how four
divergent copies of this checklist came to exist (see `history.md` 2026-07-16).

Tick against a **named revision**, never against "the PCB" — see [Revision naming](#revision-naming).

## Design

- [ ] Pass ERC on the schematic (0 errors; investigate every warning)
- [ ] Standard package 0603. An 0805 footprint fits both sizes
- [ ] Connectors positioned so the mounting panel doesn't cross the PCB. Prefer the middle of a PCB
      side — simplifies the box and keeps things symmetrical
- [ ] Screw holes, even if the assembly is designed differently (groove-fit etc.). A screw + nut and
      plastic spacers let you layer PCBs later
- [ ] Silkscreen text:
  - [ ] Names on LEDs and connectors
  - [ ] Board name, **revision**, input voltage, date, description
  - [ ] Where the documentation is (link, QR, folder name) — plenty of room on the back
  - [ ] Pin 1 marked on connectors so orientation is unambiguous; per-pin names if they fit
  - [ ] Arrows for input vs output (Alt+26)
  - [ ] MOSFETs marked P/N-channel + depletion/enhancement; transistors NPN/PNP
- [ ] Ground plane ISOLATE > 0 mm
- [ ] A little clear space around the PCB edge — protects components from knocks, helps it sit in a box
- [ ] PCB outline and mounting holes on round mm values, not 99.7 × 80.3
- [ ] Solder-bridge resistors where a section must be isolated for testing (e.g. either side of a
      DC-DC, so the board can be externally powered with the main connector plugged in)
- [ ] A header per voltage level (GND, 3V3, 5V, 12V…) with an LED indicator, placed after the solder
      bridge on the consumer side — powers that side easily, and a multimeter anywhere tests the source
- [ ] At least one LED on a microcontroller GPIO — proves the micro is alive
- [ ] Reset button for the microcontroller
- [ ] GND vias for connection quality and to cool hot components
- [ ] Input protection: short-circuit fuse; reverse-voltage (series diode, diode-to-GND that blows the
      fuse, or a P-channel enhancement MOSFET); overvoltage (Zener clamp, e.g. 5.1 V 1N4733A). An
      e-fuse covers all of it at once — TPS2663x (60 V, 6 A, reverse polarity + surge + OV + OC),
      TCKE8xx (18 V 5 A, **not** reverse-polarity)
- [ ] Components that the factory can pre-solder are marked as such (especially BGA)
- [ ] Any component behind an SDC relay has a 2-pin header to bridge it
- [ ] **Track width matches the current each net actually carries** — including inrush, not just
      steady state. A net's copper is its job description: signal-width copper on a power net is a
      design error no added component fixes. State the design current for every power net
- [ ] Thicker copper ordered if needed (2 oz / 70 µm instead of 1 oz / 35 µm)
- [ ] Antenna keepout respected for any RF module: no copper, no pour, no metal within the datasheet's
      published zone. Overhang the board edge if orientation allows
- [ ] If free space remains, easter eggs

## Pre-fab validation

- [ ] DRC to 0 errors / 0 unexpected warnings. Suppress only SPARE/NC pin warnings, explicitly
- [ ] DRC constraints set for the chosen fab before running it. JLCPCB standard 2-layer 1 oz is a safe
      conservative baseline that AISLER also accepts: track/clearance 0.2 mm (their min is 0.127 mm —
      the margin is deliberate), via 0.45 mm with 0.2 mm drill, hole-to-hole 0.5 mm, annular ring
      0.13 mm, silk width 0.153 mm, text height 1 mm
- [ ] Schematic parity: PCB and schematic agree (DRC's "Test for parity" option)
- [ ] Every net label has a counterpart at the other end — no dangling labels. Every component has a
      value and a footprint. Every connector pin has a net or an NC flag
- [ ] BOM exported; DNP parts excluded; quantities match actual stock — no surprise purchases
- [ ] Gerbers exported and opened in a *separate* viewer. Check copper, silkscreen legibility, drill
      alignment
- [ ] 3D viewer sanity check (Alt+3): connector heights, header sockets, TO-220 orientation, collisions
- [ ] **1:1 paper print** of outline + footprints. Put the real parts on top and confirm every pin
      lands on its pad
- [ ] Fab-side DFM preview run (AISLER preview / JLC previewer)
- [ ] Row-by-row walk of the board's pinout doc against the schematic
- [ ] Board tagged `<board>-v<rev>` and the fab package committed under `fab/<board>/<rev>/`

## Revision naming

Every fabricated board gets its own name. "The PCB" is ambiguous the moment a second one exists, and
this repo already has an assembled board plus a next revision in progress being discussed as "V2".

- Format `<board>-v<N>` — `medulla-v1`, `medulla-v2`. Matches the existing tag convention in
  `AGENTS.md` (`<board>-v<rev>`, firmware `<board>-v<rev>-fw`)
- The name goes **on the silkscreen**, in the KiCad title block, on the git tag, and on the
  `fab/<board>/<rev>/` folder. A board you cannot name by looking at it is a board you cannot debug
- Never reuse a number. A respin after a fab error is a new number, not "v2 again"
