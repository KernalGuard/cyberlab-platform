# CyberLab — Research Methodology (draft for faculty review and IRB submission)

> **Status:** Draft 0.1 (2026-11-18). Not reviewed by a faculty sponsor or the IRB. **No student data may be collected for research until the CUNY HRPP has issued an exempt determination or approval (RES-02).** Instruments are in [instruments.md](instruments.md). Items marked **[confirm]** need the faculty sponsor, the course instructor or the John Jay HRPP Coordinator.

| Field | Value |
|---|---|
| Working title | Containerized, seeded virtual laboratories for cybersecurity and digital forensics education: a feasibility and learning-outcomes pilot |
| Student investigator | Sharif Vadon, M.S. Digital Forensics and Cybersecurity, John Jay College (CUNY) |
| Faculty advisor | **[confirm — OD-01; required for a student-led IRB submission]** |
| Setting | One or more John Jay courses that adopt the labs in Spring 2027 **[confirm course numbers — OD-02]** |
| Intervention | CyberLab Labs 0–4 (v0.5.0 or later), used as normal course assignments |
| Target submission | IRBManager, by 2026-12-15 (risk R-11) |

## 1. Purpose

Hands-on cybersecurity and forensics labs usually depend on campus computer labs or heavyweight virtual machines. CyberLab delivers each lab as Docker containers that run on a student's own computer, with a per-student, reproducible evidence set and a partly automated grading pipeline. This study asks whether that approach is **feasible** in real courses and whether it is associated with **learning gains** and acceptable **usability** for students and **workload** for instructors.

The study evaluates the *labs as an instructional practice*, not individual students.

## 2. Research questions

| ID | Question | Primary evidence |
|---|---|---|
| RQ1 Feasibility | Can students set up and complete the labs on their own computers, and what blocks them? | Setup success rate and time (Lab 0), `verify` reports, help requests by category |
| RQ2 Learning | Is lab completion associated with gains in (a) task self-efficacy and (b) performance on lab-aligned skills? | Pre/post self-efficacy survey; pre/post skills check; consented lab scores |
| RQ3 Student experience | How usable and valuable do students find the labs, and how do they perceive the realism and the continuing case story? | System Usability Scale (SUS); Likert items; open-ended responses |
| RQ4 Instructor experience and grading | What does it cost instructors to run the labs, and how well does automated scoring agree with human grading? | Instructor time log and interview; auto-score vs. second-grader agreement on consented reports |

**Hypotheses (directional, for RQ2):** post-test self-efficacy and skills scores will exceed pre-test scores. RQ1, RQ3 and RQ4 are descriptive.

## 3. Design

**Mixed methods, single group, pre/post** within the course(s) that adopt the labs. If another section of the same course runs its usual (non-CyberLab) labs in the same term, it may serve as a **non-equivalent comparison group** for RQ2 **[confirm — OD-12]**; otherwise the single-group design is used and its limits are reported (section 9).

```
Week 1          Weeks 1–2     Weeks 3–12             End of term          After grades are final
Consent  ──▶    Pre-survey    Labs 0–4 (normal       Post-survey          Instructor interview;
(online)        + skills       coursework; verify     + skills check       consented scores and
                check          reports kept)          + SUS                reports released to the
                                                                          researcher (de-identified)
```

## 4. Participants and recruitment

- **Population:** students enrolled in the adopting course(s), 18 or older. Students under 18 may complete the labs as coursework but are **excluded** from the research data.
- **Expected size:** 20–80 students across one to three sections **[confirm]**. For RQ2, a paired comparison with a medium effect (d = 0.5), α = 0.05 and power 0.80 needs about 34 participants; with fewer, RQ2 is reported as exploratory with effect sizes and confidence intervals.
- **Instructors:** the instructor(s) of the adopting course(s), for RQ4 only, with separate consent.
- **Recruitment** is done by the student investigator, **not by the course instructor**, through a short in-class or LMS announcement (script in [instruments.md](instruments.md)). The instructor leaves the room or does not post the announcement.
- **Voluntariness:** participation has no effect on grades. **No extra credit is offered** (this avoids an alternative-assignment requirement and any appearance of pressure) **[confirm with the instructor]**.
- **Instructor blinding:** the instructor does not learn who consented until final grades are submitted. Consent records are held only by the student investigator.

## 5. Intervention

The labs are part of the course regardless of research participation. Every student receives the same materials, support and grading. The research adds only optional surveys and a short skills check, and with consent, the reuse of coursework records that already exist.

