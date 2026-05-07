<!-- reference — read when relevant -->
---
last_verified: 2026-05-07
kicad_version: 10.0.x
os: macOS
purpose: |
  Verified UI cheat-sheet for KiCad 10 on macOS. Grep this file before
  describing any KiCad UI element. Do NOT invent menu paths, panel names,
  icon shapes, or hotkeys. If something is not in this file and you cannot
  verify it from the cited sources, say "I don't know — let me check" and
  ask the user, rather than guessing.
---

## 1. Top-level apps and their roles

KiCad 10 ships several integrated apps. The **project manager** (the window that opens when you launch KiCad) is the launcher; the editors can also be opened standalone. [source: https://docs.kicad.org/10.0/en/kicad/kicad.html]

| App | Role | File extension(s) |
| --- | --- | --- |
| **KiCad** (project manager) | Project tree + launcher for editors | `.kicad_pro` |
| **Schematic Editor** (Eeschema) | Schematic capture, ERC, BOM | `.kicad_sch` |
| **PCB Editor** (Pcbnew) | Board layout, routing, DRC | `.kicad_pcb` |
| **Symbol Editor** | Edit `.kicad_sym` symbol libraries | `.kicad_sym` |
| **Footprint Editor** | Edit `.pretty/*.kicad_mod` footprints | `.kicad_mod` |
| **3D Viewer** | View board in 3D (launched from PCB Editor) | — |
| **Drawing Sheet Editor** | Edit title block / page borders | `.kicad_wks` |
| **Gerber Viewer** | Inspect generated Gerbers | — |
| **Plugin and Content Manager** | Install plugins / library bundles | — |

[source: https://docs.kicad.org/10.0/en/kicad/kicad.html]

## 2. Settings / Preferences dialog

On macOS, the settings dialog is opened via **`KiCad → Settings…`** (the label is "Settings", not "Preferences", on every platform including macOS). [source: https://docs.kicad.org/10.0/en/kicad/kicad.html — "On macOS, the preferences are accessed via 'KiCad → Settings…'"]

The dialog is shared across all KiCad apps. Some pages are global; others are tool-specific (only appear when the relevant editor is installed/active).

### Global sections (verified)

| Section | Purpose |
| --- | --- |
| **Common** | General UI and interaction settings |
| **Mouse and Touchpad** | Input device configuration |
| **SpaceMouse** | 3D navigation device settings |
| **Hotkeys** | Keyboard shortcut customization (see Section 3 / 4) |
| **Version Control** | Git integration settings |
| **Data Collection** | Crash reporting opt-in |
| **Packages and Updates** | Plugin and library bundle management |
| **Plugins** | API / Python interpreter configuration |
| **Maintenance** | Cache and dialog reset options |

[source: https://docs.kicad.org/10.0/en/kicad/kicad.html]

### Tool-specific sections

The KiCad 10 manual states: *"some preferences apply to all tools, and some are specific to a certain tool"* but does not enumerate every PCB Editor / Schematic Editor sub-page in the cited section. [source: https://docs.kicad.org/10.0/en/kicad/kicad.html]

The following sub-pages are referenced elsewhere in the docs and confirmed to exist in KiCad 10. Sub-pages not listed here are `[unverified — couldn't confirm in docs]`:

- **PCB Editor → Grids** — grid list / overrides. Confirmed by AGENTS.md note from this repo's prior verification: *"Grids live in `KiCad → Settings… → PCB Editor → Grids`, not under the View menu."*
- **PCB Editor → Display Options** `[unverified — name plausible but not quoted in fetched docs]`
- **PCB Editor → Editing Options** `[unverified]`
- **PCB Editor → Colors** `[unverified]`
- **Schematic Editor → Field Name Templates** `[unverified — sub-page name not confirmed]`
- **Schematic Editor → Net Inspector** `[unverified — sub-page name not confirmed; the Net Inspector is also a panel, see Section 4]`

> If you need a sub-page name and it's marked unverified above, open Settings in KiCad 10 and read the actual label rather than guessing.

## 3. Schematic Editor (Eeschema)

### Top-level menus

The KiCad 10 schematic editor has these top-level menus: **File**, **Edit**, **View**, **Place**, **Inspect**, **Tools**, **Preferences**, **Window**, **Help**. [source: https://docs.kicad.org/10.0/en/eeschema/eeschema.html]

Specific verified menu items:

- **Edit → Change Symbols…** [source: same]
- **View → Show hidden pins** [source: same]
- **View → Mark items which are excluded from simulation** [source: same]
- **View → Panels → …** — toggles for docked panels (Properties, etc.) [source: same]
- **Inspect → Compare Symbol With Library** [source: same]
- **Tools → Update Symbols from Library…** [source: same]
- **Tools → Edit Symbol Library Links…** [source: same]

A complete menu enumeration is `[unverified — fetched documentation does not list every menu item]`. To get the full list, open the Schematic Editor and read it, or run `Help → List Hotkeys…` (Ctrl+F1).

### Verified default hotkeys

| Key | Action |
| --- | --- |
| `A` | Place symbol |
| `W` | Draw wire |
| `L` | Place local label |
| `H` | Place hierarchical label |
| `J` | Place junction `[unverified — not in fetched excerpt; J is conventional]` |
| `P` | Place power port `[unverified — not in fetched excerpt]` |
| `Q` | Place no-connect flag `[unverified — fetched docs explicitly say "no default hotkey specified"; placement is via right toolbar]` |
| `E` | Edit properties |
| `M` | Move |
| `G` | Drag |
| `R` | Rotate |
| `X` / `Y` | Mirror in X / Y |
| `Ctrl+E` | Edit symbol with Symbol Editor |
| `U` / `V` / `F` | Edit Reference / Value / Footprint field |
| `O` | Autoplace fields |
| `D` | Show datasheet |
| `Ctrl+F1` | Display hotkey list |
| `Esc` | Cancel tool / clear selection |
| `Space` | Reset relative coordinates |
| `Shift+Space` | Cycle line modes |
| `F8` | Update PCB from Schematic `[verified in PCB editor docs as same hotkey across editors]` |

[source: https://docs.kicad.org/10.0/en/eeschema/eeschema.html]

### Label types

Four label kinds, all placed from the right toolbar palette ("Place a local label, directive label, global label, or hierarchical label"). [source: https://docs.kicad.org/10.0/en/eeschema/eeschema.html#labels-and-net-names]

| Label | Scope |
| --- | --- |
| **Local Label** | Connections within one sheet only |
| **Global Label** | Connections anywhere in the schematic, any sheet |
| **Hierarchical Label** | Connection between a subsheet and its parent sheet |
| **Directive Label** (a.k.a. Net Class Directive) | Assigns a net class to an individual net |

[source: same]

### No-connect flag semantics

A no-connect flag means *the designer intentionally left this pin externally unconnected*. It does NOT say anything about the silicon. Two effects: [source: https://docs.kicad.org/10.0/en/eeschema/eeschema.html#no-connect-flag]

1. Suppresses the "unconnected pin" ERC warning for that pin.
2. When two pins are stacked on the same point, adding a no-connect flag forces them onto separate nets instead of being treated as one net.

Placed via the right toolbar (no-connection icon). Default hotkey is `[unverified — docs do not list a default]`.

### Panels (docked)

| Panel | Location | Notes |
| --- | --- | --- |
| **Selection Filter** | Lower-left corner of the editor window | Filters which object types the mouse can select |
| **Hierarchy Navigator** | Docked panel, toggled via left toolbar | Tree of sheets in a hierarchical schematic |
| **Properties Manager** | Docked panel, toggled via left toolbar or `View → Panels → Properties` | Edits properties of the current selection |

[source: https://docs.kicad.org/10.0/en/eeschema/eeschema.html]

### Common operations

| Operation | How to invoke |
| --- | --- |
| Place wire | `W`, or right toolbar |
| Place local / global / hierarchical / directive label | `L` / palette / `H` / palette (right toolbar palette) |
| Place power symbol | Right toolbar (default hotkey `[unverified]`) |
| Place no-connect | Right toolbar |
| Place junction | Right toolbar (default hotkey `[unverified]`) |
| Annotate | `Tools → Annotate Schematic…` `[menu string unverified — name conventional]` |
| ERC | `Inspect → Electrical Rules Checker` `[menu string unverified]` |
| Update PCB from schematic | `Tools → Update PCB from Schematic…` (`F8`) |
| Export netlist | `File → Export → Netlist…` `[menu string unverified]` |
| Edit symbol fields (project-wide) | `Tools → Edit Symbol Fields…` `[menu string unverified]` |
| Find / Replace | `Ctrl+F` / `Ctrl+H` (standard) `[unverified for KiCad 10 specifically]` |

## 4. PCB Editor (Pcbnew)

### Top-level menus

KiCad 10 PCB Editor has top-level menus including **File**, **Edit**, **View**, **Place**, **Route**, **Inspect**, **Tools**, **Preferences**, **Window**, **Help**. A complete item-by-item enumeration is `[unverified — fetched documentation excerpt does not list every menu item]`. Verified items:

- **File → Board Setup…**
- **File → Save As…**
- **View → Flip board view**
- **Tools → Update PCB from Schematic…** (`F8`)
- **Preferences → Hotkeys** (opens hotkey editor)

[source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

> The View menu in the PCB editor does NOT contain a "Grid" entry that opens grid settings — grid management lives in `KiCad → Settings… → PCB Editor → Grids` and the toolbar grid dropdown. (Confirmed by AGENTS.md note from prior repo verification.)

### Verified default hotkeys

| Key | Action |
| --- | --- |
| `n` / `N` | Cycle to the next / previous grid in the list |
| `Ctrl+H` | Cycle through layer display modes (Normal, Dim, Hide) |
| `Space` | Reset relative coordinates to zero |
| `` ` `` (backtick) | Highlight net of selected/hovered copper object |
| `~` (tilde) | Clear net highlighting |
| `` Ctrl+` `` | Toggle net highlighting display on/off |
| `U` | Expand selection to connected copper items |
| `Ctrl+F1` | Display current hotkey list |
| `F8` | Update PCB from Schematic |
| `Shift+S` | Toggle snapping between all layers vs. current layer only |
| `Ctrl+Tab` | Quick preset switcher (hold Ctrl, press Tab) |
| `Shift+Tab` | Quick viewport switcher (hold Shift, press Tab) |
| `Ctrl` (held) | Disable grid snapping |
| `Shift` (held) | Disable object snapping |

[source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

The KiCad 10 docs note: *"Many actions do not have hotkeys assigned by default, but hotkeys can be assigned or redefined using the hotkey editor."* That means commonly-cited keys like `B` (refill zones), `F5` (recompute ratsnest), `V` (add via), `X` (route track), `6` (differential pair) are conventional from older KiCad versions but **not confirmed as default in KiCad 10** by the cited docs.

| Key | Conventional action | KiCad 10 status |
| --- | --- | --- |
| `B` | Fill all zones / refill zones | `[unverified — not in fetched docs; check Preferences → Hotkeys to confirm]` |
| `F5` | Recompute ratsnest | `[unverified — not in fetched docs]` |
| `V` | Add via while routing | `[unverified — not in fetched docs]` |
| `X` | Route single track | `[unverified — not in fetched docs]` |
| `6` | Route differential pair | `[unverified — not in fetched docs]` |
| `s` | Toggle grid snap | `[unverified — Shift+S verified for layer-snap mode, but plain `s` snap toggle not confirmed]` |

> When in doubt, press **`Ctrl+F1`** in the PCB editor to view the live hotkey list — that is the source of truth on the running install. Do not quote conventional hotkeys to the user as if they were verified defaults.

### Appearance panel (right side)

Three tabs: **Layers**, **Objects**, **Nets**. [source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

**Layers tab.** Each board layer with visibility controls. Active layer shows *"highlighted with an arrow indicator to the left of the color swatch."* Toggle visibility, change colors (requires a custom color theme set in Preferences first). An expandable section below contains layer display options for inactive layers (normal / dimmed / hidden).

**Objects tab.** Like Layers but for graphical object types. *"Some objects have no color setting and ... four types of objects (tracks, vias, pads, and zones) have opacity control sliders."*

**Nets tab.** *"A list of all nets and net classes in the board. Each net has a visibility control that controls the visibility of that net in the ratsnest."* Colors can be assigned to nets and net classes. Net-color application mode: **All**, **Ratsnest**, or **None**.

> **Important caveat — see Section 8 (gotchas).** The eye-icon visibility toggle in the Nets tab does NOT cleanly subtract a single net from the visible ratsnest. The reliable per-net hide is: select a pad/track of that net (or right-click directly on it), then **Net Inspection Tools → Hide Net in Ratsnest**. The inverse is **Show Net in Ratsnest** in the same submenu. [source: KiCad 10 PCB editor right-click menu, observed 2026-05-07; GitLab #7039 for the eye-icon desync]

### Net Inspector panel

In KiCad 10, the Net Inspector is a **docked panel**, not a menu entry under Inspect. Its location and toggle: `[unverified — the fetched docs reference the Net Inspector but do not specify the dock side / toggle path; AGENTS-level guidance from this repo notes it is bottom-docked]`. Open the PCB editor and look for "Net Inspector" in `View → Panels` (or equivalent) to confirm the toggle path.

What it offers (verified): *"Double click a net in the Net Inspector"* highlights it. Right-click on a copper object also exposes **Net Inspection Tools → Highlight Net**. [source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

Column list and right-click action list: `[unverified — fetched documentation does not enumerate them]`.

### Selection Filter panel

Located *"in the lower right corner of the PCB Editor window."* [source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

- **All items** checkbox — shortcut to toggle every other type on/off.
- **Locked items** checkbox — independent; controls whether locked items can be selected at all.
- **Right-click an object type** in the filter to *"quickly change the filter to only allow selecting that type of object."*
- When you keep clicking on a disabled type, the filter *"will visually flash the checkbox for that object type as a reminder."*

### Hide / show ratsnest per net

Two paths exist; only one works as expected.

1. **Select a pad/track of the net (or right-click directly on it) → Net Inspection Tools → Hide Net in Ratsnest** — verified label, observed in KiCad 10. The inverse is **Show Net in Ratsnest** in the same submenu. The Net Inspection Tools submenu also contains **Highlight Net** and **Clear Net Highlighting**. The Show/Hide entries are greyed out unless a copper object on a real net is selected/right-clicked — empty-canvas right-click won't expose them.
2. **Appearance panel → Nets tab → eye icon next to a net** — known to be out of sync with the Net Inspection Tools toggle: the eye-icon state does not match the actual visibility set via the right-click submenu. [source: https://gitlab.com/kicad/code/kicad/-/issues/7039]

Use path 1 when hiding a single net's ratsnest. The eye-icon column is reliable for net **color** settings but not for clean per-net ratsnest hide.

The Appearance panel also has a global **"Net Display Options"** with modes **All / Ratsnest / None** controlling how net colors apply, and ratsnest-display modes for visible-layers vs all-layers `[unverified — exact label strings for the global ratsnest display dropdown not in fetched docs]`.

### Common operations

| Operation | How to invoke |
| --- | --- |
| Place footprint | Right toolbar (Add Footprint) |
| Route track | Right toolbar (Route tracks). Hotkey `[unverified, conventionally X]` |
| Route differential pair | Right toolbar (Route differential pairs). Hotkey `[unverified, conventionally 6]` |
| Add via | Right toolbar (Add vias). Hotkey `[unverified, conventionally V while routing]` |
| Tune length | Right toolbar (Tune length) |
| Edit track widths / net classes | `File → Board Setup… → Net Classes` |
| Add zone (copper pour) | Right toolbar (Add Filled Zone) |
| Refill all zones | Conventional hotkey `B` `[unverified in KiCad 10 docs]`; menu equivalent: `Edit → Fill All Zones` `[menu label unverified]` |
| Recompute ratsnest | Conventional hotkey `F5` `[unverified in KiCad 10 docs]`; AGENTS.md notes the View menu has **`View → Recalculate Ratsnest`** verified for this repo's install |
| Update PCB from schematic | `Tools → Update PCB from Schematic…` (`F8`) |
| Run DRC | `Inspect → Design Rules Checker` `[menu label unverified]` |
| Set design rules | `File → Board Setup…` |
| Set net classes | `File → Board Setup… → Net Classes` |
| Set stackup | `File → Board Setup… → Board Stackup` `[menu label unverified]` |

### Magnetic points / object snap

Object snap (snap to pad / snap to track) is configured in **Settings → PCB Editor**, sub-page name `[unverified — likely "Editing Options" or "Display Options" but not confirmed in fetched docs]`. The `Shift` modifier held while moving disables object snapping; `Ctrl` held disables grid snapping. [source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

## 5. Symbol Editor & Footprint Editor

### Symbol Editor

- Open from project manager (icon in launcher), or from Schematic Editor with `Ctrl+E` while a symbol is selected (edits that symbol).
- Library tables: managed via **`Preferences → Manage Symbol Libraries…`** `[menu label conventional; verified path on macOS is via the same Settings dialog — see global Settings section]`.
- Edits the master `.kicad_sym` library file. Note the two-copy rule (master in `<project>.kicad_sym` and snapshot in the schematic's `lib_symbols` block — see AGENTS.md item 6).

### Footprint Editor

- Open from project manager, or from PCB Editor.
- Library tables: managed via **`Preferences → Manage Footprint Libraries…`** `[menu label conventional]`.
- Edits `.pretty/*.kicad_mod` files.

Both editors have their own preference sub-pages in the Settings dialog (e.g. **Symbol Editor → …**, **Footprint Editor → …**). Specific sub-page names are `[unverified]`.

## 6. Project files

| File | Holds |
| --- | --- |
| `.kicad_pro` | Project settings: net classes, design rules, hidden_nets, layer presets, board setup defaults |
| `.kicad_sch` | Schematic (one file per sheet; root sheet is `<project>.kicad_sch`). S-expression text |
| `.kicad_pcb` | Board layout, tracks, footprints, zones, stackup. S-expression text |
| `.kicad_sym` | Symbol library file (one file holds many symbols) |
| `.pretty/*.kicad_mod` | Footprint library — one footprint per `.kicad_mod` file inside a `.pretty/` directory |
| `fp-lib-table` | Project-local list of footprint libraries |
| `sym-lib-table` | Project-local list of symbol libraries |
| `.kicad_dru` | Custom DRC rules (project-local) |
| `.kicad_wks` | Drawing sheet (title block / page border) |

> `.kicad_sch` and `.kicad_pcb` are S-expression text. They diff in git, but they are **not safely line-mergeable** — a "successful" git merge can produce a structurally broken file. One person per board at a time (per repo AGENTS.md).

## 7. kicad-cli

Verified subcommands available in KiCad 10. Each accepts `-o <path>` (or `--output <path>`) to redirect output. Without `-o`, kicad-cli writes report files to the current working directory. [source: https://docs.kicad.org/10.0/en/cli/cli.html]

```
kicad-cli sch erc            <input.kicad_sch>
kicad-cli sch export netlist <input.kicad_sch>
kicad-cli sch export bom     <input.kicad_sch>
kicad-cli pcb drc            <input.kicad_pcb>
kicad-cli pcb export gerbers <input.kicad_pcb>
kicad-cli pcb export drill   <input.kicad_pcb>
kicad-cli pcb export pos     <input.kicad_pcb>
kicad-cli pcb export step    <input.kicad_pcb>
```

Always pass `-o /tmp/<file>` for ERC/DRC reports so they don't land in the repo. (See repo AGENTS.md workflow item 3.)

## 8. Known UI gotchas / version notes

1. **`KiCad → Settings…`, not "Preferences"** on macOS. The label is "Settings" cross-platform. [source: https://docs.kicad.org/10.0/en/kicad/kicad.html]

2. **Net Inspector is a docked panel, not a menu entry.** Don't tell the user to look under `Inspect` for it. (Toggle path `[unverified]` — confirm in `View → Panels` on the live install.)

3. **Appearance → Nets tab eye-icon column does NOT cleanly hide ratsnest for one net.** Its state does not stay in sync with the per-net hide state. To hide one net's ratsnest, **select a pad/track of that net → right-click → Net Inspection Tools → Hide Net in Ratsnest**. Inverse: **Show Net in Ratsnest** in the same submenu. The Show/Hide entries are greyed out if no net is selected. [source: observed in KiCad 10 right-click menu 2026-05-07; GitLab #7039 for the eye-icon desync]

4. **No grid entry under View in PCB editor.** Grid configuration lives in `KiCad → Settings… → PCB Editor → Grids` and in the toolbar grid dropdown. The View menu does not have a Grid sub-menu. (Per repo AGENTS.md verification.)

5. **`no_connect` markers are about wiring intent, not silicon.** They mean "the designer left this pin externally unconnected on purpose" and (a) silence the ERC unconnected-pin warning, (b) split stacked pins onto separate nets. [source: https://docs.kicad.org/10.0/en/eeschema/eeschema.html#no-connect-flag]

6. **`Ctrl+F1` is the source of truth for hotkeys.** Many actions in the PCB editor have no default hotkey in KiCad 10 — `B`, `F5`, `V`, `X`, `6` are conventional from older versions, not confirmed defaults. Use `Ctrl+F1` to read the live hotkey list. [source: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html]

7. **Two-copy rule for symbols.** Each symbol exists twice: master in `<project>.kicad_sym` and a snapshot in the schematic's `lib_symbols` block. KiCad renders from the snapshot. After editing the master, run **`Tools → Update Symbols from Library…`** in the schematic editor to refresh the snapshot. (Per repo AGENTS.md.)

8. **MCP cache vs direct file edits.** kicad-mcp-pro caches `.kicad_sch` after `kicad_set_project` and silently flushes on the next MCP write. Don't mix MCP writes with direct file edits in one session. (Per repo AGENTS.md item under "Editing KiCad files outside KiCad".)

## Sources

- KiCad 10 Project / Settings — https://docs.kicad.org/10.0/en/kicad/kicad.html
- KiCad 10 Schematic Editor — https://docs.kicad.org/10.0/en/eeschema/eeschema.html
- KiCad 10 Schematic — labels and net names — https://docs.kicad.org/10.0/en/eeschema/eeschema.html#labels-and-net-names
- KiCad 10 Schematic — no-connect flag — https://docs.kicad.org/10.0/en/eeschema/eeschema.html#no-connect-flag
- KiCad 10 PCB Editor — https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html
- KiCad 10 PCB Editor — inspecting a board — https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#inspecting-a-board
- KiCad 10 PCB Editor — routing tracks — https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#routing-tracks
- KiCad 10 kicad-cli — https://docs.kicad.org/10.0/en/cli/cli.html
- GitLab #7039 — Net Tools Hide Net vs Appearance panel eye icon out of sync — https://gitlab.com/kicad/code/kicad/-/issues/7039
- Repo `AGENTS.md` (this repo) — verified macOS labels for `KiCad → Settings…`, `View → Recalculate Ratsnest`, MCP gotchas
