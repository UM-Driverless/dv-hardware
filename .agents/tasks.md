<!-- read in full — kept under 150 lines -->

# Tasks

Shared task board for `kart-medulla` schematic cleanup. Update status as you go: `TODO → In Progress → Done`. Read before editing; claim by adding `[YYYY-MM-DD <name>]` and the section change.

## TODO

### Run `Tools → Annotate Schematic` once

The recently-added `+3V3` power symbol replacing the old `SPARE__3V3` label has Reference `#PWR?` (intentionally — KiCad will assign the next free number on annotate). One click of the Annotate button clears the "Item not annotated" error.

### Schematic ERC cleanup (~32 warnings, 0 errors)

The schematic is logically correct and netlist-clean. Remaining items are GUI cleanup or design-decision documentation. Run `Inspect → Electrical Rules Checker → Run ERC` to see the live list.

#### Wire endpoint cleanup (~25 warnings)
Floating wire stubs left over from the EasyEDA import. For each `unconnected_wire_endpoint`:
- Click the marker in the ERC panel → schematic jumps to the spot.
- Either drag the endpoint onto its real target (`M` to grab, snap onto pin/label), or delete the dangling stub.

Hot spots (multiple wire-end warnings clustered):
- Voltage divider section near (78–137, 228) — pressure dividers
- Throttle mux area near (151–242, 214–215) — analog switch wiring
- DAC/level-shifter area near (45–164, 298–308)
- A few scattered single endpoints

#### Isolated single-pin labels (6 warnings — accept or annotate)
These are real signals exiting the board through one connector pin each. The warning *is* the documentation that they go off-board to a test point or external wire. Either:
- Accept and right-click each marker → **Exclude this violation** (silences future ERC), or
- Add a "TestPoint" or "Connector" symbol if you want them visible in BOM.

The 6:
- `TX0` @ (427.99, 48.26)
- `RX0` @ (427.99, 50.80)
- `SDC_ENABLE` @ (427.99, 66.04)
- `LED` @ (427.99, 83.82)
- `USB_D+` @ (427.99, 91.44)
- `USB_D-` @ (427.99, 93.98)

Confirmed by grep: each has zero matching counterparts elsewhere on the sheet.

#### `no_connect_connected` on U14 MCP4922 NC pin (1 warning)
**Location:** Symbol U14 (it's actually the MAX4660 throttle mux — reference numbering is misleading), pin 2 at (384.81, 217.17).
**Cause:** A wire from PEDAL_ACC__0_5V touches a pin we currently have marked `no_connect`. But the symbol pin is named "NC" because in the **MAX4660 datasheet** "NC" means *Normally Closed switch contact* (a real functional pin you wire), not "no connection". I had previously fixed pin 2's etype to `passive`, but the warning is back — possibly because the cached lib_symbols entry got rolled back during recovery commits, or because of how the GUI session re-saved.
**Fix:** Open the symbol editor on `kart-medulla:MAX4660EUA_T`, change pin 2 (NC) electrical type from `Unconnected` to `Passive`. Save the lib AND let KiCad rebuild the schematic's lib_symbols cache (Tools → Update Symbols from Library).

### Place LM358 unit B with safe tie-back (optional but recommended)

`U1B` (the unused half of the LM358 dual op-amp) is currently placed with NC markers on pins 5/6/7. That silences ERC but leaves the silicon op-amp floating, which can oscillate or couple noise into the active half. **Better:** replace the NC markers with:
- Pin 6 → Pin 7 (loop, unity-gain follower)
- Pin 5 → GND (input held at fixed voltage)

For an FS prototype this is unlikely to cause real issues, but it's the standard analog practice.

### When all warnings are addressed: PCB layout

The board hasn't been laid out yet. Workflow once schematic is settled:
1. `Tools → Update PCB from Schematic` (in PCB editor) to sync footprints.
2. Lay out per the constraints in `~/repos/kart-docs` (mounting holes, connector positions, height).
3. Run `kicad-cli pcb drc -o /tmp/drc.rpt projects/kart-medulla/kart-medulla.kicad_pcb` before fab.

## In Progress

(none)

## Done

- 2026-05-04 — Schematic ERC: 313 → 32 (0 errors). Major cleanups: extracted EasyEDA-cached symbols into project lib + registered sym-lib-table; set pin electrical types on all chips; added PWR_FLAGs on +3V3/+5V_USB/+12V/GND rails; split LM358DR into proper multi-unit symbol; converted text annotations to real labels; wired ESP32 header pin-pair shorting on U23; renamed CN4 I2C labels (`STEER_SDA__I2C` → `SDA__I2C`, same for SCL — was a real bus-rename orphan that would have left steering sensor unwired); promoted/demoted labels for consistent local-vs-global scope; replaced misnamed `SPARE__3V3` with proper +3V3 power symbol on the connector; documented strap pins (U23 27/28 + U24 8) with NC + text annotation. See `.agents/history.md` for the lessons learned (KiCad no_connect semantics, isolated_pin_label false-confidence trap, mid-wire labels vs wire endpoints).

## Notes for the next person

- `~/repos/kart-docs` is the source-of-truth for kart facts (sensor parts, voltage rails, mechanical). Grep there before asking.
- `.agents/history.md` has a running log of decisions/gotchas (grep, don't read in full).
- `.agents/error-log.md` has prevention rules from past mistakes — **especially the rule that `no_connect` markers mean "designer chose not to wire, on this board" and not "pin doesn't exist on silicon", and the rule to grep each `isolated_pin_label` before classifying it as "legitimate"**.
- The schematic is on a single sheet (`kart-medulla_P1.kicad_sch`). Hierarchical labels are not used; if you split into multiple sheets later, convert the relevant globals to hierarchical labels and add sheet pins.
