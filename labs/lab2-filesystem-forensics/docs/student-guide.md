# Lab 2 — Linux File-System Forensics and Evidence Examination

> **Status:** Draft v0.3.0-dev (2026-11-17). Every command in Parts A–G was run against the `demo` evidence: in the Lab 2 container on macOS Apple Silicon (Docker Desktop, Sleuth Kit 4.12.1, libewf 20140816) for Part A and the key steps, and on Linux x86-64 with the same Sleuth Kit version for the rest. Windows is **UNTESTED**, and no student has walked through this guide yet.

## 1. Laboratory title

**Lab 2 — Linux File-System Forensics and Evidence Examination: The Cedarwick Workstation Disk**

## 2. Course level

**Intermediate undergraduate** (digital forensics course, after Lab 1). Graduate students complete the same tasks plus the items marked **[Grad]**, including the journal recovery in Part G.

**Undergraduate expectation:** handle the evidence correctly, find each artifact, and support every finding with the command and metadata that show it.
**Graduate expectation:** everything above, plus recovery from the file-system journal, a stated confidence for each conclusion, and an explicit reconciliation of the disk evidence with your Lab 1 network findings.

## 3. Estimated completion time

**90–120 minutes** for the examination (sections 8–9), plus **45–60 minutes** for the report. Graduate students should budget 45 extra minutes.

## 4. Prerequisite knowledge

- **Lab 0 and Lab 1 completed.** Keep your Lab 1 report and `findings.json` open: this lab continues the same incident.
- Basic file-system ideas: a file has a **name** (stored in its directory) and an **inode** (its metadata: owner, size, times, and where its data lives). A name points to an inode.
- No prior Sleuth Kit experience is needed.

## 5. Learning objectives

By the end of this lab you will be able to:

| ID | Objective | Bloom level | Practised in |
|---|---|---|---|
| L2-1 | Verify forensic images (E01 and manifest hashes), make verified working copies, and record acquisition metadata in a chain of custody. | Apply | Part A |
| L2-2 | Examine ext4 and FAT32 file systems in place with The Sleuth Kit (`fsstat`, `fls`, `istat`, `icat`) without mounting them. | Apply | Parts B–E |
| L2-3 | Reconstruct user activity from shell history, desktop recent-files lists, logs and file timestamps. | Analyze | Parts C–D |
| L2-4 | Recover deleted data by carving unallocated space, and explain why a modern Linux kernel leaves no name or block map. | Analyze | Part F |
| L2-5 | Identify persistence, hidden files and timestamp manipulation, and justify each finding with metadata. | Analyze | Part E |
| L2-6 | Correlate disk findings with the Lab 1 network evidence and assess where they agree or conflict. | Evaluate | Parts E–F, section 10 |
| L2-7 | Produce a findings file, a timeline and an examination report another examiner could reproduce. | Create | Part H, section 12 |

## 6. Scenario background

Your Lab 1 report convinced **Cedarwick Neighborhood Aid** that one staff workstation was compromised and that donor records left the network. That evening the workstation was shut down. The next morning the IT contractor used a write blocker to image two items:

1. the workstation's internal disk (`workstation.E01`), and
2. a USB stick that was still plugged into it (`usb.E01`).

The executive director now asks:

1. **How did the malware get onto the computer, and from where?**
2. **How does it start, and what is it configured to do?**
3. **What did it prepare and then delete?** Can you recover it?
4. **Does the disk agree with your network findings from Lab 1?**

Read `/evidence/CASE-BRIEF.txt` first. Your instructor's evidence for you continues **your own** Lab 1 variant, so names, domains and counts should line up with your Lab 1 answers.

> **Everything in this evidence is synthetic.** All people, accounts, domains and records are fictional, and the "malware" is inert text with every command commented out. Do not look up any name or domain on the internet.

### What is realistic and what is simplified

