# Products — why, not what

**What is on the shelf, in what size, and whether it may be used here is not in
this file.** It changes when a bottle is bought, opened or emptied.

```
# the CLI - run each command on its own, no shell variables, no chaining
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory                    everything, grouped by class
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory --class never      the ones to refuse
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank staging    a dose, computed from measured volume
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory-change open prime  record that a bottle was opened
```

This file is the **reasoning** behind the classes — why something is routine,
reserve or refused. Read it before recommending, endorsing or ruling out anything;
read `aqua` for whether it is actually in the cupboard.

Classes `aqua` uses:

| Class | Meaning |
|---|---|
| `routine` | in regular use |
| `screen` | gives an indication, not a measurement |
| `reserve` | situational, conditions attached |
| `paused` | usable, deliberately not in use |
| `emergency-only` | real hazards attached; not for routine use |
| `never` | present in the cabinet, not to be used in these tanks |
| `do-not-buy` | not owned, and not the right answer here |

---

## The one live hazard: salt beside zeolite

**This is the most important thing in this file.**

Both aquarium salt and a zeolite ammonia remover are in the cabinet. Zeolite
(clinoptilolite) binds ammonium by exchanging it for sodium. Adding sodium
chloride reverses that exchange and **releases the resin's entire accumulated
ammonium load into the water at once** — a tank that was being rescued becomes a
tank being poisoned, in minutes.

If zeolite is ever deployed, salt stays in the cupboard until the resin is out and
discarded.

Salt is separately a poor fit here regardless: shrimp and snails tolerate it
badly, and suckermouth catfish are sensitive to it. There is no scenario in these
two tanks where it is the right tool. If someone suggests salt for a sick fish —
a common and otherwise reasonable suggestion — this is why the answer is no.

---

## Why zeolite is emergency-only rather than routine

- **It starves the nitrifying colony.** Removing ammonium removes the substrate
  the bacteria live on, so it stalls biological maturation. A tank held on zeolite
  is not cycling.
- **Zero affinity for nitrite.** Useless for a nitrite problem, which is the
  problem people usually reach for it during.
- **The salt interaction above.**

If deployed, it is temporary while the cause is fixed. Remove and discard the bag
afterwards rather than leaving it in — an exhausted resin sitting in a filter is a
loaded gun waiting for someone to add salt.

---

## Why a marine ich treatment is refused

Formalin-and-malachite-green formulations are marine-labelled for a reason:

- Malachite green is toxic to invertebrates, and the manufacturer's own label
  warns it may harm some. Independent sources are blunter.
- Formalin depletes dissolved oxygen quickly.
- **Explicitly contraindicated with sulfinate/sulfoxylate conditioners**, which
  includes the conditioner in routine use here.
- Its own instructions say to treat in a separate quarantine tank, remove carbon,
  and do a large water change before each dose.

**If ich appears:** treat affected fish in a separate bare hospital tank with no
invertebrates, or use an invert-safe alternative. Never dose a tank holding shrimp
and snails.

---

## Why a general slime-coat product is refused

Redundant with the primary conditioner for dechlorination, and the aloe vera in it
can coat and foul fine shrimp gill filaments. Nothing gained, a real cost.

---

## Reserve products, and the conditions attached

**Carbon.** Situational adsorption of tannins, odours and chemical contaminants —
the first response to a suspected aerosol or lotion contamination. Exhausts in
three to four weeks. **Remove before dosing any medication**; it strips the
medication straight back out.

**Hydrogen peroxide.** Useful for spot-treating algae and for emergency
oxygenation, and genuinely risky around shrimp, which are more sensitive than fish
— shrimplets and biofilm more so again.

- **Never pour it into the tank freehand.** Whole-tank dosing in an invertebrate
  system is not worth it.
- Spot treatment means a syringe, filter briefly off, applied directly to the
  target, ideally with the target out of water.
- It kills biofilm — which in a tank whose grazers are already short of food is a
  direct cost to the animals.
- If asked about it, get specifics first — which tank, what target, how much water
  — and default to mechanical removal or a blackout.

**Melafix-type melaleuca products.** Not prohibited, but two honest caveats:

- **Efficacy is weakly supported.** Reviews find no good evidence for it treating
  bacterial infection in fish. It is not a substitute for a real antibacterial.
- **It is invert-safe** at label dose and will not harm the biofilter. Many
  keepers halve it with shrimp present anyway — `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose melafix --tank <tank>
  --scenario with-shrimp`.
- **The real cost is the surface film.** The oil reduces gas exchange at the
  surface, and these tanks depend on surface agitation for *both* oxygenation and
  evaporative cooling, so a film has an outsized effect. Keep agitation high and
  expect cooling to drop.

**Fertilizer.** Paused rather than refused. Potassium salts raise TDS and EC
without contributing GH, so it will move the spectator-ion figure without
improving hardness. Resume at half strength only on visible plant deficiency, and
check iron first. **Never use it to try to raise GH.**

---

## Why remineralizers are "do not buy"

While GH sits inside the range the shrimp need, dosing minerals is solving a
problem that does not exist — and dosed minerals are harder to control than a
partial water change. Revisit only if GH drops below the calcification line.

Note the scope carefully: this prohibits **dosing a tank to raise its GH**.
Preparing matched water for a water change is a different question, and swapping
water from a harder tank into a softer one is a third. Both of those are fine.
Applying the prohibition to them is exactly the kind of scope error the skill
warns about.

---

## Testing

**A strip is a screen, not a measurement.** Useful for the things nothing else
here measures — free chlorine, copper, iron — and demonstrably unreliable for pH.
`aqua` records which instrument produced each reading and keeps untrusted ones out
of the trend while still storing them: `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings ph --all-instruments` shows
what was filtered.

**Liquid kits are the reference for nitrogen.** Judge colour in neutral daylight
against a white background, never in warm low sun — it shifts every tube orange.
Note that an ammonia scale usually runs yellow (0) to green (high), the opposite
direction from nitrite and nitrate.

**Photometers decide hardness.** Never substitute marine-range checkers; their dye
chemistries need seawater ionic strength.

**A calibrated probe beats a colour chart for pH.** When they disagree, the probe
is right — and check the time of day before calling it a shift at all.

---

## Gaps

`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py inventory` lists what is missing at the end of its output. Raise a gap when
the subject comes up naturally, not as a standing recommendation to buy things.
