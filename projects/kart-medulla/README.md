# kart-medulla

PCB pairs with the firmware in [UM-Driverless/kart-medulla](https://github.com/UM-Driverless/kart-medulla).

Originally called "ESP32 Expander" in EasyEDA (Jan 2026), renamed to "Kart Medulla (expander for ESP 32)" in May 2026. Both EasyEDA exports kept under `easyeda-source/` for diff history.

## Board identity

**A manufactured board is identified by the dv-hardware commit its gerbers were exported from**,
written on the board as a QR code or label — short form is enough, e.g. `84d6dd0`. Firmware repos
quote that hash to say which hardware they target, so "does this code match this board?" is a
question anyone can answer by reading the board.

Use the **gerber-export** commit, not the last commit that touched the schematic. They are usually
different, and only the export is what a fab house ever received.

**A board stops matching its hash the moment it is reworked.** The hash names the design it was made
from; a lifted pin or a patch wire exists on that one physical board and in no commit. So each board
also carries a rework list below. A rework entry may name the commit whose behaviour it brings the
board up to — that is how a patched board gets described precisely without inventing a new
identifier for it.

### Boards in existence

**`84d6dd0`** — "medulla: add fabrication gerbers + drill files (zip for fab)". The last commit
touching `fabrication/`, so it is the best available evidence of what the fab house received;
inferred from this repo rather than read off a purchase order. Paired with kart-brain `main` at
`c200e56`.

Two pins are also used for something other than their designed signal on this board (the steering
sensor's PWM on `PRESSURE_3`, the compressor MOSFET gate on `BUZZER`) — that is firmware assignment
rather than copper, so it is listed in
[`docs/pinout-esp32-s3.md`](docs/pinout-esp32-s3.md) under "As-built pin use". Read both that section
and the list below to know what this board actually does.

Rework outstanding on this board:

- **CN10.2 brake output is on the wrong side of the LM358.** The board carries the unamplified 0-5 V
  DAC output where the valve needs 0-10 V, and the U13.10 -> U1.3 copper (DAC to amplifier input) is
  unrouted. Fixed in the design by `f68cc1f`, which is *after* this board was made, so the board
  still has the fault. Needs a physical patch — see [`tasks.md`](tasks.md).
- **Throttle has no working output.** The MCP4922 SPI write was never implemented in firmware. If the
  filtered-PWM bypass is taken instead of fixing the firmware, that adds rework here: U13 pin 14
  lifted, and an RC network from the dev board's GPIO 38 to U14 pin 8. Decision tracked in the
  firmware repo's `tasks.md`.

## Migration status (2026-05-03)
Converted via [ConvertEDA](https://converteda.com) from EasyEDA Pro 2.2.47.7. KiCad 10.0.1's built-in `Import Non-KiCad Project → EasyEDA Pro` silently failed on this `.epro` (produced empty stubs) — likely a format-version lag against EasyEDA Pro 2.2.47.x. ConvertEDA handled it cleanly.

Renamed all internal references from `Kart_Medulla_(expander_for_ESP_32)` to `kart-medulla` (file names, sheet refs, project name, title block) for consistency with the firmware repo.

### Known cleanup needed (raw conversion baseline)
- 347 ERC violations: mostly missing `gen` symbol library (converter creates `gen:` lib_id refs but doesn't ship the library), `power` library mismatches (`12V`, `+5V_REG` not in KiCad's stdlib power), missing `fp-lib-table`.
- 165 DRC violations + 31 unconnected items: expected until footprint library is registered and net ties verified.

Cleanup work tracked separately. The current commit is the as-converted baseline so future cleanup commits show a clean diff.

## Fonts

Silkscreen text on the PCB uses **DejaVu Sans Mono**. There is no monospace font shared by default between macOS and Ubuntu, so contributors must install it locally:

- **Ubuntu:** ships by default — no action needed.
- **macOS:** `brew install --cask font-dejavu` then restart KiCad.

Alternatively, `File → Board Setup → Embedded Files` lets KiCad embed the font into the .kicad_pcb so it travels with the project. See `history.md` 2026-05-09 entry for details.
