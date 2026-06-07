"""Convert a JSON array file into Elasticsearch-friendly JSONL/ndJSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8") as source:
        data = json.load(source)

    if not isinstance(data, list):
        raise ValueError("input must be a JSON array")

    with output_path.open("w", encoding="utf-8") as target:
        for item in data:
            target.write(json.dumps(item, ensure_ascii=False) + "\n")

    return len(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    count = convert(args.input, args.output)
    print(f"converted {count} records to {args.output}")


if __name__ == "__main__":
    main()

