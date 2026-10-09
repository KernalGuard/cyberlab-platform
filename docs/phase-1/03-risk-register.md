# Implementation Risk Register

Likelihood (L) and Impact (I) are scored 1 (low) – 3 (high). **Score = L × I.** Risks scoring ≥ 6 are reviewed every week.

| ID | Risk | L | I | Score | Mitigation | Trigger / early warning | Owner |
|---|---|---|---|---|---|---|---|
| R-01 | Students cannot install Docker (no admin rights, old hardware, Chromebook, virtualization disabled in BIOS) | 3 | 3 | **9** | Lab 0 pre-flight checklist sent one week before the first lab; Tier 2 browser-hosted fallback (dev container); offline image tarballs; early IT conversation | > 10% of pilot students fail Lab 0 | Developer + instructor |
| R-02 | Schedule overrun: four labs in eight weeks is ambitious for one part-time developer | 3 | 2 | **6** | MVP first (Lab 0 + Lab 1); Labs 3–4 may be beta at Week 8 and finished in Weeks 9–12, before the January pilot; scope cuts pre-agreed (see roadmap) | Week 3 MVP not accepted by 2026-10-30 | Developer |
| R-03 | **Synthetic realism gap:** `debugfs rm` leaves ext4 extent data intact, so deleted files are trivially recoverable — unlike deletion by the Linux kernel, which clears the inode's extent tree | 3 | 2 | **6** | **Found in spike, 2026-10-09.** Generator must emulate kernel behavior (zero the extent fields after deletion) so recovery requires carving from unallocated space; validate against an image produced by a real kernel in a VM; document any remaining differences to students | Recovery result differs from VM reference image | Developer |
| R-04 | Evidence not byte-reproducible (timestamps, UUIDs, hash seeds, nanosecond fields) | 2 | 3 | **6** | **Spike, 2026-10-09:** reproducibility achieved after pinning UUID/hash seed and normalizing every inode timestamp (+ `_extra` fields). CI double-build test on every commit | CI double-build hashes differ | Developer |
| R-05 | Answer leakage: generators, keys, or the public demo variant shared between students | 2 | 3 | **6** | Private instructor repo; HMAC-derived seeds; per-student or pooled variants; CI secret/leak scanning; rotate `course_secret` each term | Identical wrong answers across students | Instructor |
| R-06 | Students use AI assistants to complete analysis without understanding it | 3 | 2 | **6** | Variant-specific findings; graded reasoning and process notes; short in-class debrief questions; explicit course AI policy (faculty decision) | Polished reports with variant-inconsistent details | Faculty |
| R-07 | Vulnerable app exposed beyond loopback (student edits Compose, or a Linux host firewall is bypassed by Docker's iptables rules) | 2 | 3 | **6** | Bind to `127.0.0.1` only; `verify` checks published bindings; app refuses to start if `LAB_BIND` ≠ loopback; teardown instructions; authorized-use agreement | `verify` warning | Developer |
| R-08 | Apple Silicon / Windows differences produce different tool output (for example, TShark field changes) and break the auto-checker | 2 | 2 | 4 | Pin tool versions in images; auto-checker compares normalized values, not raw tool output; CI runs tests on amd64 and arm64 | Test diff across arches | Developer |
| R-09 | Docker Desktop updates change behavior mid-semester | 2 | 2 | 4 | Document a minimum version; test against current release monthly during term; known-issues page | Student reports after an update | Developer |
| R-10 | Lab 3/4 resource use exceeds 8 GB laptops | 2 | 2 | 4 | Per-service limits; PostgreSQL tuned small (or SQLite fallback); measure with `docker stats` in CI | Peak > 3 GB measured | Developer |
| R-11 | IRB timing prevents Spring 2027 data collection | 2 | 2 | 4 | Submit protocol by December 2026; pilot can proceed as normal instruction with no research data; research data collection can shift to Fall 2027 | IRB not submitted by 2026-12-15 | Developer + faculty sponsor |
| R-12 | No faculty sponsor or course slot confirmed | 2 | 3 | **6** | Open-decisions list goes to a prospective sponsor in Week 1; the platform remains valuable as an independent-study artifact | No sponsor by Week 3 | Developer |
| R-13 | Supply-chain risk from third-party images and packages | 2 | 2 | 4 | Debian base only; pin digests; vulnerability scanning; minimal packages; SBOM generated in CI | Critical CVE in scan | Developer |
| R-14 | TA/instructor grading load too high (≈ 80 reports × 4 labs) | 2 | 2 | 4 | Auto-checker covers 30–40 objective points; rubric with anchored descriptors; graded exemplar | Grading time > 15 min/report in pilot | Instructor |
| R-15 | Accessibility barriers (screen readers and the CLI, color-only Wireshark cues) | 2 | 2 | 4 | Text-first instructions; TShark text output path; consult the campus accessibility office | Accommodation request | Faculty |
| R-16 | AI workspace cannot pull container images (egress policy), so builds can't be tested here | 3 | 1 | 3 | Test generators and scripts natively here; build and test images in GitHub Actions and on the developer's Mac; label untested artifacts | — (known) | Developer |
| R-17 | Students run lab tooling against systems outside the lab | 1 | 3 | 3 | No-network labs; internal networks; authorized-use agreement; course policy references | Incident report | Faculty |
| R-18 | Docker Desktop license terms change, or are interpreted as not covering institutional use | 1 | 2 | 2 | Document free alternatives (Docker Engine on Linux, Colima, Rancher Desktop, Podman) and test with at least one | License notice | Developer |

## Spike evidence (2026-10-09)

Executed in this workspace (Ubuntu 24.04, x86-64, Sleuth Kit 4.12.1, e2fsprogs 1.47.0) as an unprivileged user:

- `mkfs.ext4 -d` + `debugfs -w` produced an ext4 image with backdated MAC/crtime timestamps and a deleted file. **No root, no loop mount.** ✅
- `fls -r -d` listed the deleted entry; `istat` showed the backdated and deletion times. ✅
- `icat` recovered the deleted file's content directly → **realism gap (R-03)**. ⚠️
- Two consecutive builds were byte-identical only after normalizing inode timestamps (SHA-256 `7dd5c46e…d1cc` both runs) → R-04 is manageable. ✅
- Normalizing *unallocated* inodes created spurious `$OrphanFiles` entries → the generator must touch only allocated inodes. ⚠️
- `mkfs.vfat` + `mcopy`/`mdel` built a FAT32 image without mounting; TSK showed the deleted entry with its first character replaced (`_ist.txt`), the classic FAT deletion artifact. ✅

Scripts are kept in [`docs/spikes/`](../spikes/) for reproducibility. **They are spike code, not production generators.**
