# Architecture Decision Records

Each significant technical decision is recorded here using a lightweight variant of Michael Nygard's ADR format. ADRs are **immutable once accepted**: a changed decision gets a new ADR that supersedes the old one. Together they form the design-rationale record for the research report's methodology section (RES-05).

| ADR | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-docker-compose-primary-runtime.md) | Docker Compose as primary runtime; Kubernetes deferred | Accepted |
| [0003](0003-two-repository-split.md) | Public platform repo + private instructor repo | Accepted |
| [0004](0004-host-depends-only-on-docker.md) | Host depends only on Docker; all scripts run in containers | Accepted |
| [0005](0005-base-image-debian-slim-multiarch.md) | Debian 13 slim multi-arch base image | Accepted |
| [0006](0006-network-isolation-patterns.md) | Network isolation patterns A and B | Accepted |
| [0007](0007-synthetic-evidence-and-pseudonymous-seeds.md) | Synthetic deterministic evidence with HMAC-derived pseudonymous seeds | Accepted |
| [0008](0008-userspace-forensic-image-generation.md) | Generate disk images in user space (no loop mounts) | Accepted |
| [0009](0009-deterministic-pcap-generation-with-scapy.md) | Deterministic PCAP generation with Scapy | Accepted |
| [0010](0010-purpose-built-vulnerable-web-app.md) | Purpose-built vulnerable web app instead of DVWA/Juice Shop | Accepted |
| [0011](0011-tshark-in-container-wireshark-on-host.md) | TShark in container required; Wireshark GUI on host optional | Accepted |

Template: [0000-template.md](0000-template.md)
