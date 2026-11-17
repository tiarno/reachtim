---
title: "The GPS That Was Certain, and Wrong"
slug: gps-certain-and-wrong
date: 2026-09-03
category: Security
tags: [GNSS, RTK, RTKLIB, vulnerability-research, drones]
summary: "A single fake antenna name can move a survey rover two metres while it insists it has a perfect fix -- or, on a differently-compiled copy of the same program, bring a drone down within tens of metres of wherever the attacker chooses. A walk through how, for people who have never touched GPS software."
---

There's a bug in a piece of free software called RTKLIB that turns a very
precise GPS receiver into one that's wrong by a couple of metres while it
reports that its answer is perfect. No crash, no warning, nothing in the log.

In a simulated drone flight, the aircraft flew to the point it was sent to,
announced arrival, and landed normally, about a metre and a half from where it
believed it was. Built with one different compiler setting, the same software
crashed instead, and the drone came down on the attacker's cue.

This post walks through how that works, for people who have never thought about
GPS software. If you already know what a mantissa is, skim the middle.

*Status as of 2026-11-16. Dates are absolute so the post stays readable after
the week it was written.*

---

# How GPS knows where you are

A GPS satellite does one useful thing. It shouts the time, constantly and very
accurately.

Your receiver listens to several of those shouts at once. It knows how fast
radio travels and roughly what time it is, so it can work out how long each
signal took to arrive. Multiply by the speed of light and you have a distance to
each satellite. With four or more distances there's only one point in space you
can be standing.

That gets you within a few metres. Fine for finding a restaurant; useless for
surveying a property line, steering a tractor between last year's rows, or
landing a drone on a platform.

The few metres come from the atmosphere. The ionosphere slows the signal a bit,
the troposphere slows it a bit differently, and the satellite's own clock and
orbit are known slightly imperfectly. Each adds a small error to every distance.

Those errors are almost identical for two receivers standing near each other,
because the same patch of sky sits over both of them.

# RTK: getting to centimetres

If two receivers a few kilometres apart are being lied to the same way, and one
of them already knows exactly where it is, it can measure the lie and tell the
other one. That's Real-Time Kinematic positioning, RTK. It has two halves:

- A **base station**, bolted to something that doesn't move, at a location
  surveyed in advance to the centimetre.
- A **rover**, the receiver that's going somewhere: a survey pole, a tractor,
  a drone.

```
                      *       *       *          GPS satellites
                       \      |      /
                        \     |     /            the same signals,
                         \    |    /             carrying the same errors
        ~~~~~~~~~~~~~~~~~~\~~~|~~~/~~~~~~~~~~~~~~~~~~~~~~~~
              atmosphere   \  |  /   (slows both of them, equally)
        ~~~~~~~~~~~~~~~~~~~~\~|~/~~~~~~~~~~~~~~~~~~~~~~~~~~
                             \|/
                    +---------+                +---------+
                    |  BASE   | =============> |  ROVER  |
                    +---------+   corrections  +---------+
                  bolted down,                  on a pole,
                  knows exactly                 a tractor,
                  where it is                   a drone

                  "the errors right      "thanks - subtracting
                   now are THIS big"      them from mine"
```

The base computes what each satellite distance *should* be, compares that with
what it measures, and streams the difference to the rover over radio, the
internet, or a phone link. The rover subtracts it, the shared error cancels, and
a few metres becomes one or two centimetres. Farms, construction sites,
surveyors, and mapping drones all run on this.

## The linchpin

The whole scheme rests on one number, **the base station's stated position.**

RTK measures the distance and direction from the base to the rover, very
precisely, then adds that to the base's stated position. If the base's
coordinate is off by two metres, every position the rover produces is off by the
same two metres. The rover has accurately measured its distance from a lie.

Nothing about that looks like an error. The rover's confidence checks look at
the quality of the measurements, and the measurements are good. Only the
starting point is wrong. That starting point is the target.

# The software and the message

RTKLIB is an open-source library that implements all of this, written by Tomoji
Takasu. It's excellent, and for years it was the only way to do serious RTK
without buying proprietary gear. It runs in Windows tools surveyors use, it's
packaged by Linux distributions, a popular fork called demo5 is what most
hobbyists use, and its code has been folded into commercial receivers. The
stable branch hasn't had a commit since December 2020.

