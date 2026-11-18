# CyberLab — Containerized Cybersecurity & Digital Forensics Laboratories

A reusable, security-hardened platform of hands-on laboratories for undergraduate and early-graduate cybersecurity and digital forensics courses. It is built on Docker and Docker Compose, with seeded synthetic evidence and reproducible grading.

> **Project status: v0.3.0, pilot preview. Labs 0, 1 and 2 are released.**
> All three labs pass their container integration tests in CI on linux/amd64 and linux/arm64 and run on macOS Apple Silicon (Docker Desktop). Windows has not been tested yet. Nothing has been classroom-tested.

| Lab | Topic | Audience | Status |
|---|---|---|---|
| [0](labs/lab0-orientation/) | Environment orientation (Docker, Linux shell, hashing) | All | **Released** (v0.1.0) |
| [1](labs/lab1-network-traffic/) | Network Traffic Analysis & Threat Identification | Intro UG (graduate extension) | **Released** (v0.2.1), awaiting first student walkthrough |
| [2](labs/lab2-filesystem-forensics/) | Linux File-System Forensics & Evidence Examination | Intermediate UG (graduate extension) | **Released** (v0.3.0), awaiting first student walkthrough |
| [3](labs/lab3-webapp-assessment/) | Web Application Security Assessment | Upper UG (graduate extension) | **Released** (v0.4.0), awaiting first student walkthrough |
| 4 | Incident Response & Multi-Source Digital Forensics | Early graduate | Planned |

## Students
1. [Set up Docker](docs/student/README.md) (do this before your first lab).
2. Complete [Lab 0](labs/lab0-orientation/docs/student-guide.md).
3. Lab 1: [Network Traffic Analysis](labs/lab1-network-traffic/docs/student-guide.md). Practice with the `demo` evidence; your instructor gives you your own evidence for graded work.
4. Lab 2: [Linux File-System Forensics](labs/lab2-filesystem-forensics/docs/student-guide.md), which continues the Lab 1 incident.
5. Lab 3: [Web Application Security Assessment](labs/lab3-webapp-assessment/docs/student-guide.md): an authorised test of Cedarwick's donation website.

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
Images (`cyberlab-base`, `cyberlab-net-analysis`, `cyberlab-fs-forensics`) are published to `ghcr.io/kernalguard/` by the release workflow on a `v*` tag (GHCR requires a lower-case owner). New packages start private: set each to Public once. To build locally instead, use `docker compose build workstation` in a lab folder. Override with `CYBERLAB_REGISTRY` if needed.

## License
Code: [Apache-2.0](LICENSE). Documentation and instructional materials: [CC BY 4.0](LICENSE-docs). *Licensing is pending institutional confirmation.*

All evidence is synthetic. All labs are isolated sandboxes for authorized educational use only.
