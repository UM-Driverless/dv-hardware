<!-- reference — read when choosing a connector or sizing a current path -->

# Connector selection — measured ratings and what they can carry

Applies to every board in this repo. Ratings below are manufacturer figures from the linked pages,
checked on the date shown, not estimates. **A connector's rated current is a ceiling for continuous
current; motor inrush is a short peak and is judged separately.**

## On-board PCB terminal blocks

| Part | Series | Pitch | Rated current | Conductor | Where used |
|---|---|---|---|---|---|
| Phoenix Contact **1990012** | PTSA 0,5/3-2,5-Z | 2.5 mm | **2 A** @ 250 V | 0.5 mm², AWG 20 max | CN1–CN10 on the assembled kart-medulla |
| WAGO **2601-3103** | 2601 (Push-in CAGE CLAMP, lever) | 3.5 mm | **17.5 A** | 1.5 mm², AWG 26–14 | 3-pole, the team's stocked standard |
| WAGO **2601-3102** | same, 2-pole | 3.5 mm | **17.5 A** | 1.5 mm², AWG 26–14 | 2-pole, the team's stocked standard |

Checked 2026-07-31 against
[Phoenix 1990012](https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-ptsa-05-3-25-z-1990012)
(figures also on [TME](https://www.tme.com/us/en-us/details/ptsa0.5_3-2.5-z/pcb-terminal-blocks/phoenix-contact/1990012/))
and [WAGO 2601-3103](https://www.wago.com/global/pcb-terminal-blocks-and-pluggable-connectors/pcb-terminal-block/p/2601-3103).

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
- **The WAGO 2601-3103 can**, with margin: 17.5 A against 6 A continuous. The team is already
  stocking these, so a future board that carries compressor power does not need a new connector
  family on the PCB for this load.
- **Deutsch DT (13 A) also clears it**; DTM (7.5 A) clears the running current but with little room,
  so DT is the safer pick if the harness side needs a sealed connector for this load.
- **Soldering the wire straight to the board** is an accepted fallback when no connector fits.

**Locked-rotor inrush was never measured.** A brushed DC motor typically draws several times running
current at stall, so peak here is plausibly 20–30 A. That peak sizes the MOSFET, the flyback path and
the copper — not necessarily the connector, which tolerates brief peaks above its continuous rating.
Measure it before designing a board that switches this motor.

## The part that connectors do not fix

A connector rating says nothing about the copper behind it. On the kart-medulla as built, `+12V` and
the motor-return net are drawn for the **~1 mA** logic supply they actually carry. Any board revision
that puts compressor current on-board starts by re-sizing those tracks (or pouring them) and their
vias for a stated design current, and writing that current down. Fitting a bigger connector to a net
sized for milliamps moves the failure, it does not remove it.
