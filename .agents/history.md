<!-- consult selectively — grep, never read in full -->

# History

Append-only log of investigations, decisions, surprising findings, and gotchas. Newest first.

## 2026-05-08 — Stacked-symbol confusion: Reference field vs parent symbol in KiCad GUI

While cleaning up a stray `U02` reference, the user found the symbol via Cmd+F (with hidden-fields search) but couldn't select-and-delete it. Two compounding causes:

1. **Two GND symbols stacked at exactly the same coordinate** `(125.73, 311.15)` — a legacy `kart-medulla:GND` (rotated 270°, with the bogus `Reference: U02`) buried under a standard `power:GND` (rotated 90°). Clicking the GND triangle selects only the top one. Grep for the coordinate (`grep "at <x> <y>" *.kicad_sch`) reveals stacks instantly.
2. **Cmd+F selects the matched property/field, not the parent symbol.** When the match is on a hidden Reference field, the side Properties panel shows `Field` with `Text = U02` and a `Visible` checkbox — that's the reference text, not the symbol. Pressing Delete from there would (try to) delete a reference field, not the symbol. The user's intuition "I thought it was part of the symbol" is right — references *are* parts of symbols — but in the GUI they're a separately-selectable child of the symbol, and selecting the field doesn't promote selection to the parent.

**How to actually delete a buried symbol via its hidden field in KiCad 10:**
- Trick that worked: in the Properties panel, tick **Visible** on the field. The reference text now shows on the canvas, anchored to the parent symbol's origin. You can see *where* the symbol lives (even if its body is overlapped by another symbol's body). Then click the symbol body at that location and Tab-cycle through stacked items, or just delete the now-visible reference's parent.
- Alternative when GUI fights you: close KiCad, surgically delete the symbol block from the .kicad_sch (Mode B per `.agents/kicad-workflow.md`).

**Confirmed safe-to-delete signal for stacked GNDs:** if `grep "at <x> <y>"` shows two power symbols + a junction at the same point, deleting one is a no-op for connectivity — the remaining symbol + junction keep the net intact. Verify with `kicad-cli sch erc` after deletion (no new violations at that coordinate).

In this case the deletion landed cleanly on disk: U02 gone, coord-occurrence count at (125.73, 311.15) dropped 9 → 4 (one full symbol's worth of property positions removed), ERC has 0 new violations at that point.

## 2026-05-07 — Investigated KiCad-AI workflow problems; added workflow doc + guard; tested kicad-sch-api

**Trigger:** Recurring failures in `.agents/error-log.md` (MCP cache clobbering edits, KiCad GUI auto-saving over agent commits, hand-rolled netlist parsers, screenshots-instead-of-MCP loops). User asked for a real fix.

**Root structural finding:** KiCad has no official IPC API for the **schematic editor** as of KiCad 10. PCB has `kicad-python` (works with running KiCad), schematic does not. Every schematic-editing MCP server (kicad-mcp-pro, Seeed-Studio, lamaalrajih, circuit-synth) is doing raw S-expression manipulation. That is the source of all our caching/conflict pain — these are not bugs in any one server, they're a structural limit until KiCad ships schematic IPC (KiCad 11+).

Seeed-Studio docs put it explicitly: *"KiCad must be closed and reopened to see file changes (no hot-reload). Use KiCad GUI for design work. Use this MCP server for analysis, validation, and code generation."* Adopted as our default.

**What was added:**
- `.agents/kicad-workflow.md` — codifies two modes: (A) read-only MCP, KiCad GUI may be open, default 90% of the time; (B) direct-edit, KiCad closed, no MCP writes that session. With tool-selection cheat-sheet.
- `scripts/guard-kicad-write.sh` — `pgrep -i kicad` and `pgrep -fl kicad-mcp-pro` preflight. Exits non-zero if unsafe. Dry-run confirmed.
- AGENTS.md "Editing KiCad files outside KiCad" updated with pointer to the workflow doc.

**kicad-sch-api evaluation (`circuit-synth/kicad-sch-api` v0.5.6):**
- **Read works.** `load_schematic('kart-medulla_P1.kicad_sch')` → 105 components, 141 wires, parses cleanly. Useful as a Python read API.
- **Write does NOT preserve format.** Round-trip test (`/tmp/kicad-sch-api-test/roundtrip.py`) produced large diff: drops `(thickness 0.1524)` from text effects, reorders properties, fills empty `Description ""` fields with library text, etc. Despite claims of "exact format preservation".
- **Reference validator is wrong.** Rejects KiCad-valid power-flag references containing `+` and `_` (`#FLG_+12V01`, `#FLG_+5V_USB01`, `#FLG_+3V3`) as "Invalid reference format". Need to call internal `_file_io_manager.save_schematic(sch._data, path)` to bypass — but the format-preservation issue is separate and worse.
- **Verdict: skip the library entirely.** Writes are broken (format reformat + buggy validator). Reads work, but reads are already covered by `kicad-mcp-pro` (`sch_get_symbols`, `sch_trace_net`, `sch_get_connectivity_graph`, `run_erc`, `export_netlist`) and `kicad-cli sch export netlist` — both already in our toolbox, neither has the MCP-write cache problem since we'd only call read tools. `kicad-sch-api` adds zero value to us. Edit-tool surgical regex remains the only direct-write path (preserves format exactly when changes are tiny). Re-evaluate when KiCad 11 ships schematic IPC.

**PCB side, when we get there:** use `kicad-python` (the official KiCad IPC API). Works with running KiCad GUI, no cache war. Enable in `KiCad → Settings… → Plugins → API server`. https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/



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

## 2026-05-07 — Git workflow: rebase-on-pull when both sides made identical changes to the same file

Situation: peer pushed commit `d0f64d1 "pcb update"` (touched `.kicad_pcb` + 1 line of `.kicad_pro`). Local had uncommitted edits including the **same 1-line change** to `.kicad_pro` (KiCad GUI clears `used_designators` automatically) plus schematic + agent-doc edits.

**Resolution path that worked cleanly:**
1. Commit local work first (split into logical commits) — gives a checkpoint to return to if anything goes wrong.
2. `git pull --rebase` — replays local commits on top of peer's. Identical `.kicad_pro` change auto-resolved with no prompt.
3. Push.

**Why `--rebase` over plain `git pull`:** plain pull creates a merge commit for trivial 1-commit divergences (noisy). Rebase produces linear history `peer → you`. Local commits get new SHAs (parent changed) — safe because they weren't pushed yet. Never rebase already-pushed commits.

**Recovery levers if rebase goes wrong:** `git rebase --abort`, `git reflog` + `git reset --hard <sha>`. Commits are nearly impossible to lose once made.

---

## 2026-05-07 — Decision: stay on KiCad long-term (vs EasyEDA)

Revisited tool choice after MCP-related friction. Decision: **KiCad**, long-term.

Reasoning:
- Open format, local files, git-tracked — work is owned, not hosted on a vendor's servers.
- No vendor lock-in; portable across fabs (not tied to JLCPCB pipeline).
- Scriptable; MCP tooling is improving and recent ERC issues were all resolved within KiCad.
- EasyEDA is fine for quick JLC-bound boards but wrong foundation for hardware meant to live for years.

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
