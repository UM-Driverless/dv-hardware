# ESP32-S3 pin capability reference

<!-- reference — read when relevant -->

Per-pin capability map for the **ESP32-S3** (and the WROOM-1 module form factor used on `kart-medulla`). This file is the answer to "can I put signal X on GPIO Y?" — it does not describe any specific board. For the medulla's actual assignments see `projects/kart-medulla/docs/pinout-kart-medulla-v1.md`; that doc cites this one when justifying constraints.

Sourced from Espressif's *ESP32-S3 Datasheet* (v1.7+) and *ESP32-S3 Technical Reference Manual*. No images; all info in plain markdown so an AI agent or grep user can read it directly.

## Quick rules

- **No input-only pins.** Unlike the classic ESP32 (where GPIO 34–39 were input-only), every S3 GPIO is bidirectional with internal pull-up / pull-down and ~40 mA drive.
- **GPIO matrix routes almost everything.** UART, I²C, SPI (except SPI0/1 flash), LEDC PWM, MCPWM, RMT, I²S, TWAI/CAN, SDIO can be assigned to any GPIO at runtime. Speed/SI may suffer at extremes; for HS-SPI / USB / ADC the dedicated pins are still preferred.
- **Strap pins must be at safe levels at reset.** Pins: **0, 3, 45, 46**. Sample at the rising edge of `CHIP_PU`. After boot they become normal GPIOs.
- **ADC2 conflicts with Wi-Fi.** GPIO 11–20 are ADC2 — usable as ADC only when the radio is idle. Treat ADC2 as "not for production analog reads."
- **Avoid WROOM-1 internal-flash pins.** GPIO 26–32 carry the in-package SPI flash on WROOM-1 / WROOM-2 and are **not exposed** on the module footprint.
- **Octal-PSRAM (R8 modules) eats GPIO 33–37.** Quad-PSRAM (R2) and no-PSRAM (no R suffix) leave them free. To stay flexible across module variants, treat 33–37 as conditional.
- **USB-OTG and USB-Serial-JTAG share GPIO 19 (D-) / 20 (D+).** If used as plain GPIOs, you lose USB.
- **DevKitC-1 quirks (when populating a stock dev board):** GPIO 43/44 are owned by the on-board CP210x USB-UART bridge; GPIO 48 drives the on-board WS2812 RGB LED; GPIO 0 is wired to the BOOT button.

## Pin / GPIO inventory

ESP32-S3 has **45 GPIOs total**, numbered 0–21 and 26–48. There is no GPIO 22, 23, 24, 25.

| Group | GPIOs | Notes |
|---|---|---|
| General digital I/O | 0–21, 26–48 | All bidirectional, all support internal PU/PD |
| RTC / LP domain | 0–21 | Usable in deep-sleep, by ULP, by LP-CPU; supports LP I²C / LP UART / LP SPI on a subset |
| Touch sensor | 1–14 | Capacitive touch channels TOUCH1–TOUCH14 |
| ADC1 | 1–10 | ADC1_CH0..CH9 — production-grade, Wi-Fi-safe |
| ADC2 | 11–20 | ADC2_CH0..CH9 — **shared with Wi-Fi**, avoid for live reads |
| USB OTG / USB-Serial-JTAG | 19 (D-), 20 (D+) | Native full-speed USB |
| Default UART0 | 43 (U0TXD), 44 (U0RXD) | Boot ROM log goes here; WROOM-1 module exposes them; on DevKitC-1 they're tied to the USB-UART bridge |
| SPI flash (in-module, WROOM-1) | 26–32 | Internal — **not on module pins** |
| Octal PSRAM (R8 modules only) | 33–37 | Internal on R8 — **do not drive externally** on R8 |
| Strap pins | 0, 3, 45, 46 | See "Strap pins" section below |
| JTAG (pin-mode) | 39 (MTCK), 40 (MTDO), 41 (MTDI), 42 (MTMS) | Used when GPIO 3 strap routes JTAG away from USB |
| VDD_SPI ref | 45 | Strap selects 1.8 V vs 3.3 V SPI flash voltage |

