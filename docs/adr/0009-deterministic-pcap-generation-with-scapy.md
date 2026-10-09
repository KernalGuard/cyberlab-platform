# ADR-0009: Deterministic PCAP generation with Scapy

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** FR-E-02, FR-E-06, NFR-05

## Context
Lab 1 needs PCAPs with normal background traffic and a hidden malicious pattern that varies per student, with an exact answer key.

## Decision
Generate packets with **Scapy**, using explicit timestamps from a seeded RNG, fixed IP IDs, TCP sequence numbers, and checksums computed by Scapy; build complete TCP conversations (handshake, data, teardown) so TShark's stream following and HTTP/DNS dissectors work. Validate with `tshark -r` (no malformed packets), `capinfos`, and the reference solution. Output pcapng with a fixed section header (no host-specific metadata).

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Capture live traffic between lab containers | Real TCP/IP stacks | Non-deterministic timing and sequence numbers | Breaks reproducibility; possible later as a realism check |
| Public PCAP datasets | Realistic | Solutions online; licensing; real addresses | Integrity |
| tcpreplay/tcprewrite edits of a base capture | Realistic base | Limited control over narrative | Less flexible |

## Consequences
+ Exact ground truth per seed. − Synthetic traffic can look "too clean"; mitigated by realistic jitter, background protocols, retransmissions, and decoys. Students are told the capture is synthetic.
**Untested:** Scapy behavior in the Debian 13 image; to verify in Week 2.
