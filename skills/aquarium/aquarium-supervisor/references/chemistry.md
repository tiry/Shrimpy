# Chemistry — mechanisms, not values

Every number in this file is a **relationship**, not a measurement. Tank values,
volumes, doses and hardness figures come from `aqua`:

```
# the CLI - run each command on its own, no shell variables, no chaining
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose <product> --tank <tank> · python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check
```

The CLI computes every conversion below. Reproduce the arithmetic by hand only to
explain it, never to answer with it.

---

## 1. Unit conversions

**Hardness.** German degrees and ppm as CaCO₃ relate by 17.86:

```
d-units = ppm / 17.86        ppm = d-units × 17.86
```

**Volume.** `gallons = L × W × H (inches) / 231`, then subtract freeboard and
displacement. This is the calculation that matters most, because getting it wrong
scales every dose in the system. A tank's nominal name is not its water volume,
and using one for the other is how a routine dose becomes a 30% overdose.

`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks` shows the full chain — gross, freeboard, displacement, water — and
marks whether the result is measured or estimated. To convert an estimate into a
measurement: during a water change, refill from a marked jug and count. Once.

**Ammonia on a Hanna HI700**, if one is ever acquired. It reads ammonia-nitrogen:

```
Total ammonia (mg/L) = HI700 reading × 1.214
```

(Molar mass ratio 17.03 / 14.01.)

**EC and TDS.** The probe reports TDS ≈ 0.5 × EC. That is a *meter setting*, an
NaCl-referenced factor, not a chemical relationship. Do not present it as physics.

---

## 2. The spectator-ion heuristic — and its limits

```
ΔTDS_spectator = TDS_measured − (GH_ppm + KH_ppm)
```

`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` computes it from the latest readings and classifies the result.

**It is a trend line, not a concentration.** Three reasons it is not a real
quantity:

1. GH and KH are reported as *ppm CaCO₃ equivalents* — a standardized proxy, not
   the dissolved mass of the ions present. Subtracting them from a mass-like TDS
   figure mixes units.
2. The calcium counted in GH is largely the same ion paired with the bicarbonate
   counted in KH. Subtracting both double-counts.
3. Conductivity-derived TDS uses an NaCl factor that under-reads Ca²⁺ and HCO₃⁻.

What it *is* good for: if GH and KH hold steady and this figure climbs, something
that is not hardness is accumulating — fertilizer salts, sodium, nitrate. Answer
that with a water change, never with a chemical additive.

**It inherits the staleness of its inputs.** GH and KH move slowly but they do
move, and a spectator figure computed against a months-old hardness reading is
progressively more wrong. `aqua` reports the age of every reading; if the figure
is driving a conclusion, say how old its inputs are.

---

## 3. Dilution and partial changes

```
TDS_final = TDS_initial × (1 − V_replaced / V_total)
```

The same fraction applies to GH and KH. That is the whole argument for matched
change water: a pure-distilled change does not just dilute nitrate, it drops
hardness by the same proportion, in one step. For an animal that needs dissolved
calcium to build a new shell, that step is the event.

**A rapid hardness *rise* is also an osmotic event.** Converging two tanks means
walking the softer one up over days with repeated partial swaps, not fixing it in
one session. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings gh --tank <tank>` shows whether it is moving.

---

## 4. Buffering with aragonite

Crushed coral is calcium carbonate. It dissolves when the water is acidic enough
to dissolve it and stops when it is not — the rate falls as pH rises and
effectively stalls around 7.2–7.5.

Two consequences worth stating plainly:

- **Overshoot is not a realistic failure mode.** It is a buffer that switches
  itself off. Undersupply is the failure mode that actually happens.
- **It is slow.** Weeks, not days. It cannot beat a molt clock on its own, which
  is why a hardness problem with animals at risk needs partial swaps *and* coral:
  swaps move the number now, coral holds it afterwards.

Placement matters more than amount past a point — media in a dead corner of a
filter does very little. Rinse before adding.

`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py tanks` carries install dates and computes when a replacement is due.

---

## 5. Product mechanisms

Which products are on the shelf, in what quantity, and whether they may be used
here: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory`. Why: `products.md`. Doses: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose`.

**Conditioners (Prime).** Neutralize chlorine and chloramine, bind heavy metals,
and temporarily complex ammonia and nitrite for roughly 24–48 hours. They do not
move pH or GH, and they do not remove nitrogen — they buy time while the cause is
found. Re-dose within that window if the cause persists.

**Bacterial supplements (Stability).** Nitrifying and facultative bacteria. Useful
after adding livestock, replacing or heavily rinsing media, cycling, or
antibacterial exposure. Pointless when ammonia and nitrite read zero and nitrate
is present — that combination means the colony is already self-sustaining.

**Zeolite (clinoptilolite).** Binds ammonium by ion exchange, swapping it for
sodium. Three properties that matter: it has **zero affinity for nitrite**, it
**starves the nitrifying colony** of its substrate and so stalls biological
maturation, and adding sodium chloride **reverses the exchange and dumps the
resin's entire accumulated ammonium load into the water at once**. Emergency use
only, and never alongside salt.

**Oxidizers (hydrogen peroxide).** Effective against algae, and indiscriminate.
Shrimp — especially shrimplets — and biofilm are more sensitive than fish. Spot
treatment only: syringe, filter briefly off, applied directly to the target.

**Carbon.** Adsorbs tannins, odours and many organics. Exhausts in weeks, not
months, and **strips medication out of the water**, so it comes out before any
treatment goes in.

---

## 6. Instruments

`aqua` records which instrument produced every reading and knows which ones are
trustworthy for which metric. `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings <metric> --all-instruments` shows
the ones it normally filters out.

The general principle: **a colour chart read under warm light is not a
measurement**, and a test strip is a screen. Judge colour in neutral daylight
against a white background. Photometers and a calibrated probe decide; strips
suggest.

Never substitute marine-range checkers for freshwater ones. Their dye chemistries
need seawater ionic strength and will read nonsense here.

Distilled water reading pH 5.5–5.8 in the jug is normal atmospheric CO₂ and will
not move tank pH — the tank's carbonate absorbs it on contact.