The base talks to the rover in a format called RTCM3. Most messages carry
corrections. A few are housekeeping, and type 1033 is one of those. It
carries five pieces of text describing the base station's hardware: antenna
model, antenna serial number, receiver model, receiver firmware version, and
receiver serial number. Labels like `TRIMBLE NETR9`. Nobody navigates by them.

Each string is sent as a length, then that many characters, like an envelope
with the page count written on the outside. The length is a single byte, so it
can say anything from 0 to 255.

# The bug

RTKLIB keeps a 64-character slot for each of those five strings. Real receiver
names are far shorter.

When the code reads characters off the wire, it uses a 32-character holding area
and reads at most 31 characters, whatever the envelope says. That part is
careful. When it copies that text into the 64-character slot, though, it uses
the length the sender declared. So a message that says "the receiver model
is 255 characters long" gets 255 characters copied into a space built for 64,
and the copy runs about 190 bytes past the end.

```
  memory:  receiver-model slot      other fields        BASE COORDINATES
           |<--- 64 bytes --->|                       |<-X-><-Y-><-Z->|
          +-------------------+----------------------+-----+-----+-----+
          | TRIMBLE NETR9     |  serial, version...  |     |     |     |
          +-------------------+----------------------+-----+-----+-----+
           ^                  ^                            ^
           |                  |                            |
           |   the slot ends here                          |
           |                                               |
           |<===== "I am 255 characters long" =============>|
                 31 real       then zeros, zeros, zeros...
                 characters
```

The security firm FuzzingLabs found and reported this overflow, along with three
similar ones, on 2026-06-09. This post follows where the overflow lands and what
that does to the receiver.

## Why it looks harmless

If you've done exploit work, a buffer overflow suggests a takeover. Two details
rule that out here.

First, **everything written past the end is zeros.** The copy stops at the end
of the real text and pads the rest of the declared length with zeros, and at
most 31 real characters were ever read. The attacker can't write chosen bytes out
of bounds. They can only erase, starting where they choose and going as far as
they choose. Think of it as an eraser.

Second, **the write stays inside its container.** The 64-character slot sits
inside a structure of around 240 kilobytes, and the worst case reaches a few
hundred bytes past the slot. No return addresses, no function pointers. The
common memory checkers watch the edges of whole allocations, so a write that
crosses a field boundary inside one passes them silently. A check that knows each
field's size catches it at once.

So it's a bug that writes zeros into the middle of a big object it can't escape.
That would be the end of it, except for what sits a couple of hundred bytes past
the receiver-model slot.

# What the zeros land on

They land on the base station's coordinates: three numbers, X, Y and Z, in a
coordinate system centred on the Earth. The number the whole system trusts.

An attacker who could write chosen values would just type in a new location.
This one can only write zeros. So what does erasing part of a number do to it?
That takes a short detour into how computers store numbers with decimal points.

## Scientific notation, in binary

You know scientific notation. Instead of `3,978,242.4348` you write
`3.9782424348 × 10⁶`. That's two pieces of information, the digits and where
the decimal point goes.

Computers store these numbers the same way, in binary. The format is called a
*double*, it takes 8 bytes, and the bytes split into three parts:

| part | size | what it does |
|---|---|---|
| sign | 1 bit | positive or negative |
| **exponent** | 11 bits | where the point goes, the overall scale |
| **mantissa** | 52 bits | the actual digits |

The **mantissa** is the digits. For a number around four million, which is
about what our coordinate is in metres, 52 binary digits pin it down to under
half a nanometre.

## Now erase some digits

On essentially every computer you'll meet, a double's 8 bytes are stored
least important digits first. So the eraser destroys the fine detail first
and only reaches the digits that matter as it keeps going.

```
  one coordinate = one double = 8 bytes

   byte 0     1     2     3     4     5     6     7
      +-----+-----+-----+-----+-----+-----+-----+-----+
      |     |     |     |     |     |     |     |     |
      +-----+-----+-----+-----+-----+-----+-----+-----+
      |<------- mantissa: the digits ------->|<-exp->|s|
      |                                      |
      | finest detail            coarsest detail
      | (billionths of a mm)     (metres, then hundreds of metres)
      |
      +-- the eraser starts HERE and works rightwards
          so precision is destroyed from the bottom up
```

Each erased byte removes 8 binary digits of precision, and the number becomes a
rounder version of itself. Picture a ruler marked in millimetres. Rub out
most of the marks and you can only read to the nearest centimetre; rub out more
and you're down to the nearest metre. The ruler still gives sensible-looking
answers. They're just coarser, and anything between the surviving marks snaps to
a mark.