## Strap pins (pins that decide boot behavior)

Strap level is sampled on the rising edge of `CHIP_PU` (≈ end of reset) and latched into the boot-mode register. After that latch the pin is a normal GPIO — but a hard reset re-samples, so the **idle state** of any signal you put on a strap pin must match the desired strap value.

| GPIO | Strap function | Default in modules | Safe usage |
|---|---|---|---|
| 0 | Boot mode select. **HIGH = SPI flash boot (normal). LOW = ROM download (UART/USB).** | Pulled HIGH inside WROOM-1 | OK as input/output if signal is HIGH or high-Z at power-on. Ideal for a momentary push-button to GND ("BOOT button"). |
| 3 | JTAG signal source. **HIGH = USB-Serial-JTAG (PHY on GPIO 19/20). LOW = pin-JTAG on GPIO 39–42. Floating = same as HIGH.** | Floating | OK as output if you don't need pin-mode JTAG. Idle-high signals (e.g. push-pull buzzers idling high) are fine. |
| 45 | VDD_SPI voltage. **LOW = 3.3 V SPI flash (default for WROOM-1). HIGH = 1.8 V SPI flash.** | Pulled LOW inside WROOM-1 | OK as output if signal idles LOW at power-on. Otherwise leave alone. |
| 46 | ROM message print. **LOW = silent boot ROM. HIGH = print boot log to UART0.** | Pulled LOW inside WROOM-1 | OK as output if signal idles LOW at power-on. |

GPIO 45 and 46 also gate the boot-ROM console behavior; flipping them by accident usually surfaces as "chip won't boot" or "garbage on UART0."

## Pins that are usually off-limits

| GPIO | Reason | Reclaimable? |
|---|---|---|
| 19, 20 | USB D- / D+ | Only if you are sure you don't need USB-OTG nor USB-Serial-JTAG |
| 26–32 | Internal SPI flash on WROOM-1 (and most -N* modules) | Never on module-form-factor designs |
| 33–37 | Octal PSRAM on R8 modules (`-N8R8`, `-N16R8`, etc.) | Yes on R2 / no-PSRAM modules; **never** on R8 |
| 43, 44 | UART0 (boot console). On DevKitC-1, hard-wired to the on-board CP210x | If using bare WROOM-1: yes, post-boot. On DevKitC-1: no. |
| 48 | DevKitC-1 on-board WS2812 RGB LED | Free on bare WROOM-1. On DevKitC-1, only if you don't mind the LED twitching. |

## Per-GPIO capability matrix

Format: `?` = supported via GPIO matrix (any GPIO can do it); `✓` = dedicated; `–` = unavailable; **bold** = dedicated peripheral on this pin.

