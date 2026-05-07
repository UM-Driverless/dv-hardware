<!-- consult selectively — grep, never read in full -->

# History

Append-only log of investigations, decisions, surprising findings, and gotchas. Newest first.

---

## 2026-05-07 — KiCad ERC: "Input pin not driven" on GND net (kart-medulla GPIO expander U25 A0)

### Problem
ERC error: `Symbol U25 Pin 1 [A0, Input, Line] — Input pin not driven by any Output pins`. A0 of the PCF8574T (I2C address pin) was tied to GND for address 0, but ERC kept failing. Took many iterations to diagnose because of multiple overlapping KiCad concepts that all *look* the same to a human.

### Root causes (compound)
1. The "GND" on A0 was a **global label** (the arrow shape, `Ctrl+L`), not a **GND power symbol** (the triangle, `P`). They share the name "GND" but live on **separate nets**. ERC does not auto-merge them.
2. Even after using the correct GND **power symbol**, ERC still complained because the **GND power symbol's pin is type Power Input**, not Power Output. A net with only Power Input pins has no driver → ERC error.
3. Fix for #2 is **PWR_FLAG** — a special symbol whose pin is type Power Output, exists exclusively to tell ERC "this rail is actually driven." Need exactly **one** PWR_FLAG per power net **across the entire design** (one for GND, one for +3V3, etc.). Two PWR_FLAGs on the same net = "Power output and Power output connected" error.

### Key facts to never re-derive
- **Global label "GND" ≠ GND power net.** Labels are just net names. Power symbols carry power-net semantics.
- **Power symbols all named "GND"** (the triangles) **share one global net** across all sheets, regardless of where placed. So one PWR_FLAG drives every GND triangle in the project.
- **Global Label "Shape" property** (Input/Output/Bidirectional/Tri-state/Passive) is **purely cosmetic** — only changes the arrow shape. Does not affect ERC electrical type. ERC drive checks look at *symbol pin types* and PWR_FLAG, never at label shapes.
- **Pin types that DRIVE a net for ERC purposes:** Power Output, Output, PWR_FLAG. Power Input does not drive (this is why GND/+3V3 power symbols alone don't satisfy ERC).
- KiCad shortcuts: `L` = local label (sheet-scoped), `H` = hierarchical label, `Ctrl+L` = global label (the arrow), `P` = power symbol (the triangles, GND/+3V3/etc.).

### Recipe to make a power net pass ERC
1. Place GND power symbol (`P` → GND) on every GND-bound wire. Make sure the pin tip lands on the wire endpoint with a green junction dot.
2. Place exactly **one** PWR_FLAG (`P` → PWR_FLAG) somewhere on the GND net. Conceptually next to the actual power source (e.g., ESP32's GND pin) is fine, but electrically it doesn't matter.
3. Repeat (#2 only) for +3V3, +5V, etc.

### Confusion to avoid next time
- Do not suggest "the wire is floating" or "no junction" without verifying — the user can see the schematic and that gaslights them. The error is almost always a **net semantics** issue (label vs. power symbol vs. missing PWR_FLAG), not a literal disconnection.
- Trust the user when they say "I already placed the power symbol" — verify by checking PWR_FLAG count and pin-to-wire snap, not by re-explaining the difference between symbols.
- The KiCad GND power symbol can appear rotated (pointing left, right, down) — it is still the same symbol. Don't mistake a rotated GND triangle for an arrow-shaped global label.

### Related (still open at end of session)
- Two PWR_FLAGs (`#FLG01` and `#FLG_GND01`) coexist on GND net → must delete one.
- A0 still showed "not driven" after PWR_FLAG added, suggesting GND power symbol on A0's wire is not snapped onto the wire endpoint (no electrical connection). Fix: drag GND triangle until green dot appears at pin/wire junction.