| Realistic | Simplified for the lab |
|---|---|
| ext4 and FAT32 structures, E01 containers, acquisition metadata | Small disks (128 MiB and 64 MiB) with only the files that matter |
| Deleted files behave as on a current Linux kernel: the name and block map are wiped, the data stays until reused | The deleted data has not been overwritten yet |
| Logs in local time with a UTC offset, a timestomped file, a hidden folder, an autostart entry | One user, one session, no operating-system files |
| The ext4 journal keeps old copies of metadata blocks | The journal holds only the transactions that matter |

## 7. Environment requirements

| Item | Requirement |
|---|---|
| Computer | 8 GB RAM, 4 CPU cores, 20 GB free disk |
| Software | Docker Desktop (macOS/Windows) or Docker Engine + Compose (Linux), working as in Lab 0 |
| Docker memory | 4 GB recommended. The lab itself is limited to 768 MB. |
| Free space for working copies | About 200 MB in `labs/lab2-filesystem-forensics/work/` |
| Download | About 120 MB the first time (the Sleuth Kit image); the demo evidence is under 1 MB |

### How the lab is built

```
Your computer
└── Docker
    └── container "workstation"        ← normal user, no network, all privileges dropped, nothing mounted
        ├── /evidence  (read-only)     ← workstation.E01, usb.E01, case brief, manifest
        └── /work      (writable)      ← your raw working copies, notes, findings.json
                                          = the labs/lab2-filesystem-forensics/work folder on your computer
```

The disk images are **never mounted**. The Sleuth Kit reads the file-system structures directly from the image file, so nothing you do can change the evidence or run anything from it.

## 8. Setup instructions

**Step 1 — Update the lab files.** In your `cyberlab-platform` folder:

```bash
git pull
cd labs/lab2-filesystem-forensics
```

**Step 2 — Choose your evidence.**

- **Practice:** the `demo` evidence in `evidence/`. Do nothing.
- **Graded work:** unzip the evidence your instructor gave you outside the repository, then in **every new terminal window**:

  ```bash
  export CYBERLAB_EVIDENCE=~/Downloads/lab2-XXXX-XXXX/evidence     # your real path
  ```

**Step 3 — Download the image and check your environment:**

```bash
docker compose pull
docker compose run --rm verify
```

You should see `OVERALL: PASS`, including `[PASS] evidence-integrity   all 3 files match MANIFEST.sha256`.

**Step 4 — Fresh templates:** `docker compose run --rm reset`. Your `work/` folder now has `findings.json`, `case-notes.md` and `chain-of-custody.md`.

**Step 5 — Open the analyst shell:**

```bash
docker compose run --rm workstation
```

Times in this container are shown in **UTC**. Keep it that way: every time in your report must be UTC.

## 9. Investigation tasks

Log every useful command in the *Working log* of `case-notes.md`, with the time (`date -u +%H:%M`) and what it showed.

### Sleuth Kit in two minutes

| You want to… | Use |
|---|---|
| Summarise a file system | `fsstat IMAGE` |
| List files (recursively, with paths) | `fls -r -p IMAGE` |
| List deleted entries only | `fls -r -d IMAGE` |
| Find the inode of a path | `ifind -n /path/in/image IMAGE` |
| Show an inode's metadata and times | `istat IMAGE INODE` |
| Print a file's content by inode | `icat IMAGE INODE` |
| Copy out unallocated space | `blkls IMAGE` |

Paths inside the image start at the image's own root (`/etc/hostname`), not at your computer's.

### Part A — Evidence handling and working copies (L2-1)

1. **Verify what you received.**

   ```bash
   cd /evidence && sha256sum -c MANIFEST.sha256 && cd /work
   ewfinfo /evidence/workstation.E01
   ewfinfo /evidence/usb.E01
   ewfverify /evidence/workstation.E01
   ewfverify /evidence/usb.E01
   ```

   An **E01** file is a forensic container: a compressed copy of the original disk plus acquisition metadata and the hash of the original media. From `ewfinfo`, record for each image: case number, description, examiner, acquisition date, media size and **MD5**. `ewfverify` must report `SUCCESS`. Add these to `chain-of-custody.md`.

