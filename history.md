<!-- consult selectively — grep, never read in full -->

# History

Append-only log. Chronological (oldest first), append at the end.

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

---

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

---

## 2026-05-04 — KiCad no_connect marker semantics (corrected)

The `(no_connect)` flag (the small "X" placed on a pin in the schematic editor) means **"the designer intentionally chose not to wire this pin to anything external on this board"**. It silences ERC's `pin_not_connected` warning by declaring the omission deliberate.

It does **not** mean:
- The pin doesn't physically exist on the package
- The pin is internally disconnected on the silicon
- The pin is a manufacturer-designated NC pad

Source: KiCad eeschema docs (master) — "No-connection flags are used to indicate that a pin is intentionally unconnected. These flags prevent 'unconnected pin' ERC warnings for pins that are intentionally unconnected." (https://docs.kicad.org/master/en/eeschema/eeschema.html)

Practical implication: any unused pin can carry a `no_connect` marker, including real-but-unused pins like the second op-amp on a dual op-amp (LM358 pins 5/6/7 when only op-amp A is used). For digital chips, NC markers are fine. For op-amps specifically, tie-back wiring (unity-gain follower with input held at a fixed voltage) is the better engineering practice — prevents the floating amplifier from oscillating or coupling noise — but NC markers are valid and ERC-clean.

Don't conflate the schematic-level `(no_connect)` marker (board-specific intent, common) with a symbol pin's `no_connect` electrical type (part-designer's intent that the pin should never be wired, used in symbol definitions for reserved/NC pads). Both silence ERC; the schematic marker is the more frequent tool.

---

## 2026-05-04 — `unconnected_wire_endpoint` requires terminating the wire's geometric endpoint, not just the net

A label sitting *mid-wire* still connects the label's net to the wire (KiCad uses the label's `(at)` point, not the wire's ends, for net assignment). But the wire's geometric endpoints are a separate ERC concern: if a wire endpoint sits in empty space — not on a pin, not at a label's `(at)` point, not at another wire/junction — ERC fires `unconnected_wire_endpoint` even though the net is logically named. Place labels at the wire endpoint (or shorten the wire to end at the label) so the geometry and the electrical termination coincide.

Mental model: ERC checks two things separately. (1) Does the *net* have at least the right kind of pins on it? (2) Does each *wire* have its endpoints terminated by something that "anchors" it (pin, label, junction, other wire)? Mid-wire labels satisfy (1) but not (2).

---

## 2026-05-07 — MAX4660 (U14) symbol audit: false alarm on pin numbers, real bug on electrical types

**Trigger:** User noticed two pins on U14 (MAX4660 SPDT throttle mux) both labeled "NC" with red X markers in the symbol drawing. Asked which one is the actual no-connect.

**Initial finding (correct):** The symbol has two `NC` labels — pin 2 is "Normally Closed" (the SPDT default-throw signal terminal, wired to `PEDAL_ACC__0_5V`) and pin 5 is the package's "No Connect" (no internal die connection). The schematic itself correctly places a no-connect flag on pin 5. The red X on pin 2 in the symbol drawing comes from the pin's *electrical type* being set to "Unconnected" — which is wrong, it should be Passive. Same issue may apply to pin 7 (V−) which also drew with an X in the symbol editor.

**Wrong escalation (then corrected):** I claimed the symbol's pin *numbers* were also shuffled vs. datasheet — basing this on a WebSearch snippet that decoded the Maxim datasheet pinout caption as `1=IN 2=N.C. 3=GND 4=COM 5=NC 6=V- 7=NO 8=V+`. I pre­sented a scary table showing the schematic would put +5V on COM, signal on V+, etc. Catastrophic-sounding but **not verified against the actual datasheet**.

**Disconfirmation:** User asked for a proper downloaded symbol. SnapEDA `MAX4660EUA+T` (SnapEDA-verified) has pin numbering: `1=COM 2=NC 3=GND 4=V+ 5=NC 6=IN 7=V- 8=NO 9=EPAD` — **identical to the original EasyEDA-converted symbol**. SnapEDA validates parts, so the correct pinout is the SnapEDA/original one, not my WebSearch interpretation. My pin-shuffling claim was wrong.

**Real status of original symbol:** Pin numbers correct. Electrical types wrong on pins 2 and 7 (drawn with X). No physical wiring danger; just an ERC and clarity issue.

**Lesson:** WebSearch snippets that "decode" a pinout caption from a position-list string are unreliable; do not present them as verified facts. SnapEDA-verified symbols and the existing project symbol agreeing with each other is much stronger evidence than a single search snippet. When two independent sources agree against my reading, retract before escalating.

**Migration context:** This symbol came in via the EasyEDA-Pro → KiCad migration (ConvertEDA, May 2026). The conversion preserved pin numbers and labels but mis-set electrical types, which is the actual EasyEDA-conversion artifact here — not pin shuffling.

**Download workflow note:** SnapEDA, Component Search Engine (Samacsys), Ultra Librarian all gate KiCad downloads behind login walls. Programmatic curl/WebFetch fails. User pointed out I could have driven their logged-in Chrome with `osascript` — viable next time, since global rules confirm Chrome has "Allow JavaScript from Apple Events" enabled. SnapEDA download did not actually require an account in this instance per the user.

**Verified MAX4660 8-pin µMAX pinout (from SnapEDA-verified symbol; matches original project symbol):**
```
1: COM    8: NO
2: NC     7: V-
3: GND    6: IN
4: V+     5: NC (no internal connection)
9: EPAD (thermal pad)
```

---

## 2026-05-07 — MAX4660 (U14) integration: SnapEDA footprint+3D adopted, hidden wire-disconnect bug found and fixed

**Symbol correctness summary (the part that confused things):**
- SnapEDA-downloaded symbol (`MAX4660EUA_T.kicad_sym` from the zip): **correct**.
- Project library symbol (entry inside `projects/kart-medulla/kart-medulla.kicad_sym`): **also already correct** (pin 2 = passive, pin 5 = no_connect).
- Cached copy inside the schematic file (`lib_symbols` block in `kart-medulla_P1.kicad_sch`): **wrong** — pin 2 = no_connect (a stale snapshot from an earlier broken symbol version).

KiCad renders symbols from the schematic's cached copy, not the library — so the symbol editor showed the broken cache, even though the library was fine. Running `Tools → Update Symbols from Library` would have fixed it. **SnapEDA was not needed to fix the symbol** — the library already had the right one. SnapEDA's actual contribution to this integration was the verified **footprint** (`SOP65P490X110-9N.kicad_mod`) and **3D model** (`MAX4660EUA_T.step`), plus confirmation that the existing pin map was correct.

After confirming the original symbol's pin numbers were correct (matched SnapEDA), did a full SnapEDA integration for U14 (MAX4660 throttle mux). Workflow:

1. User downloaded `MAX4660EUA_T.zip` from SnapEDA without needing an account (so the SnapEDA login wall reported earlier wasn't actually blocking — should have tried first).
2. Extracted: symbol `MAX4660EUA_T.kicad_sym`, footprint `SOP65P490X110-9N.kicad_mod`, 3D model `MAX4660EUA_T.step`.
3. Copied footprint into `projects/kart-medulla/kart-medulla.pretty/`.
4. Created `projects/kart-medulla/3dmodels/` and put `MAX4660EUA_T.step` there. (First 3D model in the project — no prior convention; chose `${KIPRJMOD}/3dmodels/` as the standard location.)
5. Added `(model "${KIPRJMOD}/3dmodels/MAX4660EUA_T.step" ...)` to the new footprint.
6. Updated `kart-medulla.kicad_sym` U14 symbol's default Footprint property → `kart-medulla:SOP65P490X110-9N`, Datasheet → analog.com.
7. Updated U14 instance in `kart-medulla_P1.kicad_sch` (Footprint + Datasheet override).
8. **Critical fix:** the cached `lib_symbols` copy of `MAX4660EUA_T` in `kart-medulla_P1.kicad_sch` had pin 2 (NC) marked as electrical type `no_connect` — wrong; the library copy in `kart-medulla.kicad_sym` correctly had `passive`. The cache had drifted from the library, and KiCad uses the cache, so the schematic editor was rendering pin 2 with the no-connect-X marker. Patched the cache to `passive`.
9. **Real bug uncovered:** with pin 2 fixed, ERC immediately fired `pin_not_connected` on U14 pin 2. Investigation showed the `PEDAL_ACC__0_5V` wire ended at x=375.92 but pin 2's connection point is at x=384.81 — an 8.89 mm gap. The wire **never actually reached pin 2**. The broken `no_connect` pin type had been silencing this ERC violation by making the pin a legal "no connect" terminal. So the throttle mux's default-throw input (sensor pedal value passing through to the motor) was not wired at all in the schematic. Extended the wire's endpoint to (384.81, 217.17) to close the gap. ERC now reports 0 errors.

**Lesson:** When ERC suddenly flags a violation after a "cosmetic" symbol fix, **the symbol bug was likely concealing a real schematic bug**. `no_connect` and similar permissive pin types act as ERC-silencers; using them inappropriately hides genuine wiring errors. Cache-vs-library drift is a known KiCad failure mode — `Tools → Update Symbols from Library...` would have surfaced this earlier.

**Files changed:**
- `kart-medulla.kicad_sym`: U14 entry — Footprint and Datasheet properties populated.
- `kart-medulla_P1.kicad_sch`: cached `MAX4660EUA_T` symbol pin 2 type `no_connect → passive`; U14 instance Footprint and Datasheet updated; `PEDAL_ACC__0_5V` wire extended from 375.92 → 384.81 to actually reach pin 2.
- `kart-medulla.pretty/SOP65P490X110-9N.kicad_mod`: new footprint with 3D model reference.
- `3dmodels/MAX4660EUA_T.step`: new (folder created).

**Verification:** `kicad-cli sch erc --severity-error` → `Found 0 violations`. Paren-balance check on all edited files passes.

---

## 2026-05-07 — kicad-mcp-pro installed; pins 20/21 (UART0 TX0/RX0) NC'd on kart-medulla

**Tooling change:**
- `kicad-cli` symlinked to `/opt/homebrew/bin/kicad-cli` (was buried inside `/Applications/KiCad/KiCad.app/Contents/MacOS/`). Reports KiCad 10.0.1.
- `kicad-mcp-pro` v3.1.8 installed via `pipx --python /opt/homebrew/bin/python3.14` (the package needs Python ≥3.12; the user's default `python3` is 3.11 from a platformio venv). Registered in Claude Code at user scope: `claude mcp add kicad -s user -- /Users/rubenayla/.local/bin/kicad-mcp-pro --transport stdio --profile agent_full`. MIT-licensed despite the "Pro" name. Other contenders considered: `lamaalrajih/kicad-mcp` (lighter, KiCad 7+), `Seeed-Studio/kicad-mcp-server` (39 tools, targets KiCad 9), `mixelpixx/KiCAD-MCP-Server`. Picked the Pro one because it's the only one that explicitly supports KiCad 10.

**Design change applied:**
- Header pins 20/21 of the ESP32-S3-DevKitC-1 footprint on `kart-medulla_P1.kicad_sch` are GPIO 44/43 = RX0/TX0 = UART0. Previously rendered as global labels `TX0` / `RX0` with single-pin wires going nowhere. Confirmed via grep that nothing on the medulla PCB or in `~/dv/kart/kart-medulla` firmware references these nets. They are nonetheless reserved by the dev board's on-board CP210x USB-UART bridge (which physically drives those module pins whenever the UART USB-C is plugged in) — so they must not be reassigned on the medulla side either. Fix: removed the global labels + their wires, added `(no_connect)` markers at the pin endpoints (389.89, 48.26 / 50.8), and added `(text)` annotations explaining the reservation. Commit `b07c56f`.

**Gotchas hit (now also rules in AGENTS.md):**
- **kicad-mcp-pro caches the schematic in memory** between calls. After `kicad_set_project`, the next MCP write call (`sch_add_no_connect`, etc.) flushes the cached copy to disk, silently overwriting any direct-file edits made between MCP calls. Symptom: `git status` shows zero changes after multiple "successful" Edit calls. Fix: pick one workflow per session — pure-MCP or pure-file-edit, never interleave. KiCad open in the GUI is *fine* if you only reload (File → Revert) and never save before the agent commits; KiCad itself only writes on explicit save.
- **`agent_full` MCP profile** is missing `sch_delete_label` and `sch_add_text`. So "replace a global label with a text annotation" must be done by direct file edit. Filed mentally as a feature gap.
- **`sch_add_no_connect` snaps to 2.54 mm by default.** Header pins on the official ESP32-S3-DevKitC-1 sit on 1.27 mm offsets (x=389.89). Marker landed 1.27 mm off; fix: pass `snap_to_grid=False`.

---

## 2026-05-07 — Idea: agent works in a separate git worktree so user can keep KiCad open

**Problem context:** Twice today the agent's edits to `kart-medulla_P1.kicad_sch` were silently clobbered — once by KiCad's stale-buffer save, once by interleaving direct file edits with kicad-mcp-pro writes. Root cause is that the agent and the user's KiCad are racing for the same on-disk file.

**Idea (not yet implemented; user said note it, don't set up):** add a sibling worktree just for agent work.

```
~/repos/dv-hardware/         user's main worktree, KiCad stays open
~/repos/dv-hardware-agent/   agent's worktree, on branch agent/<topic>
```

Setup is `git worktree add ../dv-hardware-agent agent-work`. Agent points the MCP at the worktree's project path with `kicad_set_project /Users/rubenayla/repos/dv-hardware-agent/projects/<board>` and edits there. KiCad's `${KIPRJMOD}` resolves relative to the worktree's `.kicad_pro`, so symbol libs (`*.kicad_sym`), footprint pretties (`*.pretty/*.kicad_mod`), and 3D models (`3dmodels/*.step`) all work without re-pathing. Agent commits + pushes on its branch; user pulls into their worktree when ready and runs `File → Revert` in KiCad to pick up the changes.

**Trade-offs to remember if/when this gets set up:**
- KiCad files are text but not line-mergeable. Concurrent edits to the *same* `.kicad_sch` or `.kicad_pcb` in both worktrees → ugly manual merge (KiCad re-formats huge sections on save, so even small logical changes can collide on hundreds of lines). Coordinate by topic — agent on one feature branch per task, user avoids touching the same file.
- The MCP is a single process. `kicad_set_project` per session is enough; no reconfig of the MCP itself.
- Could be wrapped in `~/.claude/skills/dv-worktree/SKILL.md` so the agent can spin one up on demand.

---

## 2026-05-07 — KiCad ERC: "Input pin not driven" on GND net (kart-medulla GPIO expander U25 A0)

### Problem
ERC error: `Symbol U25 Pin 1 [A0, Input, Line] — Input pin not driven by any Output pins`. A0 of the PCF8574T (I2C address pin) was tied to GND for address 0, but ERC kept failing. Took many iterations to diagnose because of multiple overlapping KiCad concepts that all *look* the same to a human.

### Root causes (compound)
1. The "GND" on A0 was a **global label** (the arrow shape, `Ctrl+L`), not a **GND power symbol** (the triangle, `P`). They share the name "GND" but live on **separate nets**. ERC does not auto-merge them.
2. Even after using the correct GND **power symbol**, ERC still complained because the **GND power symbol's pin is type Power Input**, not Power Output. A net with only Power Input pins has no driver → ERC error.
3. Fix for #2 is **PWR_FLAG** — a special symbol whose pin is type Power Output, exists exclusively to tell ERC "this rail is actually driven." Need exactly **one** PWR_FLAG per power net **across the entire design** (one for GND, one for +3V3, etc.). Two PWR_FLAGs on the same net = "Power output and Power output connected" error.

### Key facts to never re-derive
- **Global label "GND" ≠ GND power net.** Labels are just net names. Power symbols carry power-net semantics.
- **Power symbols all named "GND"** (the triangles) **share one global net** across all sheets, regardless of where placed. So one PWR_FLAG drives every GND triangle in the project.
- **Global Label "Shape" property** (Input/Output/Bidirectional/Tri-state/Passive) is **purely cosmetic** — only changes the arrow shape. Does not affect ERC electrical type. ERC drive checks look at *symbol pin types* and PWR_FLAG, never at label shapes.
- **Pin types that DRIVE a net for ERC purposes:** Power Output, Output, PWR_FLAG. Power Input does not drive (this is why GND/+3V3 power symbols alone don't satisfy ERC).
- KiCad shortcuts: `L` = local label (sheet-scoped), `H` = hierarchical label, `Ctrl+L` = global label (the arrow), `P` = power symbol (the triangles, GND/+3V3/etc.).

### Recipe to make a power net pass ERC
1. Place GND power symbol (`P` → GND) on every GND-bound wire. Make sure the pin tip lands on the wire endpoint with a green junction dot.
2. Place exactly **one** PWR_FLAG (`P` → PWR_FLAG) somewhere on the GND net. Conceptually next to the actual power source (e.g., ESP32's GND pin) is fine, but electrically it doesn't matter.
3. Repeat (#2 only) for +3V3, +5V, etc.

### Confusion to avoid next time
- Do not suggest "the wire is floating" or "no junction" without verifying — the user can see the schematic and that gaslights them. The error is almost always a **net semantics** issue (label vs. power symbol vs. missing PWR_FLAG), not a literal disconnection.
- Trust the user when they say "I already placed the power symbol" — verify by checking PWR_FLAG count and pin-to-wire snap, not by re-explaining the difference between symbols.
- The KiCad GND power symbol can appear rotated (pointing left, right, down) — it is still the same symbol. Don't mistake a rotated GND triangle for an arrow-shaped global label.

### Resolution
User fixed it by placing **three separate GND power symbols, one per pin (A0, A1, A2)**, instead of wiring all three pins together to a single shared GND symbol. ERC then passed (0 violations).

### Why three-symbols-works when one-symbol-wired-to-all-three didn't (NOT FULLY EXPLAINED)
Electrically these should be identical: all three pins on the global GND net via the PWR_FLAG elsewhere. Power symbols with the same name (`GND`) merge into one global net regardless of how many copies are placed. **No confirmed root cause** for why the single-symbol version failed ERC on A0 specifically.

Most likely candidate (unverified): a hidden wire-connectivity issue where A0's pin or one wire segment was off-grid / not actually joined to the rest. ERC's "Input pin not driven" fires when a net has only Input-type pins and no driver — *including* the case where the "net" is just one pin with nothing else on it (a one-node net counts as undriven). That would explain why A0 alone failed while A1/A2 passed. But the user did not visually confirm a misalignment, so this remains a hypothesis.

### Lesson for future ERC drive errors
If ERC says "Input not driven" on **one specific pin** when adjacent pins on what looks like the same wire are fine: try dropping a power symbol directly on the offending pin (bypass the wire). If that fixes ERC, the wire connectivity was the issue. If not, there's something else going on — inspect the .kicad_sch file via MCP rather than guessing.

### Final final
- One PWR_FLAG per power net across the whole design (not per sheet, not per symbol). On disk this project has `#FLG01` (GND), `#FLG_+3V3`, `#FLG_+5V_USB01`, `#FLG_+12V01`. Don't add more.
- The kicad MCP (`mcp__kicad__run_erc`, `grep PWR_FLAG <sch>`) reads disk and is far faster than iterating from screenshots.

---

## 2026-05-07 — Decision: stay on KiCad long-term (vs EasyEDA)

Revisited tool choice after MCP-related friction. Decision: **KiCad**, long-term.

Reasoning:
- Open format, local files, git-tracked — work is owned, not hosted on a vendor's servers.
- No vendor lock-in; portable across fabs (not tied to JLCPCB pipeline).
- Scriptable; MCP tooling is improving and recent ERC issues were all resolved within KiCad.
- EasyEDA is fine for quick JLC-bound boards but wrong foundation for hardware meant to live for years.

---

## 2026-05-07 — Git workflow: rebase-on-pull when both sides made identical changes to the same file

Situation: peer pushed commit `d0f64d1 "pcb update"` (touched `.kicad_pcb` + 1 line of `.kicad_pro`). Local had uncommitted edits including the **same 1-line change** to `.kicad_pro` (KiCad GUI clears `used_designators` automatically) plus schematic + agent-doc edits.

**Resolution path that worked cleanly:**
1. Commit local work first (split into logical commits) — gives a checkpoint to return to if anything goes wrong.
2. `git pull --rebase` — replays local commits on top of peer's. Identical `.kicad_pro` change auto-resolved with no prompt.
3. Push.

**Why `--rebase` over plain `git pull`:** plain pull creates a merge commit for trivial 1-commit divergences (noisy). Rebase produces linear history `peer → you`. Local commits get new SHAs (parent changed) — safe because they weren't pushed yet. Never rebase already-pushed commits.

**Recovery levers if rebase goes wrong:** `git rebase --abort`, `git reflog` + `git reset --hard <sha>`. Commits are nearly impossible to lose once made.

---

## 2026-05-07 — Parallel work on a single KiCad PCB: not really viable

Question: can two+ people work on different regions of the same `.kicad_pcb` in parallel without merge conflicts?

**Short answer: no, not on a shared `.kicad_pcb`.** Reasons:
- `.kicad_pcb` is one monolithic S-expression file. Footprints, tracks, vias, zones are flat lists.
- KiCad's save serialization is **not order-deterministic** between sessions, so even non-overlapping spatial edits can produce diff hunks git can't auto-merge cleanly.
- Global state (net classes, design rules, stackup, board outline) is shared — any edit there forces a manual merge.

**What works:**
- **Schematic ↔ PCB split** (different files). What we're doing now — Rubén on schematic + docs, peer on PCB. Trivially parallel.
- **Multi-board projects** — split logically into separate KiCad projects (e.g. main board + sensor adapter). Each is its own file set.
- **Time-sliced single-writer** via the `tasks.md` claim pattern. Boring but reliable.

**What sort-of works:** spatial division + serialized merges (A: top quadrant, B: bottom). Second person rebases and copies changes manually. Painful at >2 people.

**What doesn't exist in stock KiCad:** real-time multi-user editing or per-region locking. (Altium 365 / OrCAD X have it; KiCad doesn't.)

**Recommendation for this team:** keep the schematic/PCB split. Third person → give them a separate sub-board as its own project, not a chunk of medulla.

---

## 2026-05-07 — Investigated KiCad-AI workflow problems; added workflow doc + guard; tested kicad-sch-api

**Trigger:** Recurring failures in error log (MCP cache clobbering edits, KiCad GUI auto-saving over agent commits, hand-rolled netlist parsers, screenshots-instead-of-MCP loops). User asked for a real fix.

**Root structural finding:** KiCad has no official IPC API for the **schematic editor** as of KiCad 10. PCB has `kicad-python` (works with running KiCad), schematic does not. Every schematic-editing MCP server (kicad-mcp-pro, Seeed-Studio, lamaalrajih, circuit-synth) is doing raw S-expression manipulation. That is the source of all our caching/conflict pain — these are not bugs in any one server, they're a structural limit until KiCad ships schematic IPC (KiCad 11+).

Seeed-Studio docs put it explicitly: *"KiCad must be closed and reopened to see file changes (no hot-reload). Use KiCad GUI for design work. Use this MCP server for analysis, validation, and code generation."* Adopted as our default.

**What was added:**
- `kicad-workflow.md` — codifies two modes: (A) read-only MCP, KiCad GUI may be open, default 90% of the time; (B) direct-edit, KiCad closed, no MCP writes that session. With tool-selection cheat-sheet.
- `scripts/guard-kicad-write.sh` — `pgrep -i kicad` and `pgrep -fl kicad-mcp-pro` preflight. Exits non-zero if unsafe. Dry-run confirmed.
- AGENTS.md "Editing KiCad files outside KiCad" updated with pointer to the workflow doc.

**kicad-sch-api evaluation (`circuit-synth/kicad-sch-api` v0.5.6):**
- **Read works.** `load_schematic('kart-medulla_P1.kicad_sch')` → 105 components, 141 wires, parses cleanly. Useful as a Python read API.
- **Write does NOT preserve format.** Round-trip test (`/tmp/kicad-sch-api-test/roundtrip.py`) produced large diff: drops `(thickness 0.1524)` from text effects, reorders properties, fills empty `Description ""` fields with library text, etc. Despite claims of "exact format preservation".
- **Reference validator is wrong.** Rejects KiCad-valid power-flag references containing `+` and `_` (`#FLG_+12V01`, `#FLG_+5V_USB01`, `#FLG_+3V3`) as "Invalid reference format". Need to call internal `_file_io_manager.save_schematic(sch._data, path)` to bypass — but the format-preservation issue is separate and worse.
- **Verdict: skip the library entirely.** Writes are broken (format reformat + buggy validator). Reads work, but reads are already covered by `kicad-mcp-pro` (`sch_get_symbols`, `sch_trace_net`, `sch_get_connectivity_graph`, `run_erc`, `export_netlist`) and `kicad-cli sch export netlist` — both already in our toolbox, neither has the MCP-write cache problem since we'd only call read tools. `kicad-sch-api` adds zero value to us. Edit-tool surgical regex remains the only direct-write path (preserves format exactly when changes are tiny). Re-evaluate when KiCad 11 ships schematic IPC.

**PCB side, when we get there:** use `kicad-python` (the official KiCad IPC API). Works with running KiCad GUI, no cache war. Enable in `KiCad → Settings… → Plugins → API server`. https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/

---

## 2026-05-08 — Source-of-truth flip + design clarifications (manual/auto mux, connector audit)

This session resolved several long-standing inconsistencies between the schematic, the pinout doc that lived in `~/dv/`, and what was actually built. Documenting the decisions here so we don't keep re-deriving them.

### Source of truth: dv-hardware (this repo) is canonical for chips and wiring

User's framing: "this is the pcb, can't be wrong." The schematic IS the physical artifact — derived docs can drift, the schematic cannot. So:

- `dv-hardware/projects/<board>/` is canonical for chip choices, nets, header pin assignments, decoupling, footprints. Anything that asks "what is on the board" → look at `kart-medulla.kicad_sch`.
- `~/dv/kart/<board>/` and `~/repos/kart-medulla` (firmware) defer. They carry firmware-specific overlays only: GPIO mode flags (open-drain etc.), idle-at-boot constraints, ISR notes, driver config.
- The pinout doc was moved from `~/dv/kart/kart-medulla/pinout-esp32-s3.md` to `dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md`. The `~/dv/` copy is now a 7-line tombstone pointing here.
- Don't write "this repo is the source of truth" inside the source-of-truth repo itself — that's circular. The pointer goes in the deferring repo. (User caught me trying to do this in `dv-hardware/AGENTS.md`; reverted.)

**Why this matters going forward:** disagreements between the schematic and any doc → fix the doc, not the schematic. PCB layout is in progress, so pin assignments will keep shifting; the doc has a header note saying re-verify before each fab release.

### Brake mux dropped — one MAX4660 is enough

Original 2026-05-01 design had two MAX4660s muxing throttle and brake separately between manual and autonomous modes. User clarified 2026-05-08: brake doesn't need autonomous-vs-manual muxing because manual mode doesn't route brake through the ESP32 at all (the manual brake is mechanical/hydraulic, not electrical). So:

- U14 MAX4660 (throttle) — kept.
- U17 MAX4660 (brake) — was never placed on the schematic. Don't add it. The brake autonomous command (`CMD_BRAKE__0_10V` on CN5) goes directly from the MCP4922 (via the 0–5 V → 0–10 V op-amp gain stage) to the brake valve driver, no switch.
- `SELECT_THROTTLE` (ESP32 GPIO 15) drives U14 SELECT only. The "drives both MAX4660 SELECT pins" wording in the old doc is wrong and has been fixed.

### CMD_REVERSE moved off ESP32 GPIO onto PCF8574 P0 (decision was 2026-05-03, but the pinout doc was still claiming the old design)

Original 2026-05-02 plan: ESP32 GPIO 36 in `OUTPUT_OPEN_DRAIN` mode, wired in parallel with the manual reverse button (wired-OR through the motor controller's existing 5 V pull-up). 2026-05-03 it moved onto U25 PCF8574T port P0 (pin 4) instead. Reasons:

- Frees GPIO 36, which was the only N8R2-only-safe GPIO assignment we had — design is now fully N8R8-compatible (no signal depends on the quad-PSRAM-only GPIOs 33–37).
- PCF8574 quasi-bidirectional outputs are natively open-drain with weak internal pull-ups, so the wired-OR architecture works the same way without needing an `OUTPUT_OPEN_DRAIN` flag in firmware.
- Firmware change: `CMD_REVERSE` is now an I²C write to the PCF8574 output register (writing 0 pulls REVERSE_WIRE LOW, writing 1 releases it to high-Z). No special pin-mode config.

**Fail-safe property preserved:** ESP32 dead or I²C bus down → P0 stays in its power-on-default state (all outputs high = high-Z) → only the manual button controls the line. Identical behavior to manual-only operation.

### Schematic-vs-doc discrepancies on the ESP32 header (7 pins)

The pinout doc still said these pins were active when the schematic actually has NC markers. All fixed in `docs/pinout-esp32-s3.md`:

| Pin | GPIO | Doc said | Schematic shows | Reason it's NC |
|---|---|---|---|---|
| 3 | 19 | USB_D- (USB-OTG to Orin) | NC | No USB-C connector on the medulla PCB this rev |
| 4 | 20 | USB_D+ | NC | Same |
| 7 | 48 | LED (status RGB) | NC | Using the dev-module's onboard LED, not an external one |
| 20 | 44 | RX0 (UART0) | NC | Dev-board's onboard USB-UART bridge already owns GPIO 43/44 |
| 21 | 43 | TX0 (UART0) | NC | Same |
| 32 | 17 | TX1 (UART1) | NC / SPARE | UART1 unused — the only UART link off-board uses UART0 via dev-module USB-C |
| 33 | 18 | RX1 (UART1) | NC / SPARE | Same |

Lesson: when a pinout doc lives in a different repo from the schematic, it drifts. With the source-of-truth flip + the doc now next to the schematic, this should stay aligned.

### SELECT_THROTTLE wiring traced clean (no action needed, just for the record)

User asked to confirm `SELECT_THROTTLE` is correctly wired. It is:

- U23 (LEFT_HEADER, SSW-122-01-T-D dual-row) symbol pins 15 & 16 (paired = LEFT_HEADER row 8 = physical Pin 30 = silkscreen `15` = ESP32 GPIO 15) → wire (313.69, 63.5)–(370.84, 63.5) → label `SELECT_THROTTLE`.
- U14 MAX4660 pin 6 (IN, the SELECT input) at (405.13, 219.71) → wire (405.13, 219.71)–(410.21, 219.71) → label `SELECT_THROTTLE`.
- R32 = 10 kΩ at (410.21, 224.79) on the same node → matches the spec'd hardware-default-manual pulldown.
- Both labels are local on a single sheet, so they form one net by name. ERC: 0 violations.

Earlier `mcp__kicad__sch_trace_net` reported "labels=2 pins=0" — that's misleading; it doesn't count pins reached via wire+label, only direct pin-to-name matches. Don't use it as a "no pins on this net" indicator.

### External-connector audit (CN1–CN10) — captured in tasks.md

Crossed every signal on the 10× green push-in connectors (CN1–CN10) against the schematic netlist. One signal definitely missing from the connectors: **`SDC_ENABLE`** (GPIO 39 — meant to drive the external SDC enable relay). The schematic only has a free-text annotation "SDC_ENABLE — orphan, expected from external module" near U24 pin 14; no actual label, no wire, no connector exit. Action item logged in `.agents/tasks.md` under "External-connector audit".

Also flagged for verification (not necessarily wrong, just worth confirming before fab): CN4 has no GND for the AS5600 (3 pins: SDA/SCL/+3V3 only); `SDC_IN_LOW_SIDE` (CN5) vs `SDC_NOT_EMERGENCY__3V3` (internal) need to be confirmed as bridged via a divider; the manual-throttle passthrough relies on `PEDAL_ACC__0_5V` branching internally to both the ADC divider and U14 NC pin.

---

## 2026-05-08 — Open question: tasks.md is getting long for human peers, three options on the table

**Problem:** `.agents/tasks.md` was written agent-first per `AGENTS.md` ("shared kanban for agents to read and update"). Long-form rationale per task is good for AI continuity but bad for human peers skimming the file. User flagged this and asked for alternatives. No decision yet — leaving the file as-is until we pick.

**Options considered:**

1. **Folder-per-task (`.agents/tasks/<slug>.md`, with `tasks.md` as a one-line-per-task index).** Best fit if individual tasks start growing real discussion threads — each gets its own git history, can be assigned by filename prefix, and humans only see the index. Cost: a tiny bit of indirection for agents (extra file open per task).
2. **GitHub Issues for humans, lean `tasks.md` for agents.** If the team is already on GitHub, peers look at issues anyway. `tasks.md` becomes a short list of refs (`#42 — SDC_ENABLE wiring`). Cost: requires the project to be on GitHub with issues enabled, and adds a sync responsibility (close-issue ↔ move-to-Done).
3. **Just compress.** Keep one file, each entry becomes one short line ("SDC_ENABLE missing — wire GPIO 39 to a connector, see history.md 2026-05-08"). Rationale lives in `history.md` (which is what `history.md` was designed for). Cheapest to do, matches the existing "history.md as the explainer, tasks.md as the to-do" split.

**My recommendation if/when this is picked up:** option 3 first (one-pass cleanup, no structural change). Move to option 1 later if individual tasks start sprouting discussion. Option 2 only if the team is already living in GitHub Issues.

---

## 2026-05-08 — kart-medulla CN1–CN10 pin assignments locked to ESP32 geometry

User asked: with CN1–CN5 going up the right side of the PCB and CN6–CN10 going down the left side (mirroring the ESP32 module's "chip" pinout convention), what's the best signal-to-CN-pin assignment so jumper wires from each ESP32 pin to its CN pin stay short?

**Result — agreed assignment (CN pin 1 / 2 / 3):**

Right side (bottom→top):
- CN1: GND / +12V_IN / GND  — battery input
- CN2: MOTOR_HALL_3 (5V) / MOTOR_HALL_2 (5V) / +5V  — halls (2 of 3)
- CN3: CMD_STEER_DIR (3V3) / EXP_P1 / EXP_P2
- CN4: REVERSE_WIRE / SDC_IN_LOW_SIDE / CMD_STEER_PWM (3V3) — final, after two corrections during the session: (a) `SDC_NOT_EMERGENCY` removed from CN4.1 (it's an internal ESP32→Q3-gate net, must not be on a CN), and (b) the `MANUAL_THR`/`PEDAL_THR` placeholder I briefly proposed for the freed pin was wrong — the manual-throttle source is the same net as `PEDAL_ACC__0_5V` (CN6.1), branched internally to the MAX4660 NC pin; no second external pedal wire exists. CN4.1 ended up as `REVERSE_WIRE` (the genuinely missing external output that I had clobbered when renaming CN8.1).
- CN5: HYDRAULIC_2 (0–5V) / PRESSURE_3 (0–10V) / GND

Left side (top→bottom):
- CN6: PEDAL_ACC (0–5V) / PEDAL_BRAKE (0–5V) / +3V3
- CN7: PRESSURE_1 (0–10V) / PRESSURE_2 (0–10V) / MOTOR_HALL_1 (5V)
- CN8: SDA (I²C) / BUZZER / EXP_P3
- CN9: SCL (I²C) / HYDRAULIC_1 (0–5V) / EXP_P4
- CN10: CMD_ACC (DAC, 0–5V) / CMD_BRAKE (DAC, 0–5V) / GND

**Rejected: swap MH1 ↔ CMD_STEER_DIR on the ESP32 to cluster all three halls on one side.** Tempting because halls then live on CN2 alone, but GPIO 0 is a strap pin (must be HIGH at boot for normal boot mode). The hall level shifter U5 (SN74LVC3G17) is push-pull, so:
1. A pull-up to 3V3 on the MH1 net can't override U5 actively driving LOW at boot — if the rotor leaves the hall LOW at power-on, ESP32 enters ROM bootloader and the kart won't run until manually rolled and reset.
2. If firmware ever mis-configures the GPIO as output, two push-pull drivers fight, risking damage to U5 or the ESP32 pad.

Keeping CMD_STEER_DIR on GPIO 0 is safe because firmware actively drives it HIGH and the SDC keeps the Cytron disabled at boot regardless. So the swap stays NOT done; MH1 stays on GPIO 16 and rides on the left-side CN7 alongside the pressure sensors. Cable layout is fine because wires terminate in independent Wago slots — per-CN cable grouping doesn't have to match standard sensor pinouts.

**Aside on GPIO 45 / Pin 8:** user spotted "VSPI" on a third-party pinout image and asked if the pin is reclaimable. The label is misleading — on ESP32-S3 it's the **VDD_SPI voltage select strap** (not the classic ESP32 "VSPI" peripheral). Internal pulldown at boot selects 3.3V flash (correct for our N8R2). The pin is usable as a regular GPIO after boot, provided nothing externally pulls it HIGH at boot. Same rule applies to GPIO 46 (Pin 36). Both still listed as RESERVED in `pinout-esp32-s3.md` out of caution; can be promoted to SPARE-usable if a future need arises. Not needed for this assignment.

---

## 2026-05-08 — Stacked-symbol confusion: Reference field vs parent symbol in KiCad GUI

While cleaning up a stray `U02` reference, the user found the symbol via Cmd+F (with hidden-fields search) but couldn't select-and-delete it. Two compounding causes:

1. **Two GND symbols stacked at exactly the same coordinate** `(125.73, 311.15)` — a legacy `kart-medulla:GND` (rotated 270°, with the bogus `Reference: U02`) buried under a standard `power:GND` (rotated 90°). Clicking the GND triangle selects only the top one. Grep for the coordinate (`grep "at <x> <y>" *.kicad_sch`) reveals stacks instantly.
2. **Cmd+F selects the matched property/field, not the parent symbol.** When the match is on a hidden Reference field, the side Properties panel shows `Field` with `Text = U02` and a `Visible` checkbox — that's the reference text, not the symbol. Pressing Delete from there would (try to) delete a reference field, not the symbol. The user's intuition "I thought it was part of the symbol" is right — references *are* parts of symbols — but in the GUI they're a separately-selectable child of the symbol, and selecting the field doesn't promote selection to the parent.

**How to actually delete a buried symbol via its hidden field in KiCad 10:**
- Trick that worked: in the Properties panel, tick **Visible** on the field. The reference text now shows on the canvas, anchored to the parent symbol's origin. You can see *where* the symbol lives (even if its body is overlapped by another symbol's body). Then click the symbol body at that location and Tab-cycle through stacked items, or just delete the now-visible reference's parent.
- Alternative when GUI fights you: close KiCad, surgically delete the symbol block from the .kicad_sch (Mode B per `kicad-workflow.md`).

**Confirmed safe-to-delete signal for stacked GNDs:** if `grep "at <x> <y>"` shows two power symbols + a junction at the same point, deleting one is a no-op for connectivity — the remaining symbol + junction keep the net intact. Verify with `kicad-cli sch erc` after deletion (no new violations at that coordinate).

In this case the deletion landed cleanly on disk: U02 gone, coord-occurrence count at (125.73, 311.15) dropped 9 → 4 (one full symbol's worth of property positions removed), ERC has 0 new violations at that point.

---

## 2026-05-08 (later) — CN cluster reshuffle: U25 moved to right side, all PCF8574-related signals re-clustered

User decided to physically place U25 (PCF8574 GPIO expander) on the right side of the PCB near CN3, and asked to cluster all U25-related signals (I²C bus + expander outputs + reverse) on the right-side CNs to minimize routing length. Six labels swapped (none of the wire/footprint geometry changed; only the net names on the CN-side labels):

  - CN3.1: `CMD_STEER_DIR__3V3` → `EXP_P3`
  - CN4.2: `SDC_IN_LOW_SIDE` → `SDA__I2C`
  - CN4.3: `CMD_STEER__PWM_3V3` → `SCL__I2C`
  - CN8.1: `SDA__I2C` → `SDC_IN_LOW_SIDE`
  - CN8.3: `EXP_P3` → `CMD_STEER_DIR__3V3`
  - CN9.1: `SCL__I2C` → `CMD_STEER__PWM_3V3`

After: CN3 = pure EXP cluster (P1/P2/P3); CN4 = REVERSE_WIRE + SDA + SCL (all U25-facing); displaced ESP32 signals (CMD_STEER_DIR, SDC_IN_LOW_SIDE, CMD_STEER_PWM) land on left-side CNs (CN8/CN9) — their ESP32 GPIOs span both sides of the module, so route length is similar; the AS5600 I²C cable now exits through CN4 closest to U25.

Pre-existing naming inconsistency surfaced during this work: `CMD_STEER__PWM_3V3` uses double-underscore between `STEER` and `PWM` (parses as signal=`CMD_STEER`, level=`PWM_3V3`) while the matching `CMD_STEER_DIR__3V3` uses single underscore between signal-internal words and double before voltage. Should arguably be `CMD_STEER_PWM__3V3`. Not fixed in this pass to avoid net-rename churn before fab; tracked as a future cleanup.

---

## 2026-05-09 — EasyEDA footprint name "9N" includes exposed pad (false alarm on U14)

While auditing 3D-model coverage on kart-medulla, flagged U14 (MAX4660EUA+T) as having a "wrong" footprint: schematic and chip suggest 10 pins (μMAX-10), but EasyEDA-cached footprint `kart-medulla:SOP65P490X110-9N` has 9 pads. Initially diagnosed as a real footprint bug.

**It wasn't.** The footprint is 8 SMD leads + 1 exposed thermal pad (EPAD) underneath. EasyEDA's naming convention treats the EP as a numbered pad — hence "9N" = 8 leads + 1 EP, **not** 9 leads. The schematic agrees: pins 1–8 are real leads (with pin 5 marked NC), pin 9 is `EP` tied to GND. The 3D model rendering "only 8 pins" is correct because that's exactly what the chip looks like; the 9th pad is invisible from above.

**Lesson:** before claiming an EasyEDA footprint name like `<package>-<N>N` is wrong, count the SMD perimeter pads vs the body-center pad. Bottom EPAD doesn't appear in the chip's pin count but does appear in the footprint's pad count — almost universally for thermal-pad packages (DPAK, QFN, μMAX-EP, SOIC-EP). Don't assume `Nn` in the footprint name = chip pin count.

**Time cost:** ~10 minutes of misdirected investigation + a script run trying to re-attach a model that was already attached. Cheap, but worth not repeating on the next thermal-pad part.

---

## 2026-05-09 — Bulk-injecting 3D models into EasyEDA-imported footprints (kart-medulla)

**Trigger:** kart-medulla PCB had 58 of 59 footprints with no 3D model attached because the EasyEDA import doesn't ship `(model ...)` clauses for cached footprints. 3D viewer was nearly empty.

**Approach that worked:** scripted regex injection of `(model "${KICAD10_3DMODEL_DIR}/<lib>.3dshapes/<name>.step" (offset/scale/rotate ...))` blocks into each `(footprint ...)` block in `kart-medulla.kicad_pcb`, keyed on footprint name. **44 of 58 succeeded** on first pass (R0603, C0603, SOIC-8/14/16W, MSOP-8, SOT-23, TO-220-3, TO-252, PinSocket 1×22 + 2×22). Parens balanced afterward — no syntax damage.

**KiCad 10 env-var name:** `${KICAD10_3DMODEL_DIR}` (verified by grepping a stock `Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod`). Earlier KiCad versions used `KICAD9_3DMODEL_DIR`, `KICAD8_3DMODEL_DIR`, etc. — the version number tracks the major release. Default base path on macOS: `/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels/`.

**Phoenix PTSA series not bundled.** KiCad ships `Connector_Phoenix_MC*`, `MSTB`, `GMSTB`, `SPT` 3dshapes — but **not** PTSA. For the 10× CN1–CN10 (`1990012`, PTSA 0,5/3-2,5-Z), downloaded STEP from SnapMagic (snapeda.com/parts/1990012/) and dropped at `projects/kart-medulla/3dmodels/1990012_PTSA_3p_2.5mm.step`. Referenced via `${KIPRJMOD}/3dmodels/...` so the project stays portable.

**Surprising finding — KiCad rotation sign convention differs between dialog and file.** The Footprint Properties → 3D Models dialog displays rotation values with **opposite sign** from what's stored in the .kicad_pcb. Verified empirically:
- File `(rotate (xyz -90 0 0))` → dialog shows `(90, 0, 0)`.
- Setting file to `(xyz 90 0 0)` (matching what dialog showed) flipped all 10 connectors upside down. Reverting to `(xyz -90 0 0)` restored correct upright orientation.
- Same pattern on Z: dialog `(0, 0, -90)` ↔ file `(xyz 0 0 90)`.
- Offsets and scale do **not** sign-flip — those are direct.

**Implication:** when a user reports values from the GUI, negate the rotation entries before writing to the file (or vice versa when reading the file to discuss with the user). Document both forms in any reference table.

**Failed iterations (good to remember so we don't redo them):**
- Asked user to nudge in Footprint Editor — wrong tool. Footprint Editor edits the *library* footprint, not the per-instance model offset. Per-instance offset only lives in pcbnew → click footprint → press `E` (Properties) → 3D Models tab. From the 3D Viewer (Alt+3) you can't edit anything; double-click does nothing.
- Tried inferring connector offset by guessing world-space displacement direction (`-1.41, 1.41, 0` then flipped X to `+1.41, 1.13, 0`). Both wrong, because the model offset is in the model's own (post-rotation, pre-yaw) frame and we don't know SnapEDA's authoring origin a priori. **Lesson: always ask the user to nudge ONE instance in the GUI and report exact numbers — then batch the rest. Don't guess offsets through coordinate-frame algebra; SnapEDA STEPs have arbitrary internal origins.**

**Final empirically-tuned values (verified visually in 3D viewer 2026-05-09):**

| Component | Footprint | 3D model | File rotation | File offset (mm) |
|---|---|---|---|---|
| CN1–CN10 (Phoenix PTSA 3p, 1990012) | `kart-medulla:CONN-TH_3P-P2.50-S5.00_1990012` | `${KIPRJMOD}/3dmodels/1990012_PTSA_3p_2.5mm.step` | `(xyz -90 0 0)` | `(-0.75, -1.2, 0)` |
| Q3 (IRLZ44N TO-220) | `kart-medulla:TO-220-3_L10.0-W4.5-P2.54-T` | `Package_TO_SOT_THT/TO-220-3_Vertical.step` | `(xyz 0 0 90)` | `(0, 2.54, 0)` |
| U24 (1×22 socket) | `kart-medulla:HDR-TH_ESQ-122-23-G-S` | `Connector_PinSocket_2.54mm/PinSocket_1x22_P2.54mm_Vertical.step` | `(xyz 0 0 90)` | `(26.6, 0, 0)` |
| U23 (2×22 socket) | `kart-medulla:HDR-TH_ESQ-122-59-G-D` | `Connector_PinSocket_2.54mm/PinSocket_2x22_P2.54mm_Vertical.step` | `(xyz 0 0 90)` | `(26.6, -1.5, 0)` |

Also re-recorded in `tasks.md` "3D-model placement values" section so peers' PCB edits don't silently regress them.

**Footprint name = body dimensions, not pin pitch alone.** EasyEDA's footprint names encode body L×W (e.g. `SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL`), which doesn't always match KiCad's stock body (`SOIC-8_3.9x4.9mm_P1.27mm`). The 3D model still looks right because pin pitch matches; the body's a few tenths of a mm off but visually fine. Don't waste time hunting for an exact-body-size match unless the visual error is obvious.

**Phoenix Contact 1990012 logged to vault inventory:** `~/vault/inventory/phoenix-contact-1990012-ptsa-0_5-3-2_5-z-3pin-25mm-push-in-terminal-block.md`. Status `Noted`, `units_to_buy: 10`, source Mouser.

---

## 2026-05-09 — U19 (L7805) PCB-vs-AI-Inventory cross-check

PCB U19 uses footprint `kart-medulla:TO-252-2_L6.6-W6.1-P4.57-LS9.9-BR-CW`, value `L7805CDT_C20611927` (LCSC C20611927) — DPAK / TO-252-2, ST.

Notion AI Inventory (data_source `34a78747-3143-81da-85fb-000b14e5f8d8`) holds three rows for `L7805CDT-TR` (ST, Mouser 511-L7805CDT-TR), qty 10 + 5 + 15 = 30 in the Milwaukee components box. PCB part **matches** stock. Also one row of `LM7805CT/NOPB` (TI, qty 3) — TO-220 through-hole, **not** a footprint substitute.

Two cleanups worth doing in Notion (not yet done):
- All four 7805 rows have an empty `Package` field — should be `TO-252-2` for the STs and `TO-220` for the TI.
- The three ST rows look like schema-merge duplicates (same MPN, same Mouser PN, same location); consider consolidating into one row with qty 30.

---

## 2026-05-09 — AISLER sponsor logo placeholder size decision

Decided on the **smallest AISLER-spec size: 30 × 7.5 mm** (4:1 ratio, AISLER's stated minimum). Rationale: the only constraint that mattered was the 22.86 mm gap between the 0.9″ ESP32 headers, but the long axis goes parallel to the headers, not across the gap, so it wasn't actually binding. The biggest size we could have used (60 × 15 mm) and any intermediate (40×10, 50×12.5) would have fit too — went small because it looks better on this board.

Source for the 30 × 7.5 mm number: Rubén in #Driverless on 2026-05-06 ("la idea es que pongáis el recuadro de 30 × 7,5 mm donde os de la gana en la pcb") + the linked AISLER community thread (https://community.aisler.net/t/adding-our-logo-to-your-pcb/5382).

Drawing rules (from the AISLER doc, quoted verbatim where it matters): rectangle must be drawn as **4 individual lines** (the rectangle tool fails AISLER's auto-detect because it groups), line width **0.08382 mm (3.3 mil) exactly**, on silkscreen. AISLER doc says "Place as many placeholders as you want — each will be replaced with the logo," so placing one on F.Silkscreen *and* one on B.Silkscreen is allowed (default plan: do both).

---

## 2026-05-09 — Silkscreen text font: DejaVu Sans Mono (chosen by peer)

Peer working on the PCB layout used **DejaVu Sans Mono** for the CN1–CN10 silkscreen pin-label blocks. Tab-aligned columns rendered acceptably (not perfect — peer's words). Note for future cross-OS work: DejaVu Sans Mono ships by default on Ubuntu but **is not installed on macOS** (verified `fc-list` on Rubén's Mac 2026-05-09 — only Menlo, no DejaVu). There is no monospace font shared by default between macOS and Ubuntu. Options to keep the project cross-platform:

- Install DejaVu on Mac: `brew install --cask font-dejavu` (matches what the peer has).
- Use KiCad's **Embed Fonts** option (`File → Board Setup → Embedded Files` in KiCad 9+) — bakes the .ttf into the .kicad_pcb so the font travels with the project, regardless of who opens it.

Recommend turning on Embed Fonts before fab so the gerber export is deterministic across both machines.

---

## 2026-05-09 — AISLER Beautiful Boards DRC config + Power net class

Configured Board Setup constraints + a custom `kart-medulla.kicad_dru` file targeting **AISLER's "Beautiful Boards" 2-layer service** (the team's PCB-fab sponsor) with ~30 % margin over published minimums. Full rationale per number in `projects/kart-medulla/docs/drc-aisler.md`.

Headline numbers: track 0.20 mm, clearance 0.20 mm, drill 0.30 mm, via 0.55 mm Ø with 0.30 mm hole, copper-to-edge 0.30 mm, hole-to-hole 0.30 mm, silk 1.0 mm × 0.15 mm, silk-clearance 0.15 mm, microvias / blind-buried disabled.

**Net classes:** `Default` (track 0.25, clearance 0.20, via 0.6/0.3) and `Power` (track 0.50, clearance 0.25, via 0.8/0.4). Pattern-based assignment of `+12V`, `+5V_USB`, `+5V_REG`, `+3V3` to the Power class via `net_settings.netclass_patterns` in `.kicad_pro`. **`GND` deliberately stays in Default** — it's a poured zone, not a routed track, so a 0.5 mm minimum-track-width rule would be noise. **`3V3` is borderline** (low-current rail, ~200 mA peak); kept in Power for visual consistency, demote to Default if routing gets tight.

**Custom DRC rules** (`kart-medulla.kicad_dru`): `edge-clearance` (0.30 mm belt-and-suspenders), `annular-min` (0.125 mm extended to pads, not just vias), `hv-pressure-clearance` (0.60 mm on the three 24 V Festo pressure-sensor input nets — IEC 60664-1 Pollution Degree 2 / Material Group IIIa says 0.50 mm at 50 V working voltage; we're at 24 V outdoors so 0.6 mm gives derating + dust margin), `power-track-width` (0.50 mm Power-class backstop), `silk-pad-clearance`.

**Implementation gotcha (worth remembering):** edited `.kicad_pro` JSON behind a running KiCad — KiCad re-saved on close and silently clobbered the edits, reverting `min_clearance`, `min_track_width`, and the entire Power class. Lesson: **never edit `.kicad_pro` from outside while KiCad has the project open.** Either close KiCad first, or do all changes through Board Setup → Net Classes (which writes the schema KiCad expects, not whatever JSON shape an external tool guessed at).

**Net pattern syntax:** KiCad 10 patterns match against the **bare net name with leading `+`** (e.g. `+5V_USB`, `+3V3`, `+12V`) — **no leading slash**. The "Nets matching" preview pane in the Netclass Assignments dialog is the fastest way to confirm the pattern actually hits anything; an empty match means the pattern is wrong. Initially tried `/3V3`, `/+5V`, etc. — none matched (the medulla's actual nets are `+3V3`, `+5V_USB`, `+5V_REG`, `+12V`, with no bare `+5V`).

---

## 2026-05-09 — 3D-model regression after peer merge → surgical recovery → library-level fix

**Sequence of events** (all on 2026-05-09):

1. Earlier session bulk-injected 3D model `(model …)` blocks into 58 footprint instances in `kart-medulla.kicad_pcb` (recorded at "Bulk-injecting 3D models into EasyEDA-imported footprints" entry below). Bindings lived per-instance only — not in the `kart-medulla.pretty/` library.
2. Peer pushed two PCB-routing commits (`6b4914e`, `5f4ee9c`). When integrating, ran `git checkout origin/main -- kart-medulla.kicad_pcb` to take peer's layout. **This silently dropped 54 of 55 instance-level 3D bindings** — peer's local PCB had been re-imported / replaced at some point and didn't carry the per-instance `(model …)` blocks. Only `MAX4660EUA_T.step` survived because that one was already library-bound in `SOP65P490X110-9N.kicad_mod`.
3. Diagnosed via `grep '(model' kart-medulla.kicad_pcb | sort -u`: 1 ref where there had been 13. 3D viewer empty for everything except the MAX4660.
4. **Recovery:** found `kart-medulla.kicad_pcb.bak.20260509f` (KiCad auto-save from earlier in the session, pre-regression) with 55 intact bindings. Wrote a Python S-expression-walker that built `refdes → (model …) block` map from the .bak, then walked the current `.kicad_pcb` and injected the matching block into each footprint that lacked one. Layout/routing/silk untouched. 54 footprints restored, 4 unmatched (`PAD1–PAD4` corner mounting holes — correctly skipped). Committed as `9596513`.
5. Peer pushed *another* PCB commit (`5f4ee9c "logo and connections"`). Same regression: 3D bindings down to 1 again. Re-ran the surgical merge — same script, same `.bak` source — recovered all 55 again. Pushed atop peer's tip.
6. **Long-term fix:** edited 12 footprints in `kart-medulla.pretty/` to carry library-level `(model …)` blocks matching the format of the existing `SOP65P490X110-9N.kicad_mod`. Path / offset / scale / rotate values lifted verbatim from the `.kicad_pcb` (PTSA's `xyz -90 0 0` rotation + `-0.75 -1.2 0` offset preserved; ESQ-122 headers' `xyz -0 -0 90`; TO-220's `xyz 0 0 90`). Committed as `a0f7a5c`.

**Lessons / rules established:**

- **Per-instance 3D bindings are fragile.** Any operation that swaps the `.kicad_pcb` (re-import from EasyEDA, library footprint replace, `git checkout` from a peer branch lacking them) silently strips them. **Always bind 3D models at the `*.kicad_mod` library level** for parts intended to live on this board.
- **Instance-level still wins over library-level** in KiCad. Adding library bindings is non-destructive — if the live PCB already has a per-instance value, that wins. Used this property to land the library-level fix without coordinating around peer's in-flight layout work.
- **KiCad auto-saves saved us.** `kart-medulla.kicad_pcb.bak.20260509b/c/d/e/f` carried successive snapshots of the pre-regression state. Without them the surgery would have required re-deriving every per-instance offset/rotation by eye. **Don't gitignore the `.bak.*` files until after they've served their recovery purpose.** (Today the team's `.gitignore` was extended to `*.bak.*` — that's fine for the *future*, not for today's recovery, since the .bak files were already on disk.)
- **The Python S-expression walker** (parens-balanced footprint extraction + refdes-keyed model-block lookup) is reusable for any future "files diverged, want to merge specific subtrees" scenario in KiCad. Keep the snippet handy.

---

## 2026-05-09 — kart-medulla DRC cleanup session

- **Auto-silkscreen plugin installed:** CGrassin/kicad-auto-silkscreen at `~/Documents/KiCad/10.0/scripting/plugins/kicad-auto-silkscreen/`. Ran once to auto-place all refdes on medulla PCB. Side effect: ~50 silk-to-pad clearance warnings (largely cleaned up afterward).
- **Power-class minimum track width: 0.5 → 0.3 → removed.** Originally 0.5 mm in `71bf70d` (AISLER setup, sized for 1.5 A IPC-2152). Actual medulla Power loads (+12V, +5V_USB, +5V_REG, +3V3) are sub-100 mA — logic ICs, op-amps, sensors only. Cytron 12V→motor path does not traverse the medulla (per 2026-05-01 decision). Dropped to 0.3 mm, then removed entirely once QFN/SOT-23 fanout demanded 0.2 mm pitch on power rails. Power class still enforces clearance (0.25 mm) and via size (0.8/0.4 mm). Updated `kicad_dru`, `kicad_pro` (Power netclass `track_width: 0.5 → 0.2`), and `projects/kart-medulla/docs/drc-aisler.md`.
- **Bulk power-track widening broke 36 connections.** Edit Track & Via Properties → "Set to net class / custom rule values" with Power-class filter widened all power tracks at once; endpoints shifted off pads. Unconnected items 3 → 39. Manual repair brought it back to 4; some still broken at session end.
- **Polygon rule area for fine-pitch SMD pad clearance.** First attempt used custom DRC rule with `A.MemberOfFootprint == B.MemberOfFootprint` — invalid in KiCad 10, broke rules compilation entirely. Replaced with rule-area approach: drew polygon (`fine-pitch-smd`) around U14, added rule:
  ```
  (rule "fine-pitch-pad-clearance"
    (constraint clearance (min 0mm))
    (condition "A.insideArea('fine-pitch-smd') && B.insideArea('fine-pitch-smd') && (A.Type == 'Pad' || B.Type == 'Pad')"))
  ```
  Resolves 7 intra-footprint pad-pad / track-pad violations on U14 (SOIC-8, 0.65 mm pitch, native 0.18 mm pad-pad). Reusable pattern for future fine-pitch parts.
- **U14 solder-mask bridges fixed via `solder_mask_margin`.** Six "Rear solder mask aperture bridges items with different nets" errors. Cause: each pad in the U14 footprint had `solder_mask_margin 0.102`, expanding apertures by 0.102 mm/side and shrinking the mask web below AISLER minimum. Initial fix targeted wrong file (`SOP65P400X130-8N.kicad_mod`); U14 actually uses `SOP65P490X110-9N.kicad_mod` (8-µMAX-EP, 9 pads incl. exposed pad), confirmed by inspecting the embedded footprint in `.kicad_pcb` (sibling 8N footprint also exists in library, `parts.md` was ambiguous). Set `solder_mask_margin 0` on correct file. **Tools → Update Footprints from Library does NOT override per-pad mask margin** (treated as user customization) — required direct sed on the embedded copy in `.kicad_pcb` to push through.
- **Min thermal spoke count: 2 → 1** (Board Setup → Constraints, per-zone). Acceptable for hand-soldered prototype; vibration/thermal-cycling longevity not a concern. Per-zone setting — existing zones may not pick up the change automatically, may need editing individually.
- **U14 confirmed: MAX4660EUA+T**, 8-µMAX-EP, footprint `SOP65P490X110-9N` from SnapEDA. Not yet in `~/vault/inventory/` — worth adding (mirror `phoenix-contact-1990012-...` format).
- **Final DRC state:** 0 errors. 5 silk text warnings (U1 refdes 0.087 mm thickness / 0.69 mm height — below AISLER 0.10 mm hard floor; 3 TrueType texts with thin stroke). 4 unconnected items pending fix.

## Reference

- KiCad EasyEDA importer docs: https://dev-docs.kicad.org/en/import-formats/easyeda/index.html
- ConvertEDA (worked): https://converteda.com
- KiCad IPC API (for future automation): https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html
- `kicad-python` (official Python bindings for IPC API): https://pypi.org/project/kicad-python/

## 2026-05-12 — WAGO push-in terminal block sourcing (2624 vs 2601)

**Trigger:** Spotted WAGO 2624 series in an Instagram reel (wagouk), wanted a 3.5 mm pitch variant compatible with team standard 18 AWG / 0.75 mm² wire (`~/vault/standards.md:236-239`).

**Finding:** The **2624 series has no 3.5 mm pitch.** Only 5 mm (2624-11xx top entry, 2624-31xx side entry) and 7.5 mm (2624-15xx, 2624-33xx). The 3.5 mm pitch sibling with same push-in-CAGE-CLAMP + lever style is the **2601 series** (e.g. 2601-3104 = 4-pole, 3.5 mm pitch, top entry). Conductor range 0.2–1.5 mm² (AWG 26–14). Don't assume pitch options carry across WAGO series numbers — verify on wago.com before quoting.

**Pitch / current cheat-sheet for push-in cage-clamp lever PCB terminals:**

| Pitch | Series | Conductor range | Rated current | Use case |
|---|---|---|---|---|
| 3.5 mm | **2601** | 0.2–1.5 mm² (AWG 26–14) | ~10 A | Signal + low-power (CAN, I²C, 0.75 mm² standard wire) |
| 5 mm | **2624** | 0.2–1.5 mm² (AWG 24–12) | ~17 A | General purpose |
| 7.5 mm | **2624-3xxx** | 0.5–6 mm² (AWG 20–10) | ~41 A | Power (4 mm² / 12 AWG, 30 A loads) |

**Modularity (Arduino-header-like behavior):** at the same pitch, N×1-pole bodies abut to span the same hole pattern as one N-pole body. PCB footprint with 4 holes at 3.5 mm pitch accepts 1× 2601-3104 OR 2× 2601-3102. Body height/depth ≈13×17 mm — leave clearance.

**Datasheet retrieval:** WAGO's own product pages don't expose static PDF URLs (priintcloud signatures are dynamic, return HTTP 400 without a session). **Bürklin mirrors clean PDFs** at `https://www.buerklin.com/Buerklin-Webshop-Site/rest;loc=de_DE/attachments/Buerklin-Webshop%253A%252FFiles_<hash>%252F<PN>-EN.pdf` — grep the product page HTML (`/en/p/wago/pcb-terminal-blocks/<PN>/<bürklin-id>/`) for the file hash. Bürklin product IDs found via search: 2601-3102 → 09H828, 2601-3103 → 09H830, 2601-3104 → 09H832.

**Final sourcing decision — stock 2-pole + 3-pole only.** Per-pin pricing is flat across pole counts (DigiKey 1-off, 2026-05): 2601-3102 $1.21/pin, 2601-3103 $1.12/pin, 2601-3104 $1.13/pin. No per-pin saving from buying higher pole counts. With {2-pole, 3-pole} you can compose every integer pole count ≥ 2 with zero gaps (2 and 3 are coprime → Frobenius = 1). 4-pole adds nothing the 2+3 set can't.

**Inventory (Notion, all "To order", 10 units each):**
- 2601-3102 (2-pole): https://www.notion.so/WAGO-2601-3102-2-pole-PCB-terminal-block-3-5-mm-pitch-push-in-lever-35e7874731438115b893eacecfce7026
- 2601-3103 (3-pole): https://www.notion.so/WAGO-2601-3103-3-pole-PCB-terminal-block-3-5-mm-pitch-push-in-lever-35e787473143816c80bdf020e0de2d64
- 2601-3104 (4-pole): created then archived after the per-pin pricing check.

Datasheets at `~/dv/datasheets/2601-310{2,3}_wago_datasheet.pdf` (4-pole removed). Standards entry added at `~/vault/standards.md` under the connectors section.

## 2026-07-10 — kart-medulla ESP32 module identified on hardware: N16R8, not N8R2

Read the fitted dev board over its COM (USB-UART) port with `esptool 5.2.0`. Measured, not recalled:

| Property | Value |
|---|---|
| Chip | ESP32-S3, QFN56, revision v0.2 |
| Base MAC | `14:c1:9f:2a:a6:18` |
| Flash | 16 MB, external, quad line (`FLASH_TYPE` eFuse = 4 data lines; `FLASH_CAP` = none, i.e. no in-package flash) |
| PSRAM | 8 MB, AP Memory, 3.3 V (`PSRAM_CAP` = 8M, `PSRAM_VENDOR` = AP_3v3) |
| USB-UART bridge | WCH CH343/CH9102, VID `0x1A86` PID `0x55D3`, product string "USB Single Serial" |

**Module is an N16R8, not the N8R2 the docs claimed.** The supplier shipped the wrong
variant. 8 MB in-package PSRAM on the ESP32-S3 only exists on the R8 die, which uses an
**octal** interface — Espressif ships no 8 MB quad variant. So GPIO 33-37 are wired to the
PSRAM die and are unusable on this board.

**No signal has to move.** The 2026-05-03 decision to push `CMD_REVERSE` onto PCF8574 P0 and
the 2026-05-08 moves (BUZZER 36→3, MOTOR_HALL_1 37→16, CMD_STEER_DIR 35→0) already made the
pinout octal-safe. Verified: in the live S3 pin table GPIO 35/36/37 are `HOLD` and 33/34 are
unassigned. The variant-agnostic layout paid for itself. `pinout-esp32-s3.md` updated
(title, octal-PSRAM note, pin-10 row, "module variant in use").

**The board is a DevKitC-1-compatible clone, not an Espressif board.** Espressif's own
ESP32-S3-DevKitC-1 bridges UART through a CP2102N (VID `0x10C4`, Silicon Labs) and silkscreens
its ports `UART`/`USB`; this one uses a WCH bridge and silkscreens `COM`/`USB`. Functionally
equivalent for our purposes. It does have two USB-C ports, so checklist item 2 in
`pinout-esp32-s3.md` ("verify native USB reaches GPIO 19/20") can be settled without a
multimeter: plug a cable into the free `USB` port and see whether it enumerates as VID `0x303A`
(the S3's built-in USB-Serial-JTAG, which needs no firmware). **Not yet done.**

Open contradiction inside `pinout-esp32-s3.md`, noticed but not resolved: the status legend says
"USB_D+/- pins not wired on this PCB", while the dev-board checklist (item 2) describes GPIO
19/20 carrying USB D-/D+ to the Orin. Someone should reconcile these against the schematic.

## 2026-07-10 — kart-medulla bench bring-up: SDC MOSFET (Q3) verified working

Board on the bench, CN8 unplugged, nothing connected to the kart. Driven from the MicroPython
REPL over the `COM` (USB-UART) port.

**Q3 (IRLZ44N, SDC low-side switch) works.** Toggled `SDC_NOT_EMERGENCY__3V3` (GPIO 18) as a
2.5 Hz square wave and measured with a multimeter. Gate follows the GPIO; drain
(`SDC_IN_LOW_SIDE`, CN8 pin 1) alternates between open and ~0 Ω to GND in step with it.
Neither failure mode is present: not stuck open (dead FET) and — more importantly — not stuck
closed (drain-source short, which would assert "no emergency" permanently regardless of firmware).

**Fail-safe default confirmed.** With GPIO 18 left as a high-impedance input, the gate reads 0:
R23's 100 kΩ pulldown holds Q3 off, so the kart powers up in the *emergency* state before
firmware drives anything. This is the behaviour the SDC design depends on.

**The chip is running MicroPython v1.19.1 (2022-06-18, IDF v4.4.1), not our ESP-IDF firmware.**
Found by reading the partition table out of flash (`nvs` / `phy_init` / `factory` 0x10000+0x1f0000
/ `vfs` FAT at 0x200000 — MicroPython's standard ESP32 layout) and grepping the app image. Nobody
recorded this anywhere. Nothing was flashed or erased during this session. Note the ESP-IDF
firmware in `~/repos/kart-medulla` cannot currently build for the S3 at all — see that repo's
`.agents/error-log.md` (2026-07-10) for the GPIO 18 / steering-PWM collision that a naive port
would introduce.

**Serial reliability: use 115200 for anything long.** `esptool read-flash` of the 16 MB image
failed at 921600 ("Serial data stream stopped") and again at 460800 ("Invalid head of packet") at
only 1.5%. 115200 was flawless. This matches the warning already in the firmware repo's AGENTS.md,
which was written about a CP2102 but holds for the CH343 too.

**U25 (PCF8574) is populated and alive on I²C.** Scanned SDA=GPIO 8 / SCL=GPIO 9. One device at
`0x20`, stable across repeated scans, returning `0xFE` (P0 low, P1–P7 high). P0 is `CMD_REVERSE`.
No AS5600 at 0x36, expected since the steering encoder is off-board and unattached. Read-only
probing was used; nothing was written to the expander, so `CMD_REVERSE` was never asserted.

**The part not yet soldered is U5, the 5 V→3V3 level shifter for the motor hall sensors** (waiting
on Mouser). So `MOTOR_HALL_1/2/3` cannot be read until U5 is fitted. (Earlier in this session the
missing part was mis-recorded as U25; corrected by Rubén.)

## 2026-07-10 — kart-medulla CN connectors face inward; pin order runs against CN order

Rubén, handling the assembled board: the wire entry of all ten CNs points **inward** toward the
middle of the PCB, and the pins within each connector count *backwards* relative to the CN
sequence. Verified against `kart-medulla.kicad_pcb`: CN1–CN5 (right) sit at rotation −90° with
pin 1 at top while the CNs ascend bottom→top; CN6–CN10 (left) sit at +90° with pin 1 at bottom
while the CNs ascend top→bottom. Both sides are counter-directional.

Proposed fix: rotate every CN 180°, which makes wires exit outward *and* puts the pin numbering
in sequence with the CN numbering on both sides. Caveat: the footprint
`CONN-TH_3P-P2.50-S5.00_1990012` has staggered pads (pins 1+3 one row, pin 2 a row 5.00 mm
across), so the flip relocates pin 2's row and forces a re-route under every connector. Task
written up in `projects/kart-medulla/tasks.md`; `docs/pinout-cn-connectors.md` corrected — it had
claimed "pin 1/2/3 from top to bottom" for all ten, which is only true of CN1–CN5.

## 2026-07-16 — tasks.md consolidated to the repo root; `.agents/tasks.md` retired

**Trigger:** Rubén's call — "tasks.md are tasks no matter if I do them or you do them. They're the
tasks of the project, and mixing two tasks.md files can only create confusion and duplicate or
outdated files."

**Background:** the split came from a rule in global `~/.claude/CLAUDE.md` that reserved a repo's
root `tasks.md` for Rubén's personal to-do list and put the agent board in `.agents/tasks.md`. The
2026-05-12 entry above already recorded the tension (agent-first long-form rationale being bad for
human peers skimming the file) and closed with "no decision yet". This is that decision.

**Done:**
- `git mv .agents/tasks.md tasks.md` (history preserved; the 4 then-uncommitted lines were
  committed first so the move is revertible).
- `AGENTS.md` knowledge-files list now points at root `tasks.md` and states there is no
  `.agents/tasks.md`.
- `projects/kart-medulla/tasks.md` header now points cross-board work at `dv-hardware/tasks.md`.
- Global `~/.claude/CLAUDE.md`: the personal-vs-agent split is replaced with "one `tasks.md` per
  project, at the repo root"; `tasks.md` removed from the `.agents/` read-mode list.

**Not done, deliberately:** earlier `history.md` and `.agents/error-log.md` entries still say
`.agents/tasks.md`. Those are dated append-only records and were accurate when written — rewriting
them would falsify the log. This entry is the forwarding pointer.

**Scope that survives:** per-board lists stay at `projects/<board>/tasks.md`. That is scoping by
board, not a competing board — root `tasks.md` is cross-board only.

**Doc bug spotted while doing this:** `AGENTS.md` tells contributors "Newest entries first" for this
file, but the file is and always has been oldest-first (2026-05-03 at the top, newest appended at the
bottom), which is what global CLAUDE.md specifies. The instruction is wrong, not the file. Left as-is
pending Rubén's call on which way to fix it.

## 2026-07-16 — kart-medulla board list moved to `tasks/kart-medulla.md`; one tasks.md per repo, no exceptions

**Trigger:** Rubén tightened the rule the same day it was written: "just 1 tasks.md file at the root.
no exceptions. only possible tasks/ folder for more complex tasks, but still those are referenced
from tasks.md at the root."

The earlier entry today consolidated `.agents/tasks.md` into the root but kept
`projects/kart-medulla/tasks.md` as "per-board scoping". That was the same two-boards shape the
consolidation existed to kill — 199 lines in the board folder against 149 at the root — and it is now
closed. Contradiction 3 in `tasks.md` is resolved by this.

**Done:**
- `git mv projects/kart-medulla/tasks.md tasks/kart-medulla.md` (history preserved).
- Root `tasks.md` gained a "Task files" index. The rule is that the root board is the only index: a
  file under `tasks/` that isn't linked from it doesn't exist as far as anyone is concerned.
- `AGENTS.md`: layout now shows `tasks.md`, `tasks/<name>.md` and `projects/<board>/requirements.md`;
  the knowledge-files entry states one `tasks.md` per repo at the root, no `.agents/tasks.md` and no
  `projects/<board>/tasks.md`.
- References repointed in `projects/kart-medulla/requirements.md` and the root board.

**Left alone deliberately:** `.agents/tasks.md` and `projects/kart-medulla/tasks.md` mentions inside
earlier `history.md` and `.agents/error-log.md` entries. Dated append-only records, accurate when
written; rewriting them would falsify the log. This entry is the forwarding pointer.

## 2026-07-16 — PCB checklist extracted to `docs/pcb-checklist.md`; revisions get names

**Trigger:** Rubén, reading the board list: "i'm seeing lots of tasks in tasks.md which are actually
just the pcb checklist. we should create a finishable task like 'pass the pcb checklist (linking it)
for the new revision of the pcb' and make sure we call each pcb with a different name."

**The problem:** the checklist existed in **four** places, all diverging — "PCB checklist — pre-fab
review and validation" and "Tomorrow (2026-05-10): pre-fab finishing" and "PCB finishing pass
(pre-fab)" as task sections, plus a copy in the team Google Drive (`el/pcb-checklist.md`, last
touched 2024-12-04, heading still "formula 23-24"). Checklist items make bad tasks: they are never
"done", they recur every revision, and copying them is what produced the four copies.

**Done:**
- `docs/pcb-checklist.md` — one checklist for every board: Design, Pre-fab validation, Revision
  naming. Merged from all in-repo copies plus the Drive one. Includes the track-width rule that came
  out of the compressor-power-path discussion the same day: a net's copper is its job description.
- `tasks/kart-medulla.md` now carries **one** finishable task — "Pass the PCB checklist for
  `medulla-v2`" — linking the doc instead of restating it. Done = every box ticked, board tagged,
  fab package under `fab/kart-medulla/v2/`.
- The two pre-fab sections were moved off the root board (they were kart-medulla-specific, so they
  never belonged on a cross-board list) into the board's file, wrapped in a `<details>` and marked
  superseded rather than pruned — the "Tomorrow (2026-05-10)" section is two months stale and Rubén
  should decide what survives.
- Revision naming written down: `<board>-v<N>`, on the silkscreen, in the title block, on the git
  tag, and on the `fab/<board>/<rev>/` folder. Numbers are never reused.

**Assumption flagged, not resolved** (`tasks.md` contradictions 7–8): the v1/v2 mapping treats the
assembled EasyEDA-origin board as `medulla-v1`, following the "V2 Hardware Improvements" heading.
Nothing on disk confirms it — `fab/` is empty and the only tag is `medulla-v0.1-converted`.

## 2026-07-16 — root board reduced to cross-board work; kart-medulla items consolidated

Checking that the checklist task linked correctly exposed that the root `tasks.md` was still almost
entirely kart-medulla work — silkscreen legend, AISLER logo, 3D-model values, connector audit, the
"In Progress: PCB layout" and "Done: LM358" entries, and the whole "Notes for the next person"
section. The root/board split announced this morning was therefore fiction: the root board *was* the
old kart-medulla cleanup board under a new name, and the same board's work lived in two files —
exactly the shape the consolidation existed to remove.

**Done:** everything kart-medulla moved verbatim (statuses preserved) into `tasks/kart-medulla.md`
under a "Moved from the root board" heading. Root keeps only genuinely cross-board work — the WAGO
2601 terminal-block standard — plus the `tasks/` index and the open-contradictions list. The
redundant "Design the buzzer circuit" pointer stub was dropped; the real task with the inventory
parts and the FS-Rules SPL constraint is in the board file.

**Lesson:** renaming a file does not change what's in it. The morning's move made the root board
*named* cross-board while its contents stayed board-specific, and nothing caught that until a link
check forced a read of the actual sections.

## 2026-07-18 — Compressor gate drive: why 3.3 V is not enough, and what the HUABAN module gives us

The EBS compressor was bench-run for the first time today (firmware detail in the `kart-medulla`
repo, `history.md` 2026-07-18). It works, but it exposed a hardware problem that belongs to this
repo, and it changes what `medulla-v2` has to carry. Task written up in
[`tasks/kart-medulla.md`](tasks/kart-medulla.md).

### The concern: a 3.3 V gate cannot drive a power MOSFET properly

The compressor is switched by an **IRLZ44N** with its gate wired straight to a 3.3 V ESP32 pin.
Measured: **6 A running at 60% duty**, and the MOSFET reached **~100 C even after the duty was cut to
20%** — hot enough on the first run at 60% to bake the adhesive around the part (the die survived).

The cause is arithmetic, not bad luck. The IRLZ44N datasheet specifies Rds(on) at Vgs = 10 V
(0.022 Ohm), 5 V (0.025) and 4 V (0.035), **and stops there**. 3.3 V is below the last specified
point, with Vgs(th) max = 2.0 V, so the device never fully enhances — roughly 0.05-0.07 Ohm cold and
~1.6x that hot. Against Rth(j-a) = 62 C/W in a bare TO-220 that is over 100 C of rise. Conduction
loss dominates switching loss by roughly 50x at 500 Hz, so **PWM frequency cannot fix it** and
neither can lowering the duty much further (the 60% -> 20% step gave far less than expected, because
motor current does not fall with duty when the pump is working against tank pressure).

Two findings worth carrying into any future board:

1. **"Logic level" on a datasheet front page means it works at 5 V, not 3.3 V.** A survey of ~150
   datasheets across Infineon, Vishay, Nexperia, Toshiba, ST, onsemi, Diodes and AOS found the
   industry floor for a *specified* Rds(on) is **Vgs = 4.5 V**. Vgs(th) max on power dice runs
   2.0-2.5 V, so a worst-case part is at threshold with a 2.5 V gate and no vendor guarantees
   anything below. Only two parts qualified at all and both had a catch (IRF3708, TO-220, specified
   at 2.8 V but obsolete; CSD17307Q5A, in production but SON surface-mount). **Assume 3.3 V direct
   gate drive is never acceptable for a power MOSFET, and budget a driver.**
2. **Beware the plot-label false positive.** Nearly every one of those datasheets contains the
   strings "VGS = 2.5 V" and "VGS = 3 V" — as *curve labels on the Rds(on)-vs-Vgs graph*, never as
   table rows. A parametric search hit claiming a 2.5 V spec is usually reading a plot annotation.
3. **The pin does not even deliver a clean 3.3 V.** The ESP32-S3 datasheet specifies IOH = 28 mA
   only at VOH >= 0.8 x VDD = **2.64 V**, so during the Miller plateau — exactly when the die is
   dissipating — the pin sags toward 2.64 V.

### What the HUABAN module gives us

In inventory: **HUABAN 4 x 25A MOSFET HA210N06 3D Printer Heated Bed Power Extension Module**,
Amazon ASIN `B089YD5XP6`, rated **25 A**, board **60 x 50 mm**, M3 mounting holes, currently listed
as unavailable. It carries an HA210N06 in TO-3P with a clip-on finned heatsink (~3 x 2 x 1 cm),
a 2-pin JST "Control In", and screw terminals marked "HOT BED" and "+ DC IN -". Datasheet for the
transistor is filed at `kart-medulla/datasheets/HA210N06_datasheet.pdf`.

It is useful to this repo in two ways:

- **As a parts donor.** The MOSFET plus heatsink can be moved onto the medulla board. But the
  HA210N06 is **not** a logic-level part — Vgs(th) is 2/3/4 V min/typ/max and Rds(on) is specified at
  exactly one point, Vgs = 10 V. Harvested on its own and wired to a 3.3 V GPIO it would be *worse*
  than the IRLZ44N fitted today, which at least specifies down to 4.0 V. Its gate is also large
  (Qg = 135 nC, Ciss = 5800 pF, about 3x the IRLZ44N), so even ignoring voltage an ESP32 pin at
  ~20 mA needs ~7 us to move the charge. **If the transistor is harvested, the driver must be
  designed in alongside it.**
- **As a reference design.** The carrier has a `U2` stage with a small resistor network that appears
  to level-shift the control input up to the DC-IN rail. If so, that is exactly the circuit v2 needs,
  already proven at 25 A, and worth copying rather than inventing.

### Open question, to test next session

**Does the module's control input actually accept 3.3 V?** Believed yes, but by *inference only*:
3.3 V is below the HA210N06's worst-case 4 V threshold, so a pass-through carrier could not work with
the 3.3 V printer boards these modules are sold for — therefore it almost certainly boosts the gate.
The Amazon listing gives no control-voltage specification, and `U2` has not been identified.

**The measurement that settles it:** 12 V on DC IN, 3.3 V on Control In, then read **gate-to-source**
at the MOSFET pads. Three outcomes, not two:
- **~10-12 V** — a level-shift stage is present and reaches the rail. The module is usable as-is and
  its `U2` circuit is worth copying onto v2.
- **~5 V** — a stage exists but only reaches a 5 V rail. Still inadequate: that is 1 V of overdrive
  against a 4 V worst-case threshold, with Rds(on) unspecified there.
- **~3.3 V** — pass-through, no stage at all, and no MOSFET choice helps without adding a driver.

(Terminology: "level shifter", not "boost". Nothing steps the voltage up — the small transistor
simply switches the big gate between GND and the 12 V rail that is already present on DC IN. A
single-transistor version of this inverts, so a non-inverting module needs two stages or a driver
IC, which is why `U2` being a SOIC-8 rather than a SOT-23 is a useful clue.)

*(Recorded because it was stated with more confidence than it deserved during the session: the
earlier advice "do not drive it from 5 V" was about the MOSFET **gate**, whereas the module's
**control input** is a different node. Both statements are compatible, but only the first is
verified.)*

## 2026-07-30 — The brake / proportional-valve command leaves the board at 0–5 V; the 0–10 V amplifier output goes nowhere

Triggered by a review of the net names around `CMD_BRAKE` on the `kart-medulla` PCB. The intended
signal chain is: MCP4922 DAC generates 0–5 V → LM358 amplifies ×2 to 0–10 V → out through a push-in
terminal to the Festo proportional pressure regulator. Only the first two thirds of that chain exist
on the board.

**Method.** Parsed `projects/kart-medulla/kart-medulla.kicad_pcb` directly (KiCad was open, so this
was read-only; no MCP writes, no file edits). Note for future parsing: in KiCad 10 board files a pad
carries `(net "NAME")` with **no net number** — a regex expecting `(net <n> "NAME")` silently matches
nothing and looks like "the net does not exist".

### Verified net map (as built)

| Net | Every pad on it |
|---|---|
| `/P1/CMD_ACC_ESP32__0_5V` | U13.14 (MCP4922 VOUTA), U14.8 (MAX4660 NO) |
| `/P1/CMD_ACC__0_5V` | U14.1 (MAX4660 COM), CN10.1 |
| `/P1/PEDAL_ACC__0_5V` | U14.2 (MAX4660 NC), CN6.2, R14.2 |
| `/P1/CMD_BRAKE__0_5V` | U13.10 (MCP4922 VOUTB), U1.3 (LM358 +IN1), **CN10.2** |
| `Net-(U1A--IN1)` | U1.2 (LM358 −IN1), R19.1, R20.2 |
| `/P1/CMD_BRAKE__0_10V` | U1.1 (LM358 OUT1), R19.2 — **and nothing else** |

The amplifier itself is correct: R20 = 1 kΩ from −IN1 to GND, R19 = 1 kΩ from −IN1 to OUT1, so
gain = 1 + R19/R20 = 2, and 0–5 V in gives 0–10 V out. U1 is supplied +12 V on pin 8 and GND on
pin 4. The unused half U1B is tied off as a follower (pin 7 → pin 6, pin 5 → GND).

### Issue 1 — the connector pin is on the wrong side of the amplifier

`CN10.2` sits on `CMD_BRAKE__0_5V`, i.e. **directly on the DAC output**, in parallel with the
amplifier input. `CMD_BRAKE__0_10V` terminates at the op-amp output and its own feedback resistor
and never reaches a connector, so the amplified signal cannot leave the PCB. The board therefore
sends 0–5 V to a device that expects 0–10 V — full DAC scale commands roughly half the pressure
range, and no code change can recover the other half.

This did not show up in ERC or DRC because `CMD_BRAKE__0_10V` has two pads on it. A net with two
connections is electrically legal; nothing checks that one of them is an exit point.

### Issue 2 — the DAC output pin is exposed on an external terminal with no protection

Because `CN10.2` is the DAC node, whatever the harness presents at that terminal lands directly on
MCP4922 VOUTB (and on the LM358 input). There is no series resistor, no clamp, no buffer. The
destination device runs on a 24 V supply, so a wiring fault or a pull-up on the receiving side puts
24 V onto a 5 V-supplied analog output pin. (The MCP4922's exact absolute-maximum rating on VOUT has
not been read — its datasheet is not yet filed in the board's `datasheets/` folder — but no 5 V CMOS
DAC output survives 24 V.) Moving the connector to the amplifier
output (Issue 1) also fixes this, since the op-amp output tolerates a short far better than the DAC
does. This risk is **not** an ESP32 risk — `CMD_BRAKE__0_5V` does not touch the ESP32 sockets U23/U24
at any pad; the ESP32 only reaches the DAC over SPI (see below).

### Issue 3 — the LM358 cannot guarantee 10 V from a 12 V rail (accepted, not fixed)

**Resolved same day: Rubén judged this not a problem for the kart — 9 bar of brake pressure is
enough.** The board keeps the +12 V supply on U1. Kept here because the numbers matter for firmware
and for the next board revision; tracked as the polish task "Give the pressure-command amplifier full
0–10 V swing on the next board revision" in `tasks/kart-medulla.md`. The consequence firmware must
respect is at the end of this section.

Checked against the TI datasheet for the fitted part (LM358DR), **SLOS068AB rev. October 2024,
section 5.7 "Electrical Characteristics: LM358, LM358A"**, saved at
`projects/kart-medulla/datasheets/LM358_TI_datasheet.pdf`. "Voltage output swing from rail,
positive rail" is specified as:

| Condition | Typ | Max |
|---|---|---|
| VS = 30 V, RL ≥ 10 kΩ | 2 V | **3 V** |
| VS = 30 V, RL = 2 kΩ, 0–70 °C | — | 4 V |

The LM358 is not rail-to-rail. On a 12 V rail with a light load the *typical* ceiling is
12 − 2 = 10 V — exactly the value the stage is asked to produce — and the *guaranteed* ceiling is
12 − 3 = 9 V. So a worst-case device clips at 90 % of the commanded range even with a perfect 12 V
rail, and the kart's "12 V" is an unregulated battery rail that sags under load, which makes it
worse.

**Why this was accepted rather than fixed.** The VPPM regulates 0.1–10 bar across the 0–10 V
setpoint, so roughly 1 bar per volt (datasheet: "Pressure regulation range 0.01 MPa…1 MPa /
0.1 bar…10 bar"). A 9 V ceiling costs the top ~1 bar, and 9 bar is more brake pressure than the kart
needs. The two candidate fixes, for whenever the analog front end is next touched: supply the op-amp
from 24 V instead of 12 V (the kart already carries a 24 V rail for the valve — a UENPO
9–36 V → 24 V / 5 A buck-boost, bought 2026-05-30, see `~/dv/kart/pneumatics/history.md`; that gives
24 − 3 = 21 V of guaranteed swing, and the LM358's absolute-maximum supply is 32 V so 24 V is well
inside it), or keep 12 V and fit a rail-to-rail-output op-amp in the same footprint.

**What firmware must not assume, on the board as built:** commanding DAC full scale does **not**
reliably produce 10 bar. The achievable maximum lands somewhere between about 9 and 10 bar depending
on the individual op-amp and the instantaneous battery voltage, and it is not repeatable from board to
board. Any pressure target above ~9 bar has to come from closed-loop control against a pressure
sensor, never from an open-loop DAC code.

Related and unquantified: the MCP4922's own output cannot reach VDD either, so full-scale at the DAC
is slightly under 5 V and the doubled result is slightly under 10 V. The MCP4922 datasheet is not yet
filed in the board's `datasheets/` folder; the exact swing limit needs checking there before the top
of the pressure range is assumed reachable.

### Issue 4 — the net naming does not match the throttle channel's convention, and does not name the signal

The throttle channel distinguishes the internal node from the exported one:
`CMD_ACC_ESP32__0_5V` (DAC side of the MAX4660 mux) → `CMD_ACC__0_5V` (what leaves on CN10.1). The
brake channel reuses **one** name, `CMD_BRAKE__0_5V`, for the DAC output, the amplifier input, and
the connector pin, which is exactly why a 0–5 V net ended up on a 0–10 V connector pin without
looking wrong. Suggested rename, following the throttle's pattern and the `__<range>` suffix
convention already used across the board:

- `CMD_BRAKE__0_5V` → `CMD_PRES_DAC__0_5V` (internal: DAC output to amplifier input)
- `CMD_BRAKE__0_10V` → `CMD_PRES__0_10V` (exported on CN10.2 to the valve)

`CMD_PRES` rather than `CMD_BRAKE` because the signal is a **pressure setpoint** for a proportional
regulator, not a brake-force or brake-position command. The silkscreen legend abbreviates CN10.2 as
`CMD_BRK` with no voltage, so a net rename does not invalidate the existing silkscreen — but the
legend should become `CMD_PRES` at the next revision.

### The destination device

Festo **VPPM-8L-L-1-G14-0L10H-V1P-S1C1** (Festo part 571293), proportional pressure regulator,
sponsored. Confirmed from its datasheet (`~/dv/kart/pneumatics/resources/festo_571293_vppm_0_10bar_0_10v.pdf`):
"Signal range analogue input **0 – 10 V**", "Signal range analogue output 0 – 10 V", operational
voltage 21.6–26.4 V DC, max current consumption 300 mA. The `0L10H` field in the part number is the
0…10 V setpoint option. The setpoint input's **impedance is not stated** in that short datasheet — it
would be in the operating instructions (Festo doc 8110177 for the LED variant, 8110160 for the C1 LCD
variant we own) and matters for choosing the op-amp load condition in Issue 3.

Two consequences of the 24 V supply worth writing into the harness documentation: the valve's 0 V
must be common with the medulla's GND for the setpoint to mean anything (CN10.3 is GND and is
presumably that return, but it is not documented as such), and the valve is fed from a different
supply than the board, so a ground-offset between the two shifts the commanded pressure.

### Documentation that states the wrong thing

Three places describe the as-built 0–5 V path as if it were correct or as if it went somewhere else:

- `projects/kart-medulla/docs/pinout-cn-connectors.md` line 66 — "CN10 … CMD_BRAKE (0–5V) …
  Throttle and brake analog commands from the MCP4922 DAC **to the motor controller**." The brake
  command does not go to the motor controller; braking on this kart is pneumatic and the command
  goes to the VPPM.
- `projects/kart-medulla/docs/pinout-esp32-s3.md` line 217 — "VOUTB | CMD_BRAKE | Brake analog
  command (0-5V) → brake valve driver". States 0–5 V as the delivered range.
- `projects/kart-medulla/docs/pinout-esp32-s3.md` line 273 — "No chip — direct DAC output | analog
  0–5 V | … MCP4922 VOUTB = `CMD_BRAKE` | → brake valve driver (no mux on PCB)". Describes the DAC
  output as going straight out, which is what the board does but not what it should do; it also does
  not mention that an amplifier exists.

`tasks/kart-medulla.md` line 348 already carried the correct intent — "Place the LM358 amp (U4) near
MCP4922 VOUTB on the brake path **before CN5 pin 3** (`CMD_BRAKE__0_10V`)" — so the amplifier's
output was always meant to reach a connector. Note that entry names **CN5.3**, which today carries
`EXP_P4`, while the brake command actually exits on **CN10.2**. Whichever pin is chosen, the amplifier
output is the net that belongs on it.

### How the ESP32 reaches the MCP4922 (the answer to "how do they connect")

They do **not** connect by any analog path. The ESP32-S3-DevKitC-1 plugs into sockets U23/U24 and
talks to the DAC over a three-wire, write-only SPI link; the DAC's analog outputs are on the other
side of the chip and never return to the ESP32.

| ESP32 GPIO | U23 socket pads | Net | MCP4922 pin |
|---|---|---|---|
| GPIO 11 | 33, 34 | `/P1/MOSI` | 5 — SDI |
| GPIO 12 | 35, 36 | `/P1/CLK` | 4 — SCK |
| GPIO 14 | 39, 40 | `/P1/CMD_DAC_CS` | 3 — CS# (active low) |
| GPIO 13 | 37, 38 | `/P1/MISO` | *not connected to U13* |

(Each signal appears on a pad pair because U23 is a dual-row socket with both rows shorted to the
same header position.) `MISO` is routed to the socket but goes nowhere else — the MCP4922 is
write-only, so the bus needs no return path and MISO is free for a future SPI peripheral.

The rest of U13's pins are static:

| MCP4922 pin | Net | Effect |
|---|---|---|
| 1 VDD, 13 VREFA, 11 VREFB, 9 SHDN# | `+5V_REG` | 5 V supply; both channels referenced to the same 5 V, so full scale ≈ 5 V; SHDN# high = both DACs enabled |
| 8 LDAC# | `GND` | tied low, so each write transfers to the output immediately — no need to strobe a latch pin from firmware |
| 12 VSS | `GND` | |
| 2, 6, 7 | unconnected | NC pins |
| 14 VOUTA | `CMD_ACC_ESP32__0_5V` | throttle command, into the MAX4660 mux |
| 10 VOUTB | `CMD_BRAKE__0_5V` | brake/pressure command, into the LM358 — and, wrongly, out on CN10.2 |

So firmware writes a 16-bit word per channel over SPI: channel select bit (A or B), buffered-VREF
bit, gain bit (1× or 2×), shutdown bit, then 12 data bits. With VREF tied to the 5 V rail the
**gain bit must be 1×** — selecting 2× asks for 10 V from a 5 V-supplied DAC and simply clips.

The two channels are asymmetric downstream, which is the part that is easy to get wrong in firmware:
VOUTA (throttle) passes through the U14 MAX4660 analog mux, which selects between the DAC and the
throttle *pedal* under control of `SELECT_THROTTLE` (GPIO on U23 pads 15/16), so the ESP32 can hand
the throttle back to the driver. VOUTB (brake/pressure) has **no mux** — the DAC always owns it, and
the only way to release the brake command is to write zero.

A note on the name `CMD_ACC_ESP32__0_5V`: the `_ESP32` suffix marks it as the ESP32-generated
(autonomous) branch feeding the mux, as opposed to `PEDAL_ACC__0_5V` (the driver's branch) and
`CMD_ACC__0_5V` (whichever one the mux selected, which is what actually leaves the board). The
suffix does not mean the net connects to an ESP32 pin — it does not.

### Also noticed while auditing the connectors

`tasks/kart-medulla.md`, in the "External-connector audit (CN1–CN10)" section, says
"`SDC_IN_LOW_SIDE` (on **CN5**)". As built it is on **CN8.1**; CN5 carries
`HYDRAULIC_2__0_5V` / `PRESSURE_3__0_10V` / `EXP_P4`. The same section says "CN8 / CN9 / CN10 have
free slots if EXP_P* are reshuffled", but CN10 has no `EXP_P*` pin at all — its three pins are
`CMD_ACC__0_5V`, `CMD_BRAKE__0_5V`, `GND`, all in use.

Full as-built connector map, for reference (all ten are 3-pin push-in terminals, Phoenix 1990012):

| | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| CN1 | `+3V3` | `+12V` | `GND` |
| CN2 | `MOTOR_HALL_3__5V` | `MOTOR_HALL_2__5V` | `+5V_REG` |
| CN3 | `EXP_P1` | `EXP_P2` | `EXP_P3` |
| CN4 | `SCL__I2C` | `SDA__I2C` | `REVERSE_WIRE` |
| CN5 | `HYDRAULIC_2__0_5V` | `PRESSURE_3__0_10V` | `EXP_P4` |
| CN6 | `PEDAL_BRAKE__0_5V` | `PEDAL_ACC__0_5V` | `+3V3` |
| CN7 | `PRESSURE_1__0_10V` | `PRESSURE_2__0_10V` | `MOTOR_HALL_1__5V` |
| CN8 | `SDC_IN_LOW_SIDE` | `BUZZER` (old name; drives the compressor MOSFET gate) | `CMD_STEER_DIR__3V3` |
| CN9 | `CMD_STEER__PWM_3V3` | `HYDRAULIC_1__0_5V` | `GND` |
| CN10 | `CMD_ACC__0_5V` | `CMD_BRAKE__0_5V` | `GND` |

## 2026-07-30 (later) — Root cause found: the connector's 0–10 V label was overwritten during the CN1–CN10 reshuffle, and the fix is one label

Follow-up to the entry above, which established *that* `CN10.2` carries the 0–5 V DAC output instead
of the amplified 0–10 V valve command. This entry establishes *when and how* that happened, and
therefore how small the fix is.

### The EasyEDA original was correct

`projects/kart-medulla/easyeda-source/kart-medulla_2026-05-03.epro` — the export that ConvertEDA
turned into this KiCad project — carries **two** `CMD_BRAKE__0_10V` net labels and **two**
`CMD_BRAKE__0_5V` ones. Locating them by nearest designator inside `SHEET/*/1.esch`:

| Label | Position | Nearest component | What it is |
|---|---|---|---|
| `CMD_BRAKE__0_5V` | (1020, 445) | U13 | DAC VOUTB |
| `CMD_BRAKE__0_5V` | (1390, 365) | U4 | op-amp input |
| `CMD_BRAKE__0_10V` | (1465, 375) | U4 | op-amp output |
| `CMD_BRAKE__0_10V` | (860, 995) | CN1/CN2/CN3 cluster | **the connector exit** |

(The op-amp is `U4` in EasyEDA and `U1` in KiCad — which is why
`tasks/kart-medulla.md` has always said "the LM358 amp (U4)". EasyEDA had connectors CN1–CN8 only;
CN9 and CN10 were added during the KiCad cleanup, so the pin *numbering* is not comparable across the
two, but the exported *net* plainly was the amplified one.)

The January 2026 pre-rename export is older still and has a single net `BRAKE_0V5` with no op-amp at
all, so the amplifier and its 0–10 V exit were both added between January and May 2026.

### The regression: commit `e8881f1`, 2026-05-08

Counting both labels in every revision of `kart-medulla_P1.kicad_sch` shows the ratio holding at
2 × `__0_5V` / 2 × `__0_10V` from the ConvertEDA baseline (`bf3dc77`) through 44 commits, then
flipping to 3 / 1 at **`e8881f1` — "kart-medulla: assign CN1–CN10 pins to match ESP32 geometry"**
(2026-05-08), and staying there ever since. That commit reassigned 30 connector pins so each would sit
next to the ESP32 pin handling its signal. Two of its edits did the damage:

```
-	(label "EXP_P7"              →  +	(label "CMD_BRAKE__0_5V"     at (218.44, 48.26)   ← became CN10.2
-	(label "CMD_BRAKE__0_10V"    →  +	(label "GND"                 at (100.33, 67.31)   ← the old exit
```

So the pin that the amplified signal used to leave through was taken for GND, and the pin that
inherited the brake command was given the **DAC-side** net name. The signal did not lose a wire; it
lost its name at the only place the name mattered.

Why nothing caught it, in the two places it should have been caught, is written up in
`.agents/error-log.md` under 2026-07-30 — briefly: the commit's stated verification ("all 30 CN pins
resolve to the intended global net") compared the edit against the same list of names being applied,
and ERC stayed silent because `CMD_BRAKE__0_10V` still had two pads (op-amp output + feedback
resistor) and a two-pad net is electrically legal. KiCad has no "this net has no exit point" rule.

### What the fix takes

**Schematic — one label.** Every connection in this chain is made by a label on a short wire stub, not
by a drawn wire, which is why a single rename is sufficient. Change the label at **(218.44, 48.26)**
on CN10 pin 2's stub from `CMD_BRAKE__0_5V` to `CMD_BRAKE__0_10V`. Nothing else moves. Afterwards:

| Net | Nodes |
|---|---|
| `CMD_BRAKE__0_5V` | U13.10 (DAC VOUTB, label sits on the pin) + U1.3 (op-amp +IN, label at (375.92, 308.61)) |
| `CMD_BRAKE__0_10V` | U1.1 (op-amp OUT, label at (393.7, 306.07)) + R19.2 + **CN10.2** |

**PCB — delete two segments, route one track.** Pad positions (all B.Cu except the through-hole
connector), derived from the board file. Note when computing these by hand that KiCad's footprint
rotation maps a pad's local (px, py) to
`x = fx + px·cos A + py·sin A`, `y = fy − px·sin A + py·cos A` — CN10 sits at (77, 91) rotated 90°, and
using +A instead of −A mirrors pin 2 to the wrong side of the connector.

| Pad | Position | Net |
|---|---|---|
| CN10.2 | (74.5, 91.0) | `CMD_BRAKE__0_5V` → becomes `CMD_BRAKE__0_10V` |
| U13.10 | (86.027, 91.44) | `CMD_BRAKE__0_5V` |
| U1.1 | (85.255, 98.425) | `CMD_BRAKE__0_10V` |
| U1.3 | (85.255, 100.965) | `CMD_BRAKE__0_5V` |
| R19.2 | (87.845, 97.573) | `CMD_BRAKE__0_10V` |

`CMD_BRAKE__0_5V` is routed as one T on B.Cu, 0.2 mm wide, ~22 mm total in 7 segments: from CN10.2
east to (82.110, 91.0), diagonally to the junction at (83.566, 92.456), then one branch up-right to
U13.10 and another down to U1.3. `CMD_BRAKE__0_10V` is a 2.95 mm stub, 0.25 mm wide, from U1.1 via
(86.108, 97.573) to R19.2.

Delete only the two segments that reach out to CN10.2 — (74.5, 91.0)→(82.110, 91.0) and
(82.110, 91.0)→(83.566, 92.456). The remaining five still join U13.10 to U1.3 through the junction at
(83.566, 92.456), so the DAC→amplifier path survives untouched. Then route CN10.2 to the
`CMD_BRAKE__0_10V` net: 13.07 mm straight-line to U1.1, or 14.88 mm to R19.2. Prefer landing on R19.2
or on the existing stub at (86.108, 97.573) rather than on U1.1 directly — U1's pins 1–4 form a
vertical column at x = 85.255 (y = 98.425 / 99.695 / 100.965 / 102.235) and pin 3 in that column is on
the 0–5 V net, so a track approaching pin 1 from below has to thread past two pins on a foreign net.
Whether the corridor between (74.5, 91) and (86, 97.5) is clear of other copper has **not** been
checked yet.

### The physical board is a separate question — check it, do not infer it

The assembled board on the kart (`medulla-v1`) is EasyEDA-origin, and the EasyEDA design had the
connector on the amplified net, so the built hardware most likely does **not** carry this bug — it was
introduced in the KiCad cleanup on 2026-05-08, after the export. That is an inference, not a
measurement, and the connector numbering differs between the two designs (EasyEDA had CN1–CN8), so it
does not even identify which physical terminal carries the valve command.

**The measurement that settles it,** with the board unpowered: buzz the terminal wired to the valve
against U1 (LM358) pin 1 and against pin 3. Continuity to **pin 1** means the built board is correct
and only the KiCad design needs the fix. Continuity to **pin 3** means the built board has the bug too
and needs rework — cut the track leaving that terminal and run a wire from the terminal to U1 pin 1.
Also confirm U1 is populated at all; if the amplifier was never fitted, the whole chain is different
from what either design file says.

## 2026-07-30 (fix applied) — valve command now leaves the board at 0–10 V, routed on F.Cu

Applied the fix described in the entry above. KiCad was closed and
`scripts/guard-kicad-write.sh` passed, so this was a direct file edit; no MCP write tools were called
(`kicad-mcp-pro` was still resident, which forbids mixing the two).

**Schematic:** the label at (218.44, 48.26) on CN10 pin 2's wire stub renamed `CMD_BRAKE__0_5V` →
`CMD_BRAKE__0_10V`. That was the entire schematic change — every connection in this chain is a label on
a stub, so no wires moved. Exported netlist confirms the split:
`CMD_BRAKE__0_5V` = U13.10 + U1.3, `CMD_BRAKE__0_10V` = CN10.2 + R19.2 + U1.1. ERC 0 violations.

**PCB:** CN10 pad 2's net updated to match, then CN10.2 routed to the 0–10 V net **on F.Cu**:
(74.5, 90.9999) → 45° → (81.0727, 97.5726) → east → (87.0, 97.5726), then a 0.6 / 0.3 mm via down onto
the existing B.Cu stub that already runs between U1.1 and R19.2. Track width 0.25 mm, matching the
existing 0–10 V copper.

F.Cu was chosen because that corridor is completely empty on the front layer, while B.Cu is not: the
0–5 V net's vertical run at x = 83.566 spans y = 92.456…99.883, the +12 V feed to U1.8 occupies
y ≈ 98.4 around x = 79.8…82.6, and U1's own pads reach out to x = 84.28 (a SOIC-8 rotated 90°, so each
pad's *long* 1.95 mm axis lies along x, not y — getting that backwards makes the corridor look ~1 mm
wider than it is). The F.Cu diagonal clears CN10.1's through-hole pad by about 0.81 mm against a
0.254 mm requirement.

**Zone refill was the one step no CLI tool does.** `kicad-cli pcb drc` does *not* refill zones, so the
first DRC run after adding copper reported 6 clearance/hole-clearance violations, every one of them
"new copper vs Zone 'GND'" with an actual clearance of 0.0000 mm — the stored fill polygons predated
the new track. Nothing was wrong with the geometry. Refilled headlessly with KiCad's Python API and
saved:

```
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
import pcbnew
b = pcbnew.LoadBoard(path); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(path)
```

(It prints a harmless `create wxApp before calling this` assert when run headless.) After that: **DRC 0
violations, 0 unconnected items.** Note `b.Save()` rewrites the whole file in KiCad's canonical format,
so the commit diff is ~850 lines even though the intended change is small; object counts were compared
before and after to confirm nothing was lost — footprints 59, pads 234, zones 7, nets 83, gr_text 4 all
unchanged, segments 332 → 332, vias 7 → 8 (the new one).

The 5 schematic-parity warnings that remain (U1's empty footprint field, and the four `PAD1`–`PAD4`
mechanical pads reported as extra footprints) are byte-identical to the same check run against the
previous commit's files — pre-existing, unrelated to this change.

### The DAC→amplifier copper had also been ripped up, and was restored

Independently of the fix, six of the seven `CMD_BRAKE__0_5V` segments had been deleted in KiCad,
leaving only the 0.6 mm stub at U1 pad 3. That left **U13.10 → U1.3 unrouted** — the DAC output no
longer reached the amplifier input in copper — which DRC reported as a missing connection between U1
pad 3 and U13 pad 10. (The deletion is identifiable as a KiCad-side save rather than a scripted edit
because the same write also dropped the `(zone_defaults)` token from the `setup` block, which only
KiCad's serializer does.)

The original geometry was restored rather than re-routed: (86.027, 91.44) → (84.582, 91.44) →
(83.566, 92.456) → (83.566, 99.8826) → (84.6484, 100.965), joining the surviving stub to U1.3. That
path was what the surrounding layout had been designed around, and it is DRC-clean.

### Still open on this signal

The four remaining items of the fix task in `tasks/kart-medulla.md` — the net rename to `CMD_PRES*`,
the DAC full-scale check (and filing the MCP4922 datasheet), the three wrong documentation lines, and
the continuity check on the assembled board — are unaffected by this commit and still stand.

## 2026-07-31 — per-board task boards, reversing the 2026-07-16 one-file-per-repo rule

On 2026-07-16 the kart-medulla task list was moved out of its project folder to `tasks/kart-medulla.md`
under a rule of "exactly one `tasks.md` per repo, at the root, no exceptions; big clusters get a
`tasks/<name>.md` linked from it". The stated reason was that a second file named `tasks.md` breeds
duplicate and stale entries.

Two weeks of use showed the split leaking in exactly the way the rule was meant to prevent. The root
board declared at its "In Progress" heading that kart-medulla items live in the other file, while its
TODO carried four of them: a bare "flip CN3 and CN4" line, which also existed as "Flip all ten CN
connectors 180°" in the board file; "Patch the fabricated board for the CN10.2 brake fix"; and four of
the eight numbered open contradictions (L7805 vs LM2596, compressor power path, `PRESSURE_3`,
`medulla-v1`/`v2` naming). The duplication had not been prevented, only moved across a directory
boundary. It also cut against this repo's own stated goal for project folders — a self-contained
`git clone` (`AGENTS.md`, "Datasheets").

Rubén's call, after asking why the board's tasks sat two directories away from the board: **each board
keeps its own `projects/<board>/tasks.md`**, and the root `tasks.md` is the cross-board board plus the
index of every per-board board. An unlinked task board is still invisible; that part of the old rule
survives.

Also asked at the same time: whether the `projects/` folder earns its level, since it holds one entry.
Kept. The repo root is not mostly boards — it is `lib/` (shared symbols, footprints, 3D models),
`fab/`, `docs/` (cross-board), `scripts/`, `.agents/` and `projects/`. Without the wrapper, a second
and third board would list alongside the shared infrastructure. It looks redundant only because there
is currently one board.

What moved:

- `git mv tasks/kart-medulla.md projects/kart-medulla/tasks.md` (history preserved); `tasks/` deleted.
- The four kart-medulla items above moved from the root board into the board file. Contradiction
  numbering is unchanged (1, 2, 3, 7 stayed at the root; 4, 5, 6, 8 moved) because entries in this
  file refer to them by number; the root keeps one-line pointers so the numbers still resolve.
- "flip CN3 and CN4" was not merged into the connector-rotation task. It arrived in `280a379` as a
  bare line with no date or context and has two readings — rotate those two connectors 180° (a subset
  of the existing task, so a duplicate) or swap their signal assignments (separate work). Filed in the
  board's task list as a question for Rubén rather than silently resolved either way.
- Path references updated in `AGENTS.md`, `README.md`, `docs/pcb-checklist.md`, and the board's
  `README.md`, `parts.md`, `requirements.md` and `docs/pinout-cn-connectors.md`. References inside
  this file and `.agents/error-log.md` were left alone — they are dated append-only records that were
  accurate when written, which is the standing question in open contradiction 2.
- The board task list's front-matter marker was `read in full — kept under 150 lines`, which the file
  has not honoured for a long time (it is ~750 lines). Changed to `reference — read when working on
  this board`.

Global `~/.claude/CLAUDE.md` carried the 2026-07-16 rule as a general convention, so it was updated
too; otherwise the next session would move the file back.

---

## 2026-07-31 — A commit hash cannot be silkscreened; the board carries a design ID and the page carries the hash

**The problem found.** The board-identity convention decided earlier today (`README.md`, "Board
identity") says a manufactured board is identified by the dv-hardware commit its gerbers were exported
from, "written on the board as a QR code or label". On a **sticker** applied after fabrication that
works. In **silkscreen** it is impossible, and not for a practical reason but a definitional one:
putting hash `H` into `kart-medulla.kicad_pcb` changes that file, so the commit containing it hashes to
something other than `H`. A commit can never contain its own hash. Stamping the parent commit is the
only variant that terminates, and the parent is precisely not the gerber-export commit the convention
asks for.

**The fix, which needs no change to the convention.** The kart-docs part-QR system already mints a
different kind of identifier: a random 16-digit **design ID** (see `kart-docs/history.md`, 2026-06-14
and 2026-07-31). It has the opposite property — it is minted *before* any layout is committed, so it
can sit in the silkscreen from the first commit and never has to change again. So:

- **On the board (silkscreen): the design ID**, as text plus a QR. Stampable in advance, permanent,
  and already resolvable by the kart-docs `/scan/` page.
- **On its page `/p/<id>/`: the gerber-export commit hash**, the fabrication date, the per-board rework
  list, and the paired firmware commits.

The two identifiers are not competitors and neither replaces the other. The design ID is a physical
handle that can never go stale because it points at a page rather than at content; the hash is the
exact content it points at. Trying to make one code do both jobs is what fails.

**It also covers the case the convention already flagged as unsolved.** A board stops matching its
hash the moment it is reworked — a lifted pin exists on one physical board and in no commit. A hash
silkscreened on the board would then be wrong with no way to correct it. A design ID stays correct,
because the rework is recorded on the page it resolves to.

**Consequence for the medulla.** `Kart Medulla PCB v2` has design ID `1604 0948 4608 5574`
(`kart-docs/docs/p/1604094846085574.md`). The v2 silkscreen should carry that number as text plus its
QR. The existing fabricated board (`84d6dd0`) predates all of this and has no silkscreened ID, so it
takes a sticker — and a sticker can carry the hash directly, since a sticker is not in the board file.

## 2026-07-31 (later) — seven of the eight open contradictions closed

Rubén: "tell me in simple terms the contradictions. we have to solve them now." Below is what each
turned out to be and how it was closed. Only number 7 is still open.

### Closed without a decision — they were factual errors, not choices

**1 — `history.md` ordering.** `AGENTS.md` said "Newest entries first"; this file has always been
oldest-first, appended at the bottom, which is what global `~/.claude/CLAUDE.md` specifies. The
instruction was wrong. `AGENTS.md` now says "Append to the end — oldest entry first, newest last".

**2 — references to `.agents/tasks.md`, a file that no longer exists.** Rubén's ruling: a dated log
is allowed to be out of date at the top, that is what the name means. Written into `AGENTS.md` as a
standing policy and into global `~/.claude/CLAUDE.md` as a general one: **dated entries are never
edited to match later reality.** A path or decision named in an old entry was accurate on its date;
when it moves or is reversed, the newer entry says so and the old one stays as written. Stale paths
in `history.md` and `.agents/error-log.md` are not inconsistencies and should not be filed as such.

**4 — L7805 linear vs LM2596SX-ADJ buck.** Not a real disagreement once checked against the
schematic: `U19` is an **L7805CDT** in a DPAK, so the linear part is what is fitted, and the LM2596
(8 in stock) was an alternative never taken. The power-architecture diagram in
`docs/pinout-esp32-s3.md` had described the choice as open; it now names the L7805 as fitted, and the
datasheet list carries both with the LM2596 marked "evaluated, not fitted".

### Closed by a decision from Rubén

**5 — does compressor motor power come on-board?** *Signals only for now; power on-board in a future
revision.* v2 routes the compressor's gate signal to a terminal and nothing else; the MOSFET, its
flyback diode and the bulk capacitance stay off-board. This **reverses the 2026-07-18 directive**
("integrate it — fewer wires running between boxes and bolted-on PCBs"), so the task
"Design the compressor MOSFET drive on-board for medulla-v2" was retitled and deferred to the later
power-section revision, with a note asking Rubén to confirm the reversal.

Rubén asked for the connector to be checked against the load. Measured compressor current is **6 A
running at 60 % duty** (bench, 2026-07-18):

| Connector | Rated | Verdict against 6 A |
|---|---|---|
| Phoenix Contact 1990012 (PTSA 0,5/3-2,5-Z) — fitted as CN1–CN10 | **2 A** @ 250 V, 0.5 mm² | **No** — 3× under, before any inrush |
| WAGO 2601-3103 — the team's stocked standard | **17.5 A**, 1.5 mm² | Yes, comfortable |
| Deutsch **DT**, size-16 contacts | 13 A continuous | Yes |
| Deutsch **DTM**, size-20 contacts | 7.5 A continuous | Marginal |

Ratings checked 2026-07-31 against the manufacturer/distributor pages, all cited in the new
`docs/connectors.md`, which is now the cross-board home for connector ratings. **The Deutsch DT
family is the team standard for harness connectors** (Rubén, 2026-07-31) — that fact was nowhere in
this repo or in `~/dv/` before today. Soldering the wire straight to the board is an accepted
fallback. Locked-rotor inrush has never been measured and must be, before that revision is designed;
it is what sizes the MOSFET, the flyback path and the copper. Rubén's emphasis, recorded verbatim in
substance: **the traces must be properly sized** — the ~1 mA copper `+12V` and the motor return carry
today is the actual blocker, and a bigger connector in front of undersized copper just moves the
failure.

**6 — two pressure channels or three?** *Three.* This overrides the 2026-07-18 reading that dropped
it to two. `PRESSURE_3`'s old pin (GPIO 1, CN5.2) stays with the steering sensor, so v2 must give the
third pressure channel a **new** ADC-capable GPIO, its own 0–10 V divider and a terminal pin. New
task on the board list; `requirements.md` amended in three places, including the V1 line that had
been marked down to two.

**8 — is the assembled board `medulla-v1`?** *Yes*, so the next revision is `medulla-v2` — which is
what the docs already assumed. Nothing on disk backs it (`fab/` is empty, the only tag is
`medulla-v0.1-converted`), so the task is now to put the name on the silkscreen and in the title
block and to tag the next fab release.

### Still open

**7 — the 4th copy of the PCB checklist**, in the team Drive at
`formula/formula_24-25-26/el/pcb-checklist.md`, stale since 2024-12-04. Rubén wants exactly one copy
and ruled out a symlink, which Drive handles badly. No symlink is needed: replacing that file's
contents with the single public URL
<https://github.com/UM-Driverless/dv-hardware/blob/main/docs/pcb-checklist.md> is a pointer, not a
second copy, and the repo is public so no GitHub account is required to follow it. Blocked on two
things: `el/` belongs to the whole electronics section rather than Driverless, so overwriting a file
there needs its owner's agreement; and the Drive integration available here can read and create but
cannot delete or overwrite, so it is a manual edit either way.

## 2026-07-31 (later still) — v2 integrates the compressor after all; connector and WAGO facts

Same day, a few hours after the entry above, which had recorded the compressor power path as "signals
only for now, power on-board in a later revision". **That is wrong and is superseded here.** The
question had been put as a binary and Rubén's fuller answer was that v2 integrates the switching
stage, motor current included — *the less wiring, the better*, and the kart runs two boxes today that
v2 is meant to collapse into one. The earlier entry stays as written, per the no-retro-editing rule
settled the same day; this one is the current state.

### The circuit already exists and is validated

The compressor MOSFET module in service has been modified: its **bridge rectifier is removed** and
the **series resistor feeding the optocoupler's LED is changed to 330 Ω** so the input works driven
from 3.3 V. It runs the compressor today, and more of the same modules are at home. So v2 copies that
circuit onto the PCB instead of designing a gate-drive stage from scratch.

This also reframes the 2026-07-18 gate-drive research further up this file. That work concluded a
3.3 V pin cannot drive a power MOSFET gate, which remains true — but the modified module does not ask
it to. The ESP32 pin drives an optocoupler LED through 330 Ω; the gate is driven on the isolated side
from the DC-IN rail. The analysis applies to the unmodified arrangement, not to what is now in
service.

Three things must be pinned down before v2 can be drawn, and none of them are in this repo yet:
**which module it actually is** (the optocoupler input and removed bridge rectifier do not match the
HUABAN HA210N06 board described earlier, which has a JST control input and an unidentified `U2`),
**its traced schematic**, and **the files** — datasheets, photos, sourcing line.

### Connector ratings, checked against the 6 A the compressor draws

| Connector | Rated | Verdict |
|---|---|---|
| Phoenix Contact 1990012 (PTSA 0,5/3-2,5-Z), fitted as CN1–CN10 | 2 A @ 250 V, 0.5 mm² | **Cannot carry it** — 3× under |
| WAGO 2601-3103, on the buy list | 17.5 A, 1.5 mm² | Yes, comfortably |
| Deutsch DT, size-16 contacts | 13 A | Yes |
| Deutsch DTM, size-20 contacts | 7.5 A | Marginal |

New file `docs/connectors.md` holds these with their sources. The **Deutsch DT family is the team
standard for harness connectors** (Rubén) — that was recorded nowhere before today.

**Locked-rotor inrush will not be measured.** Rubén: the circuit is validated in service, and having
components bigger than strictly needed costs nothing when they are already in stock. So the rule for
this load is *pick from the shelf and leave margin*, not *measure the peak and size to it*. What does
still have to be got right is the copper: `+12V` and the motor return are drawn for ~1 mA today, and
his emphasis was that **the traces being properly sized is the important part** — a bigger connector
in front of undersized copper just moves the failure.

### WAGO 2601 — which variant is the vertical one

Asked because a photo of a top-entry 2601 looked like a better fit than what might have been ordered.
Answer: **`2601-31xx` is top entry** — wire in from above, perpendicular to the board, levers on the
front face — and that is already what the buy list names (`2601-3102` 2-pole, `2601-3103` 3-pole).
`2601-11xx` is the side-entry variant of the same series. WAGO's page for `-3103` says "top entry"
and for `-1103` says "side entry"; the `-3102` page does not print the phrase, so that one is read
from the series numbering and is worth confirming on the datasheet before ordering.

**None of them are in inventory.** `~/vault/inventory/` had only the Phoenix 1990012 (status
`Noted`, also not bought) and WAGO 221 lever nuts, which are in-line splice connectors and unrelated.
New vault entry: `~/vault/inventory/wago-2601-pcb-terminal-blocks.md`.

### Connector rotation, and the checklist copies

**All ten CN connectors get rotated 180°**, not a subset — confirming the existing task and disposing
of the bare "flip CN3 and CN4" line that had been on the root board since `280a379`. Wires exit
outward and pin numbering runs with the CN numbering.

Searching Drive for the "4th" stale PCB checklist found **four copies plus a backup**, all owned by
Rubén, so the `el/`-folder-ownership blocker recorded earlier does not apply. The root task now lists
each with its link. The fix stays a manual one: the Drive integration here can read and create but
cannot overwrite or delete.

### Pushing

Global `~/.claude/CLAUDE.md` said push only with explicit confirmation. Rubén: that belongs to
specific projects, not to every repo. Changed to push after committing by default, with ask-first
being something a project states in its own `AGENTS.md`.

## 2026-07-31 (evening) — U2 identified as a PC817; the WAGO swap makes the rotation task moot

### The compressor module's input stage

Photograph supplied by Rubén, saved at
`projects/kart-medulla/docs/images/compressor-module-U2-PC817.png`. It shows:

- **`U2` = Sharp `PC817`**, lot code `CW831` — a 4-pin phototransistor optocoupler, mounted
  surface-style on the carrier.
- **`R2`, `R3`, `R4` all marked `1002` = 10 kΩ**, in a row directly above `U2`.

This closes the question opened on 2026-07-18 ("Does the module's control input actually accept
3.3 V?", and the sub-question of what `U2` is). The answer recorded then reasoned toward a
transistor level-shifter and treated `U2`'s package as a clue to how many stages it had. That was
the wrong shape of answer: the module is **opto-isolated**. The ESP32 pin drives an LED, and the
MOSFET gate is driven on the far side from the module's own DC-IN rail. Both earlier statements
survive — a 3.3 V pin still cannot drive a power MOSFET gate, and this module does not ask it to.

Two things the photograph does *not* settle, now written into the task:

- **The 330 Ω is not in the frame.** None of `R2`/`R3`/`R4` is 330 Ω, so the resistor Rubén changed
  to make the input work at 3.3 V is elsewhere on the board, probably `R1`.
- **The output side is unseen.** If a 10 kΩ turns out to be the only pull-up on a gate the size of
  the HA210N06's (Qg = 135 nC, Ciss = 5800 pF), that is an RC of tens of microseconds and the device
  crosses its linear region slowly on every edge. Survivable at 500 Hz, but that part should be
  replaced with a real driver when the circuit is copied onto the PCB rather than reproduced as-is.

### The connector rotation task is obsolete

Rubén, on being offered the "rotate all ten CN connectors 180°" task as the next piece of work:
*obsolete if we use WAGO*. Correct, and it had not occurred to me while writing the task up an hour
earlier. That task exists only because the Phoenix 1990012 parts are already placed the wrong way
round. v2 replaces them with WAGO 2601-31xx, a different footprint at a different pitch, so there is
nothing to rotate — the new footprints get placed correctly the first time, and the two complaints
behind the rotation task (wires must exit outward; pin numbering must run with the CN numbering)
become placement requirements instead of rework.

New task **"Switch CN1–CN10 to WAGO 2601-31xx on v2"** supersedes it. What it costs, which is more
than a symbol swap: **pitch goes 2.5 mm → 3.5 mm**, so every connector widens and the board outline
and edge keep-outs need re-checking; neither part has a footprint or 3D model in
`kart-medulla.pretty` yet; the silkscreen legend and `docs/pinout-cn-connectors.md` need the new pin
order; and whether *all ten* swap or only the high-current path needs confirming before ordering,
since it changes the quantity.

The old rotation task is kept below it rather than deleted — it is the clearest statement of what
"placed correctly" means and of what the 1990012's staggered pin-2 row costs.

### The Drive checklist copies

Handed to a different agent session. The root task is flagged claimed so the work is not repeated,
with its findings (four copies plus a backup, file IDs and links) left in place in case that session
stops early.

### Correction, same evening — the 330 Ω arithmetic, and what the photograph is

The entry above listed "where the 330 Ω went" as an open question because none of `R2`/`R3`/`R4` in
the photograph reads 330 Ω. That was a wasted question: **the photograph is from before the resistor
was changed**, so it shows as-shipped values, and 330 Ω was already stated plainly.

The value also checks out on its own, which is the point that should have been made instead of asking
about it. The PC817's LED drops about 1.2 V, so the series resistor sets LED current:

| Series resistor | Drive voltage | LED current |
|---|---|---|
| 10 kΩ as shipped | 12 V | (12 − 1.2) / 10 k = 1.1 mA |
| 10 kΩ as shipped | 3.3 V | (3.3 − 1.2) / 10 k = 0.21 mA — dead |
| **330 Ω fitted** | **3.3 V** | (3.3 − 1.2) / 330 = **6.4 mA** |

The as-shipped 10 kΩ was sized for a 12 V control input. At 3.3 V it delivers a fifth of a milliamp,
far under the IF = 5 mA point where the PC817's CTR is specified (80–160 % for rank A), so the
phototransistor barely conducts. 330 Ω gives 6.4 mA — just above the characterised point, roughly
5–10 mA of collector current — and costs an ESP32-S3 pin rated 28 mA nothing. That is the entire
modification, and it is sound.

## 2026-07-31 (late) — connector audit re-checked against the netlist; five doc errors found

Prompted by Rubén: lots of tasks left, and the answers were not actionable. So instead of asking,
three tasks that needed nobody else were worked: the brake-command documentation, the stale
references in the connector audit, and the MAX4660 wiring check. Everything below comes from a fresh
`kicad-cli sch export netlist` on the current schematic, not from re-reading the docs.

### As-built connector map, 2026-07-31

| | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| CN1 | `+3V3` | `+12V` | `GND` |
| CN2 | `MOTOR_HALL_3__5V` | `MOTOR_HALL_2__5V` | `+5V_REG` |
| CN3 | `EXP_P1` | `EXP_P2` | `EXP_P3` |
| CN4 | `SCL__I2C` | `SDA__I2C` | `REVERSE_WIRE` |
| CN5 | `HYDRAULIC_2__0_5V` | `PRESSURE_3__0_10V` | `EXP_P4` |
| CN6 | `PEDAL_BRAKE__0_5V` | `PEDAL_ACC__0_5V` | `+3V3` |
| CN7 | `PRESSURE_1__0_10V` | `PRESSURE_2__0_10V` | `MOTOR_HALL_1__5V` |
| CN8 | `SDC_IN_LOW_SIDE` | `BUZZER` (= compressor gate) | `CMD_STEER_DIR__3V3` |
| CN9 | `CMD_STEER__PWM_3V3` | `HYDRAULIC_1__0_5V` | `GND` |
| CN10 | `CMD_ACC__0_5V` | `CMD_BRAKE__0_10V` | `GND` |

### What the audit had wrong

1. **`SDC_IN_LOW_SIDE` was recorded on CN5. It is on CN8.1.** Already known and filed; now corrected
   in place.
2. **"CN8 / CN9 / CN10 have free slots if `EXP_P*` are reshuffled" — there are no free slots.** All
   thirty pins are assigned. The only reshufflable pins on the whole board are `EXP_P1`–`EXP_P3` on
   CN3 and `EXP_P4` on CN5.3.
3. **`EXP_P1`–`EXP_P7` on CN8/CN9/CN10 — wrong on both counts.** They are on CN3 and CN5.3, and only
   four exist: `EXP_P5`–`EXP_P7` are not nets in the schematic at all. Four pins is therefore the
   board's entire spare capacity, and `SDC_ENABLE` and the encoder's power/ground are both competing
   for it.
4. **CN4 is worse than recorded.** The audit said "no GND; pins are SDA / SCL / +3V3". Actually its
   pins are `SCL__I2C` / `SDA__I2C` / **`REVERSE_WIRE`** — so the steering encoder gets its two bus
   lines and *neither* power nor ground, and nothing documents where those come from. Worth settling
   during the WAGO footprint swap rather than after it, since the pole count is in play then.
5. **"+12V on CN6, +5V from the LM2596 buck" — both wrong.** `+12V` is on **CN1.2** and feeds `U19`,
   an **L7805CDT**. The buck was evaluated and never fitted.

### Two open questions answered without asking anyone

- **Where the motor halls' 5 V comes from:** the medulla supplies it. `CN2.3` exports `+5V_REG`, the
  L7805's output, and the three hall sense lines sit on CN2.1, CN2.2 and CN7.3. The same pin can
  instead accept an external 5 V tied onto the shared net. Remaining: a load check, since that
  regulator's budget was written up as ~1 mA for the analog chips.
- **`REVERSE_WIRE` and the I²C rename:** both already done. `REVERSE_WIRE` is on `CN4.3` (the task
  proposed CN8), and the nets are `SDA__I2C` / `SCL__I2C` with no `STEER_` prefix. Marked done.

### MAX4660 (U14)

Schematic side re-verified and unchanged since 2026-05-07: COM=`CMD_ACC__0_5V`, NC=`PEDAL_ACC__0_5V`,
NO=`CMD_ACC_ESP32__0_5V`, IN=`SELECT_THROTTLE`, V+=`+5V_REG`, pin 5 unconnected, GND/V−/EP to GND.
ERC 0 violations. Nothing left in this repo — the remaining item is firmware driving GPIO 15.

### Brake-command documentation

Three lines corrected to describe the board as it now is: `CN10.2` exports **0–10 V** to the Festo
VPPM after the LM358 ×2, not 0–5 V to the motor controller; the VOUTB row now separates the DAC-side
0–5 V from the exported 0–10 V; and the signal-path table names the LM358 stage while keeping the
"no mux" point, which is real — unlike the throttle there is no MAX4660 here, so the DAC always owns
the command and the only release is writing zero. Also documented on CN10.3: the VPPM runs from a
separate 24 V supply, so its 0 V must be common with the medulla's GND or the commanded pressure
shifts by the offset.

### Follow-ups, same night

**WAGO 2601 footprints ship with KiCad 10 — nothing to draw.** The task written earlier tonight said
neither part was in `kart-medulla.pretty` and that WAGO's own downloads might be needed. Wrong:
`TerminalBlock_WAGO_2601-3102_1x02_P3.50mm_Vertical` and `..._2601-3103_1x03_P3.50mm_Vertical` are in
the stock `TerminalBlock_WAGO` library, reachable with no setup because the global `fp-lib-table`
nests KiCad's own table. KiCad's naming also settles the variant question independently of WAGO's
website: every `-31xx` footprint is `_Vertical`, every `-11xx` is `_Horizontal`.

Comparing the two footprint files gives the real cost of the swap, which is not the pitch:

| | Phoenix `1990012` | WAGO `2601-3103` |
|---|---|---|
| Holes per 3-pole | 3 | **6** — two per pole, rows 5 mm apart |
| Pitch | 2.5 mm | 3.5 mm |
| Pin-1→pin-3 span | 5.0 mm | 7.0 mm |
| Drill | 1.0 mm | 1.2 mm |
| Arrangement | staggered, pin 2 offset 5 mm | regular grid |

Twelve extra holes appear along each board edge, all on nets that already exist. But the staggered
pin-2 row — the thing that made the old rotation task expensive, because rotating it moved which side
pin 2 sat on — simply disappears. The swap widens the connectors and simplifies the copper under them
at the same time.

**`CN8.2` frees up on v2.** Rubén, on being told there are no free connector pins: the buzzer is not
needed on v2 either. `CN8.2` carries the net still named `BUZZER`, which actually drives the external
compressor MOSFET's gate — and v2 brings that MOSFET on-board, so the signal stops leaving the PCB.
Nothing will reclaim the pin, since the kart carries no buzzer at all. So v2's spare capacity is one
free pin plus the four reshufflable `EXP_P*` pins, and `SDC_ENABLE` (no exit anywhere) and CN4's
missing encoder power/ground are the claims on it.

**Vault:** the WAGO 2601 entry moves from `Noted` to `To Buy` — confirmed we are buying them.

### The v2 board gets re-laid-out, not patched

Rubén, same night: enough has changed to be worth a redo of the board, so the existing routing can
go. Measured to check that, rather than taking it on feel:

- The board carries **332 track segments, 14 vias, 8 zones, 60 footprints**.
- **27 of the 82 nets reach a CN connector**, and **201 of the 332 track segments — 60 % — sit on
  one of those nets.** All ten connector footprints change pitch and hole pattern in v2, so every one
  of those segments moves regardless.

Add the parts that do not exist on the board at all yet — the compressor switching stage, `+12V` and
the motor return re-sized from ~1 mA copper to 6 A, a `PWR_GND` split off the signal ground, a third
pressure channel — and preserving the remaining 40 % is not worth routing around. So: rip up and
start again.

**Sequencing matters more than the decision does.** The rip-up is one operation and reversible
through git, but doing it before the v2 schematic is settled produces an empty board paired with a
stale schematic, which is worse than what exists now. It belongs at the moment the schematic is
finished.

The "Lay out the medulla PCB" task is rewritten as this re-layout. Its placement list also had three
wrong references, corrected against the netlist while rewriting: it called the op-amp `U4` (it is
`U1`), said "CN1–CN8" when there are ten connectors, and put the throttle and pressure commands on
CN7.3 and CN5.3 when both are on CN10.

**Everything decided for v2 is now on the board list.** Checked one by one: WAGO connector swap,
on-board compressor switching, 6 A copper sizing, third pressure channel on a new pin, separate
`PWR_GND`, GPIO 38/39 routed out, `medulla-v1`/`v2` naming on silkscreen and title block, the op-amp
0–10 V swing fix, the silkscreen legend redo, CN4's missing encoder power and ground, `SDC_ENABLE`
having no exit, and the steering sensor becoming a first-class signal. The one thing that had *not*
been written down until now is this decision itself — the individual changes were all recorded, but
nothing said the board would be redone rather than edited.

### What is actually left to settle the v2 schematic, checked 2026-07-31

Three items from the "Finish medulla schematic" list were checked against the netlist rather than
re-read, and two of them turned out to be already done:

- **Title capitalisation** (`ESP32-S3-DevkitC-1` → `DevKitC-1`): done, no lowercase variant remains.
- **SPARE / RESERVED pins flagged**: done. 24 unconnected pins across the design, all flagged, ERC
  0 violations — `U24` 14, `U25` 4, `U13` 3, `U23` 2, `U14` 1.
- **ADC filter caps: genuinely missing, on all seven analog inputs.** Every input does have its
  divider (`PEDAL_ACC` R14/R15, `PEDAL_BRAKE` R16/R17, `HYDRAULIC_1` R24/R25, `HYDRAULIC_2` R26/R27
  as two-resistor 0–5 V dividers; `PRESSURE_1` R11/R12/R13, `PRESSURE_2` R4/R6/R7, `PRESSURE_3`
  R8/R9/R10 as three-resistor 0–10 V chains). But the board carries only six capacitors, C1–C6, and
  all six are on power rails. No ADC node has one. The task list has asked for 100 nF at each ADC pin
  since 2026-05; it was never done.

**Spare capacity found while counting:** `U25` (PCF8574) pins 10, 11, 12 — `EXP_P5`–`EXP_P7` — are
unconnected on the chip, as is `INT#` on pin 13. That is three more expander outputs available for
free, which matters because the connector audit had concluded the board's spare capacity was four
`EXP_P*` pins plus `CN8.2` freeing up on v2. They suit anything needing a slow on/off line —
`SDC_ENABLE` above all — and suit nothing needing PWM, timing, analog, or supply current, since a
write costs an I²C transaction.

### ADC filter caps added — C7–C13

The seven 100 nF capacitors the task list had been asking for since 2026-05 are now on the schematic:
`C7` `PEDAL_ACC__3V3`, `C8` `PEDAL_BRAKE__3V3`, `C9` `HYDRAULIC_1__0_3V3`, `C10`
`HYDRAULIC_2__0_3V3`, `C11` `PRESSURE_1__0_3V3`, `C12` `PRESSURE_2__0_3V3`, `C13`
`PRESSURE_3__0_3V3`. Each is `kart-medulla:C0603`, one pin on the divider's output node and one on
GND, drawn as a label-on-stub block in free sheet space at X≈490, Y 88.9–165.1 — the same style the
rest of this schematic uses, so nothing had to be routed through existing geometry.

**Why 100 nF is the right value here.** The corner frequency depends on the divider's source
impedance, which differs per input:

| Input | Divider | Source impedance | −3 dB with 100 nF |
|---|---|---|---|
| `PEDAL_ACC`, `PEDAL_BRAKE` | 10 k / 10 k | 5.0 kΩ | 318 Hz |
| `HYDRAULIC_1`, `HYDRAULIC_2` | 2 k / 3.9 k | 1.32 kΩ | 1.2 kHz |
| `PRESSURE_1`–`3` | 20 k / 10 k | 6.67 kΩ | 239 Hz |

All three are far above the bandwidth of a pedal position or a tank pressure and far below anything
the ADC needs to track, so the same value works everywhere. The second reason matters more: the
ESP32-S3's SAR ADC charges an internal sampling capacitor from whatever it is connected to, and
6.67 kΩ is a high source impedance for that. The 100 nF sits next to the pin as a charge reservoir,
so the sampling cap is fed from it rather than through the divider.

**Method note.** `scripts/guard-kicad-write.sh` reported `kicad-mcp-pro` running, so this was a
direct file edit with no MCP write calls, per the one-mode-per-session rule. Verified three ways:
ERC 0 violations, a fresh netlist export confirming all seven caps on their intended nets with GND on
the other pin, and an SVG render. The render caught something the netlist could not — at the first
attempt the caps were spaced 7.62 mm apart, which put each one's `100nF` value text exactly on the
next one's reference designator. Re-done at 12.7 mm.

**Left for the PCB:** each cap has to be placed at the ESP32's ADC pin, not next to its divider. At
the wrong end of the trace it does nothing.

### Valve-command task: three of its four items closed 2026-07-31

**Net rename (item 3).** `CMD_BRAKE__0_5V` → `CMD_PRES_DAC__0_5V`, `CMD_BRAKE__0_10V` →
`CMD_PRES__0_10V`, following the throttle channel's internal-vs-exported pattern. `CMD_PRES` because
the signal is a pressure setpoint for a proportional regulator, not a brake-force command. Applied to
the schematic (4 occurrences), the PCB (15) and both pinout docs, so schematic and board stay in
parity: ERC 0 violations, DRC 0 violations, 0 unconnected items. One `CMD_BRAKE` reference remains in
`docs/pinout-esp32-s3.md` and is correct where it sits — under the "Legacy: classic ESP32 (previous
board)" heading. The built board's silkscreen still reads `CMD_BRK`; the legend gets updated at the
next revision.

**MCP4922 datasheet filed (item 4).** DS22250A, 2010, from
<https://ww1.microchip.com/downloads/en/DeviceDoc/22250A.pdf>, now at
`datasheets/MCP4922_Microchip_datasheet.pdf`. It answers the question the task asked, and the answer
is that the DAC is *not* the binding constraint:

- **Output swing: 0.01 V to VDD − 0.04 V typical.** On the 5.0 V rail that caps full scale at about
  **4.96 V**, 0.8 % short of 5 V. Doubled by the LM358 it is **9.92 V rather than 10.00 V** — about
  0.08 bar on a valve regulating roughly 1 bar per volt.
- Beside the LM358's own 1–2 V of lost headroom on a 12 V rail, that is noise. The op-amp remains
  what limits the top of the range, which is what the separate polish task already says.
- Calibration caveat: accuracy is guaranteed better than 1 LSb only for VOUT between 10 mV and
  VDD − 40 mV, so the extreme codes are outside spec.

**Two firmware constraints fall out of it,** both in the same 16-bit write word (Register 5-1, page
24), and neither is implemented — there is no MCP4922 write in `~/repos/kart-medulla` at all:

- **`GA` = 1** selects 1×. `GA` = 0 selects 2×, which asks a 5 V-supplied part for 10 V and clips at
  ~4.96 V.
- **`BUF` = 0**, unbuffered VREF. Buffered mode accepts VREF only from 0.040 V to VDD − 0.040 V, and
  VREF here *is* VDD — outside that window. Unbuffered accepts 0 to VDD at 165 kΩ input impedance,
  which the 5 V rail drives easily.

**The over-voltage number (item 2).** The task had asked for the exact absolute-maximum rating once
the datasheet was filed. It is **−0.3 V to VDD + 0.3 V** on any input or output referred to VSS, so
**−0.3 V to +5.3 V** here, with output-pin current capped at ±25 mA. The valve runs on 24 V, so a
harness fault at the old CN10.2 wiring presented roughly **19 V over the absolute maximum** directly
onto VOUTB, with no series resistor, clamp or buffer. Moving CN10.2 onto the op-amp output removed
that path.

Only item 1 of the four is left, and it is not desk work: a continuity check on the assembled board.
