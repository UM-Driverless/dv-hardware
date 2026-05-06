<!-- consult selectively — grep, never read in full -->

# History

Append-only log. Newest first.

## 2026-05-04 — `unconnected_wire_endpoint` requires terminating the wire's geometric endpoint, not just the net

A label sitting *mid-wire* still connects the label's net to the wire (KiCad uses the label's `(at)` point, not the wire's ends, for net assignment). But the wire's geometric endpoints are a separate ERC concern: if a wire endpoint sits in empty space — not on a pin, not at a label's `(at)` point, not at another wire/junction — ERC fires `unconnected_wire_endpoint` even though the net is logically named. Place labels at the wire endpoint (or shorten the wire to end at the label) so the geometry and the electrical termination coincide.

Mental model: ERC checks two things separately. (1) Does the *net* have at least the right kind of pins on it? (2) Does each *wire* have its endpoints terminated by something that "anchors" it (pin, label, junction, other wire)? Mid-wire labels satisfy (1) but not (2).

## 2026-05-04 — KiCad no_connect marker semantics (corrected)

The `(no_connect)` flag (the small "X" placed on a pin in the schematic editor) means **"the designer intentionally chose not to wire this pin to anything external on this board"**. It silences ERC's `pin_not_connected` warning by declaring the omission deliberate.

It does **not** mean:
- The pin doesn't physically exist on the package
- The pin is internally disconnected on the silicon
- The pin is a manufacturer-designated NC pad

