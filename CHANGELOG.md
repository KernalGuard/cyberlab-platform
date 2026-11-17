# Changelog

All notable changes are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

## [0.2.1] — 2026-11-17 — Lab 1 continuity fix

### Changed
- Lab 1 demo evidence regenerated with generator 1.1.0: the compromised workstation's own browser now reports **Ubuntu Linux**, while its implant keeps sending a fake Windows User-Agent. This makes Lab 1 consistent with Lab 2, which examines the same workstation's (Linux) disk, and adds a lesson: a User-Agent is chosen by the sender and can lie. **All answer values are unchanged** (same seed, same indicators); only the capture bytes differ.
- Student guide Part C and guided question 5 ask students to compare the suspect host's User-Agents with each other.
- Lab 1 images and Compose default to `0.2.1`.

### Testing status (2026-11-17)
- Generator 1.1.0: 10/10 seeds byte-reproducible, 0 malformed, reference solution 40/40 (TShark 4.2.2, Python 3.13, Scapy 2.8.0).

## [0.2.0] — 2026-11-17 — Lab 1 (Milestone 2)

### Added
- **Lab 1 — Network Traffic Analysis and Threat Identification** (`labs/lab1-network-traffic/`): the Cedarwick Neighborhood Aid scenario, public `demo` evidence (≈ 17 MB pcapng, case brief, manifest), Compose file (Pattern A), `lab.yaml` verify checks, work templates (`findings.json`, case notes, chain of custody).
- Lab 1 student guide (all 16 sections; DNS/DGA, HTTP check-ins, upload decoding, findings format) and architecture document.
- `cyberlab-net-analysis` image (TShark 4.4, capinfos, editcap, mergecap) built on `cyberlab-base`.
- Lab 1 container integration test (`tests/integration.sh`, ≈ 25 checks; asserts no case answers) and its CI job on amd64 and arm64, with image-size reporting and a Trivy report for both images.
- Reusable release workflow (`.github/workflows/_build-image.yml`): the release now publishes `cyberlab-base` and then `cyberlab-net-analysis` built on the same-version base.

### Changed
- Lab 1 images and Compose default to version `0.2.0`; Lab 0 stays on `0.1.0` (published images are never overwritten).

### Fixed
- hadolint DL3006 (ARG-based `FROM`) and DL4006 (pipefail) in both Dockerfiles; CI is green for the first time.

### Testing status (2026-11-17)
- CI on GitHub Actions: lint, unit, policy, leak, Lab 0 and Lab 1 integration on linux/amd64 and linux/arm64 all pass. Lab 1 peak memory 92–93 MB (limit 512 MB); `cyberlab-net-analysis` ≈ 100 MB compressed.
- macOS Apple Silicon (Docker Desktop): Lab 1 build, `verify` 10/10, guide Part D decode.
- **Untested:** Windows; a student walkthrough of Lab 1; the two-image release workflow until this tag runs.

## [0.1.0] — 2026-11-17 — Milestone 1 (platform foundation + Lab 0)

First tagged release: `ghcr.io/kernalguard/cyberlab-base:0.1.0` (amd64 + arm64).

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
