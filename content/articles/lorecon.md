---
title: "LoRecon: LoRa Reconnaissance on a $20 Board"
slug: lorecon
date: 2026-08-15
category: Security
tags: [LoRa, hacking, ESP32, Meshtastic]
summary: "A teaching walkthrough of a passive LoRa sniffer for cheap ESP32 hardware — the scanning problem it solves, exactly what it can and can't decrypt, and how the pieces fit together."
---

There is a surprising amount of radio traffic going on above your head that
nobody thinks of as a network. Meshtastic nodes relaying each other's
messages. LoRaWAN sensors reporting soil moisture. Someone's weather station,
someone's mesh of hiking radios, someone's "private" channel still running on
whatever key it shipped with. It's all in the license-free ISM bands, it's all
long-range by design, and almost none of it expects a listener.

[LoRecon](https://github.com/haksht/lorecon) is that listener. It's firmware
for a twenty-dollar ESP32 board that turns it into a self-contained LoRa
reconnaissance tool, driven from a phone over its own web interface. I wrote
it; I'll teach it the way I'd want it explained to me — starting from the one
fact that makes sniffing LoRa harder than sniffing WiFi.

# Why you can't just listen

On WiFi, one radio hears every other radio on the same channel. LoRa doesn't
work that way. "LoRa" is a modulation scheme, not a protocol — every network
built on it picks its own **frequency**, **spreading factor**, **bandwidth**,
and **coding rate**, and a receiver has to match all four before it can
demodulate anything at all. Get one of the four wrong and the transmission
isn't garbled — it's silence. You never even see it.

So a passive sniffer can't just "listen." It has to *guess*, methodically,
across every combination anyone actually uses. LoRecon carries a table of 29
such combinations, covering five network families, and cycles through them
one at a time, dwelling about twelve seconds on each before moving on. A full
lap is roughly six minutes. Whatever's in range and transmitting during its
slice gets captured, classified, and — where possible — decrypted, before the
radio retunes and moves to the next slot.

<figure class="diagram" markdown="0">
<svg viewBox="0 0 880 170" role="img" aria-labelledby="scan-title scan-desc" xmlns="http://www.w3.org/2000/svg">
<title id="scan-title">The 29-configuration scan cycle</title>
<desc id="scan-desc">A row of 29 small blocks grouped into five clusters — Meshtastic (11), LoRaWAN/TTN (7), Helium (6), MeshCore (3), and ISM (2) — with one block highlighted to show the radio's current position in the sweep.</desc>
<style>text{font-family:var(--font-mono);}</style>
<text x="30" y="24" font-size="11" letter-spacing="0.14em" fill="var(--muted)">SCAN CYCLE</text>

<!-- 29 bars: widths 22, gap 2 within a cluster, gap 14 between clusters -->
<g>
<rect x="60" y="48" width="22" height="26" fill="var(--teal)"/>
<rect x="84" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="108" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="132" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="156" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="180" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="204" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="228" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="252" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="276" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="300" y="48" width="22" height="26" fill="var(--line-strong)"/>

<rect x="336" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="360" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="384" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="408" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="432" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="456" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="480" y="48" width="22" height="26" fill="var(--line-strong)"/>

<rect x="516" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="540" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="564" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="588" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="612" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="636" y="48" width="22" height="26" fill="var(--line-strong)"/>

<rect x="672" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="696" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="720" y="48" width="22" height="26" fill="var(--line-strong)"/>

<rect x="756" y="48" width="22" height="26" fill="var(--line-strong)"/>
<rect x="780" y="48" width="22" height="26" fill="var(--line-strong)"/>
</g>

<line x1="58" y1="90" x2="822" y2="90" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="822,85 830,90 822,95" fill="var(--line-strong)"/>
<text x="60" y="108" font-size="12" fill="var(--muted)">0:00</text>
<text x="822" y="108" font-size="12" fill="var(--muted)" text-anchor="end">~6:00</text>

<text x="191" y="128" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">Meshtastic</text>
<text x="191" y="144" font-size="11.5" fill="var(--muted)" text-anchor="middle">11 configs</text>

<text x="419" y="128" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">LoRaWAN / TTN</text>
<text x="419" y="144" font-size="11.5" fill="var(--muted)" text-anchor="middle">7 configs</text>

<text x="587" y="128" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">Helium</text>
<text x="587" y="144" font-size="11.5" fill="var(--muted)" text-anchor="middle">6 configs</text>

<text x="707" y="128" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">MeshCore</text>
<text x="707" y="144" font-size="11.5" fill="var(--muted)" text-anchor="middle">3 configs</text>

<text x="779" y="128" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">ISM</text>
<text x="779" y="144" font-size="11.5" fill="var(--muted)" text-anchor="middle">2 configs</text>
</svg>
<figcaption>Twenty-nine frequency/spreading-factor/bandwidth/coding-rate combinations, grouped by the network family that uses them. The highlighted block is wherever the sweep currently sits — roughly twelve seconds per config, about six minutes for a full loop.</figcaption>
</figure>

That's also why the scan takes minutes instead of being instant: there's no
shortcut around trying each combination in turn. It's the same reason a
Meshtastic node in your backpack and a LoRaWAN sensor on someone's roof can
share the same air without ever hearing each other — they were never
listening on the same "channel" in the first place.

# What it does once it hears something

Once a packet is captured, LoRecon classifies it by protocol and tries to
open it. Three things happen, depending on what it heard:

- **Default-key decryption.** It carries 23 known and historically common
  Meshtastic channel PSKs and tries each against what it captured. For
  MeshCore, the public channel key is fixed and shipped on every device, so
  that one's automatic; a handful of common hashtag-room keys (`#general`,
  `#emergency`, and similar) are derived from the room name and tried too.
  For LoRaWAN, it checks 16 default AppKeys against any Join Request it
  catches.
