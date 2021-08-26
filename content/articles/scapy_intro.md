Title: `Scapy` Tips: IPv6 and Berkeley Packet Filtering
Tags: Python, hacking
Status: Draft
Category: Python
Date: 01-30-2020

**Table of Contents**

[TOC]

# Overview

`Scapy` is a Python program and library that you can use to send, sniff, dissect and forge network packets.
`Scapy` is a powerful interactive packet manipulation program (in Python). It is able to forge or decode packets of a wide number of protocols, send them on the wire, capture them, match requests and replies, and much more.
Use as-is or use it to create your own custom tools that can probe, scan or attack networks.

Documentation: (`Scapy` Documentation)<https://scapy.readthedocs.io/en/latest/>

automotive, bluetooth, `ipv4`/`ipv6`

use with Wireshark if you want:

```python
# First, generate some packets...
packets = IP(src="172.20.10.3", dst=Net("172.20.10/30"))/ICMP()

# Show them with Wireshark
wireshark(packets)

packets = IP(src="fe80::4a7:8c:5d62:9e0e", dst=Net("google.com"))/ICMP()
wireshark(packets)
```

## `Scapy` Usage: Interactive

## `Scapy` Usage: As a Library

# BPF Filters

Some of the tools they built: `tcpdump`, `libpcap`, `traceroute`

The general format of a filter is `id` `qualifier` `qualifier` ... `qualifer`
Documentation with many examples: (tcpdump)<https://www.packetlevel.ch/html/tcpdumpf.html>
Qualifiers might be:

- type of thing (`host`, `net`, `port`, `portrange`)
- direction (`src`, `dst`)
- protocol (`ether`, `ip`, `ip6`, `arp`, `tcp`, `udp`)

You can even look into the protocol data inside the packet with syntax `proto[ expr: size]`. For example:
`ip[0] & 0xf != 5` catches all IPv4 packets with options. You can use some special shorthands for some fields, 
like with ICMP you can find the `icmp_echoreply`, `icmp-unreach`, etc.

With these qualifiers, you can make up some pretty complex expressions by joining them with `and`, `or`, and `not`. Here's an example that selects IPv4 packets traveling between `pserver` and any other host except for the `db03_unx`.

```bash
ip host pserver and not db03_unx
```

Or say you want to see all the ICMP packets that are not ping request/replies. You can use some built-in shorthands like this:

```bash
icmp[icmptype] != icmp-echo and icmp[icmptype] != icmp-echoreply
```

or, to accomplish the same thing but for IPv6:

```bash
icmp6[icmp6type] != icmp6-echo and icmp6[icmp6type] != icmp6-echoreply
```

## Syntax

- type (`host`, `net` , `port`, `portrange`). default = `host`
- dir (direction: `src`, `dst`, `src or dst`, `src and dst`). default = `src or dst`
- protocol (`rarp`, `ether`, `ip`, `ip6`, `arp`, `tcp`, `icmp`, `udp`). default = all protocols
- primitives `gateway`, `broadcast`, less, greater, [arithmetic ops]
- on `iface`

protocols shorthand: `icmptype`, `icmpcode`, `tcpflags`, `tcp-fin`, `tcp-syn`, `tcp-rst`, `tcp-push`, `tcp-ack`, `tcp-urg`

- Negation (`!` or `not`)
- Concatenation (`&&` or `and`)
- Alternation (`||` or `or`)

# Examples

# Addendum: lambda filters

```python
res, unans = sr( IP(dst="target")
                /TCP(flags="S", dport=(1,1024)) )
res.nsummary( lfilter=lambda (s,r): (r.haslayer(TCP) and (r.getlayer(TCP).flags & 2)) )
```

## IPv6

- google says 30% of traffic is now `ipv6`
- in the US, it's about 50%
- 1998 became an IETF standard
- address exhaustion
- IPSec was mandatory, now it's optional
- firewalls with `ipv4` locked down may have `ipv6` wide open

## Dangers

You may be using IPv6 and not be aware of it. You might be able to take advantage of situations where IPv4 is locked down tight but IPv6 traffic is wide open.

## Neighbor Discovery

like `arp` and can be spoofed like `arp` poisoning

# `Scapy` and IPv6: Scanning

# Spoofing Neighbors
