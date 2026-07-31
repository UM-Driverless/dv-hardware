<!-- reference — read when choosing a connector or sizing a current path -->

# Connector selection — measured ratings and what they can carry

Applies to every board in this repo. Ratings below are manufacturer figures from the linked pages,
checked on the date shown, not estimates. **A connector's rated current is a ceiling for continuous
current; motor inrush is a short peak and is judged separately.**

## On-board PCB terminal blocks

| Part | Series | Pitch | Rated current | Conductor | Wire entry | Where used |
|---|---|---|---|---|---|---|
| Phoenix Contact **1990012** | PTSA 0,5/3-2,5-Z | 2.5 mm | **2 A** @ 250 V | 0.5 mm², AWG 20 max | 45° | CN1–CN10 on the assembled kart-medulla |
| WAGO **2601-3103** | 2601 (Push-in CAGE CLAMP, lever) | 3.5 mm | **17.5 A** | 1.5 mm², AWG 26–14 | **top entry** | 3-pole, on the team's buy list |
| WAGO **2601-3102** | same, 2-pole | 3.5 mm | **17.5 A** | 1.5 mm², AWG 26–14 | **top entry** | 2-pole, on the team's buy list |
| WAGO **2601-1103** | same, 3-pole | 3.5 mm | 17.5 A | 1.5 mm², AWG 26–14 | side entry | not chosen — listed to show the difference |

Checked 2026-07-31 against
[Phoenix 1990012](https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-ptsa-05-3-25-z-1990012)
(figures also on [TME](https://www.tme.com/us/en-us/details/ptsa0.5_3-2.5-z/pcb-terminal-blocks/phoenix-contact/1990012/)),
[WAGO 2601-3103](https://www.wago.com/ca-en/pcb-terminal-blocks-and-pluggable-connectors/pcb-terminal-block/p/2601-3103)
and [WAGO 2601-1103](https://www.wago.com/us/pcb-interconnect/pcb-terminal-block/p/2601-1103).

### Which WAGO 2601 is the "vertical" one

**`2601-31xx` is top entry — the wire goes in from above, perpendicular to the board, with the
orange levers on the front face.** That is the shape most people mean by "vertical", and it is the
one already on the buy list. `2601-11xx` is the side-entry variant of the same series: same pitch,
same current, wire arriving parallel to the board.

The middle two digits carry the entry style and the last two the pole count, so `2601-3102` is the
2-pole top-entry part and `2601-3103` the 3-pole. WAGO's page for `-3103` states "top entry" and
`-1103` states "side entry"; the `-3102` page does not print the phrase, but **KiCad 10's stock
library confirms it independently** — it names every `-31xx` footprint `_Vertical` and every `-11xx`
one `_Horizontal`.

**Confirmed 2026-07-31 that these are being bought**, but none are owned yet — `~/vault/inventory/`
holds the Phoenix 1990012 (also never purchased) and WAGO 221 lever nuts, which are in-line splice
connectors and unrelated.

**KiCad 10 ships the footprints**, so nothing has to be drawn:
`TerminalBlock_WAGO:TerminalBlock_WAGO_2601-3102_1x02_P3.50mm_Vertical` and
`..._2601-3103_1x03_P3.50mm_Vertical`. The library is reachable from any project through the stock
table with no setup.

Stock only the 2-pole and 3-pole WAGO parts: with {2, 3} any pole count from 2 upward composes with
no gaps, and per-pin price is flat across pole counts, so higher counts save nothing.

## Harness connectors (board-to-cable, off-PCB)

**The Deutsch DT family is the team standard** for harness connections (Rubén, 2026-07-31). Sealed,
keyed, crimped, and the usual choice in motorsport wiring.

| Series | Contact size | Rated current per contact | Wire |
|---|---|---|---|
| **DT** | 16 | 13 A continuous | AWG 20–14 |
| **DTM** | 20 | 7.5 A continuous | AWG 22–14 |

Checked 2026-07-31 against the
[TE DT series technical manual](https://www.farnell.com/datasheets/628276.pdf) and the
[DTM series sheet](https://www.elecdirect.com/media/specsheets/Deutsch-Connectors-DTM-Series.pdf).

## The worked example: the EBS compressor, 6 A

The compressor was measured at **6 A running at 60 % duty** on the bench, 2026-07-18. Against that
number:

- **The Phoenix 1990012 fitted to the assembled board cannot carry it** — 2 A rated against 6 A
  measured is 3× over, before any inrush. Compressor current must not be routed through CN1–CN10 as
  the board stands.
- **The WAGO 2601-3103 can**, with margin: 17.5 A against 6 A continuous. It is already the team's
  chosen part, so medulla-v2 — which *does* carry compressor power on-board — does not need a new
  connector family for this load.
- **Deutsch DT (13 A) also clears it**; DTM (7.5 A) clears the running current but with little room,
  so DT is the safer pick if the harness side needs a sealed connector for this load.
- **Soldering the wire straight to the board** is an accepted fallback when no connector fits.

**Locked-rotor inrush will not be measured** — Rubén, 2026-07-31: the circuit is already validated
in service, and over-sizing costs nothing when the parts are in stock. So the design rule for this
load is *pick from what's on the shelf and leave margin*, not *measure the peak and size to it*. For
reference, a brushed DC motor typically draws several times running current at stall, so the peak
here is plausibly 20–30 A; the 17.5 A WAGO tolerates brief peaks above its continuous rating, and
the copper is sized generously rather than exactly.

## The part that connectors do not fix

A connector rating says nothing about the copper behind it. On the kart-medulla as built, `+12V` and
the motor-return net are drawn for the **~1 mA** logic supply they actually carry. medulla-v2 brings
compressor current on-board, so it starts by re-sizing those tracks (or pouring them) and their vias
for a stated design current, and writing that current down. Fitting a bigger connector to a net sized
for milliamps moves the failure, it does not remove it. Rubén's emphasis, 2026-07-31: **the traces
being properly sized is the important part.**