- **Position extraction.** A successful decrypt of a Meshtastic `POSITION_APP`
  packet yields GPS coordinates, exportable straight to KML or GeoJSON.
- **Replay.** Ten storage slots, configurable repeat count and delay, for
  testing how your own gear reacts to a packet it's seen before.

Everything captured is reachable from a six-tab web UI the board serves
itself — over its own access point if there's no WiFi around — and exportable
as CSV or Wireshark-ready PCAP for the Python toolkit that ships in the repo:
a `report` command that turns a capture into a prioritized findings page, a
`map` command that plots extracted GPS onto an interactive map, and a
`topology` command that draws the mesh as a graph, labeling nodes with
whatever operator name it could decrypt.

# The boundary: what a default key doesn't get you

This is the part I'd want to know first if I were reading instead of writing:
**a cracked default key does not hand you someone's private messages.**

Meshtastic firmware from 2.5.0 onward split its encryption into two systems,
and it's worth understanding both, because the difference is the entire
argument for why this tool is interesting rather than alarming.

Everything a node broadcasts automatically — its position, its telemetry, its
node info, its traceroutes, routing packets, and anything typed into a
*channel* (as opposed to a direct message) — is wrapped in one shared AES key
per channel. If that key is still the factory default, which most deployments
never change, LoRecon's 23-key database opens it in one pass. That's the
finding: not that the crypto is broken, but that almost nobody rotates the
key it shipped with.

Direct messages and admin commands are different. Since firmware 2.5.0 they
get a second, independent layer — Curve25519 public-key encryption, keyed to
the *recipient's* device, whose private key never leaves that device. No
database of default values gets you through that layer, because there isn't
a shared secret to guess. It isn't weak encryption tested and found wanting;
it's the correct primitive, used correctly.

<figure class="diagram" markdown="0">
<svg viewBox="0 0 880 320" role="img" aria-labelledby="enc-title enc-desc" xmlns="http://www.w3.org/2000/svg">
<title id="enc-title">What a default channel key does and doesn't open</title>
<desc id="enc-desc">A LoRa packet passes through a shared channel-PSK layer. Automatic broadcasts such as position, telemetry, and node info become plaintext once that layer opens. Direct messages and admin commands carry a second Curve25519 layer that a channel key never opens.</desc>
<style>text{font-family:var(--font-mono);}</style>
<text x="30" y="24" font-size="11" letter-spacing="0.14em" fill="var(--muted)">ENCRYPTION BOUNDARY</text>

<text x="440" y="54" font-size="13" fill="var(--ink)" text-anchor="middle">LoRa packet, captured over the air</text>
<line x1="440" y1="62" x2="440" y2="86" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="435,86 440,94 445,86" fill="var(--line-strong)"/>

<rect x="270" y="90" width="340" height="54" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="440" y="112" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">CHANNEL PSK · AES-256-CTR</text>
<text x="440" y="130" font-size="11.5" fill="var(--muted)" text-anchor="middle">shared key — often still the factory default</text>

<line x1="440" y1="144" x2="440" y2="162" stroke="var(--line-strong)" stroke-width="1.25"/>
<line x1="230" y1="162" x2="650" y2="162" stroke="var(--line-strong)" stroke-width="1.25"/>
<line x1="230" y1="162" x2="230" y2="178" stroke="var(--line-strong)" stroke-width="1.25"/>
<line x1="650" y1="162" x2="650" y2="178" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="225,178 230,186 235,178" fill="var(--line-strong)"/>
<polygon points="645,178 650,186 655,178" fill="var(--line-strong)"/>