| GPIO | RTC | ADC | Touch | Strap | USB | UART (default) | SPI flash | Octal PSRAM (R8) | DevKitC-1 use | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | ✓ | – | – | **BOOT** | – | – | – | – | BOOT button to GND | Must be HIGH at reset. Strap-safe signals: HIGH idle, high-Z, momentary-LOW push-button |
| 1 | ✓ | **ADC1_CH0** | **TOUCH1** | – | – | – | – | – | exposed | Production ADC pin |
| 2 | ✓ | **ADC1_CH1** | **TOUCH2** | – | – | – | – | – | exposed | Production ADC pin |
| 3 | ✓ | **ADC1_CH2** | **TOUCH3** | **JTAG src** | – | – | – | – | exposed | Strap default = floating ≡ HIGH (USB-JTAG). Idle-high outputs (push-pull HIGH) are safe. |
| 4 | ✓ | **ADC1_CH3** | **TOUCH4** | – | – | – | – | – | exposed | Production ADC pin |
| 5 | ✓ | **ADC1_CH4** | **TOUCH5** | – | – | – | – | – | exposed | Production ADC pin |
| 6 | ✓ | **ADC1_CH5** | **TOUCH6** | – | – | – | – | – | exposed | Production ADC pin |
| 7 | ✓ | **ADC1_CH6** | **TOUCH7** | – | – | – | – | – | exposed | Production ADC pin |
| 8 | ✓ | **ADC1_CH7** | **TOUCH8** | – | – | – | – | – | exposed | Production ADC pin |
| 9 | ✓ | **ADC1_CH8** | **TOUCH9** | – | – | – | – | – | exposed | Production ADC pin |
| 10 | ✓ | **ADC1_CH9** | **TOUCH10** | – | – | – | – | – | exposed | Production ADC pin |
| 11 | ✓ | ADC2_CH0 | **TOUCH11** | – | – | – | – | – | exposed | ADC2 conflicts with Wi-Fi |
| 12 | ✓ | ADC2_CH1 | **TOUCH12** | – | – | – | – | – | exposed | ADC2 conflicts with Wi-Fi |
| 13 | ✓ | ADC2_CH2 | **TOUCH13** | – | – | – | – | – | exposed | ADC2 conflicts with Wi-Fi |
| 14 | ✓ | ADC2_CH3 | **TOUCH14** | – | – | – | – | – | exposed | ADC2 conflicts with Wi-Fi |
| 15 | ✓ | ADC2_CH4 | – | – | – | – | – | – | exposed | ADC2 conflicts with Wi-Fi |
| 16 | ✓ | ADC2_CH5 | – | – | – | – | – | – | exposed | ADC2 conflicts with Wi-Fi |
| 17 | ✓ | ADC2_CH6 | – | – | – | UART1 TXD (default) | – | – | exposed | Default UART1 TX (but UART is matrix-routable) |
| 18 | ✓ | ADC2_CH7 | – | – | – | UART1 RXD (default) | – | – | exposed | Default UART1 RX (but UART is matrix-routable) |
| 19 | ✓ | ADC2_CH8 | – | – | **D-** | – | – | – | exposed | USB OTG / USB-Serial-JTAG D-. Becomes plain GPIO only if USB unused. |
| 20 | ✓ | ADC2_CH9 | – | – | **D+** | – | – | – | exposed | USB OTG / USB-Serial-JTAG D+. Becomes plain GPIO only if USB unused. |
| 21 | ✓ | – | – | – | – | – | – | – | exposed | General-purpose, no special function |
| 26 | – | – | – | – | – | – | **SPICS1** | – | not on module | Internal flash CS1 |
| 27 | – | – | – | – | – | – | **SPIHD** | – | not on module | Internal flash HOLD |
| 28 | – | – | – | – | – | – | **SPIWP** | – | not on module | Internal flash WP |
| 29 | – | – | – | – | – | – | **SPICS0** | – | not on module | Internal flash CS0 |
| 30 | – | – | – | – | – | – | **SPICLK** | – | not on module | Internal flash CLK |
| 31 | – | – | – | – | – | – | **SPIQ** | – | not on module | Internal flash MISO |
| 32 | – | – | – | – | – | – | **SPID** | – | not on module | Internal flash MOSI |
| 33 | – | – | – | – | – | – | – | **SPIIO4** (R8) | exposed | Free on R2/no-PSRAM. **Off-limits on R8.** |
| 34 | – | – | – | – | – | – | – | **SPIIO5** (R8) | exposed | Free on R2/no-PSRAM. **Off-limits on R8.** |
| 35 | – | – | – | – | – | – | – | **SPIIO6** (R8) | exposed | Free on R2/no-PSRAM. **Off-limits on R8.** |
| 36 | – | – | – | – | – | – | – | **SPIIO7** (R8) | exposed | Free on R2/no-PSRAM. **Off-limits on R8.** |
| 37 | – | – | – | – | – | – | – | **SPIDQS** (R8) | exposed | Free on R2/no-PSRAM. **Off-limits on R8.** |
| 38 | – | – | – | – | – | – | – | – | exposed | General-purpose, no special function |
| 39 | – | – | – | – | – | – | – | – | exposed | Default JTAG MTCK (when GPIO 3 routes JTAG to pins) |
| 40 | – | – | – | – | – | – | – | – | exposed | Default JTAG MTDO |
| 41 | – | – | – | – | – | – | – | – | exposed | Default JTAG MTDI |
| 42 | – | – | – | – | – | – | – | – | exposed | Default JTAG MTMS |
| 43 | – | – | – | – | – | **U0TXD** | – | – | tied to USB-UART bridge | Boot console TX. On DevKitC-1: not reclaimable. |
| 44 | – | – | – | – | – | **U0RXD** | – | – | tied to USB-UART bridge | Boot console RX. On DevKitC-1: not reclaimable. |
| 45 | – | – | – | **VDD_SPI** | – | – | – | – | exposed | Idle LOW at power-on (3.3 V flash). Internal pull-down on WROOM-1. |
| 46 | – | – | – | **ROM print** | – | – | – | – | exposed | Idle LOW at power-on (silent boot). Internal pull-down on WROOM-1. |
| 47 | – | – | – | – | – | – | – | – | exposed | General-purpose, no special function |
| 48 | – | – | – | – | – | – | – | – | WS2812 RGB LED on DevKitC-1 | Free on bare WROOM-1; LED-coupled on DevKitC-1 |

