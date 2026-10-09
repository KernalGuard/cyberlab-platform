# ADR-0005: Debian 13 slim multi-arch base image

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** FR-P-06, FR-P-08, NFR-01, SEC-10

## Context
Images must run natively on amd64 and arm64 (Apple Silicon). Forensic tools (Sleuth Kit, TShark, e2fsprogs) should come from a maintained distribution with security updates.

## Decision
All tool images derive from `debian:trixie-slim` (Debian 13), pinned by digest at release. Tools come from Debian packages where available; Python libraries are pinned in `requirements.txt` with hashes. Builds use native arm64 GitHub runners rather than QEMU emulation.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Ubuntu 24.04 | Familiar | Larger; older TShark (4.2.x in noble) | Debian slimmer, newer tool versions |
| Alpine | Very small | musl libc quirks with Python wheels and some forensic tools | Compatibility risk |
| Kali / REMnux / SIFT images | Tools preinstalled | Very large (GBs); amd64-centric; many tools unused | Fails resource/arch goals; poor least-functionality |

## Consequences
+ One OS across labs; predictable package versions. − Must monitor Debian security updates and rebuild images regularly (monthly in term).

## Evidence
Debian 13 package listings (checked 2026-10-09): sleuthkit 4.12.1, tshark 4.4.x. GitHub arm64 hosted runners are generally available for public repositories (GitHub changelog, 2025-08-07).
