Title: Reading Binary Data with Python
Tags: Python, hacking
Category: Python
Date: 01-20-2020
Summary: Two ways to read binary data into a Python data structure.

[TOC]

# Overview

When you deal with external binary data in Python, there are a couple of ways to get that
data into a data structure. You can use the `ctypes` module to define the data structure
or you can use the `struct` python module.

You will see both methods used when you explore tool repositories
on the web. This article shows you how to use each one to read an IPv4 header off the network.
It's up to you to decide which method you prefer; either way will work fine.

- `ctypes` is a foreign function library for Python. It deals with C-based languages to provide
            C-compatible data types, and enables you to call functions in shared libraries.
- `struct` converts between Python values and C structs that are represented as Python bytes objects.

So `ctypes` handles binary data types in addition to a lot of other functionality, while
handling binary data is the main purpose of the `struct` module.

Let's see how these two libraries are used when we need to decode an IPv4 header off the
network.

First, here's the structure of the IPv4 header. This is from the IETF RFC 791:

```bash
A summary of the contents of the internet header follows:


    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |Version|  IHL  |Type of Service|          Total Length         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |         Identification        |Flags|      Fragment Offset    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Time to Live |    Protocol   |         Header Checksum       |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                       Source Address                          |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Destination Address                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

                    Example Internet Datagram Header
```

## Initial Data from the Network

We need some data to work with, so let's get a single packet from the network.
This little snippet show do fine. I ran this on Linux.

```python
import socket
import sys

def sniff(host):
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sniffer.bind((host, 0))

    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # read and return a single packet
    return sniffer.recvfrom(65535)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '192.168.1.69'

    buff = sniff(host)
```

We just grab a single raw packet from the network and put it into a variable, `buff`.
So now that we have binary data, let's look at how to use it.

# `ctypes` module

The following code snippet defines a new class, `IP` that
can read a packet and parse the header into its separate fields.

```python
from ctypes import *
import socket
import struct

class IP(Structure):
    _fields_ = [
        ("ihl",           c_ubyte,   4),
        ("version",       c_ubyte,   4),
        ("tos",           c_ubyte,   8),
        ("len",           c_ushort, 16),
        ("id",            c_ushort, 16),
        ("offset",        c_ushort, 16),
        ("ttl",           c_ubyte,   8),
        ("protocol_num",  c_ubyte,   8),
        ("sum",           c_ushort, 16),
        ("src",           c_uint32, 32),
        ("dst",           c_uint32, 32)
      ]
    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L",self.dst))

```

You can see that the `_fields_` structure defines each part of the header,
giving the width in bits as the last argument. Being able to specify the bit
width is handy. Our `IP` class inherits
from the `ctypes` `Structure` class, which specifies that we must have
a defined `_fields_` structure before any instance is created.

## Class Instantiation