## Capabilities that are not pin-tied (GPIO matrix)

These peripherals can be routed to **any GPIO** at runtime through the IO MUX / GPIO matrix. The "default" pins shown in the matrix above are just the values the boot ROM and `idf.py menuconfig` start with — software is free to remap.

- **UART0 / UART1 / UART2** — any GPIO. Three UARTs total.
- **I²C0 / I²C1** — any GPIO. Two I²C controllers; LP-I²C also available on RTC pins.
- **SPI2 (FSPI) / SPI3 (HSPI)** — any GPIO. (SPI0/SPI1 are reserved for the in-module flash.)
- **LEDC PWM** — 8 channels, any GPIO output. Up to 14-bit resolution at lower frequencies.
- **MCPWM (motor PWM)** — 2 units × 3 operators, any GPIO.
- **RMT (remote control / pulse-train)** — 4 TX + 4 RX channels, any GPIO. Used for WS2812, IR, etc.
- **I²S0 / I²S1** — any GPIO. Two controllers.
- **SDIO host / device** — any GPIO (subject to speed; 4-bit SDIO at high speed prefers low-skew groups).
- **TWAI (CAN 2.0)** — TX/RX on any GPIO. One controller; needs an external transceiver.
- **PCNT** — pulse counter, any GPIO.
- **GPTimer** — internal, no pins.

## Quick decision tree for pin assignment

1. **Is the signal an analog input?** Pick from GPIO 1–10 (ADC1). Avoid GPIO 11–20 (ADC2) unless Wi-Fi is off.
2. **Is the signal capacitive touch?** Pick from GPIO 1–14.
3. **Is the signal USB?** GPIO 19/20, full stop.
4. **Is the signal high-speed digital (SPI > 40 MHz, HS-SDIO)?** Prefer the low-numbered pins close to the IO MUX dedicated path (GPIO 10–14 for FSPI). Otherwise the matrix-routed pins work but at lower max speed.
5. **Is the signal a slow digital I/O (I²C, UART, LEDC PWM, plain GPIO)?** Pick any free GPIO that isn't a strap, USB, flash, or PSRAM pin.
6. **Will the board sleep?** Restrict the signal to GPIO 0–21 if you need it to drive / be sampled in deep-sleep or by the LP-CPU.
7. **Strap pins last.** Only use 0/3/45/46 if the signal's reset-time idle state matches the strap default (see the Strap pins table above), and document the assumption.

## Module-suffix decoder

WROOM-1 ordering codes (relevant for which pins are usable):

| Suffix | Flash | PSRAM | Pins consumed by PSRAM |
|---|---|---|---|
| `-N4` | 4 MB | none | none — GPIO 33–37 free |
| `-N8` | 8 MB | none | none — GPIO 33–37 free |
| `-N16` | 16 MB | none | none — GPIO 33–37 free |
| `-N4R2` | 4 MB | 2 MB quad | none — GPIO 33–37 free |
| `-N8R2` | 8 MB | 2 MB quad | none — GPIO 33–37 free *(this is what kart-medulla uses)* |
| `-N16R2` | 16 MB | 2 MB quad | none — GPIO 33–37 free |
| `-N8R8` | 8 MB | 8 MB octal | **GPIO 33–37 reserved internally** |
| `-N16R8` | 16 MB | 8 MB octal | **GPIO 33–37 reserved internally** |

