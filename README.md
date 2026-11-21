# Domain Squatting Detector

A defensive domain-monitoring CLI that generates likely typo-squatted variants, checks DNS and mail-service indicators, and correlates results with Certificate Transparency records.

## Features

- Character omission, insertion, adjacent-key substitution, transposition, and homograph-style replacement generation
- A, AAAA, MX, NS, and CNAME resolution checks
- Certificate Transparency queries through crt.sh
- JSON and CSV report output
- Conservative thresholds and configurable target domains

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
python3 main.py --config config.yaml --format json
python3 main.py --domains example.com paypal.com --format csv
python3 main.py --check-limit 500 --ct-limit 100
```

Use this tool only for authorized monitoring and incident-response investigations. Respect DNS provider and crt.sh rate limits.

## Configuration

Edit `config.yaml` to set target domains, TLD variants, DNS/Certificate Transparency thresholds, and output format.
Targets must be YAML list items, with a space after each dash:

```yaml
targets:
  - newlinkigadgets.com
  - tesla.com
  - example.com
  - another-example.net
```

Each report row's `candidate` is a generated domain and `source_domain` is the
domain it was generated from. The JSON report includes every checked candidate,
including those with no DNS records. To list candidates, use:

```bash
jq -r '.[].candidate' output/<report-file>.json
```

Replace `<report-file>.json` with the report filename printed when the scan
finishes.
`exists: false` means no A, AAAA, MX, NS, or CNAME records were found; it does
not confirm that the domain is available for registration.
