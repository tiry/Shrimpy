"""Reporting: CSV for spreadsheets, PNG charts, one self-contained HTML report.

Constrained by what is actually importable in the deployment container, verified
by live probe: **no openpyxl, no xlsxwriter, no pandas, no matplotlib, no numpy.**
The venv is root-owned read-only and ``HERMES_DISABLE_LAZY_INSTALLS=1``, so the
bundled ``xlsx`` skill is non-functional there as shipped.

Pillow *is* a core Hermes dependency (``pyproject.toml:245``), so charts are drawn
with ``PIL.ImageDraw`` — and PNG is what renders inline in Element. If Pillow is
ever absent the chart degrades to stdlib SVG rather than failing.

``ImageFont.load_default()`` only: no font file is required, which keeps "adding
the skill is enough" true.
"""

from __future__ import annotations

import base64
import csv
import html
import io
from pathlib import Path

import _calc as calc
import _store as store

PLOT_METRICS = ("ph", "temperature", "tds", "orp", "gh", "kh")

WIDTH, HEIGHT = 720, 260
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 62, 18, 26, 34


# --------------------------------------------------------------------------- #
# CSV
# --------------------------------------------------------------------------- #

def cmd_export(st, args, out) -> int:
    target = Path(args.out) if args.out else st.root / "export"
    target.mkdir(parents=True, exist_ok=True)

    written = []
    written.append(_write_csv(
        target / "readings.csv",
        ["at", "tank", "metric", "value", "value_min", "value_max", "unit", "instrument", "note"],
        st.readings(),
    ))
    written.append(_write_csv(
        target / "events.csv", ["at", "tank", "type", "detail", "note"], st.events()
    ))
    written.append(_write_csv(
        target / "livestock.csv",
        ["tank", "id", "name", "species", "count", "added", "confidence", "notes"],
        st.livestock(),
    ))
    written.append(_write_csv(
        target / "inventory.csv",
        ["id", "product", "size", "on_hand", "class", "opened", "notes"],
        st.inventory(),
    ))

    tanks = []
    for tank_id, tank in st.tanks().items():
        dims = tank.get("dimensions_in", {})
        tanks.append({
            "tank": tank_id,
            "name": tank.get("name"),
            "length_in": dims.get("length"),
            "width_in": dims.get("width"),
            "height_in": dims.get("height"),
            "gross_gal": calc.gross_volume_gal(tank),
            "water_gal": calc.water_volume_gal(tank),
            "volume_method": tank.get("volume_method"),
            "regime": tank.get("water_regime"),
        })
    written.append(_write_csv(
        target / "tanks.csv",
        ["tank", "name", "length_in", "width_in", "height_in", "gross_gal", "water_gal",
         "volume_method", "regime"],
        tanks,
    ))

    for path, count in written:
        out(f"{path}  ({count} rows)")
    return 0


def _write_csv(path: Path, columns: list[str], rows: list[dict]) -> tuple[Path, int]:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path, len(rows)


# --------------------------------------------------------------------------- #
# charts
# --------------------------------------------------------------------------- #

def _pil():
    try:
        from PIL import Image, ImageDraw, ImageFont  # noqa: PLC0415

        return Image, ImageDraw, ImageFont
    except ImportError:
        return None


