#!/usr/bin/env python3

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Iterable

import yaml

from modules.cert_logger import CertificateTransparencyLogger
from modules.dns_checker import DnsChecker
from modules.generator import DomainVariationGenerator


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError("Configuration root must be a mapping")
    return config


def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower().rstrip(".")
    if "://" in domain:
        from urllib.parse import urlparse

        domain = urlparse(domain).hostname or domain
    return domain


def build_variations(
    domains: Iterable[str], replacement_tlds: Iterable[str], limit: int
) -> dict[str, str]:
    if limit <= 0:
        return {}
    if isinstance(domains, str):
        domains = [domains]
    generator = DomainVariationGenerator(replacement_tlds=replacement_tlds)
    candidates = {}
    for domain in domains:
        normalized = normalize_domain(domain)
        if not normalized:
            continue
        for candidate in generator.generate(normalized):
            candidates.setdefault(candidate, normalized)
            if len(candidates) >= limit:
                return candidates
    return candidates


def write_report(records: list[dict], output_dir: Path, output_format: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = "json" if output_format == "json" else "csv"
    path = output_dir / f"domain-squatting-report-{timestamp}.{suffix}"

    if output_format == "json":
        path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    else:
        fieldnames = [
            "candidate",
            "source_domain",
            "a",
            "aaaa",
            "mx",
            "ns",
            "cname",
            "exists",
            "certificates",
        ]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                row = dict(record)
                row["certificates"] = len(row.get("certificates", []))
                for key in ("a", "aaaa", "mx", "ns", "cname"):
                    value = row.get(key)
                    row[key] = ";".join(value) if isinstance(value, list) else value
                writer.writerow({key: row.get(key) for key in fieldnames})
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and monitor likely domain-squatting variants."
    )
    parser.add_argument("--config", default="config.yaml", help="Path to YAML configuration")
    parser.add_argument("--domains", nargs="+", help="Target domains (overrides config)")
    parser.add_argument("--format", choices=("json", "csv"), help="Report format")
    parser.add_argument("--check-limit", type=int, help="Maximum DNS candidates to check")
    parser.add_argument("--ct-limit", type=int, help="Maximum Certificate Transparency records")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(Path(args.config))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Error loading configuration: {exc}", file=sys.stderr)
        return 1

    targets = args.domains or config.get("targets", [])
    replacement_tlds = config.get("replacement_tlds", ["com", "net", "org", "io", "co"])
    thresholds = config.get("thresholds", {})
    output_config = config.get("output", {})
    dns_limit = args.check_limit or thresholds.get("dns_check_limit", 1000)
    ct_limit = args.ct_limit or thresholds.get("cert_check_limit", 100)
    output_format = args.format or output_config.get("format", "json")
    output_dir = Path(output_config.get("directory", "output"))

    normalized_targets = [normalize_domain(value) for value in targets]
    candidates = build_variations(normalized_targets, replacement_tlds, dns_limit)
    dns_checker = DnsChecker(timeout=float(thresholds.get("dns_timeout_seconds", 3)))
    ct_logger = CertificateTransparencyLogger()

    records = []
    for candidate, source in candidates.items():
        dns_result = dns_checker.check(candidate)
        certificates = ct_logger.query(candidate, limit=ct_limit) if dns_result["exists"] else []
        records.append({"candidate": candidate, "source_domain": source, **dns_result, "certificates": certificates})

    report_path = write_report(records, output_dir, output_format)
    print(f"Checked {len(records)} candidates")
    print(f"Report saved to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