| Lab | Topic | Level |
|---|---|---|
| 0 | Environment orientation (Docker, shell, hashing) | All |
| 1 | Network traffic analysis | Intro UG |
| 2 | Linux file-system forensics | Intermediate UG |
| 3 | Web application security assessment (authorised, loopback-only) | Upper UG |
| 4 | Incident response, multi-source forensics | Early graduate |

The course instructor decides which labs are assigned **[confirm]**.

## 6. Measures

| Measure | RQ | When | Source | Notes |
|---|---|---|---|---|
| Task self-efficacy (12 items, 1–7) | RQ2a | Pre, post | Survey | Items written for the lab objectives (see instruments); internal consistency (Cronbach's α) reported |
| Skills check (10 items, ~15 min) | RQ2b | Pre, post | Survey | Parallel forms A/B, counterbalanced; not graded by the course |
| Lab scores (auto-scored findings, 0–40 per lab; rubric totals) | RQ2b, RQ4 | After grades are final | Instructor gradebook export | **Consent required.** De-identified before transfer (section 7) |
| Setup outcome and time (Lab 0) | RQ1 | Week 1–2 | Post-Lab-0 survey items | Self-reported minutes; OS; success yes/no; what blocked |
| `verify` reports (`labN-check.json`) | RQ1 | Each lab | Submitted with coursework | Contain only architecture, kernel, CPU and memory, versions and check results: **no names or accounts**. Used only with consent |
| Help requests by category | RQ1 | Ongoing | Instructor/TA tally sheet | Counts by category; no student identifiers |
| System Usability Scale (10 items) | RQ3 | Post | Survey | Standard SUS scoring (0–100) |
| Value, realism, story continuity (Likert) and three open-ended questions | RQ3 | Post | Survey | |
| Instructor time log and 30-minute interview | RQ4 | Term, end | Instructor | Separate consent; audio recorded only if agreed, transcribed and deleted |
| Second grading of a sample of consented reports | RQ4 | After term | Second grader | Agreement between graders (ICC) and with the auto-score |

## 7. Data management and privacy

- **Identifiers.** Surveys ask for the student's **CyberLab pseudonym** (already issued for the labs, e.g. `K7QX-2M4P`), not a name or EMPLID, so pre/post responses and lab records can be linked without names. The pseudonym-to-student map stays with the instructor, as it already does for grading (OD-05). The researcher never receives it.
- **Linking consent to records.** The consent form collects the student's name and pseudonym. After final grades, the investigator gives the instructor the list of **consenting pseudonyms only**. The instructor exports those students' scores keyed by pseudonym, with names removed. Non-consenting students' records are never exported.
- **FERPA.** Lab scores and reports are education records. They are released only with the student's written consent on the consent form, and only after grades are final **[confirm the wording with the HRPP and, if needed, the Registrar]**.
- **Storage.** Survey data in a CUNY-approved survey platform **[confirm which]**. Analysis files on CUNY-approved encrypted storage. Nothing in the public or private GitHub repositories. Audio deleted after transcription.
- **Retention.** De-identified data kept for at least three years after the study ends, or longer if CUNY policy requires **[confirm]**. The consent forms are kept separately from the data.
- **Reporting.** Aggregate results only. No cell with fewer than five students is reported. Quotes are anonymised and checked for identifying details.
- **Telemetry.** The labs collect no telemetry. Nothing is sent from student computers (RES-03).

## 8. Analysis plan

| RQ | Analysis |
|---|---|
| RQ1 | Proportion completing Lab 0 setup within the session (95% CI); setup time median and IQR by OS; `verify` pass rates per lab; help-request categories (frequency table) |
| RQ2 | Paired t-test (or Wilcoxon signed-rank if non-normal) on self-efficacy and skills scores, pre vs. post; Cohen's d (paired) with 95% CI. With a comparison section: ANCOVA on post scores, controlling for pre scores. Missing data: complete-case analysis, with a comparison of completers vs. non-completers on pre-test scores |
| RQ3 | SUS mean and 95% CI against the commonly used benchmark of 68; Likert distributions; thematic analysis of open-ended responses (two coders on a 20% sample; Cohen's κ reported) |
| RQ4 | Instructor time per lab per student (setup, support, grading); interview themes; ICC(2,1) between human graders on rubric totals; agreement between auto-scored findings and a human check of the same items |

Analysis is done in Python or R with scripts versioned in the private instructor repository **[confirm location]**. No inferential claim is made beyond the participating sections.

## 9. Threats to validity

| Threat | Mitigation / how it is reported |
|---|---|
| No control group (history, maturation, testing effects) | Comparison section if available; parallel skills forms; report as association, not causation |
| Self-report bias in self-efficacy | Pair with the skills check and lab scores |
| Instructor effect; single institution | Describe the setting; avoid generalising; invite replication (public materials, seeded evidence) |
| Selection bias (who consents) | Compare consenters vs. the class on anonymous aggregate lab completion if the instructor can provide it **[confirm]** |
| Developer as researcher (investigator bias) | Pre-registered analysis plan (this document); second coder and second grader; report negative findings |
| Variant difficulty differs across students | Generators fix the story and item set; acceptance tests check that every variant has the same items and is solvable at 100% |
| Small sample | Effect sizes with CIs; RQ2 labelled exploratory if n < 34 |

## 10. Risks, benefits and safeguards

- **Risk level: minimal.** The labs are coursework that every student does anyway. The research adds about 20 minutes of surveys at each of two time points and the reuse of existing records.
- **Coercion** is the main ethical risk, because participants are students. It is addressed by recruitment by the student investigator, no extra credit, and instructor blinding until grades are final.
- **Lab safety.** Labs run offline or on loopback-only networks. The Lab 3 site is intentionally vulnerable but reachable only from the student's own computer. Students sign an authorised-use agreement. All evidence is synthetic. No malware is distributed.
- **Benefits:** none directly for participants. Indirect benefits: better labs for later students and evidence for other instructors.

## 11. Likely review category

The study appears to fit the **exempt** categories for research in established educational settings involving normal educational practices (45 CFR 46.104(d)(1)) and for surveys with appropriate protections (46.104(d)(2)). **The HRPP, not the investigator, makes this determination.** Because student records (grades, reports) are reused with consent, the HRPP may ask for additional protections or a different category.

## 12. IRB submission checklist (John Jay / CUNY)

From John Jay's "ABCs of the IRB" (2022): submissions go through IRBManager with CUNY Login, require CITI training, and student investigators need an active faculty advisor who signs off. Exempt review usually takes a few days once the application is complete. The HRPP Coordinator is reachable at Jj-irb@jjay.cuny.edu.

| # | Item | Status |
|---|---|---|
| 1 | Faculty advisor agrees to supervise and sign (OD-01) | **Blocking** |
| 2 | Adopting course(s), instructor(s) and term confirmed (OD-02); instructor letter of support | Open |
| 3 | CITI training: Human Subjects Research (and Responsible Conduct of Research) for the investigator and the advisor | Open |
| 4 | IRBManager account (add CUNY email to profile); read the Researcher Manual | Open |
| 5 | Protocol narrative (this document, sections 1–11) | Draft |
| 6 | Consent form (students); consent form (instructors) | Draft in [instruments.md](instruments.md) |
| 7 | Recruitment script and LMS announcement | Draft in [instruments.md](instruments.md) |
| 8 | Instruments: pre/post survey, skills check forms A/B, SUS, instructor interview guide | Draft in [instruments.md](instruments.md) |
| 9 | Data management plan (section 7), incl. survey platform and storage | Draft; platform **[confirm]** |
| 10 | Email the HRPP Coordinator to confirm the route (exempt vs. expedited) and FERPA wording before submitting | Open |
| 11 | Submit by 2026-12-15; respond to comments; no recruitment before the determination letter | Open |

## 13. Timeline

| Date | Milestone |
|---|---|
| 2026-11-20 → 11-30 | Faculty advisor confirmed; CITI complete; course and instructor confirmed |
| 2026-12-01 → 12-12 | Advisor review of this protocol and instruments; HRPP pre-submission questions |
| 2026-12-15 | IRBManager submission |
| 2027-01 | Determination; revise if asked; finalise survey platform |
| 2027 Spring, week 1–2 | Recruitment, consent, pre-measures |
| 2027 Spring, weeks 3–12 | Labs as coursework |
| 2027 Spring, end of term | Post-measures; instructor interview after grades are final |
| 2027 Summer | Analysis and write-up |

## 14. Relationship to the platform

The platform was built for this design: pseudonymous evidence variants (no names in any lab file), reproducible generators (equal difficulty across students), auto-scored findings (consistent RQ4 baseline), and `verify` reports that record the environment without personal data (RQ1). Architecture decisions are recorded as ADRs (RES-05). Releases are tagged and citable (`CITATION.cff`; archiving with a DOI is still to do, RES-04).
