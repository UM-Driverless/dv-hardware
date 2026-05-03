<!-- consult selectively — grep, never read in full -->

# History

Append-only log. Newest first.

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
- Project folder named `kart-medulla` (matches `kart_medulla` firmware repo modulo case, and team verbal usage — `kart-brain` / `kart-medulla`).
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