The wrinkle with `ctypes` `Structure` abstract base class is the `__new__` method.
See the documentation for full details:
[ctypes module](https://docs.python.org/3.8/library/ctypes.html#ctypes.Structure).

The `__new__` method takes the class reference as the first argument. It creates and
returns an instance of the class, which passes to the `__init__` method.

We create the instance normally, but underneath, Python invokes the class
method `__new__`, which fills out the `_fields_` data structure immediately before
instantiation (when the `__init__` method is called). As long as
you've defined the structure beforehand, just pass the `__new__` method the
external (network packet) data, and the fields magically appear as attributes
on your instance.

# `struct` module

The `struct` module provides format characters that you used to specify the structure
of the binary data. The first character (in our case, `<`) specifies the "endianness" of the
data. See the documentation for full details:
[struct module](https://docs.python.org/3.8/library/struct.html).

```python
import ipaddress
import struct

class IP:
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xF

        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        # human readable IP addresses
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

```

Here are the individual parts of the header.

1. B 1 byte (`ver`, `hdrlen`)
2. B 1 byte `tos`
3. H 2 bytes `total len`
4. H 2 bytes `identification`
5. H 2 bytes `flags + frag offset`
6. B 1 byte `ttl`
7. B 1 byte `protocol`
8. H 2 bytes `checksum`
9. 4s 4 bytes `src ip`
10. 4s 4 bytes `dst ip`

Everything is pretty straightforward, but with `ctypes`, we could specify the bit-width
of the individual pieces. With `struct`, there's no format character for a `nybble` (4 bits),
so we have to do some manipulation to get the `ver` and `hdrlen` from the first part of
the header.

## Binary Manipulations

The wrinkle with `struct` in this example is that we need to do some manipulation
of `header[0]`, which contains a single byte but we need to create two variables
from that byte, each containing a `nybble`.

### High `nybble`

We have one byte and for the `ver` variable, we want the high-order `nybble`.
The typical way you get the
high `nybble` of a byte is to right-shift.

We right shift the byte by 4 places, which is like prepending 4 zeros
at the front so the last 4 bytes fall off, leaving us with the first `nybble`:

```bash
0 	1 	0 	1 	0 	1 	1 	0 	>> 4
-----------------------------
0 	0 	0 	0 	0 	1 	0 	1 	
```

### Low `nybble`

We have one byte and for the `hdrlen` variable, we  want the low-order `nybble`. 
The typical way you get the
low `nybble` of a byte is to `AND` it with `F` (00001111):

```bash
0 	1 	0 	1 	0 	1 	1 	0 	&F
0 	0 	0 	0 	1 	1 	1 	1 	
-----------------------------
0 	0 	0 	0 	0 	1 	1 	0 	
```

Let's look an example in the Python REPL:

```python
    >>> m = 66
    >>> m
    66
    >>> bin(m)
    '0b1000010' # or 0100 0010
    >>> bin(m>>4)
    '0b100'     # or 0100
    >>> bin(m&0xF)
    '0b10'      # or      0010

```

Now, more specifically to our IPv4 case, the first byte in the header is
always `0x45 = 69 decimal = 01000101 binary`.

See what that looks like when we right-shift
it by 4 and then `AND` it with `F`:

```python
    >>> '{0:08b}'.format(0x45)
    '01000101'
    >>> '{0:04b}'.format(0x45>>4)
    '0100'
    >>> '{0:04b}'.format(0x45&0xF)
    '0101'
```

You don't have to know binary manipulation backward and forward for decoding an IP header,
but there are some patterns like these (shift and `AND`) you will see over and over again as you code and as you explore other hackers' code.

That seems like a lot of work doesn't it? In the case where we have to do some bit
shifting, it does take effort. But for many cases (e.g. ICMP),
everything works on an 8-byte boundary and so is very
simple to set up. Here is an "Echo Reply" ICMP message;
you can see that each parameter of the ICMP header can be
defined in a `struct` with one of the existing format letters (BBHHH) (RFC777):

```bash
 Echo or Echo Reply Message

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Type      |     Code      |          Checksum             |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Identifier          |        Sequence Number        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |     Data ...
   +-+-+-+-+-
```

A quick way to parse that would simply be:

```python
class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]
```

# Conclusion

You can use either the `ctypes` module or the `struct` module to read and parse
binary data. Here is an example of instantiating the class no matter which method
you use. You instantiate the `IP` class with your packet data
in the variable `buff`:

```python
   mypacket = IP(buff)
   print(f'{mypacket.src_address} -> {mypacket.dst_address}')
```

With `ctypes`, make sure you define your `_fields_` structure and hand
the data to it in the `_new_` method. When you instantiate the class, you'll have the
access to the data attributes automatically.

With `struct`, you define how to read the data with a format string. For data attributes
that don't lie on the 8-byte boundary, you may need to do some binary manipulation.

In short, use whichever method fits your brain. But always be aware that you may see
code from others that use a different method. Hopefully, now you'll see it and
understand it.
