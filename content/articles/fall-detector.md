---
title: "I Built a Fall Detector. The Data Killed It."
slug: fall-detector
date: 2026-08-30
category: Hardware
tags: [ESP32, sensors, measurement, health]
summary: "Twenty-five false alarms in five hours, and it still missed half the falls in a 523-fall dataset. Why wrist-worn fall detection failed for me, why it fails for almost everyone, and what survived the wreck."
---

I set the watch down on my desk, face up, the way you'd put down a phone. Ten
seconds later it buzzed, lit up, and started counting down to calling my family.

Nothing had happened. Nobody had fallen. And it took me longer than I'd like to
admit to accept that the detector had not malfunctioned — it had done exactly
what I built it to do. A watch dropped onto a hard desk **is** a fall, as far as
an accelerometer strapped to a wrist can tell. There was a sharp deceleration,
the orientation changed from upright to flat, and then it lay perfectly still.
Every stage of my carefully staged detection cascade fired in order, and the
cascade was right about every one of them.

This is what came of building a wrist-worn fall detector, measuring it properly,
and concluding that it should never be allowed to page anyone. I'll walk through
how these things are supposed to work, the two numbers that killed mine, and the
part I genuinely did not expect: the published research has been saying the same
thing since 2012, and mostly nobody acts on it.

# What I was building, and why

A family member has limited mobility and lives at home. The goal was
unglamorous — a watch that notices a fall, waits a few seconds in case it's
wrong, and escalates to a small relay server that texts and calls a list of
family contacts if nobody cancels.

The hardware is a LilyGO T-Watch Ultra: an ESP32-S3, a Bosch BHI260AP motion
sensor, a screen, a vibration motor, a LoRa radio, and a battery. The firmware
is mine. The detection logic lives in plain C with no Arduino or FreeRTOS
dependencies, so it compiles on my laptop and I can replay recorded motion
through it in a test harness. There are signed over-the-air updates that refuse
to install older versions, HMAC-signed alerts with replay protection, and a
journal that writes an alert to flash *before* it tries to send it, so a
network outage can't quietly swallow one.

All of that works. None of it is what went wrong.

# How fall detection is supposed to work

Nearly every accelerometer-based fall detector is a state machine looking for
the same four-part signature, in order. Mine was built from the published
descriptions, and it looks like this.

<figure class="diagram" markdown="0">
<svg viewBox="0 0 880 280" role="img" aria-labelledby="casc-title casc-desc" xmlns="http://www.w3.org/2000/svg">
<title id="casc-title">The four-stage fall detection cascade</title>
<desc id="casc-desc">Four stages in sequence — free-fall, impact, orientation change, and stillness — each gating the next. Below them, the same four stages shown being satisfied by the ordinary act of setting the watch down on a desk, ending in a countdown to calling the family.</desc>
<style>text{font-family:var(--font-mono);}</style>
<text x="40" y="24" font-size="11" letter-spacing="0.14em" fill="var(--muted)">THE CASCADE</text>

<rect x="40" y="44" width="170" height="58" rx="4" fill="none" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="125" y="72" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">1 · FREE-FALL</text>
<text x="125" y="90" font-size="11.5" fill="var(--muted)" text-anchor="middle">under 0.6 g, 80 ms</text>

<rect x="250" y="44" width="170" height="58" rx="4" fill="none" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="335" y="72" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">2 · IMPACT</text>
<text x="335" y="90" font-size="11.5" fill="var(--muted)" text-anchor="middle">a spike over 4 g</text>

<rect x="460" y="44" width="170" height="58" rx="4" fill="none" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="545" y="72" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">3 · ORIENTATION</text>
<text x="545" y="90" font-size="11.5" fill="var(--muted)" text-anchor="middle">gravity turns 40°</text>

<rect x="670" y="44" width="170" height="58" rx="4" fill="none" stroke="var(--line-strong)" stroke-width="1.25"/>
<text x="755" y="72" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">4 · STILLNESS</text>
<text x="755" y="90" font-size="11.5" fill="var(--muted)" text-anchor="middle">quiet for 8 s</text>

<line x1="214" y1="73" x2="240" y2="73" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="240,69 248,73 240,77" fill="var(--line-strong)"/>
<line x1="424" y1="73" x2="450" y2="73" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="450,69 458,73 450,77" fill="var(--line-strong)"/>
<line x1="634" y1="73" x2="660" y2="73" stroke="var(--line-strong)" stroke-width="1.25"/>
<polygon points="660,69 668,73 660,77" fill="var(--line-strong)"/>