Here's that on a real coordinate from the test data, a base station at
X = `-3,978,242.4348` metres:

```
  FULL PRECISION - every fine gradation still present

    -3978244        -3978243        -3978242        -3978241
   -----|---------------|---------------|---------------|----->
                                 x
                                 |
                                 +--- true position of the base:
                                      -3978242.4348


  ERASE 4 BYTES - only every 2 metres survives

    -3978244                        -3978242
   -----|-------------------------------|---------------------->
                                 x      |
                                 |      |
                                 +----->+
                                  snaps to the nearest
                                  surviving mark, toward zero

                                  new coordinate: -3978242.0000
                                  the base has "moved" 0.43 m
```

Erasing always rounds toward zero, so the direction comes from the
station's own coordinate, and the attacker doesn't get to pick it. Here's every
rung on the same coordinate. The coordinate sits 208 bytes past the start of the
field, so a declared length of 208 erases one byte and each extra unit erases
one more:

| bytes erased | declared length | resulting grid | coordinate becomes | error |
|---|---|---|---|---|
| 1 | 208 | 0.00012 mm | −3978242.4348 | none you could measure |
| 2 | 209 | 0.03 mm | −3978242.4348 | none you could measure |
| 3 | 210 | 8 mm | −3978242.4297 | **5 mm** |
| 4 | 211 | **2 m** | −3978242.0000 | **0.43 m** |
| 5 | 212 | 512 m | −3978240.0000 | **2.43 m** |
| 6 | 213 | 131 km | −3932160.0000 | 46 km |

Each extra byte makes the grid 256 times coarser. That means the attacker picks
the *scale* of the error and the station's coordinate decides the exact amount.

The grid for a given rung depends only on which power of two the coordinate
falls between, and that depends on where on Earth the station is. So an
attacker who knows roughly where the target is can pick the rung without knowing
the coordinate. Across the globe, about a third of locations get a 2-metre grid
at the 4-byte rung, a third get 4 metres, and the rest get 1 metre or finer. The
attack is weakest around the Mississippi valley and strongest at low to middle
latitudes near the prime meridian and its opposite: southern Europe, Africa,
eastern Australia, New Zealand.

Below the right rung, the error is too small to matter. Above it, the error is
so large that the receiver stops giving a confident answer. For most of the
planet there's a band in between where the damage matters and stays invisible.

# The message triggers its own damage

When RTKLIB finishes decoding a type 1033, it reports "this was an antenna
information message." The real-time server responds by taking the base
coordinates and adopting them as the reference for every position it computes
from then on, without checking them.

So one message both corrupts the coordinate and puts it into service.

It doesn't last on its own. A working base repeats its true coordinates every
few seconds in a type 1005 message, and the next one puts the right value back.
To keep the error in place, the attacker re-sends after every 1005, which is
what the test harnesses do. The silent attack needs a transmitter that keeps
running.

RTKLIB's other code path, the one that processes recorded data after the fact,
does check. It refuses a base coordinate of exactly zero. That would catch a
fully erased coordinate. It wouldn't catch one rounded off by a couple of
metres. The live path, the one taking bytes off a radio, has no check at all.

## Couldn't an attacker just send a fake coordinate?

They could. The correction link has no authentication, so anyone who can transmit on
it can send their own type 1005 with any base coordinate they like, and every
RTK receiver will believe it. That needs no bug.

This bug adds three things:

- **The attacker doesn't need to know where the base is.** A fake 1005 that
  moves the base two metres has to start from the true coordinate. This bug
  rounds off whatever's already in memory.
- **It arrives in a message tamper monitoring isn't built to inspect.** Anything
  watching a correction stream for a moved base looks at the 1005s. A 1033 is supposed to carry an
  antenna name.
- **On a hardened build it's a kill switch.** No well-formed 1005 can crash the
  receiver. This message can, as you'll see below.

The underlying problem is the unauthenticated link. This bug is one sharp
example of what that allows.

# What the receiver does about it

The receiver doesn't react at all. I ran a clean data set and an attacked one
all the way through and compared them position by position. This run used the 5-byte rung, which gave a
big, unmistakable number against this station:

