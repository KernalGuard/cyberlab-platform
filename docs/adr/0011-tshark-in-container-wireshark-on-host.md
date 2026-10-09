# ADR-0011: TShark in container is required; Wireshark GUI on host is optional

- **Status:** Proposed
- **Date:** 2026-10-09
- **Related requirements:** NFR-01, NFR-02, FR-P-05, NFR-09

## Context
Wireshark's GUI is the most familiar tool for beginners, but running a GUI from a container needs X11/VNC forwarding, which is fragile on macOS and Windows and costs memory.

## Decision
All required tasks are achievable with **TShark** (and `capinfos`/`editcap`) inside the `net-analysis` container. Evidence and exported files are available in the bind-mounted `work/` folder, so students *may* open them in a natively installed Wireshark. Guides show both paths, with TShark as the graded path. TShark's text output is also the more accessible route for screen-reader users.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Wireshark GUI via noVNC container | Browser-only, no host install | ~1 GB RAM; laggy; large image | Resource budget; possible for hosted mode |
| Require host Wireshark | Best GUI UX | Host dependency; version variance | Violates ADR-0004 |

## Consequences
+ Works identically everywhere; teaches scriptable, repeatable analysis. − Beginners face a CLI learning curve; Lab 0 and guided Lab 1 steps compensate.