def chart_png(records: list[dict], metric: str, tank: str, target: dict | None) -> bytes | None:
    """A time-series line chart. Returns PNG bytes, or None if Pillow is absent."""
    modules = _pil()
    if modules is None or len(records) < 1:
        return None
    Image, ImageDraw, ImageFont = modules
    spec = calc.metric_spec(metric)

    values = [r.get("value") for r in records if isinstance(r.get("value"), (int, float))]
    if not values:
        return None

    low, high = min(values), max(values)
    if target:
        for bound in (target.get("min"), target.get("max")):
            if isinstance(bound, (int, float)):
                low, high = min(low, bound), max(high, bound)
    if high == low:
        high, low = high + 1, low - 1
    pad = (high - low) * 0.12
    low, high = low - pad, high + pad

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    plot_w = WIDTH - MARGIN_L - MARGIN_R
    plot_h = HEIGHT - MARGIN_T - MARGIN_B

    def x_at(index: int) -> float:
        if len(records) == 1:
            return MARGIN_L + plot_w / 2
        return MARGIN_L + plot_w * index / (len(records) - 1)

    def y_at(value: float) -> float:
        return MARGIN_T + plot_h * (1 - (value - low) / (high - low))

    # target band first, so the line sits on top of it
    if target and isinstance(target.get("min"), (int, float)) and isinstance(target.get("max"), (int, float)):
        draw.rectangle(
            [MARGIN_L, y_at(target["max"]), MARGIN_L + plot_w, y_at(target["min"])],
            fill=(232, 244, 234),
        )

    for step in range(5):
        value = low + (high - low) * step / 4
        y = y_at(value)
        draw.line([(MARGIN_L, y), (MARGIN_L + plot_w, y)], fill=(228, 228, 228))
        draw.text((6, y - 4), f"{value:.{spec['precision']}f}", fill=(90, 90, 90), font=font)

    draw.rectangle([MARGIN_L, MARGIN_T, MARGIN_L + plot_w, MARGIN_T + plot_h], outline=(170, 170, 170))

    points = [(x_at(i), y_at(r["value"])) for i, r in enumerate(records)
              if isinstance(r.get("value"), (int, float))]
    if len(points) > 1:
        draw.line(points, fill=(31, 92, 160), width=2)
    for x, y in points:
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(31, 92, 160))

    first, last = records[0].get("at", ""), records[-1].get("at", "")
    draw.text((MARGIN_L, HEIGHT - MARGIN_B + 10), str(first)[:16], fill=(90, 90, 90), font=font)
    label = str(last)[:16]
    draw.text((MARGIN_L + plot_w - 6 * len(label), HEIGHT - MARGIN_B + 10), label,
              fill=(90, 90, 90), font=font)
    unit = f" ({spec['unit']})" if spec["unit"] else ""
    # ImageFont.load_default() is a bitmap font with no em-dash; anything outside
    # ASCII renders as tofu. Keep every drawn string plain.
    title = f"{tank} - {spec['label']}{unit}".encode("ascii", "replace").decode("ascii")
    draw.text((MARGIN_L, 8), title, fill=(20, 20, 20), font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def chart_svg(records: list[dict], metric: str, tank: str) -> str:
    """Stdlib fallback when Pillow is unavailable."""
    spec = calc.metric_spec(metric)
    values = [r.get("value") for r in records if isinstance(r.get("value"), (int, float))]
    if not values:
        return ""
    low, high = min(values), max(values)
    if high == low:
        high, low = high + 1, low - 1
    plot_w, plot_h = WIDTH - MARGIN_L - MARGIN_R, HEIGHT - MARGIN_T - MARGIN_B
    points = []
    for index, value in enumerate(values):
        x = MARGIN_L + (plot_w * index / max(len(values) - 1, 1))
        y = MARGIN_T + plot_h * (1 - (value - low) / (high - low))
        points.append(f"{x:.1f},{y:.1f}")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}">'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>'
        f'<text x="{MARGIN_L}" y="18" font-size="12">{html.escape(tank)} — '
        f'{html.escape(spec["label"])}</text>'
        f'<polyline fill="none" stroke="#1f5ca0" stroke-width="2" points="{" ".join(points)}"/>'
        f"</svg>"
    )


def cmd_plot(st, args, out) -> int:
    metric = args.metric
    calc.metric_spec(metric)
    tank_id = st.resolve_tank(args.tank)
    records = calc.series(st.readings(), tank_id, metric)
    if args.since:
        since = calc.parse_when(args.since)
        records = [r for r in records if r.get("at", "") >= since]
    if not records:
        out(f"no {metric} readings for {tank_id}")
        return 1

    target = (st.tank(tank_id).get("targets") or {}).get(metric)
    png = chart_png(records, metric, tank_id, target)
    destination = Path(args.out) if args.out else st.root / "export" / f"{tank_id}-{metric}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)

    if png is None:
        destination = destination.with_suffix(".svg")
        destination.write_text(chart_svg(records, metric, tank_id), encoding="utf-8")
        out(f"{destination}  (SVG — Pillow unavailable)")
    else:
        destination.write_bytes(png)
        out(f"{destination}  ({len(records)} readings)")
    if len(records) == 1:
        out("one reading — the chart is a single point, not a trend.")
    return 0


# --------------------------------------------------------------------------- #
# HTML report
# --------------------------------------------------------------------------- #