| | clean | attacked |
|---|---|---|
| positions produced | 85 | 85 |
| flagged "RTK FIXED" (best quality) | 17 | 17 |
| flagged "float" (second best) | 68 | 68 |
| any quality flag different, at any moment? | — | **no** |
| how far the position moved | — | **2.435 m** |

The position moved by exactly the injected error, and **the quality flags were
identical** at every moment. The receiver's flags describe how well it solved
the geometry, and it solved the geometry beautifully. It has no way to question
the starting point it was handed.

The logs don't help either. RTKLIB's diagnostic log does record each 1033, but
it prints the 31-character holding buffer, which the attacker can make look
completely ordinary. **The declared length, the number that does the damage, is
never logged at any verbosity.** The step that puts the corrupted coordinate
into service isn't logged at all; the only trace is a counter ticking up by one.
At maximum logging, an operator sees a plausible antenna name and no record that
the base coordinates changed.

# The compiler setting

C compilers on Linux have an optional safety feature, glibc's
`_FORTIFY_SOURCE`. With it on, certain copies get a check: *does this fit where
it's going?* If not, the program kills itself. The copy in this bug is exactly
that kind, so on a hardened build the program dies instead of corrupting
anything. One message is a remote crash.

Which builds have it? Almost none of the ones measured:

- **Both Windows distributions**, the official tools and the demo5 fork, wrote
  a corrupted base coordinate into their output files and exited cleanly. The
  feature belongs to the GNU C library, and these are built against different
  libraries where it doesn't exist.
- **Debian's package**, at the exact version studied here, has no hardened
  functions anywhere in the ARM binary, despite Debian's policy asking for them.
  The likeliest cause is RTKLIB's build files overriding the flags the
  distribution injects.
- **The feature comes in levels.** At level 2 the same message crashed the
  program. At level 1 the write went through and moved the coordinate, because
  at that level the check doesn't know the destination field's size.

So the crash is mostly what you get by compiling RTKLIB yourself at level 2. The
one product exception is current firmware for Emlid's Reach M2 and RS2, covered
below.

*(A footnote on processors: the memory layout that decides which erasures reach
the coordinate is identical on the six architectures checked, 32-bit and 64-bit
alike, so the same message works on all of them unchanged. Older 32-bit PCs pack
the record four bytes tighter, so the message needs a slightly shorter name
there. And on processors that store numbers big end first, the same erasure
wipes out the coordinate entirely, so the attack turns loud.)*

# Flying it

To see what a vehicle does, I built a closed loop. A simulated drone's true
position feeds a synthetic GPS signal generator, which feeds RTKLIB, whose
output is the autopilot's only GPS. The malicious message is spliced into the
correction stream mid-flight, as it would arrive over a radio link.

```
        real base station                    ATTACKER
        (legitimate corrections)             (one fake antenna-name message)
                  |                                |
                  +--------------+-----------------+
                                 |
                                 v
                        unauthenticated radio link
                                 |
                                 v
                        +------------------+
                        |     RTKLIB       |  <-- base coordinate corrupted
                        +------------------+      here, and adopted here
                                 |
                              position
                                 |
                                 v
                        +------------------+
                        |    autopilot     |
                        +------------------+
                                 |
                                 v
                           vehicle moves
                                 |
        +------------------------+
        |   (and its true position becomes the
        v    input to the GPS simulation, closing the loop)
```

Same aircraft, same flight plan, same message, flown twice. The only difference
was which build of RTKLIB was in the loop.

**The usual build.** The drone took off, hovered, received the message, and
carried on. Sent to a point 30 metres away, it flew there, announced arrival,
and landed normally, 1.4 metres from where it believed it was. Its flight log
has zero errors, and GPS quality read best-possible from takeoff to
touchdown.

**The hardened build.** The message arrives while the drone hovers:

```
87.5 s   GPS quality: BEST -> NONE        (RTKLIB has just died)
91.4 s   ERROR: EKF primary changed
91.5 s   ERROR: EKF variance
91.5 s   ERROR: navigation failsafe
91.5 s   MODE -> LAND                     "EKF Failsafe: changed to Land Mode"
105.9 s  SmartRTL deactivated: bad position
120.6 s  Hit ground at 0.50 m/s
122.7 s  Disarming motors
```

Four seconds from losing GPS to declaring an emergency, and 33 seconds to the
ground, touching down at half a metre per second. That's a controlled landing, with four
errors logged along the way.

