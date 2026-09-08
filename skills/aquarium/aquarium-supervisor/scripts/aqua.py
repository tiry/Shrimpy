#!/usr/bin/env python3
"""aqua — the aquarium's live data.

Reads and writes measurements, livestock, supplies and events for Tiry's two
freshwater tanks. Stdlib only, so installing the skill is the whole installation.

    python3 ${HERMES_SKILL_DIR}/scripts/aqua.py status
    python3 ${HERMES_SKILL_DIR}/scripts/aqua.py log ph 6.91 --tank display -i kactoily
    python3 ${HERMES_SKILL_DIR}/scripts/aqua.py dose prime --tank staging

Data lives at $HERMES_HOME/workspace/aquarium/ — on the volume, not in the repo,
because the agent writes it and the agent cannot write to a repo. See specs/06.

Three things this CLI does that prose could not:

  * every dose is computed from measured volume and shows its basis
  * every logged reading comes back with the prior value and the delta
  * `status` says how old the data is, so a stale snapshot cannot pass as current
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _calc as calc  # noqa: E402
import _store as store  # noqa: E402
from _store import AquaError, Store  # noqa: E402


# --------------------------------------------------------------------------- #
# output helpers
# --------------------------------------------------------------------------- #

def out(line: str = "") -> None:
    print(line)


def emit(payload, args) -> int:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, default=str))
    return 0


# --------------------------------------------------------------------------- #
# read commands
# --------------------------------------------------------------------------- #

def cmd_status(st: Store, args) -> int:
    tanks = st.tanks()
    readings = st.readings()
    wanted = [st.resolve_tank(args.tank)] if args.tank else sorted(tanks)

    payload = {"tanks": {}, "stale": calc.stale_summary(readings)}

    if st.seeded:
        out("Initialised from the skill's bundled snapshot. No live readings logged yet.")
        out()
    warning = payload["stale"]
    if warning:
        out(f"!! {warning}")
        out()

    for tank_id in wanted:
        tank = tanks[tank_id]
        volume = calc.water_volume_gal(tank)
        animals = [a for a in st.livestock() if a.get("tank") == tank_id]
        roster = ", ".join(f"{a['count']}x {a['name']}" for a in animals) or "none recorded"

        out(f"== {tank.get('name', tank_id)} ({tank_id})")
        out(f"   {volume} gal water ({tank.get('volume_method', 'estimated')}) · {roster}")

        rows = []
        for metric in calc.known_metrics():
            found = calc.series(readings, tank_id, metric)
            if not found:
                continue
            newest = found[-1]
            spec = calc.metric_spec(metric)
            unit = f" {spec['unit']}" if spec["unit"] else ""
            spark = calc.sparkline([r.get("value") for r in found])
            extra = f"  {spark}" if spark else ""
            rows.append(
                f"   {spec['label']:<12} {calc.format_value(newest, spec)}{unit}"
                f"  ({newest.get('instrument', '?')}, {calc.age_phrase(newest.get('at', ''))}){extra}"
            )
        if rows:
            out("\n".join(rows))
        else:
            out("   no readings logged")

        flags = calc.check_targets(tank, readings, tank_id)
        for flag in flags:
            spec = calc.metric_spec(flag["metric"])
            out(f"   !! {spec['label']} {flag['value']} is {flag['bound']} target {flag['limit']}"
                + (f" — {flag['note']}" if flag.get("note") else ""))

        bands = tank.get("prior_bands") or {}
        shown = [k for k in bands if k != "_comment"]
        if shown:
            pairs = ", ".join(
                f"{calc.metric_spec(k)['label']} {bands[k][0]}-{bands[k][1]}" for k in shown
            )
            out(f"   prior bands (pre-log, no timestamps): {pairs}")

        payload["tanks"][tank_id] = {
            "volume_gal": volume,
            "roster": roster,
            "flags": flags,
        }
        out()

    open_questions = [q for q in st.questions() if q.get("status") == "open"]
    if open_questions:
        out(f"Open questions ({len(open_questions)}):")
        for question in open_questions:
            out(f"   {question['id']}. {question['text']}")
    payload["open_questions"] = open_questions
    return emit(payload, args)


def cmd_tanks(st: Store, args) -> int:
    tanks = st.tanks()
    wanted = [st.resolve_tank(args.tank)] if args.tank else sorted(tanks)
    payload = {}
    for tank_id in wanted:
        tank = tanks[tank_id]
        dims = tank.get("dimensions_in", {})
        volume = calc.water_volume_gal(tank)
        payload[tank_id] = {**tank, "water_volume_gal": volume,
                            "gross_volume_gal": calc.gross_volume_gal(tank)}
        out(f"== {tank.get('name', tank_id)} ({tank_id})")
        out(f"   dimensions   {dims.get('length')} x {dims.get('width')} x {dims.get('height')} in")
        out(f"   gross        {calc.gross_volume_gal(tank)} gal")
        out(f"   water        {volume} gal ({tank.get('volume_method')}) "
            f"— gross minus {tank.get('freeboard_gal')} freeboard "
            f"and {tank.get('displacement_gal')} displacement")
        if tank.get("volume_note"):
            out(f"                {tank['volume_note']}")
        out(f"   substrate    {tank.get('substrate')}")
        for item in tank.get("filtration") or []:
            out(f"   filtration   {item}")
        for media in tank.get("media") or []:
            out(f"   media        {media.get('amount')} {media.get('product')}, "
                f"installed {media.get('installed')} ({calc.age_phrase(media.get('installed', ''))})")
            if media.get("note"):
                out(f"                {media['note']}")
        if tank.get("cooling"):
            out(f"   cooling      {tank['cooling']}")
        out(f"   regime       {tank.get('water_regime')}")
        for note in tank.get("notes") or []:
            out(f"   note         {note}")
        out()
    return emit(payload, args)


def cmd_livestock(st: Store, args) -> int:
    animals = st.livestock()
    if args.tank:
        tank_id = st.resolve_tank(args.tank)
        animals = [a for a in animals if a.get("tank") == tank_id]
    for animal in animals:
        flag = "" if animal.get("confidence") == "confirmed" else f"  [{animal.get('confidence')}]"
        out(f"{animal['tank']:<9} {animal['count']:>3}x {animal['name']}{flag}")
        if animal.get("notes"):
            out(f"          {animal['notes']}")
    total = sum(a.get("count", 0) for a in animals)
    out(f"\n{total} animals across {len(set(a['tank'] for a in animals))} tank(s)")
    return emit(animals, args)


def cmd_inventory(st: Store, args) -> int:
    items = st.inventory()
    if args.klass:
        items = [i for i in items if i.get("class") == args.klass]
    order = ["routine", "screen", "reserve", "paused", "emergency-only", "never", "do-not-buy"]
    items = sorted(items, key=lambda i: (order.index(i["class"]) if i.get("class") in order else 99,
                                         i.get("product", "")))
    for item in items:
        size = f" ({item['size']})" if item.get("size") else ""
        out(f"[{item.get('class','?'):<14}] {item.get('product')}{size}")
        if item.get("notes"):
            out(f"                 {item['notes']}")
    gaps = store.read_json(st.root / "inventory.json", {}).get("gaps") or []
    if gaps and not args.klass:
        out("\nGaps:")
        for gap in gaps:
            out(f"  - {gap}")
    return emit(items, args)


def cmd_readings(st: Store, args) -> int:
    metric = args.metric
    calc.metric_spec(metric)
    tank_id = st.resolve_tank(args.tank) if args.tank else None
    records = st.readings()
    if tank_id:
        records = [r for r in records if r.get("tank") == tank_id]
    records = [r for r in records if r.get("metric") == metric]
    if args.since:
        since = calc.parse_when(args.since)
        records = [r for r in records if r.get("at", "") >= since]
    if not args.all_instruments:
        records = [r for r in records if calc.trusted_for(r.get("instrument", ""), metric)]
    records = sorted(records, key=lambda r: r.get("at", ""))[-args.limit:]

    spec = calc.metric_spec(metric)
    for record in records:
        note = f"  {record['note']}" if record.get("note") else ""
        out(f"{record.get('at'):<17} {record.get('tank'):<9} "
            f"{calc.format_value(record, spec):>10} {spec['unit']:<6} "
            f"{record.get('instrument', '?'):<10}{note}")
    if len(records) >= 2:
        out(f"\ntrend {calc.sparkline([r.get('value') for r in records])}  "
            f"({len(records)} readings, {calc.age_phrase(records[0].get('at',''))} to "
            f"{calc.age_phrase(records[-1].get('at',''))})")
    elif len(records) == 1:
        out("\none reading — not a trend. Ask for the previous one before recommending action.")
    elif not records:
        out(f"no {metric} readings" + (f" for {tank_id}" if tank_id else ""))
    return emit(records, args)


def cmd_dose(st: Store, args) -> int:
    tank_id = st.resolve_tank(args.tank)
    tank = st.tank(tank_id)
    result = calc.dose(args.product, tank, args.scenario)
    out(calc.format_dose(result))
    # The volume is computed from measured dimensions; what is estimated is the
    # displacement. Saying so stops the caveat being reported as "we did not
    # measure the tank".
    if tank.get("volume_note"):
        out(f"  volume: {tank['volume_note']}")
    if result.get("note"):
        out(f"  {result['note']}")
    return emit(result, args)


def cmd_check(st: Store, args) -> int:
    readings = st.readings()
    tanks = st.tanks()
    wanted = [st.resolve_tank(args.tank)] if args.tank else sorted(tanks)
    payload = {}
    any_flag = False
    for tank_id in wanted:
        flags = calc.check_targets(tanks[tank_id], readings, tank_id)
        payload[tank_id] = flags
        out(f"== {tank_id}")
        if not flags:
            out("   all logged metrics inside target")
        for flag in flags:
            any_flag = True
            spec = calc.metric_spec(flag["metric"])
            out(f"   !! {spec['label']} {flag['value']} {flag['bound']} {flag['limit']} "
                f"(logged {calc.age_phrase(flag['at'])})")
            if flag.get("note"):
                out(f"      {flag['note']}")

        gh = calc.latest(readings, tank_id, "gh")
        kh = calc.latest(readings, tank_id, "kh")
        tds = calc.latest(readings, tank_id, "tds")
        if gh and kh and tds:
            spectator = calc.spectator_ions(tds["value"], gh["value"], kh["value"])
            out(f"   spectator ions {spectator['value']} ppm — {spectator['verdict']}")
            payload.setdefault("_spectator", {})[tank_id] = spectator
        out()
    return emit(payload, args) or (1 if any_flag and args.strict else 0)


def cmd_questions(st: Store, args) -> int:
    questions = st.questions()
    if not args.all:
        questions = [q for q in questions if q.get("status") == "open"]
    for question in questions:
        mark = "?" if question.get("status") == "open" else "+"
        out(f"{mark} {question['id']}. {question['text']}")
        if question.get("answer"):
            out(f"     answered {question.get('answered_at')}: {question['answer']}")
    return emit(questions, args)


# --------------------------------------------------------------------------- #
# write commands
# --------------------------------------------------------------------------- #

def cmd_log(st: Store, args) -> int:
    metric = args.metric
    spec = calc.metric_spec(metric)
    tank_id = st.resolve_tank(args.tank)
    when = calc.parse_when(args.at)

    existing = st.readings()
    # Prefer a trusted prior for the delta, but fall back rather than claiming
    # there is no history — "no prior reading" when one exists would invite
    # exactly the unanchored recommendation SOUL.md warns against.
    prior = calc.latest(existing, tank_id, metric)
    prior_untrusted = False
    if prior is None:
        prior = calc.latest(existing, tank_id, metric, trusted_only=False)
        prior_untrusted = prior is not None

    record = calc.as_dict(
        at=when,
        tank=tank_id,
        metric=metric,
        value=calc.coerce_value(args.value),
        value_min=calc.coerce_value(args.min) if args.min is not None else None,
        value_max=calc.coerce_value(args.max) if args.max is not None else None,
        unit=spec["unit"],
        instrument=args.instrument,
        note=args.note,
    )
    st.add_reading(record)

    out(f"logged {spec['label']} {calc.format_value(record, spec)}"
        f"{' ' + spec['unit'] if spec['unit'] else ''} for {tank_id} at {when}"
        f" ({args.instrument})")
    suffix = f" [{prior.get('instrument')}, not trusted for {metric}]" if prior_untrusted else ""
    out(f"  {calc.delta_phrase(record, prior, spec)}{suffix}")

    # The instrument caveat comes before the target verdict: whether the reading
    # can be believed decides whether the verdict means anything.
    if not calc.trusted_for(args.instrument, metric):
        note = store.reference()["instruments"].get(args.instrument, {}).get("note", "")
        out(f"  !! {args.instrument} is not trusted for {metric}. {note}")

    tank = st.tank(tank_id)
    target = (tank.get("targets") or {}).get(metric)
    if target:
        low, high = target.get("min"), target.get("max")
        value = record["value"]
        if low is not None and value < low:
            out(f"  !! below target {low}" + (f" — {target['note']}" if target.get("note") else ""))
        elif high is not None and value > high:
            out(f"  !! above target {high}" + (f" — {target['note']}" if target.get("note") else ""))
        else:
            band = f"{low}-{high}" if low is not None and high is not None else (low or high)
            out(f"  inside target {band}")
    return emit(record, args)


def cmd_event(st: Store, args) -> int:
    tank_id = st.resolve_tank(args.tank) if args.tank else None
    record = calc.as_dict(
        at=calc.parse_when(args.at),
        tank=tank_id,
        type=args.type,
        detail=args.detail,
        note=args.note,
    )
    st.add_event(record)
    out(f"recorded {args.type} for {tank_id or 'the system'} at {record['at']}")
    return emit(record, args)


def cmd_livestock_change(st: Store, args) -> int:
    animals = st.livestock()
    index = {a["id"]: a for a in animals}

    if args.action == "add":
        if not (args.id and args.name and args.tank):
            raise AquaError("add needs --id, --name, --tank and --count")
        tank_id = st.resolve_tank(args.tank)
        if args.id in index:
            index[args.id]["count"] += args.count
            out(f"{args.id}: now {index[args.id]['count']}")
        else:
            animals.append(calc.as_dict(
                id=args.id, tank=tank_id, species=args.species, name=args.name,
                count=args.count, added=calc.parse_when(args.at), confidence="confirmed",
                notes=args.note,
            ))
            out(f"added {args.count}x {args.name} to {tank_id}")
    elif args.action == "remove":
        entry = index.get(args.id) or _die(f"no livestock entry {args.id!r}")
        entry["count"] = max(0, entry["count"] - args.count)
        st.add_event({"at": calc.parse_when(args.at), "tank": entry["tank"], "type": "loss",
                      "detail": f"{args.count}x {entry['name']}", "note": args.note})
        out(f"{entry['id']}: now {entry['count']}. Recorded as an event — investigate any death.")
    elif args.action == "move":
        entry = index.get(args.id) or _die(f"no livestock entry {args.id!r}")
        destination = st.resolve_tank(args.tank)
        source = entry["tank"]
        entry["tank"] = destination
        st.add_event({"at": calc.parse_when(args.at), "tank": destination, "type": "transfer",
                      "detail": f"{entry['count']}x {entry['name']} {source} -> {destination}",
                      "note": args.note})
        out(f"moved {entry['name']} from {source} to {destination}")
    elif args.action == "note":
        entry = index.get(args.id) or _die(f"no livestock entry {args.id!r}")
        entry["notes"] = args.note or entry.get("notes")
        out(f"{entry['id']}: note updated")

    st.save_livestock(animals)
    return 0


def cmd_inventory_change(st: Store, args) -> int:
    items = st.inventory()
    index = {i["id"]: i for i in items}
    entry = index.get(args.id) or _die(
        f"no inventory item {args.id!r}. Known: " + ", ".join(sorted(index))
    )
    if args.action == "use":
        if isinstance(entry.get("on_hand"), (int, float)):
            entry["on_hand"] = max(0, entry["on_hand"] - args.count)
        out(f"{entry['product']}: {entry.get('on_hand')} on hand")
    elif args.action == "restock":
        entry["on_hand"] = (entry.get("on_hand") or 0) + args.count
        out(f"{entry['product']}: {entry['on_hand']} on hand")
    elif args.action == "open":
        entry["opened"] = calc.parse_when(args.at)
        out(f"{entry['product']}: opened {entry['opened']}")
    elif args.action == "set-class":
        if not args.klass:
            raise AquaError("set-class needs --class")
        entry["class"] = args.klass
        out(f"{entry['product']}: class {args.klass}")
    st.save_inventory(items)
    return 0


def cmd_question(st: Store, args) -> int:
    questions = st.questions()
    if args.action == "add":
        new_id = max((q["id"] for q in questions), default=0) + 1
        questions.append({"id": new_id, "text": args.text, "status": "open",
                          "asked": calc.parse_when(None), "answered_at": None, "answer": None})
        out(f"added question {new_id}")
    else:
        target = next((q for q in questions if q["id"] == args.id), None) or _die(
            f"no question {args.id}"
        )
        target["status"] = "answered" if args.action == "answer" else "closed"
        target["answered_at"] = calc.parse_when(None)
        target["answer"] = args.text
        out(f"question {args.id} {target['status']}")
    st.save_questions(questions)
    return 0


def cmd_tank_set(st: Store, args) -> int:
    tanks = st.tanks()
    tank_id = st.resolve_tank(args.tank)
    try:
        value = json.loads(args.value)
    except ValueError:
        value = args.value
    node = tanks[tank_id]
    parts = args.key.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value
    st.save_tanks(tanks)
    out(f"{tank_id}.{args.key} = {value!r}")
    if parts[0] in ("dimensions_in", "freeboard_gal", "displacement_gal"):
        out(f"  water volume now {calc.water_volume_gal(tanks[tank_id])} gal — "
            "every dose recomputes from this")
    return 0


# --------------------------------------------------------------------------- #
# admin
# --------------------------------------------------------------------------- #

def cmd_init(st: Store, args) -> int:
    root = st.root
    if store.is_initialised(root) and not args.force:
        out(f"already initialised at {root} — refusing to overwrite. --force to replace.")
        return 1
    store.initialise(root, force=args.force)
    out(f"initialised {root} from the skill's bundled snapshot")
    out("This is a bootstrap snapshot, not a mirror. It goes stale from the first live reading.")
    return 0


def cmd_migrate(st: Store, args) -> int:
    steps = store.migrate(st.root)
    out("\n".join(steps) if steps else "already at the current schema")
    return 0


def cmd_doctor(st: Store, args) -> int:
    problems: list[str] = []
    warnings: list[str] = []
    tanks = st.tanks()
    if not tanks:
        problems.append("no tanks defined")
    for tank_id, tank in tanks.items():
        try:
            volume = calc.water_volume_gal(tank)
            if volume <= 0:
                problems.append(f"{tank_id}: computed water volume is {volume}")
        except AquaError as exc:
            problems.append(f"{tank_id}: {exc}")
        if not tank.get("targets"):
            warnings.append(f"{tank_id}: no target bands, so `check` can say nothing")

    known_tanks = set(tanks)
    for animal in st.livestock():
        if animal.get("tank") not in known_tanks:
            problems.append(f"livestock {animal.get('id')}: unknown tank {animal.get('tank')!r}")
        if animal.get("species") and animal["species"] not in store.reference().get("species", {}):
            warnings.append(f"livestock {animal.get('id')}: species "
                            f"{animal['species']!r} not in reference.json")

    metrics = set(calc.known_metrics())
    instruments = set(store.reference().get("instruments", {}))
    for record in st.readings():
        if record.get("metric") not in metrics:
            problems.append(f"reading at {record.get('at')}: unknown metric {record.get('metric')!r}")
        if record.get("tank") not in known_tanks:
            problems.append(f"reading at {record.get('at')}: unknown tank {record.get('tank')!r}")
        if record.get("instrument") and record["instrument"] not in instruments:
            warnings.append(f"reading at {record.get('at')}: unknown instrument "
                            f"{record.get('instrument')!r}")
        if calc.to_datetime(record.get("at", "")) is None:
            problems.append(f"reading has unreadable timestamp {record.get('at')!r}")

    for item in st.inventory():
        product = item.get("reference_product")
        if product and product not in store.reference().get("products", {}):
            warnings.append(f"inventory {item.get('id')}: reference_product "
                            f"{product!r} has no dose formula")

    stale = calc.stale_summary(st.readings())
    if stale:
        warnings.append(stale)

    for line in problems:
        out(f"ERROR   {line}")
    for line in warnings:
        out(f"warning {line}")
    if not problems and not warnings:
        out(f"clean — {len(st.readings())} readings, {len(st.livestock())} livestock entries, "
            f"{len(st.inventory())} inventory items")
    out(f"\nschema v{store.schema_version(st.root)} at {st.root}")
    return 1 if problems else 0


def _die(message: str):
    raise AquaError(message)


# --------------------------------------------------------------------------- #
# parser
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aqua",
        description="Live data for Tiry's two freshwater tanks.",
    )
    parser.add_argument("--data-dir", default=None,
                        help="override the data directory (default: $HERMES_HOME/workspace/aquarium)")
    parser.add_argument("--json", action="store_true", help="also emit the result as JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    def tank_arg(p, required=False):
        p.add_argument("--tank", "-t", required=required, default=None,
                       help="display or staging (aliases accepted)")

    p = sub.add_parser("status", help="everything worth knowing, per tank")
    tank_arg(p)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("tanks", help="identity, dimensions, computed volume, media")
    tank_arg(p)
    p.set_defaults(func=cmd_tanks)

    p = sub.add_parser("livestock", help="who lives where")
    tank_arg(p)
    p.set_defaults(func=cmd_livestock)

    p = sub.add_parser("inventory", help="what is on the shelf and whether it may be used")
    p.add_argument("--class", dest="klass", default=None)
    p.set_defaults(func=cmd_inventory)

    p = sub.add_parser("readings", help="history for one metric")
    p.add_argument("metric")
    tank_arg(p)
    p.add_argument("--since", default=None)
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--all-instruments", action="store_true",
                   help="include instruments not trusted for this metric")
    p.set_defaults(func=cmd_readings)

    p = sub.add_parser("dose", help="compute a dose from measured volume")
    p.add_argument("product")
    tank_arg(p, required=True)
    p.add_argument("--scenario", default="standard")
    p.set_defaults(func=cmd_dose)

    p = sub.add_parser("check", help="compare the latest readings against target bands")
    tank_arg(p)
    p.add_argument("--strict", action="store_true", help="exit 1 if anything is out of band")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("questions", help="open questions")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_questions)

    p = sub.add_parser("log", help="record a measurement")
    p.add_argument("metric")
    p.add_argument("value")
    tank_arg(p, required=True)
    p.add_argument("--instrument", "-i", default="observed")
    p.add_argument("--at", default=None, help="YYYY-MM-DD or YYYY-MM-DDTHH:MM (default: now)")
    p.add_argument("--min", default=None, help="lower bound, if the reading was a band")
    p.add_argument("--max", default=None, help="upper bound, if the reading was a band")
    p.add_argument("--note", "-n", default=None)
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("event", help="record something that happened")
    p.add_argument("type", help="water-change, media-added, loss, transfer, feeding-change, ...")
    tank_arg(p)
    p.add_argument("--detail", "-d", default=None)
    p.add_argument("--at", default=None)
    p.add_argument("--note", "-n", default=None)
    p.set_defaults(func=cmd_event)

    p = sub.add_parser("livestock-change", help="add, remove, move or annotate animals")
    p.add_argument("action", choices=["add", "remove", "move", "note"])
    p.add_argument("--id", default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--species", default=None)
    p.add_argument("--count", type=int, default=1)
    tank_arg(p)
    p.add_argument("--at", default=None)
    p.add_argument("--note", "-n", default=None)
    p.set_defaults(func=cmd_livestock_change)

    p = sub.add_parser("inventory-change", help="use, restock, open or reclassify a product")
    p.add_argument("action", choices=["use", "restock", "open", "set-class"])
    p.add_argument("id")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--class", dest="klass", default=None)
    p.add_argument("--at", default=None)
    p.set_defaults(func=cmd_inventory_change)

    p = sub.add_parser("question", help="add, answer or close an open question")
    p.add_argument("action", choices=["add", "answer", "close"])
    p.add_argument("--id", type=int, default=None)
    p.add_argument("--text", default=None)
    p.set_defaults(func=cmd_question)

    p = sub.add_parser("tank-set", help="change a tank's configuration")
    p.add_argument("key", help="dotted path, e.g. dimensions_in.length or targets.ph.min")
    p.add_argument("value")
    tank_arg(p, required=True)
    p.set_defaults(func=cmd_tank_set)

    p = sub.add_parser("export", help="write CSVs of every table")
    p.add_argument("--format", default="csv", choices=["csv"])
    p.add_argument("--out", default=None)
    p.set_defaults(func=lambda st, a: _report(st, a, "export"))

    p = sub.add_parser("report", help="a single self-contained HTML report with charts")
    p.add_argument("--out", default=None)
    p.add_argument("--since", default=None)
    p.set_defaults(func=lambda st, a: _report(st, a, "report"))

    p = sub.add_parser("plot", help="a PNG trend chart for one metric")
    p.add_argument("metric")
    tank_arg(p)
    p.add_argument("--out", default=None)
    p.add_argument("--since", default=None)
    p.set_defaults(func=lambda st, a: _report(st, a, "plot"))

    p = sub.add_parser("init", help="seed the data directory from the bundled snapshot")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("migrate", help="bring older data up to the current schema")
    p.set_defaults(func=cmd_migrate)

    p = sub.add_parser("doctor", help="validate the data and report inconsistencies")
    p.set_defaults(func=cmd_doctor)

    return parser


def _report(st: Store, args, kind: str) -> int:
    import _report as reporting

    return getattr(reporting, f"cmd_{kind}")(st, args, out)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = store.data_dir(args.data_dir)
        auto = args.command not in ("init",)
        st = Store(root, auto_init=auto)
        return args.func(st, args) or 0
    except AquaError as exc:
        print(f"aqua: {exc}", file=sys.stderr)
        return 2
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