<text x="40" y="150" font-size="11" letter-spacing="0.14em" fill="var(--muted)">WHAT HAPPENS WHEN I SET IT ON A DESK</text>

<text x="125" y="180" font-size="16" fill="var(--teal)" text-anchor="middle">✓</text>
<text x="125" y="200" font-size="11.5" fill="var(--muted)" text-anchor="middle">the drop from</text>
<text x="125" y="216" font-size="11.5" fill="var(--muted)" text-anchor="middle">my hand</text>

<text x="335" y="180" font-size="16" fill="var(--teal)" text-anchor="middle">✓</text>
<text x="335" y="200" font-size="11.5" fill="var(--muted)" text-anchor="middle">the tap on</text>
<text x="335" y="216" font-size="11.5" fill="var(--muted)" text-anchor="middle">hard wood</text>

<text x="545" y="180" font-size="16" fill="var(--teal)" text-anchor="middle">✓</text>
<text x="545" y="200" font-size="11.5" fill="var(--muted)" text-anchor="middle">wrist upright to</text>
<text x="545" y="216" font-size="11.5" fill="var(--muted)" text-anchor="middle">screen flat</text>

<text x="755" y="180" font-size="16" fill="var(--teal)" text-anchor="middle">✓</text>
<text x="755" y="200" font-size="11.5" fill="var(--muted)" text-anchor="middle">a desk does not</text>
<text x="755" y="216" font-size="11.5" fill="var(--muted)" text-anchor="middle">move at all</text>

<text x="440" y="258" font-size="12.5" fill="var(--brick)" text-anchor="middle">a countdown starts, and then the family gets a call</text>
</svg>
<figcaption>Each stage gates the next, so nothing alerts on a single spike. The trouble is that the four conditions describe an object arriving on a hard surface, which is a much larger category of event than a person collapsing.</figcaption>
</figure>

The logic is sound and the staging genuinely helps. A gesture that spikes past
4 g does nothing, because no free-fall preceded it. A free-fall with a soft
landing does nothing, because no impact followed. Getting straight back up
after a stumble cancels the whole thing at stage four.

Read the sequence again, though, and notice what it actually describes: *an
object that dropped, hit something hard, ended up at a different angle, and
then stopped moving.* A person collapsing on a kitchen floor fits. So does a
watch meeting a desk.

# The first number: how often it cried wolf

I wore it for a day and logged every verdict.

**Twenty-five alerts in five hours and twenty minutes.** One false alarm every
thirteen minutes.

The same watch, left on a table for fifteen hours, produced zero. Every one of
those alarms was caused by ordinary living — setting a mug down hard, dropping
my arm onto the armrest of a chair, putting the watch on and taking it off,
resting a hand flat on a table and leaving it there.

Any one of those, on its own, would be a tuning problem. You raise a threshold,
you lengthen a window, you move on. Twenty-five an hour and a half is a
different kind of message.

# The second number: how often it caught an actual fall

The false alarm rate is the easy half to measure, because you only have to wear
the thing. Measuring the other half — how many real falls it catches — means
having real falls, and I am not going to produce those on demand.

