Title: Berkeley Packet Filtering with Scapy
Tags: Python, hacking
Status: Draft
Category: Python
Date: 01-30-2020


**Table of Contents**

[TOC]

# Overview

Scapy is a Python program and library that you can use to send, sniff and dissect and forge network packets. 
Use as-is or use it to create your own custom tools that can probe, scan or attack networks.

Documentation: (Scapy Documentation)[https://scapy.readthedocs.io/en/latest/]

automotive, bluetooth, ipv4/ipv6, 

use with Wireshark if you want.

## Scapy Usage: Interactive 

## Scapy Usage: As a Library


# BPF Filters

- protocol
- host
- and or not
- port

## Syntax


- type (host, net , port, portrange). default = host
- dir (direction: src, dst, src or dst, src and dst). default = src or dst
- proto (protocol: rarp, decnet, ether, ip, ip6, arp, tcp, icmp, udp). default = all protocols
- primitives: gateway, broadcast, less, greater, [arithmetic ops]
- on [iface]

protocols shorthand: icmptype, icmpcode, tcpflags, tcp-fin, tcp-syn, tcp-rst, tcp-push, tcp-ack, tcp-urg


    Negation (`!' or `not'). 
    Concatenation (`&&' or `and'). 
    Alternation (`||' or `or'). 


# Examples

# Addendum: lambda filters

```python
res, unans = sr( IP(dst="target")
                /TCP(flags="S", dport=(1,1024)) )
res.nsummary( lfilter=lambda (s,r): (r.haslayer(TCP) and (r.getlayer(TCP).flags & 2)) )
```