Autonomous systems are built to handle *"my sensor stopped working."* That's an
expected condition with a plan: alarm, stop, land. Almost nothing is built to
handle *"my sensor is confidently wrong,"* because there's no signal to react
to. On the question of whether anyone finds out, the crash is the better
outcome.

# The crash is an attack too

Look at one line from that log:

```
105.9 s  SmartRTL deactivated: bad position
```

With no position, the drone couldn't fly home. Its only option was to land where
it was, and the attacker decides when that happens. Someone who can see the
target can wait until it's over a lake or the far side of a fence, then send one
message.

How well can that be aimed? With no position estimate the drone can't hold
station, so it drifts during the descent:

| | |
|---|---|
| height when the emergency fired | 15 metres |
| descent | 29 seconds |
| **sideways drift before touchdown** | **10.13 metres** |
| character of the drift | one direction, never corrected |

So the attacker picks a circle tens of metres across. Good enough for a lake,
too coarse for a particular lane of traffic. Two runs drifted 10.13 and 10.76
metres, both with no wind, a low drone, and almost no forward speed, so treat
10 metres as a best case. A
pilot watching can take over and fly by hand. An unattended automated flight
can't be rescued.

```
                    ONE MALICIOUS MESSAGE
                             |
              +--------------+--------------+
              |                             |
       build without the            build with the
       safety check                 safety check
       (most builds)                (current Emlid M2/RS2,
                                     or compile it yourself)
              |                             |
              v                             v
       coordinate quietly            the program dies
       wrong by a few m                     |
              |                             v
              v                      aircraft loses GPS,
       vehicle flies on,             cannot fly home,
       reports success,              lands within ~10 m
       logs ZERO errors              of the attacker's choosing
              |                             |
              v                             v
      +----------------+           +------------------+
      | SILENT ATTACK  |           |   LOUD ATTACK    |
      | on ACCURACY    |           | on AVAILABILITY  |
      +----------------+           +------------------+
       nobody finds out             everybody finds out,
                                    but it is on the ground
```

| | the usual build | the hardened build |
|---|---|---|
| what it does | moves the reported position | brings the aircraft down |
| magnitude | a few metres, before it starts looking wrong | total |
| does anyone notice? | **no** | yes, immediately |
| how long it lasts | until the next real 1005, so it's re-sent every few seconds | one message is enough |
| useful for | quietly ruining survey, farm, or landing accuracy | taking an aircraft down at a chosen moment |

If the goal is to put a drone in a lake, the hardened build is the better tool.
Two metres of silent error won't do it; a forced landing will. Turning on the
compiler's safety feature trades a quiet attack for a loud one. That's a good
trade if you care about knowing you were attacked, and most people do, but it
leaves the bug in place.

# The fix

Refuse to believe a declared length bigger than what was actually read:

```c
if (n >31) n =31;
if (m >31) m =31;
if (n1>31) n1=31;
if (n2>31) n2=31;
if (n3>31) n3=31;
```

The holding buffers are 32 characters, so this only stops the copy from
claiming more than arrived. Run with and without the change, attacked streams
come back at the true coordinate and legitimate messages decode identically.

Two sibling decoders, for message types 1007 and 1008, have the same missing
check on the antenna name and serial number. Those fields sit too early in
memory to reach the coordinates, so on the usual builds they're harmless. On a
level-2 build an oversized name crashes the program, the same kill switch as
1033. Three more lines close them:

```c
if (n>31) n=31;            /* decode_type1007 */
if (n>31) n=31;            /* decode_type1008 */
if (m>31) m=31;
```