<rect x="70" y="180" width="320" height="120" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="230" y="202" font-size="11" letter-spacing="0.1em" fill="var(--muted)" text-anchor="middle">AUTOMATIC BROADCASTS</text>
<text x="230" y="220" font-size="12" fill="var(--ink)" text-anchor="middle">position · telemetry · nodeinfo</text>
<text x="230" y="236" font-size="12" fill="var(--ink)" text-anchor="middle">routing · channel messages</text>
<g transform="translate(218,244)" fill="none" stroke="var(--brick)" stroke-width="2">
  <rect x="2" y="12" width="20" height="14" rx="2"/>
  <path d="M6 12 V9 a6 6 0 0 1 11 -3"/>
</g>
<text x="230" y="292" font-size="12.5" font-weight="600" fill="var(--brick)" text-anchor="middle">plaintext once the key hits</text>

<rect x="490" y="180" width="320" height="120" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="650" y="202" font-size="11" letter-spacing="0.1em" fill="var(--muted)" text-anchor="middle">DIRECT MESSAGES &amp; ADMIN</text>
<text x="650" y="220" font-size="12" fill="var(--ink)" text-anchor="middle">firmware 2.5.0 and newer</text>
<text x="650" y="236" font-size="12" fill="var(--ink)" text-anchor="middle">Curve25519 key pair</text>
<g transform="translate(638,244)" fill="none" stroke="var(--teal)" stroke-width="2">
  <rect x="2" y="12" width="20" height="14" rx="2"/>
  <path d="M6 12 V8 a6 6 0 0 1 12 0 v4"/>
</g>
<text x="650" y="292" font-size="12.5" font-weight="600" fill="var(--teal)" text-anchor="middle">stays encrypted — no key for this</text>
</svg>
<figcaption>The channel PSK is one shared secret protecting everything a node sends automatically. A hit opens it all at once. Direct messages and admin commands sit behind a second, independent lock keyed to one device’s private key — a channel-PSK hit never reaches it.</figcaption>
</figure>

If an operator has set a custom channel PSK, the 23-key database simply
doesn't match anything, and the broadcasts stay encrypted blobs too. That's
the correct outcome, and honestly the whole point of running the tool against
your own mesh: one six-minute sweep tells you which side of that line you're
on.

One historical wrinkle worth knowing: before firmware 2.5.0, direct messages
were just channel messages with a destination field, protected by the same
shared key as everything else. Pre-2.5.0 devices don't get the Curve25519
protection at all. If you're auditing an older deployment, "we're on the
default key" and "our DMs are private" are not both true at once.

# From antenna to report

None of this needs a laptop in the field, and none of it needs a cloud
service. The whole pipeline fits on the board and the phone in your pocket:

<figure class="diagram" markdown="0">
<svg viewBox="0 0 880 200" role="img" aria-labelledby="path-title path-desc" xmlns="http://www.w3.org/2000/svg">
<title id="path-title">LoRecon's end-to-end data path</title>
<desc id="path-desc">LoRa RF flows one-way into the ESP32 board, which serves a web UI to a phone or laptop over WiFi. Captures export as CSV, PCAP, KML, or GeoJSON to Python tools that run entirely offline.</desc>
<style>text{font-family:var(--font-mono);}</style>
<text x="440" y="24" font-size="11" letter-spacing="0.14em" fill="var(--muted)" text-anchor="middle">END-TO-END DATA PATH</text>
<text x="440" y="44" font-size="12.5" fill="var(--muted)" text-anchor="middle">no cloud in this picture — a phone is enough, and every analysis step after export runs offline</text>

<rect x="16" y="90" width="130" height="70" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="81" y="120" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">LoRa RF</text>
<text x="81" y="138" font-size="10.5" fill="var(--muted)" text-anchor="middle">passive reception</text>

<line x1="146" y1="125" x2="228" y2="125" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="228,120 236,125 228,130" fill="var(--line-strong)"/>
<text x="191" y="112" font-size="10.5" fill="var(--ink)" text-anchor="middle">receive only</text>
<text x="191" y="178" font-size="10" fill="var(--brick)" text-anchor="middle">(no transmit path)</text>

<rect x="236" y="90" width="150" height="70" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="311" y="120" font-size="12" font-weight="600" fill="var(--ink)" text-anchor="middle">ESP32-S3 + SX1262</text>
<text x="311" y="138" font-size="10.5" fill="var(--muted)" text-anchor="middle">scans &amp; decrypts</text>

<line x1="386" y1="125" x2="438" y2="125" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="438,120 446,125 438,130" fill="var(--line-strong)"/>
<text x="416" y="112" font-size="10.5" fill="var(--ink)" text-anchor="middle">WiFi</text>

<rect x="446" y="90" width="150" height="70" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="521" y="120" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">Phone or laptop</text>
<text x="521" y="138" font-size="10.5" fill="var(--muted)" text-anchor="middle">web UI, no install</text>

