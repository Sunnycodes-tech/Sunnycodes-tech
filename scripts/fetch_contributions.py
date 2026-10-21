
import json
import re
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Sunnycodes-tech"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path("data/contributions.json")


def fetch_contributions():
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Each tooltip is linked to a calendar cell by its "for" attribute.
    cells = {
        cell.get("id"): cell
        for cell in soup.select("[data-date][id]")
    }

    contributions = {}

    for tooltip in soup.select("tool-tip[for]"):
        cell = cells.get(tooltip.get("for"))
        if not cell:
            continue

        day = cell.get("data-date")
        label = tooltip.get_text(" ", strip=True)

        if not day:
            continue

        if "no contributions" in label.lower():
            count = 0
        else:
            match = re.search(
                r"([\d,]+)\s+contributions?\s+on\b",
                label,
                re.IGNORECASE,
            )
            if not match:
                raise RuntimeError(
                    f"Could not parse tooltip for {day}: {label}"
                )
            count = int(match.group(1).replace(",", ""))

        contributions[day] = count

    if not contributions:
        raise RuntimeError("No daily contribution data found.")

    result = [
        {"date": day, "count": contributions[day]}
        for day in sorted(contributions)
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(result)} dates to {OUTPUT}")
    print(f"Total contributions: {sum(x['count'] for x in result)}")
    print(f"Active days: {sum(x['count'] > 0 for x in result)}")


if __name__ == "__main__":
    fetch_contributions()