So I used a public research dataset,
[FallAllD](https://ieee-dataport.org/open-access/fallalld-comprehensive-dataset-human-falls-and-activities-daily-living),
which recorded 15 volunteers performing falls and everyday activities with
sensors at the wrist, the waist, and on a neck pendant simultaneously. I pulled the wrist channel, converted
every trial into my replay format, and ran the exact production detection code
over all of it.

**258 of 523 falls reached the alerting verdict. 49.3%.**

## Where that data comes from, exactly

Since the whole argument rests on this dataset, here is precisely what it is.

FallAllD was collected by Majd Saleh and Régine Le Bouquin Jeannes, published
open-access on IEEE DataPort in April 2020, and described in *IEEE Sensors
Journal* the following year. Fifteen participants wore three data-loggers
simultaneously — waist, wrist, and neck — each carrying an accelerometer,
gyroscope, magnetometer, and barometer. It runs to 26,420 files.

Reading the archive rather than trusting a description of it, the structure is:

- One file per sensor per trial, named like `S01_D1_A013_T01_A.dat` — subject,
  device, activity, trial, sensor. Accelerometer and gyroscope arrive as
  **separate** files and have to be paired; there is no combined record.
- Each is a headerless three-column CSV of raw 16-bit integers, exactly 4,760
  rows — **20.000 seconds at 238 Hz**, constant across every file I checked.
- Activity IDs split cleanly: 001–044 are everyday activities, 101–135 are the
  35 fall types. Seventy-nine IDs across fifteen subjects.

Three things about it are worth stating plainly, because each one could have
quietly produced a wrong headline number.

**The falls are simulated.** Participants fell deliberately, knowing it was
coming. This is standard practice and it is the only ethical way to build a
dataset like this, but it is exactly the gap Bagalà's study is about.

**No README ships in the archive, so which device is the wrist is inferred.** I
worked it out from three independent signals that agree: twelve activities exist
only on device 2 and are all wrist-specific gestures the torso mounts never saw;
device 2 has the highest gyroscope RMS of the three; and device 2 shows by far
the widest spread of mean gravity direction across trials, which is the
signature of a mount that rotates freely. Waist and neck mounts do not do that.
Reading the wrong device would have silently produced a *waist*-mounted recall
figure and I would never have known.

**The raw values are integers, and the scale factor is not given.** My converter
refuses to run without an explicit scale, and there is a separate step that
infers it from physics — a resting wrist must read 1 g — and reports every
candidate against that standard. The scale turned out to be 1/4096 g per count.
Getting this wrong by a factor of 4096 produces a perfectly plausible-looking
recall number computed from nonsense, with nothing on the surface to show it.

I also left the data at its native 238 Hz rather than resampling to the 100 Hz
my firmware runs at. I tried resampling first, and measuring it showed the
interpolation was quietly shaving peaks off impacts — the thing the detector
keys on.

It missed slightly more than half. And here is the detail that mattered most to
me: of the falls it missed completely, **61% had an impact peak comfortably
above the 4 g threshold.** The detector saw the impact perfectly well. It threw
the event away at the orientation stage.

# Both numbers at once

Either number alone leaves you somewhere to go.

A detector that catches 49% of falls but is otherwise silent is a weak safety
net that might still be worth wearing. A detector that catches nearly
everything but shouts too often is annoying, and you tighten the thresholds and
trade some sensitivity for quiet.

Mine did both simultaneously. It missed half of what it existed for **while**
paging roughly three times an hour. There's no threshold adjustment that
resolves that, because the two problems pull in opposite directions and neither
one has any slack. Tightening it to silence the false alarms pushes recall below
49%. Loosening it to catch more falls makes an already unusable alarm rate
worse.

There is no operating point. That's the whole finding, and it took measuring
both axes to see it — which is precisely why I think most people never see it.

# Why it misses: your wrist doesn't know what your body is doing

Stage three is where the falls died, and stage three is the one carrying an
assumption I'd never examined: **that the sensor's orientation tells you the
body's orientation.**

Strap a sensor to somebody's waist and that assumption is close enough to true.
The torso is upright when standing and horizontal when lying down, and the
gravity vector rotates roughly 90° between the two.

Your wrist does no such thing. Your arm rotates through most of that range while
you're making a sandwich. It can end a genuine fall pointing in almost any
direction, including the one it started in — if you fall while reaching for a
railing, your forearm may finish more or less where it began, and the stage sees
nothing worth reporting.

I could test this directly, because FallAllD recorded all three sensor positions
during the same falls. Same subjects, same events, matched trial by trial.

<figure class="diagram" markdown="0">
<svg viewBox="0 0 880 240" role="img" aria-labelledby="mount-title mount-desc" xmlns="http://www.w3.org/2000/svg">
<title id="mount-title">Recall by sensor mounting position</title>
<desc id="mount-desc">A bar chart of the same detector's recall on identical matched falls at three sensor positions: wrist 44.4 percent, waist 54.2 percent, and neck pendant 63.1 percent.</desc>
<style>text{font-family:var(--font-mono);}</style>
<text x="40" y="24" font-size="11" letter-spacing="0.14em" fill="var(--muted)">SAME DETECTOR, SAME FALLS, THREE MOUNTS (n=214 MATCHED TRIALS)</text>

<rect x="180" y="106" width="100" height="84" fill="var(--brick)"/>
<text x="230" y="96" font-size="15" font-weight="600" fill="var(--ink)" text-anchor="middle">44.4%</text>
<text x="230" y="212" font-size="12.5" fill="var(--ink)" text-anchor="middle">wrist</text>

<rect x="400" y="87" width="100" height="103" fill="var(--teal)" opacity="0.55"/>
<text x="450" y="77" font-size="15" font-weight="600" fill="var(--ink)" text-anchor="middle">54.2%</text>
<text x="450" y="212" font-size="12.5" fill="var(--ink)" text-anchor="middle">waist</text>

<rect x="620" y="70" width="100" height="120" fill="var(--teal)"/>
<text x="670" y="60" font-size="15" font-weight="600" fill="var(--ink)" text-anchor="middle">63.1%</text>
<text x="670" y="212" font-size="12.5" fill="var(--ink)" text-anchor="middle">pendant</text>

<line x1="150" y1="190" x2="790" y2="190" stroke="var(--line-strong)" stroke-width="1.25"/>
</svg>
<figcaption>Moving the sensor from the wrist to the chest is worth about nineteen points of recall, which confirms the mechanism. It also lands well short of anything you'd trust with someone's safety. On matched everyday activities the three mounts were indistinguishable (1.5%, 1.7%, 1.3%), so this says nothing about which mount raises fewer false alarms.</figcaption>
</figure>

Nineteen points sitting in the mounting position tells you the orientation stage
was the problem all along. It also tells you that relocating the sensor doesn't
rescue the idea — a pendant still misses more than a third of falls, and comes
with its own well-known problem, which is that people don't wear pendants.
Stigma, forgetting, taking it off in the shower and leaving it there. The
wrist's compliance advantage is exactly why wrist devices dominate the market
despite worse physics.

# This is not just my detector

Here's the part I wasn't expecting, and the reason I'm writing this up rather
than quietly deleting the repo.

In 2012, Fabio Bagalà and colleagues published a study in *PLOS ONE*,
[Evaluation of Accelerometer-Based Fall Detection Algorithms on Real-World Falls](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0037062),
that took **thirteen already-published fall detection algorithms** — algorithms
with strong reported results — and ran them against real falls recorded from
high-fall-risk patients going about their lives.

Sensitivity collapsed to **57.0% on average**, with the best of the thirteen
reaching 82.8%. And when they monitored three representative fallers for a day
each, the algorithms produced between **3 and 85 false alarms per day.**

Set that beside my results:

| | Bagalà 2012, thirteen published algorithms | Mine, 2026 |
| --- | --- | --- |
| Falls caught | 57.0% average | 49.3% |
| False alarms | 3–85 per day | ~25 in 5h20m |

I landed inside their range on both axes, at the wrist, fourteen years later,
with a considerably better sensor. I had independently reproduced a result that
was already in the literature — which is reassuring about my measurement and
depressing about the state of the field.

Two details make my number worse:

- **My 49.3% was measured against staged falls.** FallAllD volunteers fell
  deliberately onto padding. Bagalà's central point is that staged falls are the
  *easy* case: real fallers grab furniture, twist, brace, and half-catch
  themselves, and those compensatory movements smear the clean signature the
  cascade is looking for. My 49.3% is a ceiling, and real-world performance
  would be lower.
- **Their algorithms were mostly waist-mounted.** As my own three-mount
  comparison shows, that's the easier position by about nineteen points.

## So how do the commercial ones manage?

They engineer around the problem rather than solving it.

Apple biases hard toward severe impacts, waits about a minute for immobility,
and **requires you to confirm** before it calls anyone. It still famously
triggers on roller coasters and ski slopes. Medical
alert pendants get better numbers largely by sitting on the torso, the mount my
own data says is worth nineteen points.

That confirmation prompt is doing enormous work. It converts an unsolved
detection problem into a "prompt the human" problem, which is tractable. When a
vendor advertises 95% accuracy, ask two questions: measured against staged falls
or real ones, and what was the false alarm rate over the same period? The second
number is almost never printed beside the first, and the pair is what tells you
whether the thing works.

<span class="note">Note: </span>None of this is medical advice, and it isn't an argument against buying a fall-detecting device. A detector that catches half of falls is better than nothing, and the confirmation prompt makes the false alarms survivable. It is an argument against believing the marketing number, and against relying on automatic detection as the only safety net for someone who lives alone.
{: .callout}

# What survived

The detector is dead. I set a compile-time flag that lets the cascade keep
running, keep recording, and keep filling the corpus, while making it
structurally incapable of summoning anyone.

What's left turns out to be most of the value.

**The escalating check-in.** A far simpler idea, and it needs no training data
at all: if the watch has seen no movement for a long time on a wrist it knows is
being worn, ask. Buzz, put a prompt on screen, wait a minute, ask harder, and
only escalate to family after several increasingly insistent prompts all go
unanswered. It catches the slow collapses the cascade is structurally blind to —
sliding out of a chair, not getting up in the morning — and it doesn't need to
recognise a fall to work.

It also failed on its first real day: thirteen pages in fifteen hours, three of
them for the crime of sitting at a desk for two hours. The difference is that
the cascade failed on physics, which no amount of design fixes, and the check-in
failed on an unfinished design, which is an ordinary engineering problem.

**Knowing whether it's on a wrist.** This one I did solve, and cleanly. Measured
over minutes, a worn wrist and a tabletop separate by a factor of about 350 in
angular movement — 80.96° against 0.21°. I was worried a sleeping arm would look
like a nightstand; the quietest five-minute window in an entire night of sleep
still read 1.67°, eight times the tabletop. That's a real discriminator with
margin on both sides, and it kills the desk problem I opened this article with.

**The instrument.** Detection logic in plain C, a replay harness that runs
recorded motion through the exact production code on a laptop, CI that gates
every push, and a dataset importer with a units-verification step you can't
skip. Building that took longer than building the detector, and it's the only
reason any of the numbers above exist.

That last part is now on GitHub as
**[detector-replay](https://github.com/tiarno/detector-replay)**, generalised so
the detector is pluggable — you point it at your own C code, tell it which of
your verdicts count as alarms, and it scores recall and false alarms separately.
It ships with the cascade above as the worked example, defects and all, the 23
labelled traces including the table set-down that started this, and the FallAllD
converter with its units gate. Everything in this article is reproducible from
it.

I also wrote down a stopping condition **before** collecting the data: if the
redesigned check-in produces more than about one false page per week over a
seven-day trial, the project stops. Deciding that in advance matters, because I
know exactly how persuasive I'd find my own excuses afterwards.

# What I'd tell you if you're starting this

**Measure both axes, or you've measured nothing.** Recall alone and false-alarm
rate alone each have a story where things are basically fine. Together they
closed the question in an afternoon. I spent weeks tuning against a number I
hadn't paired with anything.

**Staged data flatters you.** Every fall in my dataset was performed on purpose
by someone who knew it was coming. Real falls are messier and partially caught,
and the published research is unambiguous that performance drops when you move
from one to the other. Treat any result from staged falls as an upper bound.

**Check what your sensor can physically know.** My orientation stage rested on
an assumption about wrists that ten minutes of thought would have refuted. It
survived for months because I'd written it down confidently, in a design
document, where it looked like a decision instead of a guess. The three-mount
comparison that finally settled it was an afternoon's work on data I already had.

**Read your own instruments.** My firmware printed a hardware capability
bitmask on every single boot for nineteen days. I decoded two bits of it. When I
finally read the rest, I discovered the board had GPS and an NFC reader on it —
both of which my design document explicitly claimed were absent. A number nobody
reads isn't observability; it just looks like it.

The working rule I've ended up with, and the one thing here I'd defend without
qualification: **build the instrument, wear the thing, read the data.** Every
failure in this project was a plausible premise that nobody had checked, and
every one of them was cheap to check the moment I stopped arguing about it and
went to measure.

# The code

**[github.com/tiarno/detector-replay](https://github.com/tiarno/detector-replay)** — the measurement
bench, the fall cascade as its worked example, the trace corpus, and the dataset converter. MIT.

If you're building a detector of your own — falls, seizures, gestures, machine
faults, anything that watches a motion stream and occasionally decides something
happened — it's built to be pointed at your code rather than mine. The README
covers what to change. FallAllD isn't redistributed there; you download it
yourself and convert it.

# Sources

- Bagalà, F. et al., [Evaluation of Accelerometer-Based Fall Detection Algorithms on Real-World Falls](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0037062), *PLOS ONE*, 2012 — the thirteen-algorithm study, and the source of the simulated-versus-real gap.
- Saleh, M. and Le Bouquin Jeannes, R., [FallAllD](https://ieee-dataport.org/open-access/fallalld-comprehensive-dataset-human-falls-and-activities-daily-living), IEEE DataPort, 2020 — 15 participants, simultaneous wrist, waist and neck loggers. Described in [IEEE Sensors Journal](https://ieeexplore.ieee.org/document/9171857/), 2021.
