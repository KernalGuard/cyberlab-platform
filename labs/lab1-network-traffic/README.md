# Lab 1 — Network Traffic Analysis and Threat Identification

| | |
|---|---|
| Level | Introductory undergraduate (graduate extension: scan analysis, report depth) |
| Time | 90–120 minutes (target) |
| Pattern | A: offline workstation, no network, read-only evidence |
| Version | 0.2.1 (pilot preview, 2026-11-17; demo evidence from generator 1.1.0) |
| Tested on | CI integration test (≈ 25 checks) on linux/amd64 and linux/arm64, 2026-11-17. macOS Apple Silicon (Docker Desktop, TShark 4.4.19): build, `verify` 10/10, guide Part D, 2026-11-17. Generator 1.1.0: 10/10 seeds, 2026-11-17. **Windows: UNTESTED. No student walkthrough yet.** |

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
