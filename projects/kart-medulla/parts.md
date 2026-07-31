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

## MCP4922-E/SL — dual 12-bit SPI DAC (U13)

- **Manufacturer:** Microchip. Dual 12-bit voltage-output DAC, SOIC-14. Channel A is the throttle
  command (`CMD_ACC_ESP32__0_5V`, into the MAX4660 mux); channel B is the pressure command
  (`CMD_PRES_DAC__0_5V`, into the LM358 ×2 stage).
- **Datasheet:** [`datasheets/MCP4922_Microchip_datasheet.pdf`](datasheets/MCP4922_Microchip_datasheet.pdf)
  — DS22250A, 2010, covering MCP4902/4912/4922. Downloaded 2026-07-31 from
  <https://ww1.microchip.com/downloads/en/DeviceDoc/22250A.pdf>.
- **Output swing** (§1.0 Electrical Characteristics, Output Amplifier): **0.01 V to VDD − 0.04 V
  typical**, with accuracy better than 1 LSb only between 10 mV and VDD − 40 mV. On this board VDD
  and both VREF pins sit on `+5V_REG`, so full scale is about **4.96 V, not 5.00 V** — 0.8 % short.
  Doubled by the LM358 that is 9.92 V rather than 10.00 V, roughly 0.08 bar on a valve that regulates
  about 1 bar per volt. Negligible beside the op-amp's own 1–2 V of lost headroom, which is the
  binding limit on this chain.
- **Absolute maximum on the outputs** (§ Absolute Maximum Ratings): any input or output referred to
  VSS is **−0.3 V to VDD + 0.3 V**, so **−0.3 V to +5.3 V** here, and output-pin current is capped at
  **±25 mA**. This is the number behind the over-voltage concern on the old CN10.2 wiring: the **Festo
  VPPM-8L proportional pressure regulator** on the far end of CN10.2 is supplied from 24 V (its
  0–10 V setpoint is a separate signal), so a harness fault at that terminal presented roughly 19 V
  over the absolute maximum directly onto VOUTB, with no series resistor, clamp or buffer in the way. Moving CN10.2 to the
  op-amp output removed that path.
- **Two write-word bits are constrained by how VREF is wired** (Register 5-1, DS22250A page 24):
  - **`GA` must be 1**, which selects 1×. `GA` = 0 selects 2× and asks for 10 V out of a 5 V-supplied
    part, which clips hard at ~4.96 V.
  - **`BUF` must be 0** (unbuffered VREF). Buffered mode accepts VREF only from 0.040 V to
    VDD − 0.040 V, and VREF here *is* VDD, which is outside that window. Unbuffered mode accepts
    0 to VDD, at 165 kΩ input impedance — fine driven from the 5 V rail.
- **Symbol source:** project library (`kart-medulla.kicad_sym`), from the EasyEDA Pro import.
