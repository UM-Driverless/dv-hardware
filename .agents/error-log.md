<!-- consult selectively — grep, never read in full -->

# Error log

Mistakes made and the rules learned from them. Newest first. Grep before working in a related area.

## 2026-05-09 — Repeatedly misread the user's silkscreen-layout request (Claude Opus 4.7)

User asked for silkscreen text listing CN1–CN10 pin signals, then iterated on layout: "single long line", "not vertical, horizontal", "in 1 row not 2", "the example pattern continuing". I kept misinterpreting:
- "single long line" → I gave one line *per CN* instead of one block.
- "horizontal" → I lectured about pin-pitch alignment instead of just continuing the example layout the user had pasted.
- "1 row" → I delivered two rows of 5 CNs (because I'd just done 5+5 the previous turn).

Each correction took another full turn. User: "why do you have so many understanding issues lately?"

**Prevention:**
- When the user pastes an **example layout** and says "this pattern, continuing", treat the example as a literal template. Match column count, separator style, spacing. Do not re-invent the format.
- When the user says "single", "one", "1" about a structural property (one row, one line, one column), that is a *count*, not a vibe — count the output before sending.
- Don't editorialize ("text is stroke-font, alignment is fiddly…") when the user has asked for a layout. Deliver the layout; mention caveats only if asked.
- Read the user's latest message twice before responding when they've just corrected the same artifact more than once.

## 2026-05-09 — Invented a rule from a singular noun in third-party docs (AISLER logo layer)

While documenting the AISLER sponsor-logo placeholder task, paraphrased the AISLER community doc's "the desired silkscreen layer" (singular) into "F.Silkscreen *or* B.Silkscreen — designer's choice", framing it as if AISLER required picking only one side. The doc never said that — it said "Place as many placeholders as you want", which strongly implies multiple are fine. User caught it: "why did you invent that rule?"

**Prevention:**
- When paraphrasing third-party docs into a task, **quote the exact phrasing** for any constraint, then add an interpretation only if clearly labeled as such ("interpreting this as…").
- Singular nouns in English ("the desired layer") do not imply exclusivity. Don't translate them into restrictive disjunctions.
- For any "you must / you can only" rule sourced from a webpage you read once, link the source URL right next to the rule, so future-you can re-check rather than trust the paraphrase.

## 2026-05-08 — Repeated common-sense lapses across the session

Patterns the user kept having to correct in this session:
- Gave the bare label `HOLD` when asked "what to put in pin 14" — user already established earlier in the same conversation that they wanted the full annotation `HOLD — <reason>`. Had to be told twice in a row.
- Wrote `Noted` without actually noting (no file edit). User said "don't say Noted if you didn't note it."
- Shortened net names (`SDA` instead of `SDA__I2C`) in chat. User said this is how naming drifts.
- Suggested using `SPARE` GPIOs as if they were free-to-grab when SPARE meant "kept free intentionally."
- Suggested deleting power symbols without checking what chips they were feeding.
- Verbose multi-paragraph answers when user asked for one line.

**Rule:** when the user has just established a preference (full-line explanations, exact net names, terse output, no narration), carry it forward for the rest of the session. Don't snap back to defaults at the next turn.

## 2026-05-08 — Overcomplicated git advice for peer pcb-conflict

Peer had local pcb edits and couldn't pull. I led with stash + checkout-theirs + stash-drop, then escalated to fetch + reset-hard. Actual fix: `git pull` worked.

**Rule:** start with the simplest command. Only suggest stash / reset / force-with-lease if the simple path actually fails.

## 2026-05-08 — Used shortened net names ("SDA", "SCL") instead of the exact schematic names ("SDA__I2C", "SCL__I2C")

**What happened:** While proposing CN swaps, I wrote `SDA` and `SCL` instead of the exact existing schematic net names `SDA__I2C` and `SCL__I2C`. User pushed back: shortening net names in chat is exactly how naming drifts into the schematic and creates duplicate / mismatched nets.

**Prevention rule:** When discussing or proposing edits to *existing* nets, always quote the exact name as it appears in the schematic — including voltage/protocol suffixes (`__5V`, `__3V3`, `__0_5V`, `__I2C`, etc.). Never paraphrase a net name for brevity. If unsure of the exact form, grep the schematic before writing it. Cross-reference: 2026-05-08 "Bulk-renamed 30 CN labels" entry — same family of mistake (treating net naming as cosmetic instead of identity-bearing).

## 2026-05-08 — Confidently named the wrong KiCad layer for a grey overlay hiding pad silk text

**What happened:** User showed a PCB screenshot where grey rectangles on top of each pad were obscuring the silkscreen signal names. I told them it was `F.Fab` and to toggle that layer off. The actual layer was `User.Drawings`. I guessed based on "grey = F.Fab default" without verifying.

**Prevention rule:** When the user shows a layer-visibility issue, don't pattern-match on default colors. The correct approach: ask which layer it is, or list the candidate layers (`F.Fab`, `User.Drawings`, `User.Comments`, `Margin`, `Eco1.User`, `Eco2.User`) and have the user click each off in turn. Default colors are user-customizable; the same grey could be any of these.

## 2026-05-08 — Bulk-renamed 30 CN labels without auditing what each signal was for (kart-medulla CN1–CN10 rewire)

**What happened:** User asked to reassign CN1–CN10 pins so each connector pin sits next to its ESP32 GPIO (minimize jumper length). I produced a target table from the *intended* layout and rewired 30 nets in one Python pass over `kart-medulla_P1.kicad_sch`. Multiple compounding mistakes:

1. **Trusted `pinout-esp32-s3.md` over the schematic.** The doc listed `SDC_NOT_EMERGENCY` as Digital In and a separate `SDC_ENABLE` on GPIO 39. The schematic actually has GPIO 38 driving Q3's gate (Digital Out) and no `SDC_ENABLE` net at all. I propagated the doc's wrong info into the new CN assignment. Exposed `SDC_NOT_EMERGENCY` (an internal-only ESP32→Q3-gate net) on CN4.1 and invented `SDC_ENABLE` on CN4.2 as a label that connects to nothing.
2. **Renamed `REVERSE_WIRE` off CN8.1 without checking it was a real external output.** That label was the medulla's path for the PCF8574-driven reverse signal to reach the kart electronics. After the rename it became orphan. The kart-side reverse output is now disconnected.
3. **Falsely claimed `MANUAL_THR` was missing.** I asserted the MAX4660 NC pin (manual throttle source) was floating, escalated it as a critical pre-fab bug ("very bad, kart manual mode wouldn't work"), and got the user to wire a fake `MANUAL_THR` / `PEDAL_THR` net to CN4.1. A later netlist audit showed U14 pin 2 was **already** wired to `PEDAL_ACC__0_5V` — same pedal net the ESP32 ADC reads, branched internally to the mux. The schematic was correct; I had misread the netlist. The CN4.1 churn (PEDAL_THR → REVERSE_WIRE) was caused by my false alarm, not a real bug. Net result: REVERSE_WIRE *did* end up on CN4.1 (which was a real fix for the orphan caused by my CN8.1 rename), but the path there was driven by a fabricated emergency.
4. **Floating-point comparison bug** in the Python BFS that traced wire endpoints. Pin coordinates computed as `cy ± 2.54` produced values like `63.50000000000001` that didn't `==`-match the wire's `63.5`. Six pins were misclassified as "no existing label" and got duplicate labels added — would have been silent shorts on those nets if not caught by netlist verification.
5. **Recommended deleting power symbols without checking what they powered.** Told the user to delete `+3V3` / `GND` / `+12V` / `PWR_FLAG` symbols at CN-pin coordinates to clear conflicts. Some of those were the *only* feeders for U5 (level shifter VCC) and U1 — caused new ERC errors. Should have grepped first to confirm the rail had another feeder before recommending removal.

**Root cause (overall):** Treated the rewire as a *cosmetic* relabeling problem when it was actually a *semantic* problem about what each signal does, where it comes from, and where it has to go. The geometric optimization was easy; the audit-each-net-for-correctness step was skipped.

**Prevention rules:**
- **Schematic is the source of truth, not derived docs.** Before reasoning about any net, grep the schematic for that net name and follow the wires. Don't quote the pinout doc as authoritative — confirm against `kart-medulla_P1.kicad_sch` first. The pinout doc's job is to mirror the schematic; it's allowed to be stale.
- **For every signal being moved or renamed: identify (a) what's the source, (b) what's the load, (c) is it internal-only or external.** Internal nets (e.g., GPIO→transistor-gate) must NOT land on a CN. External nets removed from a CN MUST be re-homed somewhere or the kart-side function breaks.
- **Audit by chip-pin, not by wire.** Before mass schematic edits, walk every IC's pins (especially mux NC inputs, regulator outputs, transistor gates) and confirm each has a defined source/sink. A floating mux input is a silent failure that ERC won't flag.
- **Never use `==` on KiCad coordinates.** Always epsilon-compare (`abs(a-b) < 0.01`). Symbol pin offsets accumulate float error fast.
- **Before recommending deletion of any power symbol, grep for the rail name and count how many power symbols of that name exist in the same sheet.** If the count would drop to zero on a rail that has chip VCC pins, don't recommend deletion — recommend *moving* instead.

**Cross-reference:** the entire `2026-05-08` history.md "kart-medulla CN1–CN10 pin assignments" entry — the assignment was *geometrically* correct but had to be patched by the user (CN4.1 swapped to MANUAL_THR, CN4.2 to SDC_IN_LOW_SIDE, REVERSE_WIRE still pending re-home as of writing). Future CN edits should re-read this entry before starting.

## 2026-05-08 — Suggested switching to the buzzer task while a PCB-sync issue was actively in flight

**What happened:** While the user was in the middle of resolving "Update PCB from Schematic" producing duplicates (the same ratsnest/PCB-sync workstream that already has a 2026-05-07 error-log entry), I read `.agents/tasks.md`, summarized the TODOs, and recommended starting the buzzer circuit "for the next thing to do on YOUR side while the peer routes." The user pushed back: poor organization, I should have known the issue we were dealing with — i.e., stay on the in-flight thread, don't pivot to an unrelated task list item.

**Root cause:** I treated `tasks.md` as the canonical "what to do next" without weighing context. The in-flight thread (PCB↔schematic resync, originally framed by the user as "use pcb with ratsnets") was the actual work; suggesting a different task is a context-switch the user didn't ask for. Same shape as past "drift away from user's stated goal" entries (e.g. 2026-05-07 "Forgot session context mid-conversation: re-suggested keeping RGB bridge open after user already established they want the LED").

**Prevention rule:**
- **Default to finishing the in-flight task before suggesting any task pivot.** "What's left" questions in the middle of a workstream mean "what's left in *this* thread first, then what's after" — not "here's a menu of unrelated TODOs."
- **When the user references an "original task" or earlier framing, anchor the response to that thread.** Re-read the recent conversation before suggesting next-step priorities. The user's framing wins over `tasks.md` ordering.
- **Task pivots are a user decision, not mine.** I can list what's open, but recommending a pivot mid-thread imposes an organizational choice the user hasn't asked for.

**Cross-reference:** 2026-05-07 ratsnest-Nets:1 entry (same workstream this conversation is continuing). 2026-05-07 RGB-bridge entry (same shape — drifting from stated goal).

## 2026-05-08 — Ranked "delete the symbol" as risky without first checking for coordinate collisions

**What happened:** User asked me to delete a hidden U02 reference in `kart-medulla_P1.kicad_sch`. I found it (a `kart-medulla:GND` symbol at (125.73, 311.15) with `Reference: U02`, hidden), and offered two options: (A) rename the reference to `#PWR<n>` — "recommended", "safe"; (B) delete the symbol — "Risky without checking the wiring." The user then asked why they couldn't simply select-and-delete it in the GUI. *That* prompted me to grep for the coordinates `125.73 311.15` — which immediately showed a second `power:GND` symbol stacked at the **exact same point**, plus a junction. The U02 GND was a fully redundant duplicate. Option B was the obvious safe answer all along; I had the file open and the grep took two seconds. The user pointed out I'd been confidently wrong.

**Root cause:** I assigned risk labels ("safe" / "risky") to the two options based on a generic prior ("deleting a wired symbol could orphan a net") without doing the cheap inspection that would have eliminated the prior in this specific case. The user's own observation — "I can find it with Find but can't click-select it" — was already strong evidence of a stacked/buried symbol; I didn't pick up on the signal. Same shape as the 2026-05-07 SELECT_THROTTLE entry: pushing a trace onto the user when the answer is one grep away.

**Prevention rule:**
- **Before assigning risk labels to schematic edits, grep the relevant coordinates / net / reference.** "Symbol at (x, y)" → `grep "at <x> <y>"` — finds stacks. "Net X" → trace netlist. "Reference Y" → grep both `Reference "Y"` and `(reference "Y")`. Cheap; eliminates whole categories of false caution.
- **"User can find it but can't click-select it" almost always means the item is stacked under another item.** Tab-cycle, or grep the coords. Don't speculate before grepping.
- **Don't pre-grade options as "safe vs risky" without the inspection that would tell you which is which.** Either do the inspection, or present both neutrally and say "I haven't checked which is safe."

**Cross-reference:** Same pattern as 2026-05-07 "Conflated firmware-doesn't-drive with hardware-not-wired" and 2026-05-07 "Made user re-explain the same KiCad ERC issue 8+ times" — reasoning from priors instead of inspecting the file.

## 2026-05-07 — Spent 20+ messages on "hide GND ratsnest" UI when the real problem was PCB/schematic out of sync (Nets: 1)

**What happened:** User asked how to show ratsnest for everything except GND. I went through ~6 wrong UI suggestions (Appearance-panel eye toggle, "Net Tools" submenu — wrong label, "Show All Hidden Nets" — invented, etc.) and only after using `osascript` to screencap KiCad's status bar did I notice **Nets: 1, Pads: 228** at the bottom. The PCB had only one net assigned across all pads — the schematic and PCB were not synced. There was no ratsnest to show because there were no nets to connect. Fix was a single F8 → "Update PCB from Schematic" → click "Update PCB". After sync: Nets: 83, ratsnest populated.

**Root cause:** I iterated on the user's described symptom ("ratsnest missing for non-GND nets") without ever verifying the underlying PCB state. Net count, pad count, footprint count, and unrouted count are all visible in the status bar at the bottom of the PCB editor — checking that first would have shown "Nets: 1" immediately and exposed the real issue. Instead I anchored on "user toggled eye → eye toggle is buggy → here are workarounds" because the user's narrative pointed there.

**Prevention rule:**
- **For any "ratsnest missing / wrong" report on a KiCad PCB, check the status bar net count first.** Pads/Nets/Unrouted at the bottom of the PCB editor. If `Nets` is much lower than expected (e.g. 1 on a real board), the PCB isn't synced — run **F8 → Update PCB from Schematic** before debugging any visibility settings. This is the single highest-leverage check.
- **`osascript` + `screencapture` is the right tool the moment a KiCad UI question goes past two wrong-path suggestions.** It costs nothing and shows ground truth.
- **Don't iterate on UI workarounds for a symptom whose root cause hasn't been verified.** "User says X is hidden" is one hypothesis; "X never existed" is another. Check the data, not the user's mental model.

## 2026-05-07 — Wrong path for "hide ratsnest of one net" in KiCad 10; iterated wrong guesses instead of verifying

**What happened:** User asked how to show ratsnest for everything except GND (planning a ground pour). I told them to use the eye-icon column in Appearance panel → Nets tab. Toggling GND's eye there blanked **all** ratsnest, not just GND. I then suggested Net Display Options ("Ratsnest display: All") and a non-existent "Net Inspector" entry under the Inspect menu. User had to push three times before I delegated to a subagent to verify the actual UI.

**Root cause:** Guessed UI behavior instead of checking. The Appearance Nets panel's eye column does not behave as "subtract this net from the visible set" — it's a known buggy interaction (KiCad GitLab #7039). The real path is the right-click context menu, which I should have known or verified up front.

**Prevention rule:**
- **KiCad 10 PCB editor — hide ratsnest of one net:** select a pad/track of that net (or right-click directly on it) → **Net Inspection Tools → Hide Net in Ratsnest**. Inverse: **Net Inspection Tools → Show Net in Ratsnest**. Greyed out if no net is selected. Hidden nets persist in `.kicad_pro` under `board.hidden_nets` (list of net names). The submenu is "Net Inspection Tools" — *not* "Net Tools" (I had this wrong twice — labels matter).
- **KiCad 10 — there is no "Net Inspector" entry in the Inspect menu.** The Net Inspector is a docked bottom panel (columns: Netclass, Total Length, Via Count, …), toggled from the left toolbar.
- **The Appearance → Nets tab eye column is not a per-net ratsnest toggle.** Don't recommend it for that purpose. Use Net Tools right-click instead.
- More generally: when a UI suggestion fails on the first try, **stop and verify the actual UI** (subagent + web search of docs.kicad.org / forum.kicad.info / GitLab issues) before offering a second guess. Three wrong-path messages is two too many.

**Cross-reference:** GitLab kicad/code/kicad #7039 (Nets-tab eye desync); forum.kicad.info threads "Hide specific ratsnests in PCB" and "How can I hide GND ratsnest".

## 2026-05-07 — Reported "Already applied" for an Edit that had failed; mistook the user's own edit for my own

**What happened:** User said "I chose short" (past tense) about a schematic annotation. I parsed it as present-tense intent ("I choose short"), called Edit on `kart-medulla_P1.kicad_sch`, got `File has been modified since read` error, then grepped, saw the new short text in the file, and replied "Already applied — the schematic now reads…" as if my edit had succeeded. The new text was the user's edit (they had already applied it themselves, which is exactly what "I chose" meant). User flagged the reading-comprehension mistake; separately flagged that I shouldn't be writing to the .kicad_sch with KiCad open at all.

**Root cause:**
1. **Tense misread.** "I chose" = past, action done. I treated it as a selection-of-options statement requiring me to act.
2. **Failure-to-success confusion.** Edit returned an error (`File has been modified since read`). That was the signal that *someone else wrote to the file* — i.e. the user. Instead of recognising that, I grepped, saw the desired content, and reported success. A tool error followed by "the desired state exists" does not mean the tool succeeded — it usually means someone else got there first.
3. **Ignored the open-KiCad rule.** AGENTS.md says don't write to `.kicad_sch` while KiCad is open unless coordinated. I didn't check `pgrep` before calling Edit. (KiCad was in fact open.)

**Prevention rule:**
- **Past-tense from the user = action already done.** "I chose / I did / I applied / I fixed" — do not re-do the action. At most, verify and acknowledge. If genuinely unsure whether it's past or imperative, ask in one line before acting.
- **An Edit failure is a signal, not noise.** `File has been modified since read` specifically means the file changed under me. Re-read and diff against my intended change before claiming any state. Never report "Already applied" off the back of a failed Edit.
- **Before any write to `.kicad_sch` / `.kicad_pcb` / `.kicad_sym`, check `pgrep -i kicad`.** If KiCad GUI is running, don't write — ask the user to apply it in the GUI, or to close KiCad first. (Already in AGENTS.md "Editing KiCad files outside KiCad" §1; this entry is the reminder that I skipped it.)

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

**Cross-reference:** `history.md` 2026-05-07 entry, "Why three-symbols-works..." section now flagged as unverified hypothesis.

## 2026-05-07 — Made user re-explain the same KiCad ERC issue 8+ times instead of inspecting the schematic via MCP

**What happened:** User had ERC error "Input pin not driven by any Output pins" on PCF8574 A0 in kart-medulla. I went through ~8 rounds of guesses (wire floating, missing junction, wrong label type, missing PWR_FLAG, wrong power symbol shape, two PWR_FLAGs, pin not snapped) without ever opening the schematic file or invoking the kicad MCP. Each round added a new wrong instruction the user had to act on before correcting me. User got progressively more frustrated ("are you blind?", "I want GND!!!", "you're asking the same things over and over"). When I finally used the MCP (`grep PWR_FLAG`, `mcp__kicad__run_erc`), it took two tool calls to find the actual answer: only one PWR_FLAG exists on disk (`#FLG01` at known coords), saved schematic passes ERC, and the duplicate-PWR_FLAG error was from the user's own newly-added flag in the unsaved GUI state.

**Root cause:** I treated the user's screenshots as the only source of truth and reasoned from images, when the schematic file is plain text on disk and a kicad MCP is connected. Iterating-from-screenshots is high-latency and low-fidelity — every wrong guess costs a real schematic edit by the user.

**Prevention rule:**
- **For any KiCad debugging session: read the schematic file or use the kicad MCP first.** `grep PWR_FLAG`, `mcp__kicad__run_erc`, and `mcp__kicad__sch_get_symbols` are one tool call each and answer most "what's actually on this net" questions definitively.
- **The MCP reads disk. The user's GUI may be unsaved.** If MCP results disagree with what the user reports, the gap is unsaved GUI state — say so directly, don't loop on guesses.
- **Stop iterating "try this, did that work?" past 2 rounds.** If two suggestions don't fix it, switch to inspecting the actual file. The user shouldn't be the debug loop.
- **KiCad ERC drive rules (do not re-derive every time):** Power Input pins (GND/+3V3 power-symbol pins, IC power pins) do NOT drive a net. Need exactly one PWR_FLAG per power net across the whole design. Global labels named "GND" do not merge with the GND power-symbol net — only power symbols join the global power net. See `history.md` 2026-05-07 entry for full breakdown.

**Cross-reference:** `history.md` "KiCad ERC: Input pin not driven on GND net" 2026-05-07.

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

## 2026-05-07 — Markdown ate a literal backtick in instructions

**What happened:** Telling the user how to highlight a net in KiCad, I wrote the keyboard shortcut as `**`** (backtick)` — a backtick wrapped in bold-asterisks. Markdown rendered it as `****` on the user's side, with the actual backtick character lost/escaped. User couldn't tell which key I meant and got (justifiably) frustrated.

**Root cause:** Wrapping a backtick — which is itself markdown's code-fence character — inside `**...**` is fragile. The renderer collapses or escapes it inconsistently. I prioritized visual emphasis over the user actually being able to read the character.

**Prevention rule:**
- When the answer IS a literal punctuation/symbol character (especially backtick, asterisk, underscore, tilde), render it inside an inline code span with double backticks: `` `` ` `` `` — not bolded, not bare.
- Never wrap a backtick in `**...**`. Same for `*` inside `*...*`, `_` inside `_..._`, etc.
- For non-US-keyboard users, also give the alternative input (e.g. `Option+Ñ` on Spanish Mac) — the literal character on its own isn't enough if the key isn't directly typeable.

## 2026-07-16 — Left a repo contradictory and reported it only in chat

**What happened:** Consolidating `.agents/tasks.md` → root `tasks.md`, I made repo-wide changes that
knowingly left contradictions behind: `AGENTS.md` still claiming "newest entries first" for an
oldest-first `history.md`, stale `.agents/tasks.md` paths in two logs, per-board vs root `tasks.md`
unresolved, and (from the same session) L7805-vs-LM2596 and the compressor-power-path conflicts. I
listed every one of them — in a long chat message, and nowhere else. Nothing went into `tasks.md`.
The repo was left in a state where two files disagreed and only the chat transcript knew why.

**Root cause:** I treated *telling the user* as equivalent to *recording it*. It isn't. Chat is
transient, unsearchable by the next session, and long answers get skimmed — reasonably so. The user's
words: "relying on me reading all the 2 page answer you just gave me without skipping anything."
A contradiction that lives only in a chat message is an undocumented bug with a witness.

**Prevention rule:**
- **A change that leaves a contradiction or an open decision does not ship until it's written into
  `tasks.md` as an actionable item.** Do this in the same turn as the change, before reporting.
  Chat mentions do not count.
- If a change makes any doc wrong (even a doc you didn't touch), that's a `tasks.md` entry naming
  both files and which one is suspect — not a footnote.
- The chat summary is a pointer to the record, never the record itself.
- Cross-reference: `history.md` 2026-07-16; the open list lives in `tasks.md` under "Resolve
  contradictions left open on 2026-07-16".

## 2026-07-30 — Verified 30 net assignments "resolve to the intended net" and still shipped a wrong one

**What happened:** Commit `e8881f1` (2026-05-08, "kart-medulla: assign CN1–CN10 pins to match ESP32
geometry") reshuffled 30 connector-pin net assignments on the medulla schematic — 25 label renames
plus 5 new wire+label pairs. Two of those edits, taken together, silently disconnected the
proportional-valve command from the outside world:

- The label on the wire stub that became **CN10 pin 2** was changed from `EXP_P7` to
  **`CMD_BRAKE__0_5V`** — the raw MCP4922 DAC output, not the amplified signal.
- The label at the stub that had carried **`CMD_BRAKE__0_10V`** — the LM358 ×2 output, and the
  design's only exit for the valve command — was overwritten with **`GND`**.

Result: the board sends 0–5 V to a Festo VPPM whose setpoint input is 0–10 V, the amplifier output
reaches no connector at all, and the DAC output pin sits unprotected on an external terminal. Found
2026-07-30, nearly three months later, and only because someone read the net names and thought one
looked wrong. Full analysis in `history.md` under that date.

**Root cause — two failures, both about what "verified" meant:**

1. The commit message says "Verified end-to-end via netlist export: all 30 CN pins resolve to the
   intended global net." That check confirmed each label **resolved to a net that exists**. It could
   not confirm the net was the **electrically correct** one, because the check's own reference for
   "intended" was the same list of names being applied. Comparing an edit against itself always
   passes. Nothing in that loop knew that a 0–10 V connector pin must not carry a 0–5 V net.
2. ERC could not catch it either. After the edit `CMD_BRAKE__0_10V` still had two pads on it — the
   op-amp output and its feedback resistor — and a two-pad net is electrically legal. KiCad has no
   check for "this net has no exit point", so a signal that terminates inside its own feedback loop
   looks exactly like a healthy net.

**Prevention rules:**
- **A net-name edit is verified against the physical requirement, not against the list of names being
  applied.** For every signal that leaves the board, state the required voltage range and the
  destination device, then confirm the net on the connector pin carries that range. The `__<range>`
  suffix already in the naming convention is what makes this checkable — use it as an assertion, not
  decoration. Two nets differing only in that suffix (`__0_5V` vs `__0_10V`) are the highest-risk
  case in a bulk rename, because they look almost identical in a diff.
- **After any bulk connector reassignment, list every net that lost a connector pin.** Diff the set of
  nets with at least one connector pad before and against after. A net dropping out of that set is
  either a deliberate removal or exactly this bug; it is never something to leave unexamined. In this
  commit `CMD_BRAKE__0_10V` left the set and nothing noticed.
- **Do not treat "ERC/DRC clean" as evidence a signal reaches the outside world.** Neither tool models
  intent to export. An amplifier output that connects only to its own feedback resistor is clean by
  both, and useless.
- Cross-reference: `history.md` 2026-07-30; the fix is the task "Fix the proportional-valve command
  path — CN10.2 is on the wrong side of the LM358" in `tasks/kart-medulla.md`.

## 2026-07-31 — Placed the same footprint twice by trusting `HEAD~1` as "the clean board"

**What happened.** While iterating on the design-ID silkscreen QR, each attempt started by restoring a
"clean" board with `git show HEAD~1:projects/kart-medulla/kart-medulla.kicad_pcb`. Another session
committed to this repo in between, so `HEAD~1` was no longer the commit before the placement — it
already contained one. The script then appended a second copy, 0.5 mm from the first.

**How it presented.** Three symptoms that all looked like problems with the change being tested rather
than with the file: 199 `silk_overlap` DRC violations between the footprint's own polygons, a
silkscreen plot where the QR modules rendered as hollow outlines and the caption lines appeared to
overlap, and a QR that would not decode. All three are what two copies of one QR offset by half a
millimetre look like. Time went into bisecting the wrong variable — whether adding a text line above
the symbol had broken something — before diffing the placed footprint blocks showed the file had 471
lines where the committed one had 235.

**Root cause.** `HEAD~1` is a moving target in a repo with concurrent sessions. It names a position in
history, not a state of the file.

**Prevention.** Restore a known state by content, not by position: strip the element being replaced
(match its name, walk its parentheses to the closing one, cut it out) and assert the result contains
zero of them before inserting, then assert exactly one afterwards. Both assertions are one line each
and would have failed immediately on the first bad run. When a change produces a wall of geometry
violations against *its own* items, check element count before investigating geometry.

## 2026-07-31 — reported a file write that never happened

**What happened.** Rubén told me to stop the audit workflow because it was eating the quota. I stopped
it, then ran a one-liner that was supposed to extract the completed findings from the workflow journal
and append them to `history.md`, followed by `&& git commit … ; echo saved`.

The Python crashed on `AttributeError: 'str' object has no attribute 'get'` — a few entries inside a
`findings` array came back as plain strings rather than objects, and the loop assumed every one was a
dict. The `open(...).write(...)` call sat *after* the loop, so it never ran. `history.md` was untouched.

**Why I said it worked anyway.** Three compounding mistakes in one command line:
1. The write was after the loop instead of incremental, so a crash mid-loop lost everything.
2. `echo saved` was chained with `;`, not `&&`, so it printed regardless of the exit status.
3. I read the word "saved" in the output and reported success without checking the file. The git
   output in the same block literally said *"nothing added to commit"* and I did not read it.

**Prevention.** After any scripted write, verify the file, not the script's own output — `grep` for
the content that should now be there. Never chain a success message with `;`. And when a command block
mixes a script and a commit, read the git output: "nothing added to commit" is the write failing loudly.

**Cost.** Low this time — the data was still in the workflow journal and the second attempt recovered
all 43 findings. The damage was to trust, not to data: Rubén had to ask what happened to `history.md`
rather than being told.
