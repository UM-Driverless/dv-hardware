# kart-medulla

PCB pairs with the firmware in [UM-Driverless/kart_medulla](https://github.com/UM-Driverless/kart_medulla).

Originally called "ESP32 Expander" in EasyEDA (Jan 2026), renamed to "Kart Medulla (expander for ESP 32)" in May 2026. Both EasyEDA exports kept under `easyeda-source/` for diff history.

## Migration status (2026-05-03)
EasyEDA Pro `.epro` exists but **KiCad 10.0.1 importer silently fails** on this project — produces empty `.kicad_sch`/`.kicad_pcb` shells. Source `.epro` is valid (verified: contains `1.esch` 83KB, `becc...epcb` 640KB, full symbol/footprint set).

Next steps to try:
- Community converter `easyeda2kicad6` (Node, third-party)
- Manual unpack + per-file import
- File a KiCad bug with this `.epro` as repro
