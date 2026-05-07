<!-- reference — read when relevant -->

# KiCad agent workflow

How agents should interact with KiCad project files in this repo. Codifies the rules that the error-log keeps catching us violating.

## Why this file exists

KiCad has **no official IPC API for the schematic editor** as of KiCad 10. The PCB editor has one (kicad-python / IPC API), the schematic editor does not. Every schematic-editing MCP server (kicad-mcp-pro, Seeed-Studio, lamaalrajih, circuit-synth) does **raw S-expression file manipulation** under the hood. That is the structural reason for our recurring failure modes:

- MCP in-memory cache silently overwrites direct file edits
- KiCad GUI auto-save reverts agent commits
- Off-grid placements on 1.27 mm devkit pins
- Tool gaps (`sch_delete_label`, `sch_add_text`) in `agent_full` profile

Upstream (Seeed-Studio) says it plainly: *"KiCad must be closed and reopened to see file changes (no hot-reload). Use KiCad GUI for design work. Use this MCP server for analysis, validation, and code generation."* This file is that rule, written for our repo.

## The two modes — pick one per session

### Mode A: read-only MCP (default — use this 90% of the time)

KiCad GUI may be open. Agent uses MCP **for reads and validation only**. No writes from agent.

Allowed MCP calls:
- `run_erc`, `run_drc`
- `sch_get_symbols`, `sch_get_labels`, `sch_get_wires`, `sch_get_pin_positions`, `sch_trace_net`, `sch_get_connectivity_graph`, `sch_get_net_names`
- `pcb_get_nets`, `pcb_get_footprints`, `pcb_get_tracks`, `pcb_get_ratsnest`
- `export_netlist`, `export_bom`, `validate_design`, `validate_footprints_vs_schematic`
- All `lib_*` reads, all `project_*` reads

Forbidden in Mode A:
- Any `sch_add_*` / `sch_delete_*` / `sch_update_*` / `sch_move_*` / `sch_swap_*`
- Any `pcb_add_*` / `pcb_delete_*` / `pcb_move_*` / `pcb_set_*`
- Any `Edit` / `Write` against `.kicad_sch` / `.kicad_pcb` / `.kicad_sym` / `.kicad_pro`

If the user wants a change, agent **describes** the change and the user makes it in the GUI. Then agent re-runs ERC/DRC to verify.

### Mode B: direct-edit, KiCad closed

Use only when the user explicitly approves, KiCad GUI is **closed**, and the kicad-mcp-pro process is also stopped (or only used for read-back after a fresh `kicad_set_project`).

Preflight (run `scripts/guard-kicad-write.sh` — exits non-zero if unsafe):
```bash
pgrep -i kicad   # must be empty
pgrep -fl kicad-mcp-pro   # must be empty, OR accept that next MCP write will clobber
```

Workflow:
1. Run guard. Abort if it fails.
2. Edit `.kicad_sch` via `Edit` / `Write` tool, or via `kicad-sch-api` Python script.
3. `kicad-cli sch erc -o /tmp/erc.rpt projects/<board>/<board>.kicad_sch` — confirm valid.
4. `git add` + `git commit` immediately.
5. `git diff HEAD -- projects/<board>/` — must be empty. If not, something reverted; investigate.
6. Tell the user "ready to reopen in KiCad."

**Do not interleave MCP writes and direct edits in the same session.** Pick one and stick to it. The MCP cache will clobber direct edits silently — no error, just a clean `git status` where your changes used to be.

## Tool selection cheat-sheet

| Question | Right tool |
|---|---|
| What's on net X? | `mcp__kicad__sch_trace_net` or `kicad-cli sch export netlist` + grep |
| Does this PWR_FLAG exist? | `grep PWR_FLAG projects/<board>/*.kicad_sch` (file-on-disk truth) |
| Are there ERC errors? | `mcp__kicad__run_erc` or `kicad-cli sch erc -o /tmp/x.rpt …` |
| What pins does this symbol have? | `mcp__kicad__sch_get_pin_positions` |
| Pin → net mapping for a whole symbol | Export netlist, parse the `(net …)` blocks. Do **not** roll your own S-expr parser (see error-log 2026-05-07 "Recommended a 'free' ESP32 GPIO"). |
| Footprint correct? | `mcp__kicad__validate_footprints_vs_schematic` |
| What's actually saved on disk vs. GUI state? | Disk wins — read the file. The GUI may have unsaved state that disagrees. |

## When MCP results disagree with the GUI

The MCP reads disk. KiCad GUI may have unsaved changes. If they disagree:
- Tell the user: "MCP shows X on disk, your GUI may have unsaved changes — save in KiCad and I'll re-check."
- Do **not** loop on guesses. Do not write to "fix" the disagreement.

## PCB-side: prefer the IPC API

When we get to PCB layout, the official KiCad IPC API + `kicad-python` works **with** a running KiCad GUI — no cache war, because edits go through KiCad's own model. Enable: `KiCad → Settings… → Plugins → API server`. See https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/ . Schematic editor is not yet covered by IPC; revisit when KiCad 11 ships.

## Cross-references

- `AGENTS.md` "Editing KiCad files outside KiCad" — short rules
- `.agents/error-log.md` — every recurrence of the failures this file is meant to prevent
- `scripts/guard-kicad-write.sh` — pre-write safety check
