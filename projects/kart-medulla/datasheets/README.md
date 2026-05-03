# kart-medulla datasheets

Datasheets for chips actually placed on this board. Copied in from the vault (`~/dv/datasheets/`) when a part is designed onto the PCB. Self-contained so a fresh `git clone` of `dv-hardware` gives you everything needed to understand the board.

## What goes here
- One PDF per chip used in the BOM. Filename: `<partnumber>_<vendor>_datasheet.pdf` (matches vault naming).
- Application notes specific to how *this* board uses the part.

## What does NOT go here
- Datasheets for parts only being evaluated (not yet on the PCB) → keep in vault.
- General electronics reference (op-amp theory, etc.) → vault `references/`.
- Datasheets shared across multiple boards: still copy here per-board (small duplication is OK; lookup pain isn't). The vault remains the master catalog.

## Source of truth
Vault `~/dv/datasheets/` is the team's full chip catalog. This folder is the per-board subset.
