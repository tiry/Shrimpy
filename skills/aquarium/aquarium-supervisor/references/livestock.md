# Livestock reference — species biology

Read this before answering any question about a specific animal's behaviour,
health, diet or compatibility.

**Who lives where, and how many, is not in this file.** It changes.

```
# the CLI - run each command on its own, no shell variables, no chaining
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock [--tank display|staging]     the current roster
python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status                                 rosters plus the water they are in
```

The tolerance ranges below are species facts. Whether *these* animals are inside
them is a question for `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check`, which compares the latest reading of every
metric against that tank's targets. Compare against the measured water, not
against a textbook ideal in isolation.

Where sources disagree, the wider tolerance and the narrower *comfort* range are
both given.

---

## Neocaridina davidi — cherry / dwarf shrimp

**Comfort:** 20–24°C optimal (tolerates 18–29°C), pH 6.5–7.8, GH 6–12 dGH,
KH 2–5 dKH, TDS 150–250 ppm (some keepers run to 400 with no ill effect).
These are also in `assets/reference.json`, which is what `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` uses.

**Molting.** Ecdysis roughly every 3–4 weeks. New cuticle calcification needs
dissolved calcium — GH below 4 dGH is the classic cause of failed molts, where the
shrimp cannot free itself from the old shell. The "white ring of death" is a
visible gap across the carapace behind the head where the molt separated but the
animal is stuck.

**Check GH per tank before deciding whether this is the risk** —
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py readings gh --tank <tank>`. A tank comfortably above the calcification line
is not at risk from low GH, and a failed molt there points at *rate of change*
instead: a sudden osmotic drop, from a large unmatched water change or a big
distilled top-off in one go, triggers premature emergency molts.

A tank below the line is on a clock, not a hypothesis — the molt cycle is three to
four weeks, so the deadline is set by biology and does not wait.

**Copper.** Highly toxic to all dwarf shrimp; commonly cited as harmful in the
low tens of ppb, with total colony loss the usual outcome of a real exposure.
Treat any copper-containing medication, fertilizer or plant dip as prohibited.
Check ingredient lists even on products labelled invertebrate-safe.

**Nitrite.** Damaging well below the threshold that troubles fish. Note that
shrimp use **hemocyanin**, not hemoglobin, so the fish methemoglobin mechanism
doesn't transfer directly — but the practical conclusion is the same: nitrite
above zero is an emergency.

**Diet.** Biofilm and aufwuchs grazers first, prepared food second. In a mature
planted tank they largely feed themselves.

**A young, heavily grazed tank is a partial case.** Bare-bottom but planted means
real surfaces for biofilm — better than bare glass — but a young setup grows it
thinly, and grazers compete for it. Count the grazers with `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock`
before assuming they are fed. Supplement with small amounts of shrimp food or
blanched vegetables, and consider moving a piece of established hardscape or
filter sponge over from the mature tank to seed the surfaces. That last option is
the most effective and costs nothing.

**Colony size.** A small colony makes every loss proportionally significant.
Investigate any death rather than writing it off as attrition, and record it —
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock-change remove` keeps the roster true and logs the date.

---

## Fancy guppies (*Poecilia reticulata*)

**Comfort:** 24–27°C preferred (tolerates ~22–28°C), pH 7.0–8.0 preferred, hard
water preferred.

**Expect a mismatch, and check it before diagnosing.** In a shared tank the
parameters are set for the shrimp, which puts guppies at the cool, soft end of
their preference. They do fine there but are not at their optimum. Before
diagnosing illness from lethargy or reduced colour, run `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` and consider
that they may simply be at the bottom of their thermal range. Do not recommend
raising temperature to suit them — the shrimp colony takes priority, and the
guppies are inside tolerance.

**Transport sensitivity.** Farmed strains are often held in soft water and go into
osmoregulatory shock if moved quickly into harder water. Presentation: clamped
fins, resting on the bottom, lethargy, decline over 12–36 hours. This is why the
45–60 minute drip acclimation exists.

**Feeding.** High metabolism, small stomach. Small daily portions, never a heavy
single feed.

**Breeding.** Livebearers, and prolific. A mixed-sex group gives fry within weeks
and a bioload that compounds on its own — which matters most in a tank with no
water changes and therefore no nitrate export. Check `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py questions`: whether the
sex ratio is known is tracked there.

---

## Otocinclus / juvenile suckermouth catfish ("window suckers")

