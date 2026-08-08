<!-- consult selectively — grep, never read in full -->

# Parts sourcing

Per-part provenance for symbols, footprints, 3D models, and datasheets used on this board. Add an entry whenever a new part is integrated. Datasheets themselves live in `datasheets/` per the convention in `datasheets/README.md`; this file just tracks where each artifact came from.

## MAX4660EUA+T (U14 — throttle SPDT mux) — NO LONGER IN THE DESIGN

**Removed from the schematic on 2026-08-08**, together with R32 (the 10 kΩ pulldown on
`SELECT_THROTTLE`) and C5 (U14's local 100 nF decoupling capacitor). Two reasons: it is a CMOS analog
switch, so with the board unpowered both channel MOSFETs are off and the driver's pedal was **not**
passed through — "normally closed" in the datasheet means closed at logic 0 with power applied, not
closed without power; and the kart's panel DPDT switch, downstream of this board, already selects the
throttle source on metal contacts that work with everything unpowered. The throttle command now runs
MCP4922 U13 pin 14 → LM358 U1B (gain 1.51) → R39 → CN10.1, with no analog switch in the path, and
GPIO 15 is free.

The part **is fitted on the fabricated v1 board**, so the sourcing details below are kept for anyone
working on that hardware.

- **Manufacturer:** Maxim Integrated (now part of Analog Devices)
- **Package:** 8-µMAX-EP (8-uSOP-EP)
- **Datasheet:** [`datasheets/MAX4660-MAX4662_Maxim_datasheet.pdf`](datasheets/MAX4660-MAX4662_Maxim_datasheet.pdf) — also at https://www.analog.com/MAX4660/datasheet
- **Symbol source:** project library (`kart-medulla.kicad_sym`, entry `MAX4660EUA_T`). Originally from EasyEDA-Pro export, ConvertEDA-migrated 2026-05-03. Pin numbering verified against SnapEDA-verified symbol on 2026-05-07. Not replaced — pin layout matches SnapEDA exactly, replacing would have broken existing wire positions.
- **Footprint source:** SnapEDA. Downloaded 2026-05-07 from https://www.snapeda.com/parts/MAX4660EUA%2BT/Maxim+Integrated/view-part/. File: `kart-medulla.pretty/SOP65P490X110-9N.kicad_mod`. Replaced the original ConvertEDA-migrated `UMAX-8_L3.0-W3.0-P0.65-LS4.9-BL-EP.kicad_mod` (still in the .pretty/ folder, unused).
- **3D model source:** SnapEDA (same download). File: `3dmodels/MAX4660EUA_T.step`.
- **Notes:** symbol has two pins both named "NC" — pin 2 is "Normally Closed" switch terminal (Passive), pin 5 is "No Connect" / do-not-wire (no_connect). See history.md 2026-05-07 entries for the full audit trail.
## LM358DR (U1 — pressure-command amplifier 0–3.3 V → 0–9.9 V, and throttle buffer)

- **Manufacturer:** Texas Instruments. Dual op-amp, SOIC-8. U1A is the non-inverting pressure-command stage, gain 3 set by R19 2 kΩ feedback and R20 1 kΩ to GND, taking MCP4922 U13 pin 10 (VOUTB, 0–3.3 V) and giving 9.9 V out. It was gain 2 with R19 = 1 kΩ until 2026-08-01 (commit `16a35fb`), when U13 moved from +5V to +3V3 and the lower full scale had to be made up in the gain; U1B is the non-inverting throttle stage, gain 1.51 set by R37 5.1 kΩ and R38 10 kΩ, taking MCP4922 U13 pin 14 (VOUTA, 0–3.3 V) in at U1 pin 5 and giving 4.99 V full scale at U1 pin 7 (net `ACC_AMP_OUT`), which reaches CN10.1 through the 1 kΩ series resistor R39.
- **Datasheet:** [`datasheets/LM358_TI_datasheet.pdf`](datasheets/LM358_TI_datasheet.pdf) — SLOS068AB, June 1976 rev. October 2024, covering LM158/158A/258/258A/358/358A/358B/358BA/2904/2904B/2904BA/2904V. Downloaded 2026-07-30 from https://www.ti.com/lit/ds/symlink/lm358.pdf. Also copied to the vault catalog at `~/dv/datasheets/LM358_TI_datasheet.pdf`.
- **The section that matters:** §5.7 "Electrical Characteristics: LM358, LM358A" — the plain LM358 grade, which is what `LM358DR` is. The B/BA grades in the same document have *different* specs (notably a 3 V–36 V supply range and much smaller output headroom), so reading the wrong table gives an over-optimistic answer.
- **Output swing from the positive rail** (§5.7, "OUTPUT" block): 2 V typ / **3 V max** at RL ≥ 10 kΩ; 4 V max at RL = 2 kΩ over 0–70 °C. The part is not rail-to-rail. On the board's +12 V rail this caps the guaranteed output at 9 V, below the 10 V the stage is asked to deliver. **Accepted, not a defect to fix on this board** — decided 2026-07-30, because the Festo VPPM regulates ~1 bar per volt and 9 bar of brake pressure is enough. Tracked for the next revision as "Give the pressure-command amplifier full 0–10 V swing on the next board revision" in `dv-hardware/projects/kart-medulla/tasks.md`; numbers and the firmware consequence are in the 2026-07-30 entry of `dv-hardware/history.md`.
- **Symbol source:** project library (`kart-medulla.kicad_sym`), split into a proper multi-unit symbol on 2026-05-04 during the ERC cleanup (it arrived from the EasyEDA-Pro export as a single flat symbol).

## MCP4922-E/SL — dual 12-bit SPI DAC (U13)

- **Manufacturer:** Microchip. Dual 12-bit voltage-output DAC, SOIC-14. Channel A is the throttle
  command (`CMD_ACC_ESP32__0_3V3`, into the LM358 U1B ×1.51 stage that drives CN10.1 — it fed the
  MAX4660 mux U14 until U14 was deleted from the schematic on 2026-08-08); channel B is the pressure command
  (`CMD_PRES_DAC__0_3V3`, into the LM358 ×3 stage). U13 runs from +3V3, so both outputs are 0–3.3 V.
- **Datasheet:** [`datasheets/MCP4922_Microchip_datasheet.pdf`](datasheets/MCP4922_Microchip_datasheet.pdf)
  — DS22250A, 2010, covering MCP4902/4912/4922. Downloaded 2026-07-31 from
  <https://ww1.microchip.com/downloads/en/DeviceDoc/22250A.pdf>.
- **Output swing** (§1.0 Electrical Characteristics, Output Amplifier): **0.01 V to VDD − 0.04 V
  typical**, with accuracy better than 1 LSb only between 10 mV and VDD − 40 mV. On this board VDD,
  SHDN# and both VREF pins sit on `+3V3` (moved there 2026-08-01, commit `16a35fb`), so full scale is
  about **3.26 V, not 3.30 V** — 1.2 % short. Tripled by the LM358 that is 9.78 V rather than 9.90 V,
  roughly 0.12 bar on a valve that regulates about 1 bar per volt. Negligible beside the op-amp's own 1–2 V of lost headroom, which is the
  binding limit on this chain.
- **Absolute maximum on the outputs** (§ Absolute Maximum Ratings): any input or output referred to
  VSS is **−0.3 V to VDD + 0.3 V**, so **−0.3 V to +3.6 V** here, and output-pin current is capped at
  **±25 mA**. This is the number behind the over-voltage concern on the old CN10.2 wiring: the **Festo
  VPPM-8L proportional pressure regulator** on the far end of CN10.2 is supplied from 24 V (its
  0–10 V setpoint is a separate signal), so a harness fault at that terminal presented roughly 20 V
  over the absolute maximum directly onto VOUTB, with no series resistor, clamp or buffer in the way. Moving CN10.2 to the
  op-amp output removed that path.
- **Two write-word bits are constrained by how VREF is wired** (Register 5-1, DS22250A page 24):
  - **`GA` must be 1**, which selects 1×. `GA` = 0 selects 2× and asks for 6.6 V out of a
    3.3 V-supplied part, which clips hard at ~3.26 V.
  - **`BUF` must be 0** (unbuffered VREF). Buffered mode accepts VREF only from 0.040 V to
    VDD − 0.040 V, and VREF here *is* VDD, which is outside that window. Unbuffered mode accepts
    0 to VDD, at 165 kΩ input impedance — fine driven from the 3.3 V rail.
- **Symbol source:** project library (`kart-medulla.kicad_sym`), from the EasyEDA Pro import.
