# DRC configuration — AISLER Beautiful Boards target

<!-- reference — read when relevant -->

The medulla is fabbed at **AISLER** ("Beautiful Boards" 2-layer, FR4 1.6 mm, 35 µm copper, sponsor for U-Motorsport Driverless). This doc explains every constraint set in `kart-medulla.kicad_pro` (Board Setup → Design Rules → Constraints) and `kart-medulla.kicad_dru` (custom rules), and the margin chosen on top of AISLER's published minimums.

## How to run the check

In KiCad 10:

1. Open `kart-medulla.kicad_pcb` in the PCB editor.
2. **Inspect → Design Rules Checker** (or `Ctrl+Shift+B`).
3. Tick *Refill all zones before performing DRC* and *Report all errors for each track*.
4. Run. **Zero errors and zero unconnected items is the gate for fab release.**

The custom rules in `kart-medulla.kicad_dru` are picked up automatically because the file lives next to the `.kicad_pcb` and shares the project basename.

## AISLER capability and our margin

Source: <https://aisler.net/help/preparing-your-design/design-rules> (Beautiful Boards tier).

| Constraint | AISLER min | Medulla setting | Margin reason |
|---|---|---|---|
| Track width | 0.15 mm (6 mil) | **0.20 mm** | +33 %. Catches accidental hairlines from auto-routed pours and from manual-routing slips on net-class change. |
| Track-to-track clearance | 0.15 mm | **0.20 mm** | +33 %. Same. Also covers small registration error between top/bottom copper and silk. |
| Mechanical drill | 0.30 mm | **0.30 mm** | At fab min. Mechanical drills are deterministic — there is no margin to chase. Anything tighter requires laser drilling, which is not on the Beautiful Boards tier. |
| Annular ring (plated through-hole / via) | 0.125 mm (5 mil) | **0.125 mm** | At fab min. Implies a min via diameter of 0.30 + 2 × 0.125 = **0.55 mm**. |
| Hole-to-hole | 0.20 mm | **0.30 mm** | +50 %. Drill jitter is the dominant fab error mode for hand-loaded panels. 0.30 mm is what AISLER themselves recommend for "best yield." |
| Copper-to-edge | 0.25 mm | **0.30 mm** | +20 %. V-cut depaneling can chip the laminate up to ~0.2 mm into the board; 0.3 mm leaves headroom. |
| Silk line width | 0.15 mm | **0.15 mm** | At fab min. Anything thinner gets dropped or smudged. |
| Silk text height | 1.0 mm | **1.0 mm** | At fab min for legibility under hand-soldering loupe. |
| Silk text thickness | 0.10 mm | **0.15 mm** | Bumps text from "barely readable" to "comfortably readable." Costs nothing. |
| Silk-to-pad clearance | n/a | **0.15 mm** | AISLER strips silk that lands on pads anyway, but the rule catches drifted refdes that would otherwise just disappear silently. |
| Microvias | not supported on this tier | **disabled** | Beautiful Boards has no laser drilling. |
| Blind / buried vias | not supported on this tier | **disabled** | Same. |

## Net classes

| Class | Track width | Clearance | Via (Ø / drill) | Used by |
|---|---|---|---|---|
| **Default** | 0.25 mm | 0.20 mm | 0.6 / 0.3 mm | All signal nets, I²C, SPI, UART, hall sensors, button reads |
| **Power** | 0.20 mm | 0.25 mm | 0.8 / 0.4 mm | `+5V`, `+12V`, `+5V_USB`, `+5V_REG`, `3V3`, `GND` and any net pattern matching `*+5V*`, `*+12V*` |

Pattern-based net-class assignment is configured in `kart-medulla.kicad_pro` under `net_settings.netclass_patterns`. Adding a new power net auto-promotes it to the Power class without manual reassignment.

### Why no track-width minimum for Power

AISLER Beautiful Boards 2-layer is 35 µm (1 oz) outer copper. The medulla Power class only carries logic-level rails (+12V, +5V_USB, +5V_REG, +3V3) feeding ICs, op-amps, and sensors — all sub-100 mA loads in practice. The 12 V → Cytron path is **not routed through the medulla** (decision 2026-05-01: Cytron is permanently powered from kart-side, only signals come through the PCB).

