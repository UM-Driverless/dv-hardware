<!-- consult selectively — grep, never read in full -->

# Error log

Mistakes made and the rules learned from them. Newest first. Grep before working in a related area.

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
- Cross-reference: `.agents/history.md` 2026-05-04 entry has the docs quote and the correction.

**Verification:** KiCad master docs, eeschema chapter — "No-connection flags are used to indicate that a pin is intentionally unconnected. These flags prevent 'unconnected pin' ERC warnings for pins that are intentionally unconnected." (https://docs.kicad.org/master/en/eeschema/eeschema.html)
