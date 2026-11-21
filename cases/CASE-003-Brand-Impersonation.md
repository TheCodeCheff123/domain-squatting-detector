# CASE-003: Brand-Impersonation Domain Investigation

## Executive Summary

This case study demonstrates a defensive workflow for identifying and triaging likely domain-squatting infrastructure associated with a protected brand. The evidence should be used to prioritize threat intelligence, monitoring, and authorized takedown or security actions.

## Scope

- **Case class:** Brand impersonation / typosquatting
- **Environment:** External internet-facing domains
- **Method:** Variation generation, DNS enrichment, and Certificate Transparency correlation
- **Constraint:** Names and example indicators are placeholders; replace them only with authorized investigative data

## Detection Method

1. Define approved root domains and candidate TLDs.
2. Generate common typo variants, including omissions, substitutions, transpositions, insertions, and TLD changes.
3. Query A, AAAA, MX, NS, and CNAME records.
4. Correlate active domains with recent Certificate Transparency entries.
5. Export findings to CSV or JSON for incident tracking.

## Triage Criteria

- **High priority:** Active DNS, MX, or certificate records matching a protected brand or similar name.
- **Medium priority:** A newly registered or previously unseen domain with active web or mail infrastructure.
- **Low priority:** A parked domain, wildcard response, CDN-only record, or a plausible unrelated name.

## Analyst Validation

1. Confirm the candidate is reachable and whether the result is a parking provider or known infrastructure.
2. Review certificate names, issuers, validity windows, and screenshot context when available.
3. Check WHOIS/RDAP history and passive DNS according to organizational policy.
4. Determine whether use is benign, abandoned, or malicious.
5. Record confidence, rationale, and source timestamps.

## Escalation

For a confirmed impersonation site:

- Preserve evidence in a case-management system.
- Notify the brand owner or security team.
- Block or detect the domain through approved email, DNS, and web controls.
- Escalate for takedown, legal review, or law-enforcement coordination where appropriate.

## Recruiter-Oriented Outcome

This workflow demonstrates structured threat hunting, DNS and certificate analysis, data normalization, repeatable CLI tooling, and documented incident-response decision-making.
