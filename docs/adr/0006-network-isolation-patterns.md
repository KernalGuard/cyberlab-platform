# ADR-0006: Network isolation patterns

- **Status:** Proposed
- **Date:** 2026-10-09
- **Related requirements:** SEC-04, SEC-05, SEC-06, NFR-10

## Context
Labs must never let students (or vulnerable services) reach external systems, and vulnerable services must never be exposed beyond the student's own machine. On Linux hosts, Docker's published ports bypass common host firewall rules (ufw), so "the firewall will catch it" is not a valid control.

## Decision
- **Pattern A (analysis labs 0–2):** `network_mode: none`. No interfaces other than loopback.
- **Pattern B (service labs 3–4):** all lab services on a Compose network with `internal: true`. A single reverse-proxy **gateway** joins both that network and a normal bridge network and is the *only* published port, bound to `127.0.0.1`. The gateway runs no student-controlled code.
- `verify` checks for violations (non-loopback bindings, unexpected networks, egress success).

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Default bridge + publish 0.0.0.0 | Simple | Exposes vulnerable app on LAN/campus Wi-Fi | Unsafe |
| Host firewall rules | Familiar | Docker bypasses them on Linux; per-OS differences | Unreliable |
| Browser inside the lab (noVNC) | No host port at all | ~1 GB extra RAM; laggy UX | Resource budget; possible later for hosted mode |

## Consequences
+ Even a fully compromised vulnerable app has no outbound route. + Maps to Kubernetes NetworkPolicy default-deny.
− The gateway container has bridge connectivity; keep it minimal and pinned. To validate in Phase 3: an integration test proving egress fails from each internal service.