Source: KiCad eeschema docs (master) — "No-connection flags are used to indicate that a pin is intentionally unconnected. These flags prevent 'unconnected pin' ERC warnings for pins that are intentionally unconnected." (https://docs.kicad.org/master/en/eeschema/eeschema.html)

Practical implication: any unused pin can carry a `no_connect` marker, including real-but-unused pins like the second op-amp on a dual op-amp (LM358 pins 5/6/7 when only op-amp A is used). For digital chips, NC markers are fine. For op-amps specifically, tie-back wiring (unity-gain follower with input held at a fixed voltage) is the better engineering practice — prevents the floating amplifier from oscillating or coupling noise — but NC markers are valid and ERC-clean.

Don't conflate the schematic-level `(no_connect)` marker (board-specific intent, common) with a symbol pin's `no_connect` electrical type (part-designer's intent that the pin should never be wired, used in symbol definitions for reserved/NC pads). Both silence ERC; the schematic marker is the more frequent tool.


## 2026-05-03 — Scripted schematic edits on kart-medulla (text-level, no KiCad GUI)

**What worked: pattern replication via direct s-expression edits.**

Tasks completed by writing s-expression blocks straight into the schematic file:
1. **Connector pin stubs** — added 8 wire+label pairs to empty pins on CN8/CN9/CN10 (push-in connectors with no wires from EasyEDA conversion). Wire length 36.83 mm leftward, matching the existing CN4-CN7 pattern. Labels named `<REF>_<PIN>_TODO` so user can grep for unrenamed ones.
2. **Sheet page resize** — A3 → A2 (one-line `(paper "A2")` change in both root and child `.kicad_sch`). Zero risk, no content moved.
3. **GPIO expander stub replication** — user added one stub on PCF8574 (U25) pin 13 INT#; we replicated the 21.59 mm pattern to other free pins.
4. **Connector column alignment** — moved CN8 by (-1.27, 0) and CN9 by (-2.54, 0) so all of CN7/CN8/CN9 share x=205.74. For each move, the connector + its 3 wires + 3 labels move as a unit (geometric coupling preserved).

**What did NOT work: free-form schematic design.** Adding new components, routing wires for new sub-circuits, deciding where connectors should live on the page — all GUI work. Programmatic placement produces overlap, ugly routing, broken visual conventions. KiCad IPC API (`kicad-python`) is for *modifying existing* schematic content, not creating new design layout.

**Lessons / gotchas:**
- **Pin "empty" detection requires checking ALL connection types**, not just wires:
  - regular `(label ...)` blocks
  - `(global_label ...)` and `(hierarchical_label ...)` blocks (different from regular labels — separate regex)
  - `(no_connect ...)` markers (pin intentionally unused — adding a wire there causes ERC errors)
  - Labels can be placed *directly on a pin attach point* with no intermediate wire (KiCad treats placement-on-pin as a connection)
  - Initial naive pass missed CMD_REVERSE (a hierarchical label sitting on U25 pin 5) and a `no_connect` marker on U25 pin 12. Resulting wires had to be removed in a follow-up edit. Always audit all four marker types before declaring a pin "empty".
- **Floating-point precision:** moving coordinates by deltas can introduce artifacts like `205.73999999999998` instead of `205.74`. KiCad tolerates these but they're ugly in diffs. Always round to 4 decimal places after coordinate arithmetic, then `:g`-format to drop trailing zeros.
- **KiCad rewrites file format on first open** after an external import: `generator` field changes (`easyeda_pro_to_kicad` → `eeschema`), whitespace/element ordering normalizes, version field bumps to KiCad's current. First post-conversion git diff is huge (thousands of lines, mostly cosmetic); subsequent diffs are small and meaningful. Don't be alarmed by the first big diff.
- **KiCad has no auto-reload of files modified externally**, and no `File → Reload from Disk`. If KiCad has the schematic editor open and the file is edited underneath, the next Ctrl+S in KiCad silently overwrites the external changes. Check for `~<projectname>.kicad_pro.lck` (project lock — held while launcher is open) AND `lsof` on the specific `.kicad_sch` (held only while the schematic editor window is open). Project lock alone doesn't mean the schematic is held — verify per-file.
- **Wire termination shortcut:** in KiCad eeschema, wire mode (`W`) is finished by **double-click** at the endpoint, NOT by Esc (Esc cancels the in-progress wire) and NOT by Enter (does nothing). Single-click on a pin/wire/junction also terminates cleanly.
- **`(at X Y)` in symbol blocks** has the rotation angle as a separate trailing integer for symbol instances (3 numbers), but for some other elements it's just X Y (2 numbers). Need separate regex patterns for both forms.
- **PCB footprint references** in `.kicad_pcb` use bare names (`"C0603"`) without library prefix when the project has a local `<projectname>.pretty/` folder — KiCad auto-discovers it if the folder name matches the project name.

**Pattern that's safe to script:** geometric translation/replication where you have:
1. Existing data to copy (length, direction, format)
2. Known target coordinates that are grid-aligned
3. No spatial design judgment required (placement decisions inherited from existing elements)

**Pattern that's NOT safe to script:** anything that requires deciding "where should this go visually" — symbol placement on an empty area, wire routing around existing elements, label placement that doesn't follow from a clear pattern.

**Two more bugs hit on day 2:**

1. **Y-flip between symbol library and schematic instance coordinates.** KiCad's `lib_symbols` use Y-up convention (paper-schematic legacy: positive Y = up the page). When a symbol is INSTANTIATED in a schematic, KiCad applies an automatic Y-flip — schematic coords are Y-down. Initial pin-position calculations did NOT apply the flip, so PCF8574T pin numbering was inverted vertically: my "P0" stub landed on P1, my "P7" stub landed on INT#, etc. The symptom: the user opens the file and sees `EXP_P0_TODO` sitting next to "P1" on the chip. Fix: world_y = symbol_y - lib_pin_y (NOT +). Verify by cross-referencing one known wire (e.g., the user-added stub's known coordinates) against your computed pin positions BEFORE doing pattern replication based on those coords.

2. **Labels are NOT always exactly at wire endpoints.** EasyEDA-converted schematics have label positions that are sometimes 1.27 mm offset from the wire's geometric endpoint (probably because EasyEDA stores label-anchor differently from KiCad). When moving a connector + wires + labels as a unit, a tight tolerance (0.05 mm) won't catch labels that are positioned slightly inside the wire. Symptom: connector and wires move, labels stay, wires now visually disconnected from labels (functionally still fine if the label connects-by-name elsewhere, but ugly and easy to misread as a broken net). Fix attempts: (a) use bigger tolerance (~2 mm) when looking for labels at wire endpoints; (b) for moves that include real-signal labels (not TODO placeholders), revert and do the move in eeschema GUI instead. Detected by ERC violation count jumping by ~3 per affected wire (single-endpoint warnings appear).

**On Y-alignment of converted connectors:** the right-side connectors (CN7-CN10) are 1.27 mm above the left-side row positions. Aligning them programmatically tripped the label-offset bug above (CN1-CN4 labels are EasyEDA-style offset from their wires). Reverted; left as a GUI task. Safe scriptable alignment was limited to X-column alignment of CN7/CN8/CN9 where all the labels were freshly-added TODO labels at exact wire endpoints.

**The Y-flip applies to connector symbols too, not just chips.** Reflex was to think the lib-vs-schematic Y-flip was a chip-pin-specific gotcha, but it's universal — every symbol's pin coords need it. For the 1990012 push-in connector: lib has pin 1 at y=+2.54 (top in lib coords), pin 3 at y=-2.54 (bottom). After the flip, world pin 1 is at center_y - 2.54 (smaller y, top of screen), pin 3 at center_y + 2.54 (bottom). Earlier connector code used `y + 2.54` for pin 1, which was wrong — the wires/labels still attached correctly because pin attach POINTS were computed for all 3 pins and the symmetry hid the bug, but pin number reporting in commit messages was inverted. Always sanity-check pin numbering against a known reference (e.g., open the schematic, see which pin number the top-most wire belongs to).

**Adding a power symbol via text edit requires THREE places to update:**
1. The symbol-instance `(at X Y angle)` in the symbol header
2. The `(property "Reference" "#PWRnn")` block (the *property* reference)
3. The `(instances ... (path "..." (reference "#PWRnn")))` sub-block (the *instance-path* reference)

Items 2 and 3 must match. KiCad uses the instance-path reference (item 3) for display; if you only update item 2, ERC and the GUI both still show the template's old reference number. Symptom: a fresh `#PWR36` symbol appears in ERC reports as `#PWR08` (the number from whatever symbol you copied as a template). Always grep for any leftover stale ref numbers after copying a symbol block.

## 2026-05-03 — EasyEDA Pro → KiCad migration (kart-medulla)

**What worked:** [ConvertEDA](https://converteda.com) (free beta web service, drag-and-drop the `.epro`). Produced full KiCad 9-format project: 175KB `.kicad_pcb`, 251KB `.kicad_sch` (hierarchical, root + `_P1` sheet), 36 footprints in `kart-medulla.pretty/`. Validated openable by KiCad 10.0.1.

**What didn't work:**
- **KiCad 10.0.1 native importer** (`File → Import Non-KiCad Project → EasyEDA Pro`): silently produced empty stubs — 79-byte `.kicad_pcb`, 230-byte `.kicad_sch`. No error shown. Likely a format-version lag — the source `.epro` was exported by EasyEDA Pro **2.2.47.7** (per `editorVersion` in the unzipped `.epcb`) and the KiCad importer probably hasn't been updated for that version yet. The `.epro` itself is a valid zip with full content (verified manually).
- **`easyeda2kicad6`** (yaybee/easyeda2kicad6, npm): wrong tool entirely — converts EasyEDA **Standard** (old JSON format) → KiCad **6**. We need Pro → KiCad 10.
- **`easyeda2kicad.py`** (uPesy/easyeda2kicad.py, pypi): only fetches individual LCSC components by ID. Not a project converter despite the name.
- **KiCad per-file import path** doesn't exist for EasyEDA Pro `.esch`/`.epcb` files. `Import → Graphics` only takes DXF/SVG; the schematic editor has no per-file Pro importer. Project-level only.

**`.epro` internal format** (useful for future debugging):
- Zip archive containing `project.json` + 8 directories: `SHEET/`, `PCB/`, `SYMBOL/`, `FOOTPRINT/`, `INSTANCE/`, `POUR/`, `PANEL/`, `BLOB/`, `FONT/`.
- Schematic data in `SHEET/<uuid>/<n>.esch`, JSON-Lines (`["DOCTYPE","SCH","1.1"]\n["HEAD",...]`).
- PCB data in `PCB/<uuid>.epcb`, same JSON-Lines style.
- For single-sheet projects, `INSTANCE/` is empty — instances are inline in the `.esch`/`.epcb`.

**Naming + repo decisions:**
- Project folder named `kart-medulla` (matches `kart-medulla` firmware repo modulo case, and team verbal usage — `kart-brain` / `kart-medulla`).
- Single monorepo (`dv-hardware`) for all KiCad projects rather than per-project repos. Reasons: shared `lib/`, single onboarding clone, atomic cross-board changes, repo size is small (KiCad files are KB/MB).
- Visibility: **public** (matches existing UM-Driverless `kart_*` and `driverless` repos).
- Naming case: **kebab-case** chosen as team standard. Searched org for documented snake_case rule — none exists (the `kart_*` snake_case is just de facto from older repos).
- Original "ESP32 Expander" project (Jan 2026, EasyEDA) was renamed to "Kart Medulla (expander for ESP 32)" in May 2026 — same board. Old export kept in `easyeda-source/kart-medulla_2026-01-10_pre-rename.epro` as historical baseline.

**Post-conversion state (raw, not yet cleaned up):**
- ERC: 347 violations. Mostly `lib_symbol_issues` for absent `gen` lib (converter emits `lib_id "gen:CAP"` / `gen:Res` but doesn't ship the `gen` library), `power` lib mismatches (`12V`, `+5V_REG` not in KiCad's stdlib), and `footprint_link_issues` from missing `fp-lib-table`.
- DRC: 165 violations + 31 unconnected items. Will mostly resolve once footprint library is registered.
- **Cleanup deferred** — design is still in active flux (more green push-in connectors being added for expander chip GPIOs). No point cleaning ERC against a moving target. Revisit when schematic stabilizes.

**Gotchas hit:**
- KiCad 10's project-local `.history/` dir contains its own internal `.git/`. When committed naively, git treats it as a submodule pointer and the `.history/` gitignore rule does NOT apply. Fix: `git rm --cached projects/<x>/easyeda-source/.history`. Gitignore alone is insufficient once the embedded repo has been seen by git.
- **Gitignore trailing comments are NOT supported.** A line like `.history/  # KiCad local history` is interpreted as a literal pattern (the spaces and `#` become part of the pattern), so the rule silently does nothing. Comments must be on their own line. Verify any rule with `git check-ignore -v <path>`.
- Opening an `.epro` directly in KiCad creates sibling stub `.kicad_pcb` / `.kicad_pro` / `.kicad_sch` files in the same directory (sized 79 / 2 / 230 bytes — clear marker of failed conversion). Added blanket gitignore for `projects/*/easyeda-source/*.kicad_*` to prevent future contamination of source archives.
- `kicad-cli sch erc <file>` writes the report to **CWD by default**, not next to the input. Always pass `-o /path/to/report.rpt` explicitly to avoid littering the working directory.
- `kicad-cli` has no `import` subcommand — only `erc`, `drc`, `export`, `upgrade`. Headless EasyEDA conversion is not possible via KiCad CLI.

**Internal renames applied to ConvertEDA output** (it preserved the EasyEDA project name verbatim):
- Filenames: `Kart_Medulla_(expander_for_ESP_32).kicad_*` → `kart-medulla.kicad_*`, same for `_P1.kicad_sch` and `.pretty/` folder.
- Internal refs in `.kicad_sch` (`Sheetfile`, `project` blocks in instances), `.kicad_pcb` (title_block), `.kicad_pro` (`meta.filename`): same global string replace `Kart_Medulla_(expander_for_ESP_32)` → `kart-medulla`. Verified no stale refs remain (except the gitignored `.kicad_prl`).

## Reference

- KiCad EasyEDA importer docs: https://dev-docs.kicad.org/en/import-formats/easyeda/index.html
- ConvertEDA (worked): https://converteda.com
- KiCad IPC API (for future automation): https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html
- `kicad-python` (official Python bindings for IPC API): https://pypi.org/project/kicad-python/