**Comfort:** 22–26°C typical (sources range 20–28°C), pH 6.0–7.5, soft to
moderately hard.

**Shoaling, and often kept alone.** Otocinclus do markedly better in groups of
5–6+. A lone specimen hides more, grazes less, and gives you no group behaviour to
compare against — which makes the belly check below the only reliable health signal
available. Check `python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock` for how many there are, and raise companions if
it is one.

**Identification matters.** Otocinclus and juvenile plecos are easily confused, and
a common pleco reaches 30 cm+ and would outgrow a tank of this size entirely.
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock` marks the entry `unconfirmed` while that is unresolved.

**The starvation problem.** These are obligate grazers on soft green diatoms and
microbial biofilm. In a pristine, high-ORP tank there is very little of it. Most
are wild-caught, arrive with a depleted gut, and starve slowly in clean tanks while
the keeper assumes they are finding food. In a well-maintained tank this is the
most likely chronic risk to the animal.

**Belly check — the key diagnostic.** View the fish against the front glass from
the side:
- **Rounded, like a small pea** → feeding, healthy.
- **Flat** → borderline. Increase targeted feeding.
- **Hollow or sunken/concave** → critical. Gut starvation. Feed a sinking wafer or
  blanched vegetable slice directly at their resting spot at lights-out, every
  evening until the belly fills out.

Blanched zucchini, cucumber and spinach are usually accepted; so are sinking
spirulina wafers. Remove uneaten portions after 2–3 hours.

---

## Albino mystery snails (*Pomacea diffusa*)

**Name correction.** These are *Pomacea diffusa*, not *Pomacea bridgesii*.
*P. diffusa* was described by Blume in 1957 as a subspecies and raised to full
species around 2007; it is the snail in the aquarium trade throughout. True
*P. bridgesii* is rare and much larger (65 mm+ shell). Older literature and many
retailers still use the old name, so both will be encountered.

**Respiration.** Dual — gills plus an extendable siphon they use to breathe air at
the surface. They must be able to reach air, hence the ≥1 in lid headspace rule.
A snail unable to surface will drown.

**Diet.** Not a plant eater in practice — prefers decaying matter, algae, and
prepared food. Sinking vegetable pellets, blanched zucchini or spinach. They will
not keep the glass clean; that's the nerites' job.

**Shell.** Calcium carbonate, so it dissolves in water that is acidic and thin on
carbonate faster than the animal can lay it down. Check pH and KH per tank —
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py check` — before deciding whether erosion is a live risk. See the shell
erosion entry in `triage.md`.

**Lifespan** is roughly 1–2 years in aquaria. A mystery snail dying of old age is
common and is not evidence of a water quality problem — but see the dead-snail
ammonia protocol in `triage.md`, because a large dead snail decomposing unnoticed
is a serious ammonia event, and the smaller the tank the faster it moves.

---

## Red Racer nerite snails (*Vittina waigiensis*)

**Strict grazers.** Diatoms and biofilm on hard surfaces. They generally refuse
prepared food. If the glass and hardscape are spotless, they are running out of
food.

**Worth watching in a young or small tank.** A bare-bottom but **planted** tank
has real grazing surface — leaves, stems and glass all grow biofilm and diatoms —
so it is not the sterile environment bare glass would be. The concern is that a
young setup grows biofilm slowly and every grazer shares it; count them with
`python3 ${HERMES_SKILL_DIR}/scripts/aqua.py livestock`. Nerites starve silently over weeks with no symptom until they
stop moving, so judge by whether they are actively moving and grazing rather than
by whether the tank looks clean. Either supplement with algae wafers and blanched
vegetables (accepting they may refuse them), seed the tank with an algae-covered
rock or a sponge from the mature tank, or move them across sooner rather than
later.

**Orientation rule.** Always place them right-side up on rock, wood, or glass.
A nerite landing upside down on open substrate frequently cannot right itself and
will die there. Check the substrate periodically for inverted snails.

**Escape behaviour.** Determined climbers with a strong intertidal instinct — they
will exit an open tank and dry out on the floor. Every filter cutout, tubing
notch and cable gap must stay sealed. A missing nerite is more likely on the floor
than dead in the tank; check there first.

**They will not breed here.** Nerite eggs need brackish water to hatch. Expect
small white egg capsules cemented to hardscape that never develop. Harmless, but
cosmetically persistent.
