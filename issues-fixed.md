# Issues Fixed and Run Notes

This document records the problems encountered while configuring and running
the domain-squatting detector, what was changed, and how to interpret the
resulting JSON report.

## 1. One-character candidates in the original report

The original report contained entries such as:

```json
{
  "candidate": "t",
  "source_domain": "t",
  "a": [],
  "aaaa": [],
  "mx": [],
  "ns": [],
  "cname": [],
  "exists": false,
  "certificates": []
}
```

In the original report, line 121 showed `"certificates": []`. That value was
not the underlying error: it indicated that no certificate records were
returned for that candidate. The actual problem was that both `candidate` and
`source_domain` were a single character.

The target in `config.yaml` was written as `-https://www.tesla.com`, without a
space after the YAML list dash. YAML therefore loaded `targets` as one string
instead of a list. The code iterated that string character by character, and
the generator treated each character as a target.

The configuration now uses a proper domain list item:

```yaml
targets:
  - tesla.com
```

`build_variations` also treats a string target as one target, rather than
iterating over its characters. This protects against the same input-shape
mistake if it occurs again.

## 2. Candidates needed to be complete domain names

The generator previously emitted bare name fragments, such as `tesla`, as
candidates. Those are not complete internet domain names and made the output
confusing.

The generator now applies the source or replacement TLD to generated name
variants and filters out malformed names. For example, it can emit
`resla.com`, rather than the bare fragment `resla`. The `source_domain` field
continues to identify the configured domain from which each candidate was
generated.

## 3. What the refined JSON output means

The new report, `output/domain-squatting-report-20261121-034042.json`,
contains 50 candidate records, all associated with `tesla.com`. Nineteen have
DNS records and one has Certificate Transparency results. For example, the
report includes a record shaped like this:

```json
{
  "candidate": "resla.com",
  "source_domain": "tesla.com",
  "a": ["216.24.57.1"],
  "aaaa": [],
  "mx": ["..."],
  "ns": ["..."],
  "cname": [],
  "exists": true,
  "certificates": []
}
```

The actual IP, mail, name-server, and certificate values depend on the DNS and
Certificate Transparency responses at scan time. In the report:

- `candidate` is the generated domain being checked.
- `source_domain` is the configured input domain.
- `a`, `aaaa`, `mx`, `ns`, and `cname` contain the DNS answers found.
- `exists: true` means at least one of those DNS record types returned an
  answer. It does not mean the candidate is malicious.
- `certificates` contains Certificate Transparency results when available.
  An empty list means no results were included; it does not by itself prove
  that a domain has never had a certificate.
- `exists: false` means no queried DNS records were found. It does not confirm
  that the domain is available to register.

Older timestamped reports are not rewritten. Use the newest report for the
corrected candidate format.

## 4. Running with the right Python environment

Running `python3 main.py` with the system Python failed because that
interpreter did not have `dnspython` installed (`ModuleNotFoundError: No module
named 'dns'`). The project virtual environment already has the required
packages. Run the program with it:

```bash
.venv/bin/python main.py
```

Alternatively, activate the environment first and then use `python3`:

```bash
source .venv/bin/activate
python3 main.py
```

## 5. Why a full run can take a long time

The default configuration checks up to 1,000 candidates. For each candidate,
the program performs five DNS lookups in sequence (A, AAAA, MX, NS, and CNAME).
Each lookup can wait up to the configured three-second timeout. If DNS is slow,
the DNS checks alone can therefore take a long time; Certificate Transparency
queries can add further waits for candidates that have DNS records.

The program writes the report and prints its path only after all candidates
have been checked. It does not currently print incremental progress or save a
partial report, so the terminal can appear idle while the scan is running.

For a quicker, smaller scan, use:

```bash
.venv/bin/python main.py --check-limit 50 --ct-limit 10
```

`--check-limit 50` checks at most 50 candidates instead of the default 1,000.
`--ct-limit 10` limits the number of certificate records requested per
candidate; it does not reduce the DNS lookups. The most recent 50-record report
was produced with this smaller candidate limit.

The focused regression tests can be run with:

```bash
.venv/bin/python -m unittest discover -s tests -v
```
