"""Filter sports-related records from a line-delimited Chinese QA corpus.

This is a cleaned reconstruction of the original internship script. The input
is expected to be JSONL, where each line is one QA record.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SPORTS_KEYWORDS = ("体育", "运动", "足球", "篮球", "排球", "网球", "乒乓球", "羽毛球")


def is_sports_record(record: dict[str, Any]) -> bool:
    """Return True when a record is likely related to sports."""
    fields = [
        str(record.get("category", "")),
        str(record.get("topic", "")),
        str(record.get("title", "")),
        str(record.get("desc", "")),
    ]
    text = " ".join(fields)
    return any(keyword in text for keyword in SPORTS_KEYWORDS)


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize different QA corpus schemas into one FAQ schema."""
    question = record.get("question") or record.get("title") or ""
    answer = record.get("answers") or record.get("answer") or record.get("content") or ""

    if isinstance(answer, list):
        answer = "\n".join(str(item) for item in answer)

    return {
        "qid": str(record.get("qid", "")),
        "category": record.get("category") or record.get("topic") or "",
        "question": str(question).strip(),
        "desc": str(record.get("desc", "")).strip(),
        "answers": str(answer).strip(),
    }


def filter_file(input_path: Path, output_path: Path) -> int:
    count = 0
    with input_path.open("r", encoding="utf-8") as source, output_path.open(
        "w", encoding="utf-8"
    ) as target:
        for line in source:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not is_sports_record(record):
                continue
            normalized = normalize_record(record)
            if normalized["question"] and normalized["answers"]:
                target.write(json.dumps(normalized, ensure_ascii=False) + "\n")
                count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    count = filter_file(args.input, args.output)
    print(f"wrote {count} sports QA records to {args.output}")


if __name__ == "__main__":
    main()