I posted the analysis on the bug report on 2026-07-27, filed the fix as
[PR #801](https://github.com/tomojitakasu/RTKLIB/pull/801) on 2026-08-31, and
added the 1007/1008 lines to the same PR on 2026-11-16. It hasn't been merged.

**If you run a receiver and can't recompile it,** tell it to use a base position
you enter by hand. In RTKLIB that's `ant2-postype`: set it to `llh` or `xyz`
with the surveyed coordinate in place of `rtcm`. The live server only adopts a
streamed base position when that option says `rtcm`, so with it set, neither this
bug nor a fake 1005 can move the base. Running corrections over an
authenticated, encrypted connection closes the door more broadly.

# Where this stands

All four FuzzingLabs reports have been open since 2026-06-09. As of 2026-11-16
none has had a reply from the maintainer, and neither has PR #801. The demo5
fork put out a release on 2026-06-22 with the flaw untouched. There's nobody to
wait for a patch from.

The 1033 bug is
[CVE-2026-56786](https://nvd.nist.gov/vuln/detail/CVE-2026-56786), and its two
official descriptions disagree:

- **The national vulnerability database entry** carries a score of 9.3 out of
  10 (CVSS 4.0, assigned by VulnCheck, the CVE's issuer) and mentions
  "arbitrary code execution." Since only zeros spill past the field, I can't
  see a route to that.
- **Debian's security tracker** rates it a minor issue and isn't issuing a security update, because
  the overflow "consists only of strncpy NUL padding." That's accurate about
  the bytes. Those zeros happen to land on the low digits of the base
  coordinate.

Debian's package is still unpatched in every release.

## Emlid's receivers

Emlid's public fork of RTKLIB carries the same code. Their firmware images are
public downloads, so I opened several without root (`dd` to carve the
partition, `debugfs` to read it) and looked at the decoder in each.

- **Reach Plus (RS+/M+), firmware 2.18.1, 2019:** Emlid's own RTKLIB build, no
  hardened functions. Running the real `rtkrcv` binary under `qemu` against a
  correction stream carrying the message, its own console reported the base at
  `-2694684.000` against a true `-2694685.4730`, a 1.473-metre shift with
  nothing in its error log.
- **Reach M2 and RS2** (the same program, byte for byte, in v33.1):

| Reach M2 firmware | Built | The 1033 decoder's copies |
|---|---|---|
| 2.24.2 to 28.4 | Nov 2020 to Mar 2022 | plain `strncpy`: silent corruption |
| **29.0** to 33.1 | **Jul 2022** to Feb 2026 | `__strncpy_chk`: the program aborts |

From v29.0 on, the M2 and RS2 are in the hardened column. The decoder still
doesn't check the declared length; the build just aborts once a copy runs past
the 64-byte field. Running the M2's logging program, which carries the same
decoder, under emulation confirmed it: a 64-character receiver name ran fine,
and 65 printed `*** buffer overflow detected ***: terminated`. Reaching the
coordinate takes 208, so on current M2 and RS2 firmware the silent attack is gone and
every attempt is a remote kill.

Two things are still open. I haven't run the program that feeds the flight
controller or seen what ArduPilot does when it stops, and I couldn't find
current Reach Plus firmware to check. Older units, including the original Reach
RS line through 28.4, stay silent.

RTKLIB's permissive license lets it go into closed firmware without its name
on the box. Farm autosteer, survey stakeout, marine autopilots, and RTK mapping
drones draw from the same small pool of open positioning code. Which of them
carry this decoder is untested.

# What I didn't do

- **No aircraft was attacked live.** The closest: two small real radios sent the
  message over the air into RTKLIB's own decoder, real firmware was pulled
  apart, and the Reach Plus program ran under emulation. None of that is a
  powered-on device with propellers.
- **The silent attack wasn't tested against a live base** sending its own
  corrections. The harnesses replay recorded streams and re-send after every
  1005. A busy radio channel is untested.
- **One base, one rover, one data set**, and an old one. Other constellations
  and modern multi-frequency receivers are untested.
- **Each drone result is one or two flights**, one airframe, stock settings.
  The direction of the result is the claim; the exact seconds are illustrative.
- **The 10-metre drift is two samples in zero wind.** Treat it as a floor.
- **The rung-by-location map is computed from geometry**, not measured at real
  stations in those places.

# Why it matters

The bug is small and the fix is eight lines.

Every safety check in this system looks at the quality of the measurements. Are
the satellites healthy? Is the geometry good? Did the maths converge? All of
those passed in every attacked run, because the measurements really were fine.

Nothing checks the assumption the measurements are built on. The base
coordinate arrives over an unauthenticated link, gets adopted without a glance,
and every check downstream confirms that the arithmetic done on it was correct.

Most systems are built the same way. They're well instrumented
where errors are expected and blind where a value is taken on faith.

---

*Corrections welcome. Everything here is reproducible, and if you know of a
build besides Emlid's that lands in the crash column, I'd like to hear about it.
The full technical writeup, with exact source, struct offsets, the reproduction
harness, sanitizer output, and every script behind every number here, is at
[github.com/tiarno/rtk-research](https://github.com/tiarno/rtk-research),
starting from
[research/README.md](https://github.com/tiarno/rtk-research/blob/master/research/README.md).*
