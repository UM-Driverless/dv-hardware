# kart-medulla

PCB pairs with the firmware in [UM-Driverless/kart_medulla](https://github.com/UM-Driverless/kart_medulla).

Originally called "ESP32 Expander" in EasyEDA (Jan 2026), renamed to "Kart Medulla (expander for ESP 32)" in May 2026. Both EasyEDA exports kept under `easyeda-source/` for diff history.

## Migration status (2026-05-03)
Converted via [ConvertEDA](https://converteda.com) from EasyEDA Pro 2.2.47.7. KiCad 10.0.1's built-in `Import Non-KiCad Project → EasyEDA Pro` silently failed on this `.epro` (produced empty stubs) — likely a format-version lag against EasyEDA Pro 2.2.47.x. ConvertEDA handled it cleanly.

Renamed all internal references from `Kart_Medulla_(expander_for_ESP_32)` to `kart-medulla` (file names, sheet refs, project name, title block) for consistency with the firmware repo.

### Known cleanup needed (raw conversion baseline)
- 347 ERC violations: mostly missing `gen` symbol library (converter creates `gen:` lib_id refs but doesn't ship the library), `power` library mismatches (`12V`, `+5V_REG` not in KiCad's stdlib power), missing `fp-lib-table`.
- 165 DRC violations + 31 unconnected items: expected until footprint library is registered and net ties verified.

Cleanup work tracked separately. The current commit is the as-converted baseline so future cleanup commits show a clean diff.
