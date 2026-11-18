# Lab 4 — Incident Response and Multi-Source Digital Forensics

> **Status: IN DEVELOPMENT (Milestone 5).** Generator 1.0.0 and the public `demo` evidence, the `cyberlab-ir-workstation` image, Compose file (Pattern A), verify checks and work templates are written. Student guide, architecture document, integration test and CI job are not yet. **UNTESTED with Docker.**

| | |
|---|---|
| Level | Early graduate (upper undergraduate with support) |
| Time | 180 minutes (target) plus the written report |
| Pattern | A: one offline workstation, no network, read-only evidence |
| Version | 0.5.0-dev |

**Scenario.** Cedarwick Neighborhood Aid (fictional) closes its story. The board relaunched the donation website you assessed in Lab 3 with only one of your fixes. Ten days later a donor reports a phishing e-mail that quotes their receipt number and gift amount. You lead the investigation: how the attacker got in, what they took, whether they are still in, and what Cedarwick must do now.

**Evidence** (all synthetic):

| File | From | You will use |
|---|---|---|
| `web/gateway.jsonl`, `web/app.jsonl`, `web/postgres.log` | the donation site (Lab 3 formats) | jq, grep |
| `network/office-edge.pcapng` | the office firewall (Lab 1 format) | tshark |
| `hosts/coordinator-laptop.E01` | a staff laptop (Lab 2 style) | ewfexport, The Sleuth Kit, sqlite3 |
| `server/auth.log` | the web server | grep |
| `db/snapshot.sql` | the site database at response time | grep, Python |

**Deliverables.** `work/findings.json` (15 items), and `work/incident-report.md`: master timeline, conclusions with confidence and an alternative explanation, containment and recovery plan, donor notification draft, and (graduate) a tested detection rule.

```bash
cd labs/lab4-incident-response
docker compose pull
docker compose run --rm verify
docker compose run --rm workstation
```

The evidence is not a live system: nothing in this lab connects to anything. Every name, domain and address is fictional (reserved `.test`/`.example` domains, documentation address ranges).
