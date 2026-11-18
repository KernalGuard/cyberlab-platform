# CyberLab — Research Instruments (draft)

> **Status:** Draft 0.1 (2026-11-18), for faculty review and IRB submission with [methodology.md](methodology.md). **Do not use with students before the HRPP determination.** Bracketed items **[…]** are to be filled in or confirmed.

## 1. Recruitment script (read by the student investigator; instructor not present)

> Hi, my name is Sharif Vadon. I'm a graduate student at John Jay, and I built the CyberLab labs you'll use in this course. I'm studying whether labs like these work well for students, and I'm asking if you'd like to take part.
>
> Taking part means two short online surveys, one now and one at the end of the term, about 20 minutes each, plus a short skills check that is **not graded**. If you agree, I'd also like to use your lab scores and reports from this course, but only after final grades are submitted and without your name.
>
> This is completely voluntary. Your instructor won't know who took part until after grades are final, and taking part or not has **no effect on your grade**. There is no extra credit. You must be 18 or older. You can stop at any time.
>
> The consent form and first survey are at **[link]**. Questions: **[investigator CUNY e-mail]**. Thank you.

The LMS announcement uses the same text and is posted by the investigator **[or by a non-teaching staff member; confirm]**.

## 2. Student consent form (key elements)

1. **Title, investigator, faculty advisor**, and contact details; the John Jay HRPP contact for questions about rights.
2. **Purpose:** to evaluate containerized lab assignments.
3. **Procedures:** pre- and post-surveys (~20 min each), an ungraded skills check, and optional permission to use course records.
4. **Records (separate checkbox):** "I agree that my CyberLab lab scores and lab reports from **[course, term]** may be used for this research after final grades are submitted, with my name removed." *(FERPA written consent; wording to be confirmed with the HRPP.)*
5. **Voluntary; no effect on grades; no extra credit;** withdraw at any time without penalty. If you withdraw, data already collected **[will / will not]** be removed **[confirm]**.
6. **Confidentiality:** pseudonym only; the instructor is not told who participated until grades are final; aggregate reporting; minimum group size of five.
7. **Risks:** minimal. **Benefits:** none directly.
8. **Age:** 18 or older.
9. **Signature/agreement**, name, CyberLab pseudonym, date.

## 3. Instructor consent form (key elements)

Purpose; time log (≈ 5 minutes per lab) and a 30-minute end-of-term interview; optional audio recording (separate checkbox; deleted after transcription); voluntary; no effect on employment or evaluation; confidentiality (role descriptions only, no names); contact details.

## 4. Pre/post survey

**Header:** CyberLab pseudonym (format `XXXX-XXXX`); course and section; time point (pre/post).

### 4.1 Background (pre only)

1. Program and level (undergraduate year / graduate).
2. Operating system of the computer you will use for labs: macOS (Apple silicon) / macOS (Intel) / Windows 10 / Windows 11 / Linux / Chromebook / Other.
3. Prior experience (none / a little / some / a lot): command line; Docker or virtual machines; Wireshark or TShark; disk forensics tools; web application testing.
4. Have you taken a hands-on security or forensics lab course before? Yes / No.

### 4.2 Task self-efficacy (pre and post; 1 = not at all confident … 7 = completely confident)

"How confident are you that you could…"

1. install and run a containerized lab environment on your own computer.
2. verify that evidence files have not been changed, using hashes.
3. find a suspicious host in a packet capture.
4. extract and decode data sent over HTTP in a capture.
5. examine a disk image without mounting or changing it.
6. recover a deleted file from a Linux file system.
7. reconstruct what a user did from logs, shell history and file timestamps.
8. find and safely validate a weakness in a web application you are authorised to test.
9. fix a SQL injection flaw and prove the fix works.
10. trace one user session across web, application and database logs.
11. build a timeline that combines several evidence sources.
12. write an incident report that states your confidence and alternative explanations.

