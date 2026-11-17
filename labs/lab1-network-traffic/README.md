# Lab 1 — Network Traffic Analysis and Threat Identification

| | |
|---|---|
| Level | Introductory undergraduate (graduate extension: scan analysis, report depth) |
| Time | 90–120 minutes (target) |
| Pattern | A: offline workstation, no network, read-only evidence |
| Version | 0.1.0 (in development — Milestone 2) |
| Tested on | Generator and reference solution: Linux x86-64, 2026-11-13, TShark 4.2.2 (10/10 seeds pass). Image build + `verify` 10/10 + guide Part D: macOS Apple Silicon, Docker Desktop, TShark 4.4.19, 2026-11-17. **Windows and CI integration: UNTESTED** |

**Scenario.** Cedarwick Neighborhood Aid, a fictional nonprofit, received an endpoint alert
on its staff workstation segment. You have one hour of traffic from a mirror port. Decide
whether a host is compromised, what it talked to, and whether data left the network.

**Evidence.** `evidence/` holds the public **demo** variant (`cedarwick-ws-segment.pcapng`,
`CASE-BRIEF.txt`, `MANIFEST.sha256`). For graded work your instructor gives you your own
variant; point the lab at it with `CYBERLAB_EVIDENCE=/path/to/your/evidence`.

**Student guide:** [`docs/student-guide.md`](docs/student-guide.md) (draft, 2026-11-17).
**Architecture:** [`docs/architecture.md`](docs/architecture.md). **Maintainer test:** `tests/integration.sh` (needs the image built).

**Quick reference**
```bash
docker compose pull
docker compose run --rm verify
docker compose run --rm reset
docker compose run --rm workstation
docker compose down --remove-orphans
```

**Maintainers:** evidence is produced by the private generator in `cyberlab-instructor/generators/lab1/`
(`generate.py --demo`). The demo is byte-reproducible; regenerate rather than edit it.
