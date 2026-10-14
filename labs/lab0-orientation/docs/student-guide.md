# Lab 0 — Environment Orientation

> **Status:** Draft v0.1.0. Every command in this guide was run in a Linux test environment on 2026-10-09 using a substitute base image. It has **not yet been walked through on macOS or Windows** or by a student.

## 1. Laboratory title

**Lab 0 — Environment Orientation: Docker, the Linux Shell, and Evidence Integrity**

## 2. Course level

All levels. This is **mandatory** before Labs 1–4, for undergraduate and graduate students alike.

## 3. Estimated completion time

**30–45 minutes**, not counting the one-time Docker installation (budget 20–40 extra minutes for that, depending on your computer and internet speed).

## 4. Prerequisite knowledge

- You can open a terminal: **Terminal** on macOS, **PowerShell** or **Ubuntu (WSL)** on Windows, any terminal on Linux.
- You have installed Docker by following the guide for your operating system in [`docs/student/`](../../../docs/student/README.md).
- No prior Linux, Docker, or forensics experience is assumed.

## 5. Learning objectives

By the end of this lab you will be able to:

| ID | Objective | Bloom level |
|---|---|---|
| L0-1 | Identify the difference between a container **image** and a running **container**. | Remember |
| L0-2 | Start, inspect, stop and remove lab containers with `docker compose`. | Apply |
| L0-3 | Navigate a Linux file system and inspect files with `pwd`, `ls`, `cd`, `cat`, `less`, `file` and `grep`. | Apply |
| L0-4 | Compute SHA-256 hashes and verify evidence against a manifest. | Apply |
| L0-5 | Explain why evidence is mounted read-only and what a hash mismatch means for an investigation. | Understand |
| L0-6 | Diagnose three common Docker errors from their messages. | Apply |

## 6. Scenario background

The owner of **Harbor Point Bakery** (a fictional business) has received e-mails about password resets she never requested. She copied a few files from the shop computer to a USB stick, computed SHA-256 hashes of them first, and sent everything to you, her IT consultant.

Your job today is **not** to solve a case. It is to learn to handle evidence like a professional: confirm your lab works, look around safely, check that what you received is what was sent, and write down what you see.

*All people, businesses, files and network addresses in this lab are fictional.*

## 7. Environment requirements

| Item | Minimum |
|---|---|
| Computer | 8 GB RAM, 4 CPU cores, 20 GB free disk |
| Operating system | macOS (Apple Silicon or Intel), Windows 10/11 with WSL 2, or Linux |
| Software | Docker Desktop (macOS/Windows) or Docker Engine + Compose plugin (Linux) |
| Docker memory | 4 GB recommended (`verify` warns below 3.5 GB) |
| Network | Needed only to download the lab once. **The lab container itself has no network.** |

### How the lab is built (why it is safe)

```
Your computer
└── Docker
    └── container "workstation"   ← runs as a normal user, no network, read-only system files
        ├── /evidence   (read-only)  ← the files you received; you cannot change them
        └── /work       (writable)   ← your notes and answers; this is the labs/lab0-orientation/work folder on your computer
```

## 8. Setup instructions

**Step 1 — Get the lab files.** Either:

```bash
git clone https://github.com/KernalGuard/cyberlab-platform.git
```

or download the repository as a ZIP from GitHub and unzip it. *(Your instructor will give you the exact address.)*

**Windows users:** run all commands inside your **Ubuntu (WSL)** terminal and keep the folder inside your WSL home directory (for example `~/cyberlab-platform`), as described in the Windows install guide.

**Step 2 — Go to the Lab 0 folder.**

```bash
cd cyberlab-platform/labs/lab0-orientation
```

**Step 3 — Download the lab image** (a few hundred megabytes the first time; later labs reuse most of it):

```bash
docker compose pull
```

**Step 4 — Check your environment:**

```bash
docker compose run --rm verify
```

Expected output (your numbers will differ):

```
CyberLab verify — lab0-orientation v0.1.0 (aarch64)
[PASS] tools                10 required tools found
[PASS] evidence-integrity   all 7 files match MANIFEST.sha256
[PASS] read-only:/evidence  write attempt refused (EROFS)
[PASS] writable:/work       work folder is writable
[PASS] network-isolation    no network: loopback only
[PASS] non-root             running as UID 1000
[PASS] capabilities         all capabilities dropped
[PASS] no-new-privileges    NoNewPrivs=1
[PASS] docker-memory        3913 MB available to Docker
[PASS] free-disk            41210 MB free

OVERALL: PASS
Report saved to /work/lab0-check.json
```

