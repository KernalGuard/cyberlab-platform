# Security Policy and Lab Safety Model

## Authorized use only
These laboratories are **isolated educational sandboxes**. Techniques practised here may be used **only** inside the lab environments provided, or on systems you own or have written permission to test. Using them anywhere else may be illegal and violates course and college policy.

## How the labs are isolated
- Analysis labs (0–2) run with **no network** at all.
- Service labs (3–4) use **internal-only** Docker networks; the single exposed port binds to `127.0.0.1` (your own computer).
- Containers run as a **non-root** user with **all Linux capabilities dropped**, `no-new-privileges`, a **read-only** root filesystem and CPU/memory/process limits.
- Evidence is mounted **read-only** and verified by SHA-256 manifest.
- All evidence is **synthetic**; no real personal data or live malware is distributed.

Containers are not virtual machines: they share a kernel. See [docs/phase-1/02-architecture.md §8](docs/phase-1/02-architecture.md#8-container-vs-virtual-machine-feasibility) for the limits of this isolation and the workloads that require VMs.

## Reporting a problem
If you find a way to break isolation, reach the internet from a no-network lab, modify evidence, or see answer-key material in this public repository, **do not share it publicly**. Report it privately to the maintainer through the course instructor or a GitHub private security advisory on this repository.