2. **Make working copies.** Examiners analyse a verified *copy*, never the original. Export a raw copy of each image into `/work` (not `/tmp`, which is too small):

   ```bash
   ewfexport -q -u -f raw -t /work/workstation /evidence/workstation.E01
   ewfexport -q -u -f raw -t /work/usb /evidence/usb.E01
   md5sum /work/workstation.raw /work/usb.raw
   ```

   `ewfexport` prints a short header even with `-q`; that is normal. Each MD5 must equal the MD5 that `ewfinfo` showed. Record both in your case notes: this proves your working copy is an exact copy of the acquired disk.

   For the rest of the lab:

   ```bash
   WS=/work/workstation.raw
   USB=/work/usb.raw
   ```

   (Set these again in every new shell.)

> **Why not run the tools on the E01 directly?** You can on many systems, but the Linux image this lab uses has a library bug that makes Sleuth Kit tools crash as they exit when they read E01 files. Working copies avoid it, and they are standard practice anyway.

### Part B — What is this computer? (L2-2)

1. **File system summary:**

   ```bash
   fsstat $WS | head -30
   ```

   Record the file-system type, the volume UUID, and the *Last Mounted* and *Last Written* times. What do they tell you about when the computer was last used?

2. **Identity of the machine and its user.** Find, print and record:

   ```bash
   icat $WS $(ifind -n /etc/hostname $WS)
   icat $WS $(ifind -n /etc/os-release $WS)
   icat $WS $(ifind -n /etc/timezone $WS)
   icat $WS $(ifind -n /etc/passwd $WS)
   ```

   In `/etc/passwd`, ordinary user accounts have IDs of 1000 and above. Which account is the workstation's user, and what is their home folder? Does the hostname match the workstation you identified in Lab 1?

3. **Overview of the user's files:**

   ```bash
   fls -r -p $WS | grep "home/" | less
   ```

   Note anything whose name starts with a dot (`.`): those are **hidden** in normal file listings.

### Part C — What did the user do? (L2-3)

1. **Shell history.** `bash` saves typed commands in `~/.bash_history` when the shell exits. It has no timestamps by default.

   ```bash
   icat $WS $(ifind -n /home/<user>/.bash_history $WS)
   ```

   What did the user run, and from where? Note any path under `/media/`: that is where Ubuntu mounts removable drives, as `/media/<user>/<VOLUME-LABEL>/`.

2. **Recent files.** The desktop records files the user opened:

   ```bash
   icat $WS $(ifind -n /home/<user>/.local/share/recently-used.xbel $WS)
   ```

   Which files were opened, from where, and when (`visited=` is UTC)?

3. **Logs.** Ubuntu logs use **local time with a UTC offset**, for example `2026-03-02T09:15:00.1-05:00` is **14:15:00 UTC** (add the 5 hours).

   ```bash
   icat $WS $(ifind -n /var/log/kern.log $WS)
   icat $WS $(ifind -n /var/log/syslog $WS)
   icat $WS $(ifind -n /var/log/auth.log $WS)
   ```

   When was a USB device attached? Where was it mounted, under which label? When did the user log in and when did the system shut down? Convert each time to UTC in your timeline.

   > The kernel log shows the USB device's **hardware** serial number. That is a property of the stick's controller, not of the file system on it. Part D finds a different number.

### Part D — The USB stick (L2-2, L2-3)

1. **File-system summary:**

   ```bash
   fsstat $USB
   ```

   Record the **volume label** and the **Volume ID**. The Volume ID is the FAT *volume serial number*. Systems display it as two groups of four hexadecimal digits: `0x1a2b3c4d` is written `1A2B-3C4D`.

2. **Files, including deleted ones:**

   ```bash
   fls -r $USB
   fls -r -d $USB
   ```

   On FAT, deleting a file replaces the **first character** of its name with a marker (Sleuth Kit shows it as `_`) but leaves the rest of the entry, so the content is often still recoverable. Which file was deleted? What was its full original name? (Compare with Part C.)

