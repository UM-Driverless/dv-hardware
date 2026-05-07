<!-- consult selectively — grep, never read in full -->

# Error log

Mistakes made and the rules learned from them. Newest first. Grep before working in a related area.

## 2026-05-07 — Conflated "firmware doesn't drive signal" with "signal is not wired" — falsely flagged SELECT_THROTTLE as a missing task

**What happened:** While auditing remaining work on the MAX4660 throttle mux, I grepped `~/repos/kart-medulla` firmware for `SELECT_THROTTLE`. No matches. I then reported to the user: *"SELECT_THROTTLE is currently a dead signal from firmware's perspective ... trace the other end of SELECT_THROTTLE in the schematic — where does it go besides pin 6 of U14?"* — implying the hardware side was incomplete or unknown. User pushed back: "I don't understand why you said it was missing task." When I actually traced the net via netlist, SELECT_THROTTLE was already cleanly wired: U14.6 (mux gate) + R32.1 (10K pull-down to GND, sets safe default) + U23.15 + U23.16 (ESP32 dev-kit header pins). The hardware audit was complete; only the firmware-side GPIO drive is missing.

**Root cause:** I treated "firmware doesn't reference this net name" as evidence that "the schematic side is also incomplete or untraced." Those are different claims. The hardware net can be fully and correctly wired regardless of whether firmware currently uses it. Worse: I had ALREADY generated and read the netlist earlier in the same session (the U14 pin 1–9 audit) and could have queried for SELECT_THROTTLE's other endpoints in seconds. I asked the user to "trace it" instead of doing the trace myself — pushing work onto them when the answer was one MCP/grep call away.

**Prevention rule:**
- **"Net X isn't referenced in firmware" ≠ "Net X is unwired in hardware."** Keep the two audits separate. State each independently: "(hardware) net X has nodes A, B, C; (firmware) net X is/isn't driven by any GPIO." Don't smear them into "X is dead."
- **Before asking the user to trace a net, trace it yourself.** Netlist export + name filter is a 30-second tool call (`kicad-cli sch export netlist` then grep for the net name in the resulting `(net ...)` blocks). Same for the kicad MCP's `sch_trace_net`. The user is not the search index.
- **Match the question to what's actually unknown.** "What firmware GPIO should drive SELECT_THROTTLE?" is a real open question. "Where does SELECT_THROTTLE go on the schematic?" is not — that's already in the file, go look.

**Cross-reference:** `projects/kart-medulla/tasks.md` 2026-05-07 entry "Triple-check MAX4660 (U14) throttle-mux wiring" now correctly states the SELECT_THROTTLE net members and isolates the open question to "which ESP32 GPIO maps to U23 pins 15/16, and update firmware to drive it."

## 2026-05-07 — Invented a confident explanation ("off-grid by one unit") for why the user's fix worked, without checking it fit the actual ERC error text

**What happened:** After user fixed the GND/A0 ERC issue by placing three separate GND power symbols (one per pin) instead of one shared wire, they asked why that worked. I confidently claimed A0's pin was "off-grid by one unit so the wire never actually touched it" — a fabricated mechanism. User pushed back: "the error didn't say it was disconnected." They were right. The ERC message was "Input pin not driven by any Output pins," which is a *net-semantics* rule (net exists but has no Power Output), not a *connectivity* rule (pin floating / not connected — KiCad has separate ERC checks for those with different message text). My explanation didn't fit the evidence; I just sounded sure.

**Root cause:** Pressure to give a clean explanation when the user asked "why did this work" led me to invent a plausible-sounding mechanism rather than say "I don't know." The fabricated detail ("one grid unit") added false specificity that made it sound investigated. Violates the global rule: "Never state as fact what you haven't verified."

**Prevention rule:**
- **When asked "why did X work," if I haven't verified the mechanism, say so explicitly.** "I'd guess X but I haven't confirmed" is fine. Inventing a precise-sounding mechanism is not.
- **Match the explanation to the actual error text.** "Input pin not driven by any Output pins" ≠ "Pin not connected" ≠ "Floating pin." If my explanation contradicts the message the user is staring at, the user will (correctly) reject it.
- **Confident wrong answers are worse than uncertain ones** — the user can audit my reasoning when I show uncertainty; they can't audit a fabricated detail.

