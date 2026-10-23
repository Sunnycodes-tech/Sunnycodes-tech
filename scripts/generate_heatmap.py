import json
from pathlib import Path
from datetime import date
import html

DATA_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("contrib-heatmap.svg")

WIDTH = 860
CELL = 11
GAP = 3
LEFT = 40
TOP = 55

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main():
   data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
   days = data["days"]
   values = {item["date"]: item["count"] for item in days}


    dates = sorted(values)
    if not dates:
        raise RuntimeError("No contribution data found.")

    first = date.fromisoformat(dates[0])
    start = date.fromordinal(first.toordinal() - first.weekday())
    last = date.fromisoformat(dates[-1])
    weeks = ((last - start).days // 7) + 1
    height = TOP + 7 * (CELL + GAP) + 45

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">',
        '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
        '<text x="20" y="30" fill="#58a6ff" font-size="16" font-family="Arial" font-weight="bold">GitHub Contributions</text>',
    ]

    for week in range(weeks):
        for day_index in range(7):
            current = date.fromordinal(
                start.toordinal() + week * 7 + day_index
            )
            count = values.get(current.isoformat(), 0)

            if count == 0:
                color = COLORS[0]
            elif count <= 3:
                color = COLORS[1]
            elif count <= 6:
                color = COLORS[2]
            elif count <= 9:
                color = COLORS[3]
            else:
                color = COLORS[4]

            x = LEFT + week * (CELL + GAP)
            y = TOP + day_index * (CELL + GAP)

            rect = (
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{color}">'
                f'<title>{html.escape(current.isoformat())}: '
                f'{count} contributions</title></rect>'
            )
            parts.append(rect)

    parts.append("</svg>")
    OUTPUT_FILE.write_text("\n".join(parts), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE} using {len(data)} contribution dates.")


if __name__ == "__main__":
    main()
