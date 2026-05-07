<!-- read in full — kept under 150 lines -->

# kart-medulla — board-specific tasks

Per-board task list. Higher-level/cross-board work lives in `dv-hardware/.agents/tasks.md`. Update status: `TODO → In Progress → Done`. Claim by adding `[YYYY-MM-DD <name>]`.

## TODO

### Investigate routing the on-board ESP32-S3-DevKitC-1 RGB LED

The DevKitC-1 has an on-board WS2812 RGB LED tied to **GPIO38** (or GPIO48 on some revisions — confirm against the exact module rev used). It is **disconnected by default**: a solder-bridge jumper on the module needs to be closed to wire the LED data line to the GPIO. If we close that bridge, that GPIO becomes unavailable for anything else on the medulla side.

**Decide:**
1. Confirm which exact GPIO the on-board LED uses on our DevKitC-1 rev (check the user-provided silkscreen / Espressif schematic for that rev).
2. Audit the current medulla schematic — is that GPIO already routed to a sensor/peripheral?
3. **If unused on our side:** leave it unwired on the medulla side AND document that closing the module's solder jumper enables the LED (→ add to `docs/`).
4. **If we're already short on pins:** skip this — the LED is a nice-to-have, not worth losing a real I/O.

Outcome to commit: a 1-line note in `docs/pinout` (or wherever pinout lives) saying "GPIO## reserved for on-board LED, leave free, requires SJ## closed on module".

### Triple-check MAX4660 (U14) throttle-mux wiring

Current verified state (per netlist generated 2026-05-07): pin 1 COM=`CMD_ACC__0_5V`, pin 2 NC=`PEDAL_ACC__0_5V`, pin 3 GND=GND, pin 4 V+=`+5V_REG`, pin 5 NC=no-connect, pin 6 IN=`SELECT_THROTTLE`, pin 7 V−=GND, pin 8 NO=`CMD_ACC_ESP32__0_5V`, pin 9 EP=GND. ERC clean.

Outstanding doubts to resolve:
- **Visual layout:** GND power symbols on pins 3 and 7 currently render with the triangle pointing *into* U14's body, making the connection look absent at a glance. Half-applied a rotation fix via MCP — the new symbols got assigned ugly auto-references (`#PWR25ce`, `#PWRdf4d`). Either finish the rename via `sch_update_properties` (rejected once — figure out the right field name first) or run KiCad's Annotate. Confirm visually after that pin 3 and pin 7 GND triangles are clearly outside the chip body.
- **Pin 9 EP overlap:** the `GND` text label on the EP power symbol overlaps with the chip's "EP" pin name. Cosmetic only — move the GND symbol up a few mm or hide the pin name on pin 9 in the symbol.
- **Functional cross-check vs firmware:** `SELECT_THROTTLE` polarity — when the ESP32 drives this line LOW, COM connects to NC (pedal pass-through, default). When HIGH, COM connects to NO (ESP32 override). Cross-check `kart-medulla` firmware to confirm it drives the line consistent with this convention. If polarity is reversed in firmware, decide whether to fix firmware or re-route NC↔NO on the schematic.

## In Progress

(none)

## Done

(none yet on this list)
