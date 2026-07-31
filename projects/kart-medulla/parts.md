<!-- consult selectively — grep, never read in full -->

# Parts sourcing

Per-part provenance for symbols, footprints, 3D models, and datasheets used on this board. Add an entry whenever a new part is integrated. Datasheets themselves live in `datasheets/` per the convention in `datasheets/README.md`; this file just tracks where each artifact came from.

## MAX4660EUA+T (U14 — throttle SPDT mux)

- **Manufacturer:** Maxim Integrated (now part of Analog Devices)
- **Package:** 8-µMAX-EP (8-uSOP-EP)
- **Datasheet:** [`datasheets/MAX4660-MAX4662_Maxim_datasheet.pdf`](datasheets/MAX4660-MAX4662_Maxim_datasheet.pdf) — also at https://www.analog.com/MAX4660/datasheet
- **Symbol source:** project library (`kart-medulla.kicad_sym`, entry `MAX4660EUA_T`). Originally from EasyEDA-Pro export, ConvertEDA-migrated 2026-05-03. Pin numbering verified against SnapEDA-verified symbol on 2026-05-07. Not replaced — pin layout matches SnapEDA exactly, replacing would have broken existing wire positions.
- **Footprint source:** SnapEDA. Downloaded 2026-05-07 from https://www.snapeda.com/parts/MAX4660EUA%2BT/Maxim+Integrated/view-part/. File: `kart-medulla.pretty/SOP65P490X110-9N.kicad_mod`. Replaced the original ConvertEDA-migrated `UMAX-8_L3.0-W3.0-P0.65-LS4.9-BL-EP.kicad_mod` (still in the .pretty/ folder, unused).
- **3D model source:** SnapEDA (same download). File: `3dmodels/MAX4660EUA_T.step`.
- **Notes:** symbol has two pins both named "NC" — pin 2 is "Normally Closed" switch terminal (Passive), pin 5 is "No Connect" / do-not-wire (no_connect). See history.md 2026-05-07 entries for the full audit trail.
## LM358DR (U1 — brake/pressure command 0–5 V → 0–10 V amplifier)

- **Manufacturer:** Texas Instruments. Dual op-amp, SOIC-8. U1A is the gain-of-2 non-inverting stage (R20 = 1 kΩ to GND, R19 = 1 kΩ feedback); U1B is unused and tied off as a follower with its input at GND.
- **Datasheet:** [`datasheets/LM358_TI_datasheet.pdf`](datasheets/LM358_TI_datasheet.pdf) — SLOS068AB, June 1976 rev. October 2024, covering LM158/158A/258/258A/358/358A/358B/358BA/2904/2904B/2904BA/2904V. Downloaded 2026-07-30 from https://www.ti.com/lit/ds/symlink/lm358.pdf. Also copied to the vault catalog at `~/dv/datasheets/LM358_TI_datasheet.pdf`.
- **The section that matters:** §5.7 "Electrical Characteristics: LM358, LM358A" — the plain LM358 grade, which is what `LM358DR` is. The B/BA grades in the same document have *different* specs (notably a 3 V–36 V supply range and much smaller output headroom), so reading the wrong table gives an over-optimistic answer.
- **Output swing from the positive rail** (§5.7, "OUTPUT" block): 2 V typ / **3 V max** at RL ≥ 10 kΩ; 4 V max at RL = 2 kΩ over 0–70 °C. The part is not rail-to-rail. On the board's +12 V rail this caps the guaranteed output at 9 V, below the 10 V the stage is asked to deliver. **Accepted, not a defect to fix on this board** — decided 2026-07-30, because the Festo VPPM regulates ~1 bar per volt and 9 bar of brake pressure is enough. Tracked for the next revision as "Give the pressure-command amplifier full 0–10 V swing on the next board revision" in `dv-hardware/projects/kart-medulla/tasks.md`; numbers and the firmware consequence are in the 2026-07-30 entry of `dv-hardware/history.md`.
- **Symbol source:** project library (`kart-medulla.kicad_sym`), split into a proper multi-unit symbol on 2026-05-04 during the ERC cleanup (it arrived from the EasyEDA-Pro export as a single flat symbol).
