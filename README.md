# CyberLab — Containerized Cybersecurity & Digital Forensics Laboratories

A reusable, security-hardened platform of hands-on laboratories for undergraduate and early-graduate cybersecurity and digital forensics courses. It is built on Docker and Docker Compose, with seeded synthetic evidence and reproducible grading.

> **Project status: Milestone 1 (platform foundation + Lab 0) — in development.**
> Lab 0 has passed its container integration tests on Linux x86-64 with a substitute base image. Debian 13, arm64, macOS and Windows runs are pending (CI and walkthroughs). Nothing has been classroom-tested.

| Lab | Topic | Audience | Status |
|---|---|---|---|
| [0](labs/lab0-orientation/) | Environment orientation (Docker, Linux shell, hashing) | All | **Built**, partially tested |
| 1 | Network Traffic Analysis & Threat Identification | Intro UG | Planned — MVP, Weeks 2–3 |
| 2 | Linux File-System Forensics & Evidence Examination | Intermediate UG | Planned |
| 3 | Web Application Security Assessment | Upper UG | Planned |
| 4 | Incident Response & Multi-Source Digital Forensics | Early graduate | Planned |

## Students
1. [Set up Docker](docs/student/README.md) (do this before your first lab).
2. Complete [Lab 0](labs/lab0-orientation/docs/student-guide.md).

The only software you need is **Docker** (with Compose). Every lab script runs inside a container.

## Instructors and reviewers
- Design: [Phase 1 package](docs/phase-1/README.md) · [Architecture Decision Records](docs/adr/README.md) · [Security model](SECURITY.md)
- Answer keys, rubrics and evidence generators for graded variants are in a separate **private** instructor repository.

## Repository layout
```
platform/   shared base image, Python library (cyberlab_common), Compose security baseline, schemas
labs/       one folder per lab: compose.yaml, lab.yaml, evidence, student guide, tests
tests/      cross-lab policy, documentation and leak tests
docs/       requirements, architecture, ADRs, student setup guides, spikes
```

## Maintainer note: image registry
Images are published to `ghcr.io/kernalguard/` by the release workflow (GHCR requires a lower-case owner). Until the first tagged release, build locally with `docker compose build`. Override with `CYBERLAB_REGISTRY` if needed.

## License
Code: [Apache-2.0](LICENSE). Documentation and instructional materials: [CC BY 4.0](LICENSE-docs). *Licensing is pending institutional confirmation.*

All evidence is synthetic. All labs are isolated sandboxes for authorized educational use only.
