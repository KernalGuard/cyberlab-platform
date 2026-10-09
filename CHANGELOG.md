# Changelog

All notable changes are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased] — Milestone 1 (Week 1)

### Added
- `cyberlab_common` shared library: SHA-256 manifests, HMAC seed derivation, `verify` framework, findings validation and scoring, reset with backup.
- `cyberlab-base` image (Debian 13 slim, Python 3, non-root `analyst` user, read-only friendly shell).
- Compose security baseline (`platform/compose/security-baseline.yaml`) for Pattern A and Pattern B labs.
- Lab 0 (Environment Orientation): compose file, `lab.yaml`, deterministic practice evidence, work templates, student guide, integration test.
- Student install guides (macOS, Windows/WSL 2, Linux) and a pre-flight checklist.
- CI (lint, unit, policy, leak scan, native amd64 + arm64 build and integration, Trivy report) and release workflow (multi-arch GHCR publish).
- Licenses (Apache-2.0 code, CC BY 4.0 docs), NOTICE, SECURITY, CONTRIBUTING, CITATION.

### Changed
- Lab 0 runs on `cyberlab-base` directly instead of a dedicated `lab0-orientation` image (fewer images; Lab 0 needs no extra tools).
- Removed the `# syntax=docker/dockerfile:1` directive: it fetches a frontend image from Docker Hub at build time, which fails on restricted networks.
- Lab 0 troubleshooting drill uses a container-name conflict instead of a port conflict (Lab 0 publishes no ports).

### Fixed (first macOS run, 2026-10-09)
- `verify` failed `network-isolation` on Docker Desktop: its LinuxKit kernel creates DOWN fallback tunnel devices (gre0, sit0, tunl0, …) in every network namespace. The check now counts only interfaces that are UP, plus IPv4/IPv6 default routes. Regression test added.
- `docker compose build` failed with `image … already exists`: three services each declared `build` for the same image. Only `workstation` builds now.

### Testing status (2026-10-09)
- Library: 69 unit tests pass as root and 70 as non-root (Python 3.13, Linux x86-64).
- Lab 0 container integration (13 checks) passes on Linux x86-64 as root and as a non-1000 user, using a **substitute Ubuntu 24.04 base** because Debian images could not be pulled in the development environment. **Debian 13 build, arm64, macOS and Windows: untested** until CI runs on GitHub and the macOS walkthrough is done.

## [0.0.1] — 2026-10-09
### Added
- Phase 1 requirements and feasibility package, ADRs 0001–0011, feasibility spikes.
