---
description: Operating profile and runbook for Tiry's two freshwater aquariums — a planted display tank and a smaller planted staging/quarantine tank, holding Neocaridina shrimp, fancy guppies, a suckermouth catfish, mystery snails and nerite snails. The live data — measurements, livestock counts, supplies — is held in a small CLI that ships with the skill, so the numbers are always current rather than remembered. Use this skill whenever the user asks anything about their aquarium, tank, shrimp, guppies, otos, snails, water parameters, pH, GH, KH, TDS, EC, ORP, ammonia, nitrite, nitrate, water changes, top-offs, dosing, feeding, acclimation, algae, sick or dead livestock, filter media, crushed coral, Seachem or API products, medications, Hanna checkers, test strips, or the aquadirector CLI, sensor readings, dashboard, alert rules, trends, charts or reports. Trigger it even for casual phrasing like "my shrimp look weird", "is 6.6 too low", "lost a guppy overnight", or a bare paste of sensor output with no question attached — the whole point is that the assistant already knows these tanks and does not re-ask setup questions.
---

# Aquarium

Category description for the aquarium skills. The `description` above is what Hermes renders
into the system-prompt skill index — **untruncated**, unlike a skill's own `description`,
which is cut to 60 characters (`SKILL_PROMPT_DESC_LIMIT` in `agent/skill_utils.py`).

That is why the trigger phrases live here rather than in `aquarium-supervisor/SKILL.md`: the
index is the only thing the model sees when deciding whether to open a skill, so a trigger
list in a truncated field is a trigger list the model never reads.

**Deliberately free of specifics.** This file is rendered into the system prompt, so it
cannot be regenerated when the data changes — which means any count, volume or reading
stated here goes stale silently and cannot be corrected by the agent. Tank sizes, livestock
counts and parameters live in the CLI (`scripts/aqua.py`), not in this description. Keep it
to trigger phrases and shape.
