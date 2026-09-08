"""Domain calculations for the aquarium CLI.

Everything here is *derived*, never stored. Volumes come from measured dimensions,
doses from measured volumes, hardness degrees from ppm. That is the point of the
whole exercise: the two errors this skill exists to prevent — dosing on a tank's
nominal name ("32 gallons") and the 3.2 mL Prime dose that followed from it — are
arithmetic mistakes, and arithmetic is the one thing that should not be recalled
from prose.

If a number can be computed, it is computed here and nowhere else.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from _store import AquaError, reference


# --------------------------------------------------------------------------- #
# time
# --------------------------------------------------------------------------- #

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M")


def parse_when(value: str | None) -> str:
    """Normalise a user-supplied timestamp. Accepts a date or a date+time."""
    if not value:
        return now_iso()
    text = value.strip().replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            continue
        return parsed.strftime("%Y-%m-%d" if fmt == "%Y-%m-%d" else "%Y-%m-%dT%H:%M")
    raise AquaError(f"cannot read {value!r} as a date. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM.")


def to_datetime(stamp: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(stamp, fmt)
        except (ValueError, TypeError):
            continue
    return None


def age_phrase(stamp: str, *, reference_time: datetime | None = None) -> str:
    """How old a reading is, in words. The honest half of a stale snapshot."""
    when = to_datetime(stamp)
    if when is None:
        return "unknown age"
    delta = (reference_time or datetime.now()) - when
    days = delta.days
    if days < 0:
        return "in the future"
    if days == 0:
        hours = delta.seconds // 3600
        return "just now" if hours < 1 else f"{hours}h ago"
    if days == 1:
        return "1 day ago"
    if days < 60:
        return f"{days} days ago"
    return f"{days // 30} months ago"


# --------------------------------------------------------------------------- #
# volume and hardness
# --------------------------------------------------------------------------- #

def water_volume_gal(tank: dict) -> float:
    """Water volume from measured dimensions, minus freeboard and displacement.

    Never from the tank's nominal name. Every dose in this system scales off this
    number, and the documented history is that using "32 gallons" for a tank
    holding ~25 made every dose ~30% too high.
    """
    dims = tank.get("dimensions_in") or {}
    try:
        gross = (
            float(dims["length"]) * float(dims["width"]) * float(dims["height"])
        ) / reference()["conversions"]["cubic_inches_per_gallon"]
    except (KeyError, TypeError, ValueError) as exc:
        raise AquaError("tank has no usable dimensions_in") from exc
    volume = gross - float(tank.get("freeboard_gal") or 0) - float(tank.get("displacement_gal") or 0)
    return round(max(volume, 0.0), 1)


def gross_volume_gal(tank: dict) -> float:
    dims = tank.get("dimensions_in") or {}
    gross = (
        float(dims["length"]) * float(dims["width"]) * float(dims["height"])
    ) / reference()["conversions"]["cubic_inches_per_gallon"]
    return round(gross, 1)


def ppm_to_degrees(ppm: float) -> float:
    return round(ppm / reference()["conversions"]["hardness_ppm_per_degree"], 1)


def degrees_to_ppm(degrees: float) -> float:
    return round(degrees * reference()["conversions"]["hardness_ppm_per_degree"], 0)


# --------------------------------------------------------------------------- #
# dosing
# --------------------------------------------------------------------------- #

def dose(product_key: str, tank: dict, scenario: str = "standard") -> dict:
    """Compute a dose from the label rate and the measured water volume."""
    products = reference().get("products", {})
    if product_key not in products:
        known = ", ".join(sorted(products))
        raise AquaError(f"no dose formula for {product_key!r}. Known: {known}")
    product = products[product_key]
    scenarios = product.get("scenarios", {})
    if scenario not in scenarios:
        known = ", ".join(sorted(scenarios))
        raise AquaError(f"{product_key} has no scenario {scenario!r}. Known: {known}")
    spec = scenarios[scenario]

    volume = water_volume_gal(tank)
    rate = float(product["label_dose_ml"]) / float(product["label_per_gallons"])
    millilitres = rate * volume * float(spec.get("multiplier", 1.0))

    drops_per_ml = reference()["conversions"]["drops_per_ml"]
    return {
        "product": product["name"],
        "scenario": scenario,
        "ml": round(millilitres, 2),
        "drops": int(round(millilitres * drops_per_ml)),
        "volume_gal": volume,
        "volume_method": tank.get("volume_method", "estimated"),
        "per_gallon_of_new_water": bool(spec.get("per_gallon_of_new_water")),
        "rate_ml_per_gal": round(rate, 4),
        "note": spec.get("note") or product.get("note"),
    }


def format_dose(result: dict) -> str:
    """One line that always shows its basis, so no dose is ever recall.

    Rounded to the precision the input actually supports. The water volume is an
    estimate with roughly half a gallon of slack in it, so quoting a dose to two
    decimal places would be precision theatre. Below 1 mL the figure is given in
    drops as well, because pouring from the bottle into four gallons overdoses
    badly.
    """
    if result["per_gallon_of_new_water"]:
        return (
            f"{result['product']}: {result['rate_ml_per_gal']:.2f} mL per gallon of NEW water "
            f"({result['scenario']})"
        )
    if result["ml"] < 1.0:
        amount = f"{result['ml']:.2f} mL (~{result['drops']} drops)"
    else:
        amount = f"{result['ml']:.1f} mL"
    return (
        f"{result['product']}: {amount} — {result['scenario']} dose for "
        f"{result['volume_gal']} gal {result['volume_method']} water volume"
    )


# --------------------------------------------------------------------------- #
# heuristics
# --------------------------------------------------------------------------- #

def spectator_ions(tds: float, gh_ppm: float, kh_ppm: float) -> dict:
    spec = reference()["heuristics"]["spectator_ions"]
    value = tds - (gh_ppm + kh_ppm)
    low, high = spec["normal_range"]
    if value >= spec["act_threshold"]:
        verdict = "elevated — with GH and KH unchanged this means non-hardness salts are accumulating"
    elif value > high:
        verdict = "above the normal band, worth watching"
    elif value < low:
        verdict = "below the normal band"
    else:
        verdict = "normal"
    return {"value": round(value, 1), "verdict": verdict, "caveat": spec["note"]}


def swap_projection(
    current_ppm: float, source_ppm: float, fraction: float, swaps: int = 5
) -> list[float]:
    """Hardness after N partial swaps with water from another tank.

    Simple dilution: each swap replaces `fraction` of the volume.
    """
    values = []
    value = current_ppm
    for _ in range(swaps):
        value = value * (1 - fraction) + source_ppm * fraction
        values.append(round(value, 1))
    return values


def dilution(initial: float, replaced_gal: float, total_gal: float) -> float:
    if total_gal <= 0:
        raise AquaError("total volume must be positive")
    return round(initial * (1 - replaced_gal / total_gal), 1)


# --------------------------------------------------------------------------- #
# readings, trends and thresholds
# --------------------------------------------------------------------------- #

def trusted_for(instrument: str, metric: str) -> bool:
    """Should this instrument's value be used for this metric?

    Encodes judgment the skill states in prose: the strip pH pad reads
    demonstrably low against a calibrated probe, and the liquid kit's pH is
    unreliable under warm light. Those readings are still recorded — they are
    evidence — but they do not drive a trend.
    """
    spec = reference().get("instruments", {}).get(instrument)
    if not spec:
        return True
    if metric in spec.get("not_trusted_for", []):
        return False
    trusted = spec.get("trusted_for")
    return metric in trusted if trusted else True


def series(readings: list[dict], tank: str, metric: str, *, trusted_only: bool = True) -> list[dict]:
    out = [r for r in readings if r.get("tank") == tank and r.get("metric") == metric]
    if trusted_only:
        out = [r for r in out if trusted_for(r.get("instrument", ""), metric)]
    return sorted(out, key=lambda r: r.get("at", ""))


def latest(readings: list[dict], tank: str, metric: str, **kw) -> dict | None:
    found = series(readings, tank, metric, **kw)
    return found[-1] if found else None


def format_value(record: dict, metric_spec: dict | None = None) -> str:
    """Render a value, showing the band when the reading was a band."""
    precision = (metric_spec or {}).get("precision", 2)
    low, high = record.get("value_min"), record.get("value_max")
    if low is not None and high is not None and low != high:
        return f"{low:.{precision}f}-{high:.{precision}f}"
    if high is not None and record.get("value") == high and low is None:
        return f"<={high:.{precision}f}"
    value = record.get("value")
    return "?" if value is None else f"{value:.{precision}f}"


def check_targets(tank_conf: dict, readings: list[dict], tank_id: str) -> list[dict]:
    """Compare the latest trusted reading of each metric against its target band."""
    flags = []
    for metric, target in (tank_conf.get("targets") or {}).items():
        record = latest(readings, tank_id, metric)
        if record is None:
            continue
        value = record.get("value")
        if value is None:
            continue
        low, high = target.get("min"), target.get("max")
        if low is not None and value < low:
            flags.append({"metric": metric, "value": value, "bound": "below", "limit": low,
                          "at": record.get("at"), "note": target.get("note")})
        elif high is not None and value > high:
            flags.append({"metric": metric, "value": value, "bound": "above", "limit": high,
                          "at": record.get("at"), "note": target.get("note")})
    return flags


SPARK = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    """A trend the agent can read inline, without producing a file."""
    numbers = [v for v in values if isinstance(v, (int, float))]
    # Two points is a delta, not a trend, and delta_phrase already says it better.
    if len(numbers) < 3:
        return ""
    low, high = min(numbers), max(numbers)
    if high == low:
        return SPARK[len(SPARK) // 2] * len(numbers)
    span = high - low
    return "".join(SPARK[min(int((v - low) / span * (len(SPARK) - 1)), len(SPARK) - 1)] for v in numbers)


def delta_phrase(current: dict, prior: dict | None, metric_spec: dict | None) -> str:
    """The context every logged reading gets.

    SOUL.md's "one reading is not a trend" asks the model to fetch the previous
    value before recommending anything. Returning it unprompted makes that
    mechanical instead of hopeful.
    """
    if prior is None:
        return "no prior reading — this is the first, so there is no trend yet"
    precision = (metric_spec or {}).get("precision", 2)
    try:
        change = float(current["value"]) - float(prior["value"])
    except (TypeError, ValueError, KeyError):
        return f"prior {format_value(prior, metric_spec)} ({prior.get('at')})"
    arrow = "+" if change > 0 else ""
    return (
        f"prior {format_value(prior, metric_spec)} ({prior.get('at')}), "
        f"Δ{arrow}{change:.{precision}f} over {age_phrase(prior.get('at', ''), reference_time=to_datetime(current.get('at', '')) or None)}"
    ).replace(" ago", "")


def stale_summary(readings: list[dict]) -> str | None:
    """Warn when the newest reading is old enough that answers built on it are guesses."""
    if not readings:
        return "no readings logged at all"
    newest = max((r.get("at", "") for r in readings), default="")
    when = to_datetime(newest)
    if when is None:
        return None
    days = (datetime.now() - when).days
    if days >= 30:
        return f"newest reading is {age_phrase(newest)} — treat every number below as historical"
    if days >= 7:
        return f"newest reading is {age_phrase(newest)}"
    return None


def metric_spec(metric: str) -> dict:
    spec = reference().get("metrics", {}).get(metric)
    if spec is None:
        raise AquaError(
            f"unknown metric {metric!r}. Known: " + ", ".join(sorted(reference()["metrics"]))
        )
    return spec


def known_metrics() -> list[str]:
    """Metrics in reference.json order, not alphabetical.

    The order there is deliberate — the continuously-measured parameters first,
    contaminants last — and a status dump that opens with "Ammonia, Copper, EC"
    buries the ones that move.
    """
    return list(reference().get("metrics", {}))


def coerce_value(raw: str) -> float:
    try:
        return float(str(raw).strip().rstrip("%"))
    except ValueError as exc:
        raise AquaError(f"{raw!r} is not a number") from exc


def as_dict(**kwargs: Any) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None}