**Cross-reference:** `.agents/history.md` 2026-05-07 entry, "Why three-symbols-works..." section now flagged as unverified hypothesis.

## 2026-05-07 — Made user re-explain the same KiCad ERC issue 8+ times instead of inspecting the schematic via MCP

**What happened:** User had ERC error "Input pin not driven by any Output pins" on PCF8574 A0 in kart-medulla. I went through ~8 rounds of guesses (wire floating, missing junction, wrong label type, missing PWR_FLAG, wrong power symbol shape, two PWR_FLAGs, pin not snapped) without ever opening the schematic file or invoking the kicad MCP. Each round added a new wrong instruction the user had to act on before correcting me. User got progressively more frustrated ("are you blind?", "I want GND!!!", "you're asking the same things over and over"). When I finally used the MCP (`grep PWR_FLAG`, `mcp__kicad__run_erc`), it took two tool calls to find the actual answer: only one PWR_FLAG exists on disk (`#FLG01` at known coords), saved schematic passes ERC, and the duplicate-PWR_FLAG error was from the user's own newly-added flag in the unsaved GUI state.

**Root cause:** I treated the user's screenshots as the only source of truth and reasoned from images, when the schematic file is plain text on disk and a kicad MCP is connected. Iterating-from-screenshots is high-latency and low-fidelity — every wrong guess costs a real schematic edit by the user.

**Prevention rule:**
- **For any KiCad debugging session: read the schematic file or use the kicad MCP first.** `grep PWR_FLAG`, `mcp__kicad__run_erc`, and `mcp__kicad__sch_get_symbols` are one tool call each and answer most "what's actually on this net" questions definitively.
- **The MCP reads disk. The user's GUI may be unsaved.** If MCP results disagree with what the user reports, the gap is unsaved GUI state — say so directly, don't loop on guesses.
- **Stop iterating "try this, did that work?" past 2 rounds.** If two suggestions don't fix it, switch to inspecting the actual file. The user shouldn't be the debug loop.
- **KiCad ERC drive rules (do not re-derive every time):** Power Input pins (GND/+3V3 power-symbol pins, IC power pins) do NOT drive a net. Need exactly one PWR_FLAG per power net across the whole design. Global labels named "GND" do not merge with the GND power-symbol net — only power symbols join the global power net. See `.agents/history.md` 2026-05-07 entry for full breakdown.

**Cross-reference:** `.agents/history.md` "KiCad ERC: Input pin not driven on GND net" 2026-05-07.

## 2026-05-07 — Said "Preferences" instead of "Settings" for KiCad menus (recurring)

**What happened:** User asked how to fix the wild trackpad zoom in KiCad. I said "Preferences → Preferences → Mouse and Touchpad". User corrected: it's `KiCad → Settings…`, not Preferences. This is a *recurring* mistake — user said "for the 100th time."

**Root cause:** I default to the macOS-typical "Preferences" wording from training data and don't verify against the actual KiCad menu. KiCad uses "Settings" cross-platform regardless of macOS conventions.

**Prevention rule:**
- **KiCad menu name is "Settings", not "Preferences".** Path is `KiCad → Settings…` on macOS, same on Linux/Windows.
- More generally: when telling the user a menu path, do not paraphrase or translate to platform conventions — use the literal label as it appears. If uncertain, say "the menu that does X" and let the user find it.
- Cross-reference: `AGENTS.md` "KiCad UI menu names" section.

## 2026-05-07 — Forgot session context mid-conversation: re-suggested keeping RGB bridge open after user already established they want the LED, ignored the just-completed TX0/RX0 cleanup precedent