Some of these rails fan out to small QFN/SOT-23 packages where 0.2 mm pin-pitch routing is necessary. The board-wide `min_track_width` (0.2 mm) is sufficient.

History (for context):
- Initial setup: Power class min 0.50 mm, conservative belt-and-suspenders.
- 2026-05-09 (a): dropped to 0.30 mm once it was clear loads are sub-1 A.
- 2026-05-09 (b): dropped entirely — small-chip fanout requires 0.2 mm routing on power rails too. Power class still applies for clearance (0.25 mm) and via size (0.8/0.4 mm).

If a future revision adds motor/solenoid power on a Power-class net, restore the `power-track-width` rule with the appropriate IPC-2221 minimum.

## Custom rules (`kart-medulla.kicad_dru`)

Five rules, in evaluation order:

1. **`edge-clearance`** — 0.30 mm copper-to-board-outline. Belt-and-suspenders for the built-in `min_copper_edge_clearance`, which can miss copper on layers other than the outline edge during V-cut panelization.
2. **`annular-min`** — 0.125 mm annular ring on every via and plated through-hole pad. Equivalent to the built-in `min_via_annular_width` but extended to pads (not just vias).
3. **`hv-pressure-clearance`** — 0.60 mm clearance on the three 24 V pressure-sensor input nets (`PRESSURE_1__24V`, `PRESSURE_2__24V`, `PRESSURE_3__24V`). Per IEC 60664-1 Pollution Degree 2 / Material Group IIIa, 0.50 mm is the minimum creepage at 50 V working voltage; we run at 24 V so 0.50 mm is plenty, but the kart is outdoors with road dust, so 0.60 mm gives derating margin.
4. **`power-track-width`** — *removed 2026-05-09.* See "Why no track-width minimum for Power" above.
5. **`silk-pad-clearance`** — 0.15 mm silk-to-pad clearance on both silk layers. Catches refdes drift that would otherwise just disappear during AISLER's silk-strip step.

The high-voltage rule will become more interesting if the team ever runs the Festo proportional valve's 24 V drive directly through the medulla (currently it doesn't — only the divided sensor-output signals are on the medulla). If that changes, **bump the rule's threshold to ~1.0 mm and add a creepage-only constraint for the high-side switch.**

## When AISLER bumps capability

AISLER occasionally tightens the Beautiful Boards minimums (most recently they reduced min drill from 0.35 mm → 0.30 mm). When that happens:

1. Re-fetch <https://aisler.net/help/preparing-your-design/design-rules>.
2. Update the **AISLER min** column in this doc.
3. Decide per-row whether to keep the existing margin, tighten our value, or stay where we are. We rarely need to chase the fab to its limit — most medulla constraints are constrained by hand-assembly and inspection comfort, not fab capability.
4. Re-run DRC. Existing layouts almost never violate a tightened fab spec; they only need updating when *we* want to use the new headroom.

## When the fab changes (e.g. JLCPCB for a prototype run)

If AISLER sponsorship lapses or a prototype goes to JLCPCB instead:

1. Copy this doc to `drc-jlcpcb.md` (or whatever vendor) and re-derive the numbers from that fab's capability page.
2. Swap the constraint values in `kart-medulla.kicad_pro` and the relevant numbers in `kart-medulla.kicad_dru`. **Don't edit two fab targets in the same project file** — keep one fab's numbers active at a time.
3. JLCPCB's standard tier is broadly similar to AISLER Beautiful Boards (6/6 mil track/space, 0.30 mm drill); the *real* differences are in panelization, plating, and silkscreen process — which DRC can't catch. See JLCPCB's capability page when that day comes.

## See also

- `lib/esp32-s3-pin-capabilities.md` — ESP32-S3 per-pin capabilities and module-suffix gotchas.
- `projects/kart-medulla/docs/pinout-esp32-s3.md` — actual medulla pin assignments (mirrors the schematic).
- AISLER capability page: <https://aisler.net/help/preparing-your-design/design-rules>