`WARN` lines are allowed. Read the arrow (→) hint under each one. If you see `FAIL`, go to [Troubleshooting](#14-troubleshooting) before continuing.

**Step 5 — Put fresh answer templates in your work folder:**

```bash
docker compose run --rm reset
```

Your `work/` folder now contains `lab0-answers.md`, `case-notes.md` and `chain-of-custody.md`. Open them with any text editor on your computer.

## 9. Investigation tasks

### Part A — Docker basics (L0-1, L0-2)

On your **computer's** terminal (not inside the container):

```bash
docker version            # client and server versions
docker info               # look for: Architecture, CPUs, Total Memory
docker image ls           # images you have downloaded
docker ps -a              # containers that exist (running or stopped)
```

An **image** is a read-only template, like a program installer. A **container** is a running instance created from an image. `docker compose run --rm` creates a container and removes it (`--rm`) when you exit.

### Part B — Enter the workstation and look around (L0-3)

```bash
docker compose run --rm workstation
```

Your prompt changes to `analyst@lab0:/work$`. You are now **inside** the container.

```bash
pwd                       # where am I?
ls -la /evidence          # what was I given?
cat /evidence/CASE-BRIEF.txt
find /evidence -type f    # every file, in every subfolder
find /evidence -type f | wc -l     # count them
less /evidence/documents/meeting-notes.txt   # press q to quit less
```

Now check what each file *really* is. A file's extension is just part of its name; the `file` command looks at the bytes inside.

```bash
file /evidence/documents/*
file /evidence/images/storefront.png
xxd /evidence/images/storefront.png | head -1      # the first bytes ("magic number")
xxd /evidence/documents/report.txt | head -1
```

If something is an archive, you can list it **without extracting it into the evidence folder**:

```bash
unzip -l /evidence/documents/report.txt
unzip -p /evidence/documents/report.txt     # print the contents to the screen
```

### Part C — Searching a log (L0-3)

```bash
less /evidence/logs/auth.log
grep "Failed password" /evidence/logs/auth.log
grep -c "Failed password" /evidence/logs/auth.log                 # count the lines
grep "Failed password" /evidence/logs/auth.log | grep -oE "from [0-9.]+" | sort | uniq -c
grep "Accepted password" /evidence/logs/auth.log
```

The `|` (pipe) sends one command's output into the next command. Try building your own pipeline to count attempts **per username**. *Hint:* `grep -oE "for (invalid user )?[a-z]+"`.

### Part D — Hashing and integrity (L0-4, L0-5)

A **hash** is a fingerprint of a file's exact bytes. Change one byte and the SHA-256 hash changes completely.

```bash
cd /evidence
sha256sum CASE-BRIEF.txt
sha256sum -c MANIFEST.sha256                       # the lab's manifest: every file as distributed
sha256sum -c transfer/sender_hashes.sha256         # the hashes the client computed BEFORE copying
```

Compare the two results carefully. Then open the file that failed and read the numbers in it:

```bash
cat documents/budget.csv
```

Record what you found in `work/case-notes.md`, with the time in UTC (`date -u` shows it).

### Part E — Read-only evidence (L0-5)

Try to change the evidence. This **should fail**:

```bash
touch /evidence/test.txt
echo "edit" >> /evidence/documents/meeting-notes.txt
```

Now write somewhere you are allowed to:

```bash
echo "Examined meeting-notes.txt at $(date -u +%FT%TZ)" >> /work/case-notes.md
exit
```

### Part F — Troubleshooting drill (L0-6)

You will cause three common errors on purpose. For each, copy the error message into your answer sheet and explain the fix.

**Problem 1 — wrong folder.** From your *home* folder:

```bash
cd ~
docker compose run --rm verify
```

**Problem 2 — name conflict.** Go back to the lab folder. Find the lab image name with `docker image ls | grep cyberlab`, then start a named scratch container **twice**:

```bash
docker run -d --network none --name lab0-scratch <image-name> sleep 300
docker run -d --network none --name lab0-scratch <image-name> sleep 300
```

**Problem 3 — stopped container.**

```bash
docker stop lab0-scratch
docker exec lab0-scratch ls /
```

Clean up the scratch container afterwards:

```bash
docker rm lab0-scratch
```

## 10. Guided questions

Answer these in `work/lab0-answers.md` (the template has numbered spaces for each):

1. What is the difference between an image and a container?
2. What architecture did `verify` report? What does that tell you about your computer?
3. How many files are in `/evidence`, including subfolders? Show your command.
4. What is `documents/report.txt` really? Why can't you trust file extensions?
5. How many failed logins are in `auth.log`, from which address, and against which usernames?
6. Is the attacking address on the shop's local network? How can you tell?
7. Which file fails the client's hash list but passes the lab manifest? What is the most likely explanation?
8. What error did you get when writing to `/evidence`, and why does that protection matter?
9. What were the three troubleshooting errors, and how did you fix each one?

## 11. Independent challenge (optional)

1. **Prove the edit.** Without the original file, use only the contents of `budget.csv` to argue which value was changed after the client hashed it. *(Hint: the columns should agree with each other.)*
2. **One-line inventory.** Write a single command that prints, for every file in `/evidence`, its size, its SHA-256 hash and what `file` says it is. Paste the command and its output into your answers.
3. **Graduate students:** in 150 words or fewer, explain why the **lab manifest** passing does not prove the evidence is *authentic*, only that it is *unchanged since the lab was packaged*. What would a real examiner need beyond hashes?

## 12. Required deliverables

| File (in your `work/` folder) | What it is |
|---|---|
| `lab0-check.json` | Created by `verify`. Shows that your environment works. Run `verify` again just before submitting. |
| `lab0-answers.md` | Your answers to questions 1–15 of the template, with the commands you used |
| `case-notes.md` | At least 5 time-stamped entries (UTC) |

## 13. Submission instructions

1. Run `docker compose run --rm verify` one last time, so `lab0-check.json` is current.
2. On your computer, open the `labs/lab0-orientation/work/` folder.
3. Upload `lab0-check.json`, `lab0-answers.md` and `case-notes.md` to the Lab 0 assignment in the course LMS (or export the Markdown files to PDF if your instructor asks for PDF).

`lab0-check.json` contains your computer's architecture, memory, Docker kernel version and the check results. It contains **no** names, usernames, hostnames or IP addresses.

## 14. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop is not running | Start Docker Desktop and wait until it says it is running, then retry. |
| `no configuration file provided: not found` | You are not in the lab folder | `cd` into `labs/lab0-orientation` (the folder that contains `compose.yaml`). |
| `[FAIL] writable:/work … EACCES` (Linux) | Your user ID is not 1000 | Run `export CYBERLAB_UID=$(id -u) CYBERLAB_GID=$(id -g)` before `docker compose` (see the Linux install guide). |
| `[FAIL] evidence-integrity` | The evidence folder was changed or is incomplete | Don't analyze it. Download the lab again; write the problem in your case notes. |
| `[WARN] docker-memory` | Docker has less than 3.5 GB | macOS: Docker Desktop → Settings → Resources → Memory = 4 GB. Windows: see the `.wslconfig` step in the Windows guide. |
| `pull access denied` / `manifest unknown` | Image not published yet, or a typo | Tell your instructor. Maintainers can build locally with `docker compose build`. |
| `Conflict. The container name "/lab0-scratch" is already in use` | Expected in Part F | `docker rm -f lab0-scratch` |
| Windows: `bash\r: No such file or directory` or odd `^M` characters | Files were checked out with Windows line endings | Clone inside WSL, not into a Windows folder (see the Windows guide). |
| Very slow on Apple Silicon | An amd64 image is being emulated | Run `docker compose pull` again; report it if `verify` shows `x86_64` on an Apple Silicon Mac. |

## 15. Cleanup instructions

```bash
docker compose down --remove-orphans     # remove any lab containers and networks
docker rm -f lab0-scratch 2>/dev/null    # in case the scratch container is still there
docker ps -a                             # should list no cyberlab or lab0 containers
```

Keep the image (`docker image ls`). Later labs reuse it. To reclaim **all** space at the end of the semester:

```bash
docker image ls | grep cyberlab          # then: docker image rm <image-name>
```

To start Lab 0 over, run `docker compose run --rm reset`. Your previous work is moved to `work/.backup/<timestamp>/`, not deleted.

## 16. Reflection questions

1. Which step took the longest, and why?
2. Before this lab, would you have trusted a file called `report.txt` to be a text file? What changed?
3. The client's hash list and the lab manifest disagreed about one file. In a real case, who would you contact, and what would you write in your notes **before** doing any more analysis?
4. What is one thing you still don't understand about containers? Bring it to the next class.