Quad PSRAM (`R2`) shares the SPI flash bus and consumes no extra GPIOs. Octal PSRAM (`R8`) needs four extra data lines plus DQS, which Espressif hard-wires to GPIO 33–37 inside the module.

## Other module-variant gotchas (beyond R8 PSRAM)

The R8-vs-R2 PSRAM pin reservation (GPIO 33–37) is the most common variant trap, but it is not the only one.

- **`-V` suffix → 1.8 V flash/PSRAM → GPIO 45 strap polarity flips.** Standard suffixes (`-N8R2`, `-N16R2`, `-N4`, etc.) run flash/PSRAM at **3.3 V**: GPIO 45 must idle **LOW** at reset, and the module's internal pull-down enforces this. Variants with the `-V` suffix (e.g. `-N32R8V`) run flash/PSRAM at **1.8 V**: GPIO 45 must idle **HIGH** at reset, and the module's internal pull is reversed accordingly. If you treat GPIO 45 as a regular GPIO with an idle-LOW signal on a `-V` variant (or idle-HIGH on a non-`-V` variant), the chip won't boot. The WROOM-1 family currently has no `-V` variants; the `-V` modules live in WROOM-2.
- **WROOM-2 ≠ WROOM-1.** `ESP32-S3-WROOM-2` uses **octal flash** (8 data lines into the in-package SPI flash), which consumes more internal pins than the quad-flash WROOM-1. WROOM-2 is sold only as `-H4` (octal flash, no PSRAM) or `-N32R8V` (octal flash + octal PSRAM at 1.8 V). It is **not pin-compatible** with WROOM-1 footprints — different pad map, different reservations. Treat it as a separate module family.
- **MINI-1 / MINI-1U exposes fewer GPIOs.** `ESP32-S3-MINI-1` is a smaller module (≈ 15.4 × 20.5 mm vs WROOM-1's 18 × 25.5 mm) that bonds out roughly **36 GPIOs instead of 45**. GPIO 26–32 are still reserved by internal flash, and additionally some of GPIO 33–48 are simply not pad-bonded. MINI is not a drop-in replacement for a WROOM-1 footprint.
- **Silicon revision (chip rev v0.1 vs v0.2) — not a pin issue, but a subversion gotcha.** Early ESP32-S3 silicon (v0.1) shipped with USB-Serial-JTAG errata that were fixed in v0.2. Symptom: a board flashes fine over UART but is unreliable / hangs over the native USB-JTAG bridge. The revision is printed on the chip die and reported by the bootloader on power-up. If you see this, suspect silicon revision before re-checking GPIO 19/20 wiring.
- **WROOM-1U vs WROOM-1.** The `U` suffix only swaps the on-module PCB antenna for a U.FL connector (external antenna). **No pin or strap difference** — fully interchangeable from the medulla's perspective.

In short: across WROOM-1 (N*, R2, R8) the only variant trap is the R8 PSRAM pin reservation. Across the wider ESP32-S3 module family (WROOM-2, MINI, `-V` suffixes, MINI-1U) there are several more, listed above.

## References

- Espressif, *ESP32-S3 Series Datasheet* (current revision) — pin function tables, electrical characteristics, strap-pin behavior.
- Espressif, *ESP32-S3 Technical Reference Manual* — IO MUX and GPIO matrix chapter, peripheral signal lists.
- Espressif, *ESP32-S3-WROOM-1 / WROOM-1U Datasheet* — module-form-factor pin map, internal flash/PSRAM wiring, strap-pin pull resistors.
- Espressif, *ESP32-S3-DevKitC-1 v1.1 schematic* — the DevKitC-specific quirks (USB-UART bridge on 43/44, RGB LED on 48, BOOT/RST buttons).

For the kart-medulla project's actual pin assignments and rationale, see `projects/kart-medulla/docs/pinout-kart-medulla-v1.md`.
