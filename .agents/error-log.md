<!-- consult selectively — grep, never read in full -->

# Error log

Mistakes made and the rules learned from them. Newest first. Grep before working in a related area.

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