3. **Recover and read it** (it is plain text and inert):

   ```bash
   icat $USB <inode>
   istat $USB <inode>
   ```

   What did it claim to do? Which paths on the workstation does it mention? Do not run any of it.

### Part E — Persistence, the hidden implant, and its configuration (L2-5, L2-6)

1. **Autostart.** Desktop sessions start programs listed in `~/.config/autostart/*.desktop`:

   ```bash
   fls -r -p $WS | grep "config/autostart"
   icat $WS <inode>
   ```

   What does the `Exec=` line start?

2. **The hidden folder.** List it and examine every file's times:

   ```bash
   fls -r -p $WS | grep "<hidden folder name>"
   istat $WS <inode>
   ```

   `istat` shows four times. On ext4, **File Created** (crtime) is set once, when the inode is created, and is hard to fake from user space. **File Modified** (mtime) can be set to anything with `touch -d`. A file whose *modified* time is **earlier than its creation time** has had its timestamp manipulated (**timestomped**). Which file? What date did the attacker want it to show, and when was it really created?

3. **Configuration.** Print the configuration file in the hidden folder. Record the C2 domains, the interval, the bot ID and the User-Agent. Compare **each** with your Lab 1 findings. What does the User-Agent setting explain about Lab 1?

4. **When was it installed?** Use the creation times of the hidden folder and its files. Put them in your timeline next to the USB events from Part C.

### Part F — Deleted data (L2-4)

1. **Deleted entries on the workstation:**

   ```bash
   fls -r -d $WS
   ```

   You will see entries under `$OrphanFiles` with **no names**. A current Linux kernel, when it deletes a file, wipes the directory entry (so the **name is gone**) and clears the inode's size and block map (so `icat` returns **nothing**). Only the inode number, some metadata and the deletion time survive. Check:

   ```bash
   istat $WS <orphan inode>
   icat $WS <orphan inode> | wc -c
   ```

   Record each orphan's **Deleted** time. Which deletion fits the incident timeline from Lab 1?

2. **Carve the data.** The deleted file's **content** is still on the disk, in blocks now marked unallocated. Copy all unallocated space out and search it:

   ```bash
   blkls $WS > /work/unalloc.bin
   strings /work/unalloc.bin | less
   strings /work/unalloc.bin | grep -n "record_id"
   ```

   Find the block of text that the deleted file held. What is it, how many **records** (rows, not counting a header line) does it contain, and does that match your Lab 1 `exfil_record_count`? Save what you recovered to `/work/recovered.csv` and record its SHA-256.

   > **Handling rule:** treat the records as personal data even though they are fictional. Quote at most three rows in your report.

3. **Where did it come from?** The user's documents contain a legitimate file with the same columns. Compare it with what you carved. Was the whole file taken, or part of it?

### Part G — [Grad] The journal remembers

ext4 writes metadata changes to a **journal** before applying them. Old journal entries are not erased when they are no longer needed, so the journal can still hold **earlier copies** of directory and inode blocks, from before a file was deleted.

1. **List the journal:**

   ```bash
   jls $WS | grep -v Unknown
   ```

   Each `FS Block N` line is a copy of file-system block N saved in the journal. Several copies of the same block mean several versions.

