#!/usr/bin/env python3
"""Convert a stimulus CSV to artworks.json for the Social Influence Task."""

import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Input CSV file")
    parser.add_argument("--n", type=int, default=50, help="Number of artworks to include (default: 50)")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON path (default: backend/app/stimuli/artworks.json)")
    args = parser.parse_args()

    if args.out is None:
        args.out = Path(__file__).resolve().parent.parent / "backend" / "app" / "stimuli" / "artworks.json"

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    artworks = []
    for row in rows[: args.n]:
        artworks.append({
            "id": int(row["ID"]),
            "title": row["Title"],
            "artist": row["Artist"],
            "year": int(row["Year"]),
            "medium": row["Medium"],
            "style": row.get("Style / Movement", row.get("Style/Movement", "")),
            "wikiart_url": row.get("WikiArt URL", ""),
            "image_url": "",
            "valence_category": row.get("Valence Category", ""),
            "familiarity_risk": row.get("Familiarity Risk", ""),
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(artworks, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(artworks)} artworks to {args.out}")


if __name__ == "__main__":
    main()