<line x1="596" y1="125" x2="648" y2="125" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="648,120 656,125 648,130" fill="var(--line-strong)"/>
<text x="626" y="112" font-size="10.5" fill="var(--ink)" text-anchor="middle">export</text>

<rect x="656" y="90" width="214" height="70" rx="4" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="763" y="120" font-size="12.5" font-weight="600" fill="var(--ink)" text-anchor="middle">Python toolkit</text>
<text x="763" y="138" font-size="10.5" fill="var(--muted)" text-anchor="middle">report · map · topology</text>
</svg>
<figcaption>CSV, PCAP, KML, and GeoJSON move the data from device to disk; `lorecon report`, `lorecon map`, and `lorecon topology` turn a saved capture into a findings page, a GPS map, and a mesh graph — all of it running on a machine that never has to touch the internet.</figcaption>
</figure>

The RF leg is drawn one-way on purpose. LoRecon never transmits — replay
writes to storage slots you trigger manually, but nothing goes out over the
air unless you ask it to, and normal operation is receive-only from power-on.

# Choosing hardware

Four boards run the same firmware and the same web UI; the differences are
about what you need in the field, not what the tool can do:

| Board | Why you'd pick it |
| --- | --- |
| Heltec WiFi LoRa 32 V3 | Cheapest, most proven. Start here. |
| Heltec WiFi LoRa 32 V4 | Optional L76K GPS, native USB |
| LilyGO T3-S3 | SD card slot — log PCAP/CSV to disk in the field |
| LilyGO T-Beam Supreme | SD, GPS, battery management, and 8 MB of PSRAM |

That last column, PSRAM, isn't a spec-sheet flourish. A long unattended
capture dies of heap fragmentation on a bare ESP32 long before anything
conceptually interesting happens to it; the T-Beam Supreme with PSRAM enabled
holds roughly 130 KB of minimum free heap after twenty hours with fifty
devices in range, against about 53 KB without. Most of the recent release
cycle was stability engineering of exactly that flavor — chunked API
responses, heap guards, crash context that survives a reboot.

# Try it yourself

There's a browser-based installer, so getting a board running doesn't require
touching a toolchain:

<https://haksht.github.io/lorecon/install/> — plug the board in, open the
page in Chrome or Edge, click flash.

If you want the Python analysis toolkit too — `report`, `map`, `topology`,
and the rest — that lives in the source repo, not the binary release, so
you'll want to clone it:

```
git clone https://github.com/haksht/lorecon.git
cd lorecon
python -m venv venv
venv\Scripts\activate.ps1        # or ./venv/bin/activate on macOS/Linux
pip install -e .
```

`lorecon --help` confirms the install worked. From there, `lorecon report
capture.csv` is the first thing worth running against anything you capture.

Building the firmware yourself is PlatformIO, with OTA updates available
after the first USB flash. MIT licensed. Current release is 2.6.0.

<span class="note">Note: </span>This is for networks you own or have written permission to test. Passive reception is generally legal in the US; interception of content can implicate 18 U.S.C. § 2511, and the rules vary considerably by jurisdiction. The default-key testing exists to demonstrate a risk, not to hand anyone a way into someone else's traffic.
{: .callout}

# Learn more

The repo's `docs/` folder is the fuller version of everything above:

- [SETUP.md](https://github.com/haksht/lorecon/blob/main/docs/SETUP.md) — flashing, first boot, WiFi provisioning
- [USAGE.md](https://github.com/haksht/lorecon/blob/main/docs/USAGE.md) — the web UI and field deployment
- [TOOLS.md](https://github.com/haksht/lorecon/blob/main/docs/TOOLS.md) — the full Python toolkit reference
- [reference/ENCRYPTION.md](https://github.com/haksht/lorecon/blob/main/docs/reference/ENCRYPTION.md) — exactly what's decryptable and why, in more depth than the section above
- [reference/NETWORK_HUNTING.md](https://github.com/haksht/lorecon/blob/main/docs/reference/NETWORK_HUNTING.md) — the full 29-config table, and where each network family tends to show up
- [developers/ARCHITECTURE.md](https://github.com/haksht/lorecon/blob/main/docs/developers/ARCHITECTURE.md) — how the firmware itself is put together, for anyone extending it

# Credit where it's due

I wrote the firmware and the tooling. The hardware side — board selection,
the antenna and power work, and the field testing that turned up most of the
bugs worth fixing — is [The-Foe](https://github.com/The-Foe), who I share the
[haksht](https://github.com/haksht) org with. A sniffer that works on the
bench and falls over after six hours in a bag is not a sniffer, and finding
that out is its own skill.

The repo is at **[github.com/haksht/lorecon](https://github.com/haksht/lorecon)**.
If it's useful to you, a star helps other people find it.
