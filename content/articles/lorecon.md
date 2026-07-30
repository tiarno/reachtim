---
title: "LoRecon: LoRa Reconnaissance on a $20 Board"
slug: lorecon
date: 2026-07-30
category: Security
tags: [LoRa, hacking, ESP32, Meshtastic]
summary: "A passive LoRa sniffer for cheap ESP32 hardware — what it sees, what it can't, and why default encryption keys are the interesting part."
---

There is a surprising amount of radio traffic going on above your head that
nobody thinks of as a network. Meshtastic nodes chatting to each other. LoRaWAN
sensors reporting soil moisture. Somebody's weather station. It's all in the ISM
bands, it's all long-range by design, and a great deal of it is running on
whatever encryption key it shipped with.

[LoRecon](https://github.com/haksht/lorecon) is a passive sniffer for that
traffic. It runs on an ESP32-S3 board with an SX1262 radio — the cheapest
supported one is about twenty dollars — and it turns that board into a
self-contained reconnaissance tool with a web interface you can drive from your
phone.

# What it does

The core problem with sniffing LoRa is that "LoRa" isn't one thing. Spreading
factor, bandwidth, coding rate and frequency all have to match before you hear
anything at all, and every network picks its own combination. So the firmware
cycles through 29 known configurations — the Meshtastic presets, LoRaWAN/TTN,
Helium, MeshCore, plain ISM — and gives each one a slice of time. A full sweep
takes about six minutes. Anything it hears gets captured, timestamped and
classified.

From there:

- **Default-key decryption.** It carries the 23 default Meshtastic PSKs and
  tries them against what it captures. It also handles MeshCore public channels
  and the common hashtag rooms. For LoRaWAN it checks 16 default AppKeys against
  captured Join Requests.
- **Position extraction.** Decrypted Meshtastic `POSITION_APP` packets give up
  GPS coordinates, which you can export straight to KML or GeoJSON and open in
  a map.
- **Replay.** Ten slots, configurable repeat and delay, for testing your own
  gear's behaviour.
- **Export that goes somewhere useful.** CSV, and PCAP that opens in Wireshark
  with a dissector. There's a Python toolkit in the repo for the analysis you'd
  rather not do on a microcontroller — topology graphs, mapping, reporting.

All of it is reachable from a six-tab web UI served by the board itself, over
its own access point if there's no WiFi around.

# What it can't do, which is the more interesting half

This is the part I'd want to know first, so: **it does not read your direct
messages.**

Meshtastic 2.5.0 moved DMs and admin messages to Curve25519 public-key
encryption. Those need the recipient's private key, and no amount of default-PSK
guessing gets you there. What the channel PSK still protects — and therefore
what a default key exposes — is everything automatic: position broadcasts,
telemetry, node info, traceroutes, routing packets, and channel messages.

That's the actual finding, and it's why the tool tests default keys at all. A
node running the factory key is quietly broadcasting where it is, what hardware
it's on, and who it can reach. Not because the crypto is broken, but because
nobody changed the key. Point the sniffer at your own mesh and you'll know
within one sweep whether that's you.

If someone has set a custom PSK, the 23-key database simply doesn't match and
you get encrypted blobs. Which is the correct outcome, and the whole argument
for doing it.

# Hardware

Four boards are supported, and the differences matter more than the price gap
suggests:

| Board | Why you'd pick it |
| --- | --- |
| Heltec WiFi LoRa 32 V3 | Cheapest, most proven. Start here. |
| Heltec WiFi LoRa 32 V4 | Optional L76K GPS, native USB |
| LilyGO T3-S3 | SD card slot — log PCAP/CSV to disk in the field |
| LilyGO T-Beam Supreme | SD, GPS, battery management, and 8 MB of PSRAM |

That PSRAM entry is not a spec-sheet flourish. Long runs on a bare ESP32 die of
heap fragmentation, not of anything conceptually interesting; the Supreme with
PSRAM sits at ~130 KB minimum free heap over twenty hours with fifty devices in
range, against ~53 KB without. Most of the last two releases were stability work
of exactly that flavour.

# Trying it

There's a web installer, so you don't have to touch a toolchain to get started —
plug the board in, open the page in Chrome or Edge, click flash:

<https://haksht.github.io/lorecon/install/>

If you want to build it yourself it's PlatformIO, with OTA updates once you're
past the first flash. MIT licensed. Current release is 2.6.0.

<span class="note">Note: </span>This is for networks you own or have written permission to test. Passive reception is generally legal in the US; interception of content can implicate 18 U.S.C. § 2511, and the rules vary considerably by jurisdiction. The default-key testing exists to demonstrate a risk, not to hand anyone a way into someone else's traffic.
{: .callout}

# Credit where it's due

I wrote the firmware and the tooling. The hardware side — board selection, the
antenna and power work, and the field testing that turned up most of the bugs
worth fixing — is [The-Foe](https://github.com/The-Foe), who I share the
[haksht](https://github.com/haksht) org with. A sniffer that works on the bench
and falls over after six hours in a bag is not a sniffer, and finding that out
is its own skill.

The repo is at **[github.com/haksht/lorecon](https://github.com/haksht/lorecon)**.
If it's useful to you, a star helps other people find it.