(Items 1–2 map to Lab 0, 3–4 to Lab 1, 5–7 to Lab 2, 8–9 to Lab 3, 10–12 to Lab 4. If the course assigns only some labs, the analysis uses the matching items.)

### 4.3 Skills check (ungraded; forms A and B, counterbalanced)

Ten multiple-choice items, each about one minute, written so that they can be answered from a short text excerpt shown on screen (no tools needed). Example items for form A:

1. Given two SHA-256 values for "the same" file, which statement is correct? *(integrity)*
2. Given five DNS response lines, which domain resolved after several NXDOMAIN answers? *(Lab 1)*
3. A base64 string is shown: what is it most likely to contain, and how would you check? *(Lab 1)*
4. An `istat` excerpt shows Created / Modified / Deleted times. Which event happened last? *(Lab 2)*
5. Why might a deleted file on ext4 have no name in a directory listing? *(Lab 2)*
6. A login form accepts a one-character password. Which risk does this create? *(Lab 3)*
7. Which code line is safe against SQL injection? (four options) *(Lab 3)*
8. Two gateway log lines carry the same session cookie from different addresses. What does this suggest, and what else would you check? *(Lab 4)*
9. Which of three bulk-looking activities is most likely legitimate, given the evidence shown? *(Lab 4)*
10. A conclusion is supported by one source. How would you word your confidence? *(Lab 4)*

Form B uses parallel items (same skill, different values). Both forms are piloted with two or three peers for timing and clarity before submission. **Peers' answers are not research data** (OD-10).

### 4.4 Post only

**System Usability Scale** (Brooke, 1996), 10 items, 1 = strongly disagree … 5 = strongly agree, with "the CyberLab labs" as the system:

1. I think that I would like to use the CyberLab labs frequently.
2. I found the CyberLab labs unnecessarily complex.
3. I thought the CyberLab labs were easy to use.
4. I think that I would need the support of a technical person to be able to use the CyberLab labs.
5. I found the various functions in the CyberLab labs were well integrated.
6. I thought there was too much inconsistency in the CyberLab labs.
7. I would imagine that most people would learn to use the CyberLab labs very quickly.
8. I found the CyberLab labs very cumbersome to use.
9. I felt very confident using the CyberLab labs.
10. I needed to learn a lot of things before I could get going with the CyberLab labs.

**Experience (1 = strongly disagree … 5 = strongly agree):**

1. The labs felt like realistic investigations.
2. Following one organisation (Cedarwick) across the labs helped me understand the material.
3. The instructions were clear enough to work without much help.
4. Running the labs on my own computer was more convenient than a campus lab would be.
5. The labs helped me understand the course content.
6. I would recommend these labs to other students.

**Setup and effort:**

1. How long did your first setup (Lab 0) take? (< 15 min / 15–30 / 30–60 / 1–2 h / > 2 h / I could not finish)
2. Which labs did you complete? (0 / 1 / 2 / 3 / 4)
3. Roughly how many hours did a typical lab take, including the report?

**Open-ended:**

1. What was the most useful thing you learned from the labs?
2. What was the most frustrating part, and what would have helped?
3. Anything else you would change?

## 5. Instructor time log (per lab)

| Lab | Preparation (min) | In-class support (min) | Out-of-class support (min) | Grading (min, total) | Issues seen (categories) |
|---|---|---|---|---|---|

Help-request categories: Docker install · Docker memory/disk · evidence path (`CYBERLAB_EVIDENCE`) · tool usage · conceptual · grading/findings format · other.

## 6. Instructor interview guide (30 minutes)

1. How did the setup go for your students, and what did you have to do?
2. Which labs worked best and worst in your course, and why?
3. How did the per-student evidence affect academic integrity and grading?
4. How useful was the auto-scored `findings.json`? Where did you disagree with it?
5. How much time did the labs take you compared with your previous labs?
6. What would stop you, or another instructor, from using them next term?
7. What should change before wider release?