def cmd_report(st, args, out) -> int:
    readings = st.readings()
    if args.since:
        since = calc.parse_when(args.since)
        readings = [r for r in readings if r.get("at", "") >= since]

    parts: list[str] = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>Aquarium report</title>",
        "<style>"
        "body{font:14px/1.5 system-ui,sans-serif;margin:2rem auto;max-width:820px;color:#222}"
        "h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:2rem}"
        "table{border-collapse:collapse;width:100%;margin:.5rem 0}"
        "th,td{border-bottom:1px solid #e2e2e2;padding:.35rem .5rem;text-align:left}"
        "th{background:#f6f6f6}img{max-width:100%;margin:.5rem 0}"
        ".warn{background:#fff4e5;padding:.6rem .8rem;border-left:3px solid #d98324}"
        ".muted{color:#666;font-size:.9em}"
        "</style>",
        "<h1>Aquarium report</h1>",
        f"<p class='muted'>Generated {calc.now_iso()} from {html.escape(str(st.root))}</p>",
    ]

    stale = calc.stale_summary(readings)
    if stale:
        parts.append(f"<p class='warn'>{html.escape(stale)}</p>")

    for tank_id, tank in sorted(st.tanks().items()):
        parts.append(f"<h2>{html.escape(tank.get('name', tank_id))}</h2>")
        volume = calc.water_volume_gal(tank)
        animals = [a for a in st.livestock() if a.get("tank") == tank_id]
        roster = ", ".join(f"{a['count']}&times; {html.escape(a['name'])}" for a in animals)
        parts.append(
            f"<p>{volume} gal water ({html.escape(str(tank.get('volume_method')))}) &middot; "
            f"{roster or 'no livestock recorded'}</p>"
        )

        rows = []
        for metric in calc.known_metrics():
            found = calc.series(readings, tank_id, metric)
            if not found:
                continue
            newest = found[-1]
            spec = calc.metric_spec(metric)
            rows.append(
                f"<tr><td>{html.escape(spec['label'])}</td>"
                f"<td>{html.escape(calc.format_value(newest, spec))} {html.escape(spec['unit'])}</td>"
                f"<td>{html.escape(str(newest.get('instrument', '')))}</td>"
                f"<td class='muted'>{html.escape(str(newest.get('at', '')))} "
                f"({html.escape(calc.age_phrase(newest.get('at', '')))})</td>"
                f"<td>{len(found)}</td></tr>"
            )
        if rows:
            parts.append(
                "<table><tr><th>Metric</th><th>Latest</th><th>Instrument</th>"
                "<th>When</th><th>Readings</th></tr>" + "".join(rows) + "</table>"
            )

        for flag in calc.check_targets(tank, readings, tank_id):
            spec = calc.metric_spec(flag["metric"])
            parts.append(
                f"<p class='warn'>{html.escape(spec['label'])} {flag['value']} is "
                f"{flag['bound']} target {flag['limit']}"
                + (f" &mdash; {html.escape(str(flag['note']))}" if flag.get("note") else "")
                + "</p>"
            )

        for metric in PLOT_METRICS:
            found = calc.series(readings, tank_id, metric)
            if len(found) < 2:
                continue
            target = (tank.get("targets") or {}).get(metric)
            png = chart_png(found, metric, tank_id, target)
            if png:
                encoded = base64.b64encode(png).decode("ascii")
                parts.append(f"<img alt='{html.escape(metric)}' src='data:image/png;base64,{encoded}'>")
            else:
                parts.append(chart_svg(found, metric, tank_id))

    events = st.events()
    if events:
        parts.append("<h2>Events</h2><table><tr><th>When</th><th>Tank</th><th>Type</th>"
                     "<th>Detail</th></tr>")
        for event in events[-30:]:
            parts.append(
                f"<tr><td>{html.escape(str(event.get('at','')))}</td>"
                f"<td>{html.escape(str(event.get('tank') or '-'))}</td>"
                f"<td>{html.escape(str(event.get('type','')))}</td>"
                f"<td>{html.escape(str(event.get('detail') or ''))}</td></tr>"
            )
        parts.append("</table>")

    open_questions = [q for q in st.questions() if q.get("status") == "open"]
    if open_questions:
        parts.append("<h2>Open questions</h2><ul>")
        for question in open_questions:
            parts.append(f"<li>{html.escape(question['text'])}</li>")
        parts.append("</ul>")

    destination = Path(args.out) if args.out else st.root / "export" / "report.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(parts), encoding="utf-8")
    size_kb = destination.stat().st_size / 1024
    out(f"{destination}  ({size_kb:.0f} KB, self-contained)")
    if _pil() is None:
        out("Pillow unavailable — charts fell back to SVG.")
    return 0
