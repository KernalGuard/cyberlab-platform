# ADR-0002: Docker Compose as primary runtime; Kubernetes deferred

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** FR-P-01, NFR-01, NFR-02, NFR-10

## Context
Students run labs on personal laptops (8 GB RAM minimum) with little Linux or Docker experience. Future hosted delivery for 25–100 concurrent students is desired but unfunded. Kubernetes is attractive for multi-tenant hosting but adds substantial conceptual and operational load.

## Decision
Use **Docker Compose (Compose Specification, Compose v2)** as the only supported runtime for Release 1. Apply Kubernetes-readiness rules (architecture §10) so a later migration is mechanical. Evaluate Kubernetes in Phase 5 strictly for *hosted, multi-student* delivery, never as a student-laptop requirement.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Virtual machines (VirtualBox/UTM OVA) | Strong isolation; full OS | Multi-GB downloads; x86/ARM split (an x86 OVA does not run well on Apple Silicon); slow reset | Fails accessibility and reproducibility goals for the 4 Release-1 labs; kept for VM-only future workloads |
| kind / k3d on laptops | Teaches Kubernetes | Extra RAM; more failure modes; Kubernetes is not a learning objective of these courses | Adds complexity without a learning benefit |
| Plain `docker run` scripts | Simplest | No multi-service orchestration; shell scripts break on Windows | Lab 3/4 need multi-service |
| Vagrant | Reproducible VMs | Same VM drawbacks; provider issues on Apple Silicon | As above |

## Consequences
+ One tool students learn in Lab 0 serves all labs. + Fast reset (`down -v` and `up`). + Low RAM.
− Container (not VM) isolation; mitigated by ADR-0006 and by keeping live-malware work out of scope.
Revisit when hosted delivery is funded (Phase 5) or a lab requires VM-level isolation.
