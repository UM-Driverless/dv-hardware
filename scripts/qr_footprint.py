#!/usr/bin/env python3
"""Generate a KiCad footprint holding a design ID as a silkscreen QR plus its human-readable digits.

The QR is emitted as one filled polygon per dark module, so it is real silkscreen geometry that any
fab renders directly — not a placeholder or an imported bitmap. Run once per design ID; the result is
a normal footprint that gets placed in the layout like any other.

Why a footprint and not loose graphics: a footprint moves as one object, survives re-layout, and can
be dropped into the next board revision without regenerating anything.

Module size: 0.4 mm by default. Silkscreen minimum feature width is typically 0.15-0.2 mm, so 0.4 mm
gives roughly a 2x margin over the process floor and reads reliably on a phone. A 16-digit ID rides
the QR's numeric mode and fits Version 1 (21x21 modules) even at ECC H, so the symbol is
21 * 0.4 = 8.4 mm square. The 4-module quiet zone (3.2 mm) is NOT drawn — it is empty board that the
layout must keep clear of other silkscreen.

Usage:
    uv run --with segno python scripts/qr_footprint.py 1604094846085574 --name kart-medulla-v2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import segno

REPO_ROOT = Path(__file__).resolve().parent.parent


def grouped(pid: str) -> str:
    """Human-display form: digits in groups of 4, as printed on labels and part pages."""
    return " ".join(pid[i:i + 4] for i in range(0, len(pid), 4))


def module_matrix(pid: str) -> list[list[int]]:
    """Dark/light module grid for the ID, without the quiet zone (border=0)."""
    qr = segno.make_qr(pid, error="h")  # make_qr, never make: Micro QR is not reliably phone-readable
    return [[int(bit) for bit in row] for row in qr.matrix]


def footprint(pid: str, name: str, module_mm: float, text_mm: float,
              caption_lines: list[str] | None = None, header: str | None = None) -> str:
    matrix = module_matrix(pid)
    n = len(matrix)
    span = n * module_mm
    # Origin at the symbol's centre so the footprint's anchor sits in the middle of the QR.
    x0 = -span / 2
    y0 = -span / 2

    polys = []
    for r, row in enumerate(matrix):
        for c, dark in enumerate(row):
            if not dark:
                continue
            x = x0 + c * module_mm
            y = y0 + r * module_mm
            # Each dark module is its own filled square. Adjacent squares abut exactly, which the
            # gerber renderer merges into solid blocks, so no gaps appear between neighbouring modules.
            polys.append(
                f'  (fp_poly (pts (xy {x:.4f} {y:.4f}) (xy {x + module_mm:.4f} {y:.4f}) '
                f'(xy {x + module_mm:.4f} {y + module_mm:.4f}) (xy {x:.4f} {y + module_mm:.4f})) '
                f'(stroke (width 0) (type solid)) (fill solid) (layer "F.SilkS"))'
            )

    # Caption below the symbol, stacked so the block stays no wider than the QR itself. A single
    # "Design ID: 1604 0948 4608 5574" line runs ~25 mm — three times the symbol — which wastes board
    # and forces the whole footprint into a wide slot no layout has spare.
    caption = caption_lines or ["Design ID", grouped(pid)]
    pitch = text_mm * 1.7
    labels = "\n".join(
        f'  (fp_text user "{line}" (at 0 {y0 + span + pitch * (i + 1):.4f}) (layer "F.SilkS")\n'
        f'    (effects (font (size {text_mm} {text_mm}) (thickness 0.15))))'
        for i, line in enumerate(caption)
    )
    # A header line above the symbol says what the number is. It goes above rather than below because
    # the caption below is already the widest part of the block, and a slot short enough to force the
    # choice usually has its spare room on the other side of the symbol.
    if header:
        head_lines = header.split("|")
        labels = "".join(
            f'  (fp_text user "{line}" (at 0 {y0 - pitch * (len(head_lines) - j):.4f}) (layer "F.SilkS")\n'
            f'    (effects (font (size {text_mm} {text_mm}) (thickness 0.15))))\n'
            for j, line in enumerate(head_lines)
        ) + labels
    body = "\n".join(polys)
    return f'''(footprint "{name}"
  (version 20241229)
  (generator "qr_footprint.py")
  (layer "F.SilkS")
  (descr "Design ID {grouped(pid)} — silkscreen QR ({n}x{n} modules at {module_mm} mm) plus digits. Keep a {4 * module_mm:.1f} mm quiet zone clear of other silkscreen on all four sides.")
  (tags "design-id qr")
  (attr exclude_from_pos_files exclude_from_bom)
  (fp_text reference "REF**" (at 0 {y0 - text_mm * 1.6:.4f}) (layer "F.Fab") hide
    (effects (font (size {text_mm} {text_mm}) (thickness 0.15))))
  (fp_text value "{name}" (at 0 {y0 - text_mm * 3.2:.4f}) (layer "F.Fab") hide
    (effects (font (size {text_mm} {text_mm}) (thickness 0.15))))
{body}
{labels}
)
'''


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a silkscreen design-ID QR footprint.")
    ap.add_argument("design_id", help="The 16-digit design ID, bare (no spaces)")
    ap.add_argument("--name", required=True, help="Footprint name, e.g. kart-medulla-v2")
    ap.add_argument("--library", default="projects/kart-medulla/kart-medulla.pretty",
                    help="Footprint library directory, relative to the repo root")
    ap.add_argument("--module-mm", type=float, default=0.4, help="Size of one QR module in mm")
    ap.add_argument("--text-mm", type=float, default=1.0, help="Height of the digits line in mm")
    ap.add_argument("--header", default=None,
                    help="Lines placed ABOVE the QR, separated by | , e.g. 'kart-medulla-v2|Design ID'")
    ap.add_argument("--caption", default=None,
                    help="Caption lines below the QR, separated by | (default: 'Design ID|<grouped id>'). Board setup may impose a minimum silk text height — KiCad DRC reports it as text_height.")
    args = ap.parse_args()

    pid = args.design_id.replace(" ", "")
    if not (pid.isdigit() and len(pid) == 16):
        raise SystemExit(f"Design ID must be 16 digits, got {pid!r}")

    lib = REPO_ROOT / args.library
    lib.mkdir(parents=True, exist_ok=True)
    out = lib / f"{args.name}.kicad_mod"
    lines = args.caption.split('|') if args.caption else None
    out.write_text(footprint(pid, args.name, args.module_mm, args.text_mm, lines, args.header))

    n = len(module_matrix(pid))
    print(f"Design ID : {pid}  ({grouped(pid)})")
    print(f"Footprint : {out.relative_to(REPO_ROOT)}")
    print(f"QR        : {n}x{n} modules at {args.module_mm} mm = {n * args.module_mm:.1f} mm square")
    print(f"Quiet zone: keep {4 * args.module_mm:.1f} mm clear of silkscreen on all four sides")


if __name__ == "__main__":
    main()