2. **Find the directory the deleted file lived in** (Part E's configuration names it) and its block number:

   ```bash
   istat $WS $(ifind -n /home/<user>/.cache/<folder> $WS)
   ```

   The number under *Direct Blocks* is the directory's block.

3. **Dump the journal copies of that block and of the inode table** and compare them:

   ```bash
   jcat $WS <journal block> | xxd | head -20
   jcat $WS <journal block> | strings
   ```

   A directory entry is: inode number (4 bytes, little-endian), entry length (2), name length (1), type (1), then the name. Which copy still names the deleted inode, and what was the file called? Explain why the newer copy does not.

4. **Bonus:** the older journal copy of the inode-table block still holds the deleted inode's **extent** (its block list). Use it to find the exact blocks of the deleted file and extract them with `blkcat`. Does the result match what you carved?

### Part H — Fill in `findings.json` (L2-7)

| Item | What to enter | Format example |
|---|---|---|
| `variant` | your pseudonym, or `demo` | `"K7QX-2M4P"` |
| `hostname` | the workstation's hostname | `"ws-99"` |
| `user_account` | the user's login name | `"jdoe"` |
| `usb_volume_label` | the USB file system's label | `"MYSTICK"` |
| `usb_volume_serial` | the FAT volume serial, `XXXX-XXXX` | `"1A2B-3C4D"` |
| `installer_deleted_name` | the deleted file's **full original** name on the stick | `"SETUP.SH"` |
| `install_utc` | when the implant was installed (creation time), to the minute | `"2026-10-10T18:00:00Z"` |
| `persistence_path` | full path of the autostart file | `"/home/jdoe/.config/autostart/x.desktop"` |
| `implant_path` | full path of the hidden **folder** | `"/home/jdoe/.local/share/.x"` |
| `timestomped_path` | full path of the timestomped file | `"/home/jdoe/.local/share/.x/y.py"` |
| `c2_domains` | every domain in the configuration | `["a.test", "b.example"]` |
| `bot_id` | the bot ID | `"0a1b2c3d"` |
| `staged_inode` | inode number of the deleted staged file | `99` |
| `staged_deleted_utc` | its deletion time | `"2026-10-10T18:00:00Z"` |
| `recovered_record_count` | rows you carved, **excluding** the header | `10` |
| `journal_recovered_name` | **[Grad]** the deleted file's name from the journal; leave `null` if you skip Part G | `"x.csv"` |

*The format examples are made up; they are not hints.* Paths are as they appear **inside the image**. Validate before submitting:

```bash
cyberlab-findings validate /work/findings.json
```

## 10. Guided questions

Answer in your report, citing the command and inode or block numbers for each.

1. Which hashes did you verify, and how do you know your working copies are exact?
2. What are the workstation's hostname, operating system, time zone and user account? How does the hostname connect to Lab 1?
3. When was the USB stick attached and mounted (UTC), under which label, and what is its volume serial? Why is the kernel's "SerialNumber" a different number?
4. What did the user run from the stick? How did you establish the file's full name when the stick only shows `_…`?
5. How does the implant start at each login? Give the file and the line.
6. Which file was timestomped? Give its claimed and real dates and explain how you can tell.
7. What does the configuration contain, and which values match Lab 1 exactly?
8. Explain the Lab 1 User-Agent puzzle using the disk evidence.
9. Which deleted file belongs to the incident, when was it deleted, and why can't `icat` show its content or `fls` its name?
10. What did you carve, how many records, and does that match Lab 1? Was it the whole donor list?
11. Build a single UTC timeline from login to shutdown that merges disk and network (Lab 1) events. Where do the two sources agree to the minute? Is there any conflict?
12. **[Grad]** What did the journal reveal, and why does it survive deletion? How confident are you in each of your four answers to the director, and what would raise your confidence?

## 11. Independent challenge (optional)

1. **The decoy.** One other deleted file on the workstation is unrelated. Carve it, identify it, and explain how you ruled it out.
2. **Timeline in one command.** Use `fls -r -m / $WS > /work/body.txt` and `mactime -b /work/body.txt -d > /work/timeline.csv` to build a full file-system timeline. Filter it to the incident window and compare it with your hand-built timeline.
3. **Hidden from whom?** List every hidden file and folder in the user's home. Which ones are normal for Ubuntu, and which are not? Justify each.
4. **[Grad]** Write a short procedure (5–8 steps) another examiner could follow to recover deleted file *names* on ext4 from the journal, including its limitations.

## 12. Required deliverables

| File | What it is | Graded by |
|---|---|---|
| `work/findings.json` | Structured answers (Part H) | Auto-checker (40 points) |
| `Lab2-Report-<pseudonym>.pdf` | Examination report (outline below), including section 10 | Instructor rubric (60 points) |
| `work/case-notes.md` | Working log, timeline, ruled-out items | Supports the report |
| `work/chain-of-custody.md` | Received, E01 verified, working copies made (with MD5), verified at end | Supports the report |
| `work/lab2-check.json` | Created by `verify`; run it again at the end | Required |

**Report outline** (undergraduate 5–8 pages; graduate 8–12 pages):

1. **Executive summary** for the director: how it got in, what it does, what was taken and deleted, what to do now.
2. **Evidence and handling:** items received, E01 metadata, hashes, working copies, tools and versions (`fls -V`, `ewfinfo -V`).
3. **Method.**
4. **Findings:** arrival (USB), persistence and implant, configuration and Lab 1 correlation, deleted and recovered data. Each with commands, inode/block numbers and times.
5. **Combined UTC timeline** (disk + Lab 1 network).
6. **Benign or unrelated items ruled out.**
7. **Conclusions and recommendations.** **[Grad]** with confidence levels and the journal findings.
8. **Appendix:** commands from your working log.

## 13. Submission instructions

1. `cyberlab-findings validate /work/findings.json`.
2. Leave the container and run `docker compose run --rm verify` again, so `lab2-check.json` shows the evidence was unchanged at the end. Add that to your chain of custody.
3. Upload the report PDF, `findings.json`, `case-notes.md`, `chain-of-custody.md` and `lab2-check.json` to the LMS.
4. **Do not** upload the evidence, the `.raw` working copies, `unalloc.bin` or `recovered.csv`.

Your evidence continues your own Lab 1 variant; answers copied from someone else will not match it. Follow your course syllabus on AI tools.

## 14. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Segmentation fault` (exit 139) after a Sleuth Kit command printed its output | The tool read an `.E01` directly (known library bug in this image) | Run Sleuth Kit on the `.raw` working copies in `/work` (Part A step 2). |
| `ewfexport` stops or the `.raw` file is too small | Exported to `/tmp` (64 MB limit) or disk full | Export to `/work/…`; free disk space; check `df -h /work`. |
| Working copy MD5 differs from `ewfinfo` | Incomplete export | Delete the `.raw` file and export again. Never analyse a copy that does not match. |
| `ifind: …: File not found` | Path typo or a path from your computer instead of inside the image | Paths start at the image root; check with `fls -r -p $WS | grep <name>`. |
| `fls`/`icat` say `Cannot determine file system type` | You used the `.E01` name with the `.raw` variable unset, or the wrong file | `echo $WS`; set `WS=/work/workstation.raw` again. |
| Times differ by 4 hours from your notes | You mixed local log times with UTC | Logs: local with offset (`-04:00` → add 4 h). Sleuth Kit in this container: UTC. |
| `[FAIL] evidence-integrity` | Wrong `CYBERLAB_EVIDENCE` path or a damaged download | Check the path; unzip again; record it in your chain of custody. |
| `[FAIL] free-disk` | Less than 1 GB free | Free space; the working copies need about 200 MB. |
| `Old package separator "'" deprecated at /usr/bin/mactime …` | Harmless Perl warnings from this version of `mactime` | Ignore them; the timeline is still correct. Add `2>/dev/null` to hide them. |
| `no configuration file provided: not found` | `docker compose` was run outside the lab folder | `cd labs/lab2-filesystem-forensics` first. |

## 15. Cleanup instructions

```bash
exit
docker compose down --remove-orphans
rm work/*.raw work/unalloc.bin       # on your computer, after you submit
docker ps -a                         # no cyberlab-lab2 containers
unset CYBERLAB_EVIDENCE
```

Keep your graded evidence until grades are final. `docker compose run --rm reset` starts over (previous work is moved to `work/.backup/<timestamp>/`).

## 16. Reflection questions

1. Which single artifact best connects the USB stick to the implant? Would it convince a sceptical reader on its own?
2. The file name was wiped by the kernel but survived elsewhere. List every place it survived. What does that teach you about "deleting" on modern systems?
3. Which of your Lab 1 conclusions did the disk confirm, change or add detail to?
4. If the attacker had also cleared `.bash_history`, what could you still have shown, and how?
5. What would you do differently on a real 500 GB disk?