**What happened:** Same session as the +5V_USB error. After finally getting the netlist right via MCP, I told the user: (a) "GPIO38 carries TX1, keep RGB bridge open and use IO17 in firmware" — i.e., **give up the LED to keep TX1**. The user pushed back: "what if I want to use the freaking LED, do we have not enough pins?" I flipped the answer to "you can use the LED, just un-short pin 20 from TX1." User then asked what TX1 even is. After I explained it's UART1, exposed on the connector but not used internally, the user said "but we agreed we didn't want that pin, UART is already in the USB connector, it shouldn't even be there." That's the same logic the user applied two commits ago (`b07c56f`: NC pins 20/21 UART0 because USB-Serial covers it). UART1 has the same status — dead silkscreen on this board. The cleanup should have been the obvious first suggestion, not something the user had to drag out of me through three contradictory answers.

**Root cause:** I treated each user message as fresh context and re-derived advice from the netlist alone, ignoring (a) the user's stated goal (use the LED — that means GPIO38 must be free, period), (b) the conversation's just-established cleanup pattern (NC unused pins on the breakout connector when their function is already covered by USB-Serial), (c) the project history visible in `git log` (the b07c56f commit literally NC'd UART0 pins for the same reason). I kept hedging with "use IO17 in firmware" / "keep bridge open" — neither of which the user asked for, both of which contradicted the user's explicit aim. When the user said "what the fuck are you saying about not using the led as a solution," that was the third correction in a row of the same shape: *I keep proposing "work around the conflict in software" when the user wants "remove the conflict from the schematic."*

**Prevention rule:**
- **Lock onto the user's stated goal at the top of the answer and don't drift.** If the user says "I want the LED to work," every subsequent suggestion must be evaluated against "does this make the LED work?" — software workarounds that leave the bridge open fail this test and shouldn't be offered.
- **Read recent commits before giving design advice.** `git log --oneline -10` takes one second and reveals patterns like "we just NC'd UART0 because USB-Serial covers it." UART1 has the same status — same fix. The user's prior decisions are the strongest design-intent signal in the repo.
- **When a net's only nodes are on the breakout connector itself (no internal consumer), default to "delete this net, NC the pins."** Don't propose firmware workarounds for nets that don't need to exist.
- **Stop suggesting firmware GPIO-matrix remaps as a "solution" to schematic conflicts.** They're rarely what the user wants; they shift complexity from PCB (one-time fix) to firmware (forever caveat). Only mention if the user explicitly asks about firmware-side options.

**Cross-reference:** Commit `b07c56f` ("kart-medulla: NC pins 20/21 (UART0 TX0/RX0)") is the precedent. UART1 (pairs 19/20, 21/22) gets the same treatment.

## 2026-05-07 — Recommended a "free" ESP32 GPIO that was actually the +5V_USB power pin

**What happened:** User asked which header pins on U23 (SSW-122-01-T-D socket for the ESP32-S3-DevKitC-1) are free so SDC could move off GPIO38 (v1.1 onboard RGB LED). I wrote a Python script to map U23 symbol pins → nets by parsing wires + labels, then cross-referenced against the Espressif J1/J3 pinout to claim "header pin 41 = GPIO13 is the only fully unused pin — use it for SDC." User caught it: pin 41 actually has `+5V_USB`. Two compounding mistakes:
1. **Script only matched `(label …)`, `(global_label …)`, `(hierarchical_label …)`** — completely missed power symbols (`+5V_USB`, `+5V_REG`, `GND` placed as `(symbol (lib_id "kart-medulla:+5V_USB") …)`). So any pin connected only to a power rail looked "empty."
2. **J1↔J3 row mapping (odd↔even pins of the dual-row Samtec connector) was guessed without verification.** Pin numbering direction (top-down vs bottom-up of the devkit) and which row maps to odd vs even symbol pins were both assumed. Output was off by at least one slot, and possibly fully inverted — which is why the same script also showed every odd-column pin as empty (almost certainly wrong; J1 carries 3V3/EN/many IOs).

In addition: my BFS over wire endpoints jumped through coincident-Y pin connection points across the symbol body, so paired odd/even pins kept reporting the same net. I noticed the artifact ("pin 19 and pin 20 both show TX1") but rationalized it instead of fixing the algorithm before recommending a pin.

**Root cause:** Trusted a hand-rolled netlist extractor over actually verifying. Three things should have stopped me: (a) every odd pin showing as empty is a screaming red flag — J1 cannot be entirely unconnected on a working board; (b) labels colliding on adjacent pins should have triggered an algorithm review, not a caveat in prose; (c) I never cross-checked that *known* power pins (5V, GND, 3V3) showed up correctly — that one sanity check would have exposed the missing power-symbol parser instantly.

**Prevention rule:**
- **For schematic netlist questions, do not roll your own parser from .kicad_sch text.** Use `mcp__kicad__sch_get_connectivity_graph`, `sch_trace_net`, `sch_get_labels`, `pcb_get_nets`, or export the netlist via `export_netlist` and read that. KiCad's tools already handle power symbols, junctions, hierarchical labels, bus entries, and global/local label scoping — none of which a regex pass handles correctly.
- **Before recommending any pin/net assignment, sanity-check against known anchors.** Power pins (5V, 3V3, GND) and the strapping pins should appear where the datasheet says. If they don't, the extractor is wrong — stop and fix it before giving advice.
- **"Every pin in row X is empty" is never a real result on a populated devkit socket.** Treat suspicious uniformity as a bug in the analysis, not a feature of the design.
- **Never claim a pin number using "the schematic's nomenclature" without stating which nomenclature.** Symbol pin numbers (1-44 on SSW-122-01-T-D), Espressif silkscreen labels (GPIO numbers), and physical row positions are three different things; mixing them silently is how this happened.

## 2026-05-07 — Mixed kicad-mcp-pro writes with direct file edits; MCP cache wiped my edits twice

**What happened:** Working on `kart-medulla_P1.kicad_sch` to remove `TX0`/`RX0` global labels (header pins 20/21, UART0) and add NC markers + text. The MCP profile lacked `sch_delete_label`, so I direct-edited the file with the Edit tool to remove the labels and their wires. Then I called `mcp__kicad__sch_add_no_connect` twice to add the NC markers — the MCP reported success, but a later `git status` showed zero changes. KiCad was *closed*; the culprit was the MCP server, which had cached the schematic in memory after `kicad_set_project` and flushed its cached copy (still containing the old labels/wires) on the next write call, silently overwriting my Edit-tool deletions. Re-did everything via direct file edit only, no further MCP calls — that worked.

**Root cause:** I treated the kicad-mcp-pro server as stateless, like a wrapper that reads the file each time. It isn't. It loads the schematic into memory at `kicad_set_project` and writes from that memory model on the next mutating call. Direct file edits made in between are invisible to the MCP and get clobbered.

**Prevention rule:**
- **Pick one workflow per session: pure-MCP or pure-file-edit. Never interleave.** If the MCP profile is missing a tool you need (e.g. `sch_delete_label`, `sch_add_text` are gaps in `agent_full`), do the *entire* edit via the Edit tool — and do not call any MCP write tools (including `sch_reload`, possibly `run_erc`) until after the user has reopened the file in KiCad and re-saved it (which lets the MCP re-cache the on-disk state).
- KiCad open in the GUI is **not** the same threat — KiCad only writes on explicit save, so direct-edit + File → Revert works. The MCP is the silent overwriter.
- After direct edits, verify the diff stuck: `cd ~/repos/dv-hardware && git status projects/<board>/`. Zero changes = something silently reverted; investigate before continuing.

**Cross-reference:** `history.md` 2026-05-07 entry has the full incident in context (symlinking `kicad-cli`, choosing `kicad-mcp-pro` over alternatives, the actual schematic change applied as commit `b07c56f`).

## 2026-05-07 — Edited KiCad files while KiCad had them open; auto-save reverted my changes

**What happened:** Edited `kart-medulla_P1.kicad_sch` to fix the U14 cached symbol pin 2 type, footprint property, datasheet URL, and a wire endpoint. Committed and pushed (ded1933). Later in the session, the user installed the KiCad MCP server and asked me to verify the symbol via MCP. When I queried via MCP, U14 showed the OLD footprint (`UMAX-8_…`) — not my fix. Investigation showed all four edits were silently reverted in the working tree: KiCad must have been open with a stale in-memory copy of the schematic; some action (MCP attach, file-watch, autosave) caused KiCad to flush its in-memory state to disk, overwriting the committed-correct file. Discovered only because the MCP showed the old footprint string. The library file (`kart-medulla.kicad_sym`) was not affected because KiCad didn't have it open in the symbol editor.

**Recovery:** `git checkout HEAD -- projects/kart-medulla/kart-medulla_P1.kicad_sch` restored the committed-correct version. ERC clean, no re-edit needed.

**Prevention rule:** **Before editing any `.kicad_sch`, `.kicad_pcb`, or `.kicad_sym` file from outside KiCad, confirm KiCad is closed.** If a session has been long, the user may have opened KiCad without saying so. Ask, or check via `pgrep -i kicad` / `osascript -e 'tell app "KiCad" to running'`. After committing KiCad-file changes, also re-verify the on-disk content matches the commit before claiming the work is done — KiCad-stale-save can revert silently between commit and the next interaction.

**Also:** When verifying via a separate tool (MCP, kicad-cli, manual grep) shows different content than expected after a "successful" edit+commit, **the file may have been clobbered post-commit** — check `git diff HEAD` before assuming the verification tool is wrong.

## 2026-05-07 — Built a "scary catastrophe" finding from an unverified WebSearch snippet

**What happened:** When evaluating the MAX4660 (U14) symbol, I asked WebSearch for the datasheet pinout. The result included a fragment "`IN N.C. V+ 1 2 8 7 NO V- NC GND COM TOP VIEW 3 4 6 5`" — a position-list snippet from the datasheet caption — which the search model interpreted as `1=IN 2=N.C. 3=GND 4=COM 5=NC 6=V- 7=NO 8=V+`. I took that as verified ground truth and produced a detailed "everything is wired wrong, this would damage the chip" table comparing it to the project's symbol. When the user later downloaded the SnapEDA-verified symbol, its pin numbers matched the project's original (`1=COM 2=NC 3=GND 4=V+ 5=NC 6=IN 7=V- 8=NO`) — meaning my "verified pinout" was a misdecoded snippet and the alarm was false.

**Root cause:** I treated a search-engine-summarized text snippet as authoritative for a precise technical claim (pin number → name mapping) without fetching the actual datasheet PDF or cross-checking against any other source. Pinout decoded from a position-list caption requires careful spatial reconstruction that an LLM summarizer is likely to get wrong. Then I escalated rhetorically ("catastrophic", "would damage the chip") on top of that unverified base.

**Prevention rule:** **Never present a pinout, register map, or other precise technical mapping as verified fact based on a single WebSearch snippet.** Either (a) fetch the actual datasheet PDF and read it, (b) cross-check with at least one other independent source (vendor symbol, SnapEDA-verified part, KiCad official lib), or (c) hedge clearly: "based on a search snippet — needs datasheet confirmation". When multiple existing sources (e.g. the project's converted symbol + a vendor verified symbol) agree against a single search snippet, treat the snippet as wrong.

**Also:** Don't escalate to alarming language ("catastrophic", "chip damage", "would not function") on top of unverified premises. Match emotional weight to evidence weight. A measured "the symbol's electrical types are wrong; pin numbers should also be cross-checked against the datasheet" would have been correct and proportionate.

## 2026-05-07 — Invented a "funnel icon" that doesn't exist in KiCad's UI

**What happened:** When the user asked where to find the wires-only selection filter in KiCad 10.0.1 schematic editor, I described it as the "funnel/filter icon" on the left toolbar. There is no funnel icon. The control is a panel at the bottom-left titled literally "Selection Filter" with checkboxes (All items, Symbols, Wires, Labels, Pins, Graphics, Text, Images, Rule Areas, Other items). When the user pushed back and shared a screenshot, I doubled down on the existing answer instead of acknowledging the funnel claim was made up.

**Root cause:** I generated a plausible-sounding UI affordance from priors about other tools (filter funnels are common in spreadsheets/databases) without verifying KiCad's actual UI. Then when corrected, I papered over the invention with a new description rather than retracting it explicitly.

**Prevention rule:** When describing UI elements I haven't directly observed, either (a) ask the user what they see, or (b) hedge with "look for a panel/menu labeled X" rather than naming an icon shape. **When the user catches an invented detail, retract it explicitly** — say "you're right, I made that up" — don't silently rewrite the description and move on. Silent rewrites feel dismissive and erode trust.

## 2026-05-04 — Overconfident "gerber-ready" claim missed broken nets disguised as `isolated_pin_label`

**What happened:** I declared the schematic "gerber-ready, 0 errors, 38 warnings, all in geometric/documentation categories." The user called it out: of the 11 `isolated_pin_label` warnings, two were broken nets — `STEER_SDA__I2C` and `STEER_SCL__I2C` were old names left over from a bus rename. The I2C bus had been renamed to `SDA__I2C`/`SCL__I2C`, but the connector CN4 labels were never updated. Result: the steering sensor was *not actually wired* to the I2C bus — a real PCB-breaking design defect, not a "legitimate one-pin board-exit signal" as I had blithely categorized it.

**Root cause:** I treated `isolated_pin_label` as a uniform category and assumed all 11 instances were spare/test signals without verifying any of them. I didn't grep for each label name to confirm whether it had a matching counterpart elsewhere, which is the only way to distinguish "intentional one-pin signal exiting the board" from "rename mistake that orphaned the net."

**Prevention rule:** Before classifying any `isolated_pin_label` as legitimate, **grep for the label name across the schematic and confirm no matching label exists elsewhere — OR if it does exist, confirm that the matching label is the truly-connected partner.** A single-instance label with a name that *looks like* a bus signal (I2C, SPI, USB, etc.) is suspect; bus signals always have multiple participants, so a one-pin bus label almost certainly indicates a typo, rename mistake, or missing wire.

**Also:** Don't use phrases like "gerber-ready" or "schematic is correct" without explicit verification. They imply a level of confidence that I haven't earned by spot-checking. Better framing: "ERC clean of errors; warnings remain — check each before declaring done." The user pointed out that the schematic isn't even fully designed yet — the PCB layout hasn't started — so "gerber-ready" was doubly wrong.

## 2026-05-04 — Misrepresented no_connect marker semantics (RECURRENCE)

**What happened:** When the user asked whether to use `(no_connect)` markers on the unused half of a dual LM358 op-amp (pins 5/6/7), I claimed NC was reserved for pins that "don't physically exist on the package" and recommended tie-back wiring as the only correct option. The user corrected me: NC simply means "designer intentionally left this pin externally unconnected on this board" — it has nothing to do with whether the silicon pin exists. ERC docs confirm.

**This is the SECOND time** the user had to explain this. First time was earlier in the same project; I fell into the same false framing again.

**Root cause:** I conflated two separate KiCad concepts and inferred a stronger semantic than the docs actually give:
1. The schematic-level `(no_connect)` marker — board-specific designer intent. Says "I'm not wiring this pin." That's all.
2. The symbol-pin electrical type `no_connect` — part-designer intent, used in symbol definitions for pads the manufacturer designates as NC.

I treated (1) as if it implied (2), which led me to advise the user that NC was wrong for "real-but-unused" pins. It isn't.

**Prevention rule:**
- When asked about `no_connect` / NC markers in any KiCad context, the default answer is: **"It declares the designer intentionally left this pin externally unconnected on this board, and silences ERC's pin_not_connected warning. That's it."**
- Do not introduce silicon-level claims unless the user explicitly asks about manufacturer NC pads.
- For unused op-amp halves specifically: NC markers are valid AND tie-back wiring is the better analog practice. Present both, don't dismiss NC as "wrong."
- Cross-reference: `history.md` 2026-05-04 entry has the docs quote and the correction.

**Verification:** KiCad master docs, eeschema chapter — "No-connection flags are used to indicate that a pin is intentionally unconnected. These flags prevent 'unconnected pin' ERC warnings for pins that are intentionally unconnected." (https://docs.kicad.org/master/en/eeschema/eeschema.html)
