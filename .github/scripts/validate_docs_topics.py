"""Read-only validator for DOCS Topic metadata and link drift.

Dialect: repository-policy. This module validates deterministic repository
contracts and never modifies the checked artifacts or their baseline.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
DEFAULT_BASELINE = REPOSITORY_ROOT / ".github" / "knowledge-link-baseline.txt"
TOPIC_FIELDS = ("topic", "created", "updated")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


@dataclass(frozen=True)
class Finding:
    code: str
    location: str
    message: str

    def render(self) -> str:
        return f"{self.code}\t{self.location}\t{self.message}"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate DOCS Topic metadata and detect new broken links."
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Known legacy broken-link baseline.",
    )
    parser.add_argument(
        "--strict-existing-links",
        action="store_true",
        help="Fail for every broken link, including baseline entries.",
    )
    parser.add_argument(
        "--print-broken-links",
        action="store_true",
        help="Print normalized broken-link keys for baseline maintenance.",
    )
    return parser.parse_args()


def repository_relative(path: Path) -> str:
    return path.resolve().relative_to(REPOSITORY_ROOT).as_posix()


def topic_directories() -> list[Path]:
    return sorted(
        path
        for path in DOCS_ROOT.iterdir()
        if path.is_dir()
        and not path.name.startswith((".", "_"))
        and path.name != "collections"
    )


def parse_topic_yaml(path: Path) -> tuple[dict[str, str], list[Finding]]:
    values: dict[str, str] = {}
    findings: list[Finding] = []
    location = repository_relative(path)

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(?:\"([^\"]*)\"|'([^']*)'|([^#]*?))\s*", line)
        if match is None:
            findings.append(
                Finding("TOPIC_YAML_SYNTAX", f"{location}:{line_number}", raw_line)
            )
            continue
        key = match.group(1)
        value = next(
            group for group in match.groups()[1:] if group is not None
        ).strip()
        if key in values:
            findings.append(
                Finding("TOPIC_YAML_DUPLICATE", f"{location}:{line_number}", key)
            )
        values[key] = value

    return values, findings


def validate_topic(topic_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    relative_dir = repository_relative(topic_dir)
    metadata_path = topic_dir / "topic.yaml"

    if not metadata_path.is_file():
        findings.append(Finding("TOPIC_YAML_MISSING", relative_dir, "topic.yaml"))
    else:
        values, parse_findings = parse_topic_yaml(metadata_path)
        findings.extend(parse_findings)
        actual_fields = tuple(values)
        if set(actual_fields) != set(TOPIC_FIELDS):
            findings.append(
                Finding(
                    "TOPIC_YAML_FIELDS",
                    repository_relative(metadata_path),
                    f"expected={','.join(TOPIC_FIELDS)} actual={','.join(actual_fields)}",
                )
            )
        if values.get("topic") != topic_dir.name:
            findings.append(
                Finding(
                    "TOPIC_NAME_MISMATCH",
                    repository_relative(metadata_path),
                    f"expected={topic_dir.name} actual={values.get('topic', '')}",
                )
            )

        parsed_dates: dict[str, date] = {}
        for field in ("created", "updated"):
            raw_value = values.get(field, "")
            try:
                parsed_dates[field] = date.fromisoformat(raw_value)
            except ValueError:
                findings.append(
                    Finding(
                        "TOPIC_DATE_INVALID",
                        repository_relative(metadata_path),
                        f"{field}={raw_value}",
                    )
                )
        if (
            "created" in parsed_dates
            and "updated" in parsed_dates
            and parsed_dates["updated"] < parsed_dates["created"]
        ):
            findings.append(
                Finding(
                    "TOPIC_DATE_ORDER",
                    repository_relative(metadata_path),
                    "updated is earlier than created",
                )
            )

    summaries = sorted(topic_dir.glob("00-*.md"))
    if len(summaries) != 1:
        findings.append(
            Finding(
                "TOPIC_SUMMARY_COUNT",
                relative_dir,
                f"expected=1 actual={len(summaries)}",
            )
        )

    return findings


def link_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", maxsplit=1)[0].strip()
    if not target or re.match(r"^(?:https?|mailto|data):", target, re.IGNORECASE):
        return None
    return unquote(target)


def broken_link_keys() -> set[str]:
    broken: set[str] = set()
    for markdown_path in sorted(DOCS_ROOT.rglob("*.md")):
        text = markdown_path.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            target = link_target(match.group(1))
            if target is None:
                continue
            resolved = (markdown_path.parent / target).resolve()
            if not resolved.exists():
                broken.add(
                    f"{repository_relative(markdown_path)} -> {match.group(1).strip()}"
                )
    return broken


def read_baseline(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = parse_arguments()
    findings: list[Finding] = []

    for topic_dir in topic_directories():
        findings.extend(validate_topic(topic_dir))

    broken = broken_link_keys()
    baseline_path = args.baseline.resolve()
    baseline = read_baseline(baseline_path)
    new_broken = broken - baseline
    resolved_legacy = baseline - broken

    if args.print_broken_links:
        for item in sorted(broken):
            print(item)

    for item in sorted(new_broken):
        findings.append(Finding("BROKEN_LINK_NEW", item, "not present in baseline"))
    if args.strict_existing_links:
        for item in sorted(broken & baseline):
            findings.append(Finding("BROKEN_LINK_LEGACY", item, "strict mode"))

    for finding in findings:
        print(f"ERROR\t{finding.render()}")
    for item in sorted(broken & baseline):
        print(f"WARN\tBROKEN_LINK_BASELINED\t{item}")
    for item in sorted(resolved_legacy):
        print(f"NOTICE\tBASELINE_ENTRY_RESOLVED\t{item}")

    print(
        "SUMMARY\t"
        f"topics={len(topic_directories())}\t"
        f"errors={len(findings)}\t"
        f"broken_links={len(broken)}\t"
        f"baselined={len(broken & baseline)}"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
