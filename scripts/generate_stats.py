
import json
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict
import html

DATA_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("stats.svg")

BG = "#0d1117"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#39d353"
BLUE = "#58a6ff"


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    contributions = {
        date.fromisoformat(item["date"]): int(item["count"])
        for item in data
    }

    if not contributions:
        raise RuntimeError("No contribution data found.")

    today = max(contributions)
    total = sum(contributions.values())
    active_days = sum(count > 0 for count in contributions.values())
    best_day = max(contributions, key=contributions.get)
    best_count = contributions[best_day]

    monthly = defaultdict(int)
    for day, count in contributions.items():
        monthly[day.strftime("%b")] += count

    ordered_months = sorted(contributions, reverse=True)
    month_dates = []
    seen = set()

    for day in ordered_months:
        key = day.strftime("%Y-%m")
        if key not in seen:
            seen.add(key)
            month_dates.append((key, day.strftime("%b")))
        if len(month_dates) == 6:
            break

    month_dates.reverse()
    month_values = []
    for key, label in month_dates:
        month_values.append((
            label,
            sum(
                count for day, count in contributions.items()
                if day.strftime("%Y-%m") == key
            )
        ))

    longest = 0
    streak = 0
    for day in sorted(contributions):
        if contributions[day] > 0:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 0

    current_streak = 0
    check_day = today
    while contributions.get(check_day, 0) > 0:
        current_streak += 1
        check_day -= timedelta(days=1)

    width, height = 820, 360
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" rx="12" fill="{BG}" stroke="#30363d"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif}.number{font-size:25px;font-weight:bold;fill:#39d353}.label{font-size:12px;fill:#8b949e}.heading{font-size:17px;font-weight:bold;fill:#58a6ff}</style>',
        '<text x="25" y="32" class="heading">GitHub Contribution Stats</text>',
        f'<text x="795" y="32" text-anchor="end" class="label">Updated from contribution calendar</text>',
    ]

    cards = [
        ("Total Contributions", f"{total:,}"),
        ("Active Days", f"{active_days:,}"),
        ("Current Streak", f"{current_streak} days"),
        ("Longest Streak", f"{longest} days"),
    ]

    positions = [(25, 55), (425, 55), (25, 125), (425, 125)]

    for (label, value), (x, y) in zip(cards, positions):
        parts.append(
            f'<rect x="{x}" y="{y}" width="370" height="58" rx="8" '
            f'fill="#161b22" stroke="#30363d"/>'
        )
        parts.append(
            f'<text x="{x + 15}" y="{y + 22}" class="label">'
            f'{html.escape(label)}</text>'
        )
        parts.append(
            f'<text x="{x + 15}" y="{y + 47}" class="number">'
            f'{html.escape(value)}</text>'
        )

    parts.append('<text x="25" y="218" class="heading">Last 6 Active Months</text>')

    chart_x, chart_y = 45, 245
    chart_width, chart_height = 730, 75
    max_value = max((v for _, v in month_values), default=1) or 1
    bar_width = chart_width / max(len(month_values), 1)

    for i, (label, value) in enumerate(month_values):
        bar_height = (value / max_value) * chart_height
        x = chart_x + i * bar_width + 14
        y = chart_y + chart_height - bar_height

        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 28:.1f}" '
            f'height="{max(bar_height, 1):.1f}" rx="3" fill="{GREEN}"/>'
        )
        parts.append(
            f'<text x="{x + (bar_width - 28) / 2:.1f}" y="340" '
            f'text-anchor="middle" class="label">{html.escape(label)}</text>'
        )

    parts.append(
        f'<text x="795" y="218" text-anchor="end" class="label">'
        f'Best day: {best_count} contributions ({best_day.isoformat()})</text>'
    )
    parts.append("</svg>")

    OUTPUT_FILE.write_text("\n".join(parts), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}: {total} contributions, {active_days} active days.")


if __name__ == "__main__":
    main()
