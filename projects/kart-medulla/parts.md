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
