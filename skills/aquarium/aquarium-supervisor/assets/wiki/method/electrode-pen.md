---
title: Electrode pens and multiparameter probes
slug: electrode-pen
category: method
aqua_key: null
aliases:
  - "probe"
  - "pen"
  - "pH meter"
  - "TDS meter"
  - "ORP"
summary: How pH, EC/TDS and ORP electrodes work, drift and mislead.
sources:
  - url: https://en.wikipedia.org/wiki/Ion-selective_electrode
    title: Ion-selective electrode
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/PH_meter
    title: pH meter
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Electrical_conductivity_meter
    title: Electrical conductivity meter
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
  - url: https://en.wikipedia.org/wiki/Reduction_potential
    title: Redox potential
    licence: CC BY-SA 4.0
    consulted: 2026-09-12
---

# Electrode pens and multiparameter probes

Background on the measuring principle. Which instrument is trusted for which metric is
data — run `aqua instruments`. What any of them last read is `aqua readings`.

## What it actually measures

An electrode pen is a **potentiometric** device: it measures a voltage, not a
concentration, and converts one to the other through a calibration curve.

A pH electrode is an ion-selective electrode — a membrane-based transducer that converts
the activity of one ion into an electrical potential. The meter reports the potential
difference between that electrode and a reference electrode. Two consequences follow and
they explain most bad readings:

- **It measures activity, not concentration.** In very soft, low-ionic-strength water
  there is little for the reference junction to work against, readings wander, and the
  number settles slowly or not at all. Soft water is exactly where a pH pen is least
  reliable, which is unfortunate because soft water is where pH matters most.
- **The calibration is the measurement.** An uncalibrated electrode is not approximately
  right — it is reporting a voltage through a curve that no longer describes it. Drift is
  gradual and silent, so a pen that has never been recalibrated reads plausibly and wrongly.

A conductivity cell is different in kind. It applies a current and measures how easily the
water carries it, which scales with total dissolved ionic content. **TDS is not a
measurement, it is conductivity multiplied by an assumed conversion factor**, and that
factor depends on which salts are actually present. Two waters with identical readings can
have quite different compositions. See `assets/wiki/method/observation.md` for what to do
when two instruments disagree, and `references/chemistry.md` for why TDS is not hardness.

ORP measures redox potential — the tendency of the water's chemistry to gain or lose
electrons, expressed in volts. It is a bulk indicator of oxidising conditions, not a test
for any specific substance.

## How these go wrong

- **Temperature.** Electrode response is temperature-dependent. A pen without compensation,
  or with compensation set for a different temperature than the sample, is offset.
- **A dirty or dried-out junction.** A pH electrode is a wet-stored device. Left dry, the
  membrane degrades permanently and the pen becomes an expensive thermometer.
- **Too short a settle.** The reading approaches its value asymptotically. Lifting the pen
  at the first stable-looking digit systematically biases toward the previous sample.
- **Cross-contamination.** Carrying a film of the last sample into the next one shifts
  low-ionic-strength readings noticeably.

## The one to be most careful with

A multiparameter pen reports several metrics from one body, which invites treating them as
equally reliable. They are not. The conductivity cell is robust and rarely lies; the pH
electrode is the fragile one; the ORP electrode is the hardest to interpret at all. A
single device presenting all three with the same number of decimal places tells the reader
nothing about which of them to believe.

`aqua instruments` records which metrics each device is trusted for, and `aqua` keeps
untrusted readings out of trends. That list is the answer, not the pen's own display.
