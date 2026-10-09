# Open Decisions and Assumptions Requiring Confirmation

Items marked **Faculty** need a faculty sponsor or course instructor; **Institution** needs college or CUNY offices; **Developer** is yours to decide.

| ID | Decision / assumption | Who | Needed by | Default if undecided |
|---|---|---|---|---|
| OD-01 | Faculty sponsor/supervisor for the project and research | Faculty | Week 3 (R-12) | Continue as independent development; research stays at proposal stage |
| OD-02 | Which John Jay courses (numbers/titles) the labs target, and where in the semester | Faculty | Week 3 | Generic mapping: intro cyber (Labs 0–1), UG forensics (Lab 2), upper UG (Lab 3), grad (Lab 4) |
| OD-03 | GitHub owner: personal account vs. organization; public visibility of the student repo | Developer (+ Faculty) | Week 1 | Personal account, public platform repo, private instructor repo |
| OD-04 | LMS in use (assumed Brightspace) and whether it supports per-student file release | Institution | Week 3 | Pooled variants (K = 8) assigned via LMS groups |
| OD-05 | Storage of the pseudonym ↔ student map (encrypted file in private repo vs. instructor-only drive) | Faculty | Week 3 | Kept outside Git on instructor storage; never in any repo |
| OD-06 | Docker Desktop permitted for students; institutional view of its license; campus machines' virtualization/admin policy | Institution (IT) | Week 4 | Students use personal machines; free alternatives documented |
| OD-07 | Licenses: code Apache-2.0, docs CC BY 4.0; intellectual-property policy for student-developed course materials | Developer + Institution | Week 1 (placeholder OK) | Placeholders until confirmed |
| OD-08 | Course AI-use policy for lab reports | Faculty | Before pilot | Guides state "follow your course syllabus policy" |
| OD-09 | Access to a Windows 11 test machine | Developer | Week 3 | Windows tested in CI only (Docker on Windows runners is limited) — flagged as a gap |
| OD-10 | Volunteer testers (peers) for walkthroughs; testing must not be framed as research data collection | Developer | Week 3 | 1–2 peers per lab |
| OD-11 | IRB route: John Jay/CUNY human-research process, and whether the study is exempt; FERPA handling if grades are used | Institution (IRB) + Faculty | Submit by 2026-12-15 | No research data collected in Spring 2027 if not approved |
| OD-12 | Comparison condition for research (e.g., prior VM-based labs or another section) | Faculty | Phase 6 | Single-group design with pre/post measures (weaker; noted as a threat to validity) |
| OD-13 | Future cloud budget or credits (AWS Academy, grants) | Faculty / Institution | Phase 5 | Parameterized cost model only |
| OD-14 | Per-student vs. pooled variants for the pilot | Faculty | Week 3 | Pooled (K = 8) for pilot; per-student supported by tooling |
| OD-15 | Whether generators are published after each term (open science) or only a scrubbed reference generator | Developer + Faculty | Before first publication | Scrubbed reference generator published; live generators remain private |
