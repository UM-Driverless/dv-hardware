<!-- consult selectively — grep, never read in full -->

# History

Append-only log of investigations, decisions, surprising findings, and gotchas. Newest first.

---

## 2026-05-07 — Decision: stay on KiCad long-term (vs EasyEDA)

Revisited tool choice after MCP-related friction. Decision: **KiCad**, long-term.

Reasoning:
- Open format, local files, git-tracked — work is owned, not hosted on a vendor's servers.
- No vendor lock-in; portable across fabs (not tied to JLCPCB pipeline).
- Scriptable; MCP tooling is improving and recent ERC issues were all resolved within KiCad.
- EasyEDA is fine for quick JLC-bound boards but wrong foundation for hardware meant to live for years.

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

### Resolution
User fixed it by placing **three separate GND power symbols, one per pin (A0, A1, A2)**, instead of wiring all three pins together to a single shared GND symbol. ERC then passed (0 violations).

### Why three-symbols-works when one-symbol-wired-to-all-three didn't (NOT FULLY EXPLAINED)
Electrically these should be identical: all three pins on the global GND net via the PWR_FLAG elsewhere. Power symbols with the same name (`GND`) merge into one global net regardless of how many copies are placed. **No confirmed root cause** for why the single-symbol version failed ERC on A0 specifically.

Most likely candidate (unverified): a hidden wire-connectivity issue where A0's pin or one wire segment was off-grid / not actually joined to the rest. ERC's "Input pin not driven" fires when a net has only Input-type pins and no driver — *including* the case where the "net" is just one pin with nothing else on it (a one-node net counts as undriven). That would explain why A0 alone failed while A1/A2 passed. But the user did not visually confirm a misalignment, so this remains a hypothesis.

### Lesson for future ERC drive errors
If ERC says "Input not driven" on **one specific pin** when adjacent pins on what looks like the same wire are fine: try dropping a power symbol directly on the offending pin (bypass the wire). If that fixes ERC, the wire connectivity was the issue. If not, there's something else going on — inspect the .kicad_sch file via MCP rather than guessing.

### Final final
- One PWR_FLAG per power net across the whole design (not per sheet, not per symbol). On disk this project has `#FLG01` (GND), `#FLG_+3V3`, `#FLG_+5V_USB01`, `#FLG_+12V01`. Don't add more.
- The kicad MCP (`mcp__kicad__run_erc`, `grep PWR_FLAG <sch>`) reads disk and is far faster than iterating from screenshots.
