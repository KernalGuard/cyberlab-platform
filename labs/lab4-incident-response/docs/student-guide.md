# Lab 4 — Incident Response and Multi-Source Digital Forensics

> **Status:** Draft v0.5.0-dev (2026-11-18). Every command in Parts A–H was run against the `demo` evidence on Linux x86-64 with the same tool versions as the lab image's key tools (The Sleuth Kit 4.12, TShark, jq, sqlite3). The image itself was built and checked on macOS Apple Silicon (Docker Desktop): `verify` passes, and the instructor's reference solution solves the demo evidence inside it. Windows is **UNTESTED**, and no student has walked through this guide yet.

## 1. Laboratory title

**Lab 4 — Incident Response and Multi-Source Digital Forensics: The Cedarwick Donation-Site Breach**

## 2. Course level

**Early graduate** (or upper undergraduate with instructor support), after Labs 1–3. Graduate students complete everything, including the items marked **[Grad]**.

**Undergraduate expectation:** find each artifact, support every finding with the record that shows it, and separate the attacker from the look-alikes.
**Graduate expectation:** everything above, plus a master timeline across all sources, a stated confidence and alternative explanation for each key conclusion, and a detection rule you have tested against the evidence.

## 3. Estimated completion time

**150–180 minutes** for the investigation (sections 8–9), plus **90–120 minutes** for the report. This is the longest lab: plan two sittings. Your notes in `work/` persist between sessions.

## 4. Prerequisite knowledge

- **Labs 0–3 completed.** Keep your Lab 1, 2 and 3 reports open: this lab closes the same story, and several answers should *look familiar*.
- From Lab 1: reading a capture with `tshark`, DNS and HTTP fields, decoding base64.
- From Lab 2: E01 working copies, `fls`, `istat`, `icat`, deleted files and unallocated space.
- From Lab 3: how the donation site works, its `cw_session` cookie (unsigned base64 JSON), its JSON logs, and what IDOR means.
- New here: `jq` for JSON logs and `sqlite3` for browser databases. Both are introduced as you go.

## 5. Learning objectives

By the end of this lab you will be able to:

| ID | Objective | Bloom level | Practised in |
|---|---|---|---|
| L4-1 | Triage a multi-source evidence bundle, verify its integrity and plan the investigation from the case brief. | Apply | Part A |
| L4-2 | Reconstruct the initial compromise from a network capture, a disk image and browser databases. | Analyze | Parts B–C |
| L4-3 | Trace a stolen session through gateway, application and database logs, and separate attacker activity from authorised and legitimate look-alikes. | Analyze | Part D |
| L4-4 | Determine the scope of the data exposure and state the confidence and an alternative explanation for each key conclusion. | Evaluate | Parts E–F, report |
| L4-5 | Build a master timeline that correlates events across sources and explain any gaps or conflicts. | Evaluate | Part G |
| L4-6 | Write a containment and recovery plan and a donor notification that match the evidence. | Create | Report sections 5–6 |
| L4-7 | **[Grad]** Write a log-based detection rule for the attack and test it against the evidence, reporting hits and false positives. | Create | Part H |

## 6. Scenario background

After Labs 1–3, **Cedarwick Neighborhood Aid** (fictional) relaunched its donation website. The board applied **one** of your Lab 3 fixes (the donor search now uses a parameterised query) and scheduled the rest "for the next sprint".

Ten days later a donor forwarded a phishing e-mail that quoted their real receipt number and gift amount. Cedarwick never sent it. Somebody had donor data.

You lead the response. The board asks four questions:

1. **How did the attacker get in?**
2. **What exactly was exposed, and about how many people?**
3. **Is the attacker still in?** (Was the web server itself compromised?)
4. **What must Cedarwick do now?**

Read `/evidence/CASE-BRIEF.txt` first. It contains the ticket, staff interview notes, the scheduled activity you must account for, and the addresses of the office and the site. Your instructor's evidence continues **your own** Lab 1 and Lab 3 variants.

> **Everything in this evidence is synthetic.** All people, accounts, domains, addresses and records are fictional; the "malware" is inert text. Do not look any of them up on the internet.

### Three kinds of activity you must tell apart

The site logs contain far more than the attack. At least three things will *look* suspicious:

| Activity | Why it looks bad |
|---|---|
| The **authorised re-test** listed in the case brief | Failed staff logins, receipt numbers that are not the tester's own |
| A **staff member exporting donors** from home in the evening | One search that returns every donor, from an unusual address |
| **Internet SSH noise** against the web server | Hundreds of failed logins |

Your report must explain, with evidence, why each one is or is not the attacker.

### What is realistic and what is simplified

| Realistic | Simplified for the lab |
|---|---|
| Log formats from a real nginx/Flask/PostgreSQL stack; a pcapng capture; an E01 image with Firefox databases | Only a few days of logs; one 90-minute capture window; a small laptop image |
| Look-alike activity and noise you must rule out | Every source's clock is correct (UTC) — in real cases clocks drift |
| A stolen session replayed from another address | The attacker made no effort to hide in volume |
| The donation site's weaknesses are the ones you reported in Lab 3 | No CDN, WAF or load balancer between the visitor and the gateway |

## 7. Environment requirements

| Item | Requirement |
|---|---|
| Computer | 8 GB RAM, 4 CPU cores, 10 GB free disk |
| Software | Docker Desktop (macOS/Windows) or Docker Engine + Compose (Linux), working as in Lab 0 |
| Docker memory | 4 GB recommended. The lab itself is limited to 1 GB. |
| Free space in `work/` | About 150 MB (one raw working copy, extracted databases, your notes) |
| Download | About 200 MB the first time (the workstation image); the demo evidence is about 15 MB |

### How the lab is built

```
Your computer
└── Docker
    └── container "workstation"        ← normal user, no network, all privileges dropped, nothing mounted
        ├── /evidence  (read-only)     ← web/, network/, hosts/, server/, db/, CASE-BRIEF.txt, MANIFEST.sha256
        └── /work      (writable)      ← working copies, notes, findings.json, incident-report.md
                                          = the labs/lab4-incident-response/work folder on your computer
```

The donation site is **not running** in this lab. You investigate what it left behind.

## 8. Setup instructions

**Step 1 — Update the lab files.** In your `cyberlab-platform` folder:

```bash
git pull
cd labs/lab4-incident-response
```

**Step 2 — Choose your evidence.**

- **Practice:** the `demo` evidence in `evidence/`. Do nothing.
- **Graded work:** unzip the evidence your instructor gave you outside the repository, then in **every new terminal window**:

  ```bash
  export CYBERLAB_EVIDENCE=~/Downloads/lab4-XXXX-XXXX/evidence     # your real path
  ```

**Step 3 — Download the image and check your environment:**

```bash
docker compose pull
docker compose run --rm verify
```

You should see `OVERALL: PASS`, including `[PASS] evidence-integrity   all 8 files match MANIFEST.sha256`.

**Step 4 — Fresh templates:** `docker compose run --rm reset`. Your `work/` folder now has `findings.json`, `case-notes.md`, `chain-of-custody.md` and `incident-report.md`. Open the last two on your computer now: you will fill them in as you go.

**Step 5 — Open the analyst shell:**

```bash
docker compose run --rm workstation
```

Then set these short names (again in every new shell):

```bash
E=/evidence
G=$E/web/gateway.jsonl; A=$E/web/app.jsonl; PG=$E/web/postgres.log
P=$E/network/office-edge.pcapng
unb64() { python3 -c 'import base64,sys; s=sys.argv[1]; print(base64.urlsafe_b64decode(s+"="*(-len(s)%4)).decode())' "$1"; }
```

`unb64` decodes the URL-safe base64 the site uses for its cookie (you met it in Lab 3).

## 9. Investigation tasks

**Every time in your notes and report must be UTC.** Each tool shows time differently; this table converts them all:

| Source | How to get UTC |
|---|---|
| JSON logs (`ts`) | already UTC (`Z` or `+00:00`) |
| `postgres.log` | already UTC (`... UTC`) |
| `auth.log` | already UTC (`+00:00`) |
| TShark | use the field `frame.time_utc` (not `frame.time`) |
| Sleuth Kit `istat` | add `-z UTC` |
| `.bash_history` `#1765...` lines | `date -u -d @1765...` |
| Firefox databases (microseconds) | `datetime(value/1000000,'unixepoch')` in sqlite3 |

Log every useful command in the *Working log* of `case-notes.md` with what it showed.

### Part A — Triage and evidence handling (L4-1)

1. **Verify what you received.**

   ```bash
   cd /evidence && sha256sum -c MANIFEST.sha256 && cd /work
   ewfinfo $E/hosts/coordinator-laptop.E01
   ewfverify $E/hosts/coordinator-laptop.E01
   ```

   Record the E01's case number, description, acquisition date and MD5 in `chain-of-custody.md`.

2. **Inventory each source.** Fill the *Evidence inventory* table in your case notes: what system each file comes from and the time range it covers. For example:

   ```bash
   jq -r .ts $G | sed -n '1p;$p'          # first and last gateway record
   jq -r .ts $A | sed -n '1p;$p'
   capinfos -a -e -c $P                     # first/last packet and count
   sed -n '1p;$p' $E/server/auth.log | cut -c1-60
   grep -m1 Dumped $E/db/snapshot.sql
   ```

   **Question to answer in your notes:** which sources overlap in time, and which events could only be seen in one source?

3. **Plan.** From the case brief, write down the people, addresses and accounts you already know (the office public address, the site's address, the test account, the staff roles). You will use them to filter every log.

### Part B — The laptop (L4-2)

The Volunteer Coordinator said her laptop "acted strangely" after she opened a link.

1. **Make a verified working copy** (as in Lab 2: into `/work`, never `/tmp`):

   ```bash
   ewfexport -q -u -f raw -t /work/laptop $E/hosts/coordinator-laptop.E01
   md5sum /work/laptop.raw         # must equal the MD5 from ewfinfo
   L=/work/laptop.raw
   ```

2. **Whose laptop is it?** Find the user with UID 1000 and the hostname:

   ```bash
   icat $L $(ifind -n /etc/passwd $L)
   icat $L $(ifind -n /etc/hostname $L)
   ```

   The username is also her username on the donation site's staff area (check `db/snapshot.sql`).

3. **What did she run?** Her shell history records a timestamp before each command (`HISTTIMEFORMAT` is set in her `.bashrc`). Print it with UTC times (replace `USER`):

   ```bash
   icat $L $(ifind -n /home/USER/.bash_history $L) | while IFS= read -r line; do
     case "$line" in \#[0-9]*) printf '%s  ' "$(date -u -d @"${line#\#}" +%FT%TZ)";; *) echo "$line";; esac
   done
   ```

4. **Where did it come from?** Firefox keeps history and cookies in SQLite databases. Copy them out and query them:

   ```bash
   fls -r -p $L | grep -E 'places.sqlite|cookies.sqlite'
   icat $L INODE_OF_PLACES  > /work/places.sqlite
   icat $L INODE_OF_COOKIES > /work/cookies.sqlite
   sqlite3 -header -column /work/places.sqlite \
     "SELECT datetime(v.visit_date/1000000,'unixepoch') AS utc, p.url
        FROM moz_historyvisits v JOIN moz_places p ON p.id = v.place_id ORDER BY v.visit_date;"
   sqlite3 -header -column /work/cookies.sqlite \
     "SELECT host, name, value, datetime(creationTime/1000000,'unixepoch') AS created_utc FROM moz_cookies;"
   ```

   Which domain imitates Cedarwick? Which cookie would let someone act as her on the donation site?

5. **What did it install?** Look for new files created within seconds of the command you found in step 3:

   ```bash
   fls -r -p $L | grep -E 'autostart|\.local/share/\.|\.cache/\.'
   istat -z UTC $L INODE        # compare the "Created" times
   icat  $L INODE               # read the .desktop file and the configuration
   ```

   Record the **full path** of the file that makes it start at every login (persistence). Compare the configuration with your **Lab 2** findings: what is the same family, and what changed?

6. **What was deleted?** The downloaded script and a staging file are gone, but on ext4 their data stays until overwritten (Lab 2, Part F):

   ```bash
   fls -r -d -p $L                       # deleted entries (no names: the kernel wiped them)
   istat -z UTC $L ORPHAN_INODE          # created / deleted times
   blkls $L > /work/unalloc.bin
   strings -n 6 /work/unalloc.bin | less # look for '#!/bin/sh' and 'Cookie File'
   ```

   What did the staging file hold, and when was it deleted?

### Part C — The office capture (L4-2)

The office firewall keeps a rolling capture. You have 90 minutes around the click.

1. **Find the download.** The laptop's address is not in the brief. Find it from the request for the script:

   ```bash
   tshark -r $P -Y 'http.request' -T fields -e frame.number -e frame.time_utc -e ip.src \
     -e http.host -e http.request.method -e http.request.uri | grep -v intranet | head -20
   ```

   Follow the download's TCP stream to read the script as it arrived (`-z follow,tcp,ascii,STREAM`, as in Lab 1). Does it match what you carved from the disk?

2. **After the click.** From the laptop's address, list DNS lookups and their answers:

   ```bash
   tshark -r $P -Y 'dns.flags.response==1 && ip.dst==LAPTOP_IP' -T fields \
     -e frame.time_utc -e dns.qry.name -e dns.flags.rcode -e dns.a
   ```

   Which names fail (rcode 3) and which one finally resolves? Compare with the configuration you found on disk.

3. **The implant's traffic.** Summarise HTTP by host and User-Agent:

   ```bash
   tshark -r $P -Y http.request -T fields -e http.host -e http.user_agent | sort | uniq -c | sort -rn
   ```

   Look at the User-Agent of the implant's requests and compare it, character for character, with your **Lab 1** answer. What does that suggest, and how sure can you be? (Write both the conclusion and the alternative explanation in your report.)

4. **The upload.** Find the POST and decode its body (Lab 1, Part D):

   ```bash
   tshark -r $P -Y 'http.request.method=="POST" && !(http.host contains "intranet")' \
     -T fields -e frame.number -e frame.time_utc -e http.host -e http.request.uri
   tshark -r $P -Y 'frame.number==FRAME' -T fields -e http.file_data | xxd -r -p | base64 -d
   ```

   Find the `cw_session` value in what was uploaded, then decode it:

   ```bash
   unb64 PASTE_THE_COOKIE_VALUE
   ```

   Record the session number `n`. Is this the same value as in the laptop's `cookies.sqlite`?

### Part D — Following the stolen session (L4-3)

The gateway log records every request, including the `session` cookie it carried. `jq` filters JSON one record per line:

| You want to… | jq |
|---|---|
| Records with a given session | `jq -c --arg s "$S" 'select(.session==$s)' $G` |
| One field per record | `jq -r '.client' $G` |
| Several fields as a table | `jq -r '[.ts,.client,.uri] \| @tsv' $G` |
| Count by value | `jq -r .client $G \| sort \| uniq -c \| sort -rn` |

1. **Where was the stolen session used?** Set `S` to the cookie value you found, then:

   ```bash
   S=PASTE_THE_COOKIE_VALUE
   jq -r --arg s "$S" 'select(.session==$s) | [.ts,.client,.user_agent,.uri] | @tsv' $G
   jq -r --arg s "$S" 'select(.session==$s) | .client' $G | sort | uniq -c
   ```

   One address is the office (from the case brief). What is the other? Did that address ever **log in** (look for `POST /staff/login` from it)? What does the User-Agent tell you, and why is it not proof?

2. **Everything the other address did.** Set `X` to it and list all its requests and application events:

   ```bash
   jq -r --arg ip "$X" 'select(.client==$ip) | [.ts,.status,.method,.uri] | @tsv' $G | less
   jq -c --arg ip "$X" 'select(.client==$ip and .event!="receipt_view")' $A
   jq -r --arg ip "$X" 'select(.client==$ip and .event=="receipt_view") | .owner_match' $A | sort | uniq -c
   ```

   Note its first request (UTC), its searches, the account it created (with what password length?), and the receipts it opened. Why does the `register` event still show a **staff** user? (Think about which cookie the browser sent.)

3. **The database's view.** The site now uses parameterised queries, so PostgreSQL logs the query and its parameters separately:

   ```bash
   grep -A1 'ILIKE' $PG | grep DETAIL | less
   ```

   Match each search to its time in the app log. Do any parameters look like SQL injection attempts? What does that tell you about the Lab 3 fix?

4. **Rule out the look-alikes.** For each, find the evidence in the logs:

   ```bash
   jq -r 'select(.event=="login_ok") | [.ts,.client,.kind,.account] | @tsv' $A | less
   jq -r 'select(.event=="login_failed") | [.ts,.client,.kind,.account] | @tsv' $A
   jq -r 'select(.event=="donor_search" and .results>20) | [.ts,.client,.user,.q,.results] | @tsv' $A
   jq -r 'select(.event=="receipt_view" and .owner_match==false) | .client' $A | sort | uniq -c
   ```

   - Which address belongs to the **authorised re-test**? (The brief gives the test account, not the address.) Does its activity fall inside the approved window?
   - Which staff member searched for **every** donor from home? Did she log in normally? Does her behaviour match what she told the director?

### Part E — Scope of the exposure (L4-4)

1. **Donors exposed.** The attacker's searches returned donor names and e-mail addresses. The app log gives a count per search, but you must check two things before adding them up:

   - Could one donor appear in two searches (overlap)?
   - Which donors existed *at that moment*? Donors who registered later were not exposed.

   Check against the snapshot. This prints every donor row with its creation time; filter it with the search terms and the time of each search:

   ```bash
   grep 'INSERT INTO public.donors' $E/db/snapshot.sql | less
   ```

   (Python is available if you prefer: `python3` then read the file and apply the same rule the database used — `ILIKE '%term%'` on the name **or** the e-mail address, case-insensitive.)

2. **Receipts viewed.** Count the receipts the attacker opened that were **not** their own, and note the first and last receipt numbers. What does each receipt reveal? (Recall Lab 3.)

3. **The attacker's account.** Find the donor ID from the `register` event, then its row in the snapshot:

   ```bash
   grep 'INSERT INTO public.donors VALUES (DONOR_ID,' $E/db/snapshot.sql
   ```

4. **Connect it to the complaint.** Is the receipt quoted in the donor's complaint (case brief) among the receipts the attacker opened?

### Part F — Is the attacker still in? The web server (L4-4)

```bash
AU=$E/server/auth.log
grep -c 'Failed password' $AU
grep 'Accepted' $AU
grep -oE 'Failed password for (invalid user )?\S+ from \S+' $AU | awk '{print $NF}' | sort | uniq -c | sort -rn
grep 'COMMAND=' $AU
```

Every successful login: who, from where, with what method? Does any failed-login address ever succeed? Does the attacker's web address appear here at all? Decide whether `give-web01` was compromised, and state your confidence. What evidence would you still want to be sure (think about what this log cannot show)?

### Part G — Master timeline (L4-5)

Build the timeline in `case-notes.md` (all UTC), from her **staff login** on the site to the **snapshot**. Include at least:

- the staff login that created the session (gateway and app log), and the matching Firefox cookie creation time;
- the phishing page visit and the script download (Firefox history **and** capture);
- the command that ran it (`.bash_history`) and the creation of the persistence file (`istat`);
- the first C2 lookup and the cookie upload (capture), and the staging file's deletion (`istat`);
- the authorised re-test, the home export, and the attacker's first and last requests (logs);
- the snapshot and the laptop acquisition.

Where two sources record the same event, write both times. **Do they agree?** If you had to rely on only one source for each step, which would you choose and why?

### Part H — [Grad] Detection rule (L4-7)

Write a rule that would have flagged this attack **from the site logs alone**, before the donor complained. Ideas (choose one, or design your own):

- one **staff** session cookie used from more than one client address;
- a staff session used from an address that never logged in;
- one donor session viewing many receipts it does not own within a few minutes.

Express it as a `jq` command (a Sigma-style description is a welcome extra), run it against `$G` or `$A`, and record: the exact command, every hit, which hits are true and false positives, and one way an attacker could evade it. Save the rule in your report, section 7.

`jq -s` reads the whole file as one array, which lets you group records: `jq -s 'group_by(.session)' $G`.

### Part I — Fill in `findings.json`

Edit `work/findings.json` on your computer. Set `variant` to your pseudonym (or `demo`). Formats:

| Item | Format | Example of the format |
|---|---|---|
| `phished_staff_username` | site username | `jdoe` |
| `phishing_domain` | domain name | `example.test` |
| `persistence_path` | full path inside the image | `/home/user/.config/…/name.desktop` |
| `new_c2_domain` | the domain that resolved | `abc123.example` |
| `implant_user_agent` | exact string | `Mozilla/…` |
| `cookie_exfil_utc` | UTC, second precision | `2026-01-01T12:00:00Z` |
| `stolen_session_n` | integer | `1234` |
| `attacker_ip` | IPv4 | `192.0.2.1` |
| `attacker_first_request_utc` | UTC (first gateway record from that address) | `2026-01-01T12:00:00Z` |
| `donor_records_exposed` | integer (distinct donors) | `42` |
| `receipts_enumerated` | integer (receipts shown that were not the attacker's) | `42` |
| `attacker_donor_email` | e-mail address | `name@example.test` |
| `authorised_test_ip` | IPv4 | `192.0.2.2` |
| `legit_export_username` | site username | `jdoe` |
| `ssh_compromised` | `yes` or `no` | `no` |

Check the JSON is valid: `jq . /work/findings.json`.

## 10. Guided questions

Answer in your report (2–5 sentences each, citing evidence):

1. Which **single** source would have told you the most if it were the only one you had? Which source added the least?
2. The attacker never typed a password on the donation site. Which Lab 3 weakness made that possible, and which fix would have stopped it?
3. The SQL-injection fix worked. Show the evidence. Why did it not prevent this breach?
4. How confident are you that this is the **same actor** as in Lab 1? List the evidence for and against, and what would raise your confidence.
5. Why must the donor-exposure count consider *when* each donor registered?
6. The re-test and the home export both did things the attacker did. What, specifically, separates each from the attack?
7. The case brief says the laptop "acted strangely". What would you ask the Coordinator in a follow-up interview, and why?
8. Which events would you have missed if the office capture had not been running at that moment? How would you have reached the same conclusions without it?
9. **[Grad]** Your detection rule: what is its expected false-positive rate on a busy site, and how would you tune it?
10. **[Grad]** The donor notification: which facts are you certain of, which are estimates, and how did you word each?

## 11. Independent challenge (optional)

Choose one:

- **Full super-timeline.** Produce a single CSV of every event from all seven sources (`time_utc,source,record,event`), sorted, and highlight the attack. `mactime` from The Sleuth Kit can contribute the file-system events (`fls -r -m / $L > body.txt; mactime -b body.txt -z UTC -d`).
- **Second rule.** Write a detection rule for the *laptop* side (for example, a new `.desktop` autostart file that runs a script from a hidden folder) and describe where in a real organisation it would run.
- **Board briefing.** A one-page brief for non-technical board members: what happened, in three sentences; what it cost; what you need from them (decisions and money).

## 12. Required deliverables

Submit from your `work/` folder:

| File | Contents |
|---|---|
| `findings.json` | All 15 items |
| `incident-report.md` | Executive summary; scope; master timeline; findings with **confidence and an alternative explanation** for each; containment and recovery plan; donor notification draft; **[Grad]** detection rule with test results; lessons learned |
| `case-notes.md` | Inventory, working log and timeline |
| `chain-of-custody.md` | Evidence received and verified, and your working copies with their hashes |
| `lab4-check.json` | Created by `verify` |

The report may be exported to PDF if your instructor prefers.

## 13. Submission instructions

1. Run `docker compose run --rm verify` once more (it refreshes `lab4-check.json`).
2. Check `findings.json`: `jq . work/findings.json` on your computer, or inside the shell.
3. Zip the `work/` folder **without** `laptop.raw` and `unalloc.bin` (they are large and the instructor can recreate them): on macOS/Linux, `cd work && zip -r ../lab4-PSEUDONYM.zip . -x laptop.raw -x unalloc.bin`.
4. Upload the zip to the LMS. Do not upload evidence files.

## 14. Troubleshooting

| Problem | Fix |
|---|---|
| `ewfexport: unable to create target` or "No space left" | Export into `/work`, not `/tmp` (only 64 MB). Free space on your computer if `/work` is full. |
| Sleuth Kit tool crashes after printing output when run on `.E01` | Known library bug in the image (Lab 2). Use the raw working copy `/work/laptop.raw`. |
| `istat` times differ from the logs by 5 hours | Add `-z UTC`. |
| `jq: error ... Cannot iterate over null` | The field does not exist in every record; add a condition, for example `select(.event=="donor_search")`. |
| `base64: invalid input` | The site's cookie uses URL-safe base64 without padding: use `unb64` from step 5 of the setup. |
| `sqlite3: unable to open database` | Copy the database out with `icat` into `/work` first; sqlite3 cannot read inside the image. |
| A command prints nothing | Check you replaced placeholders like `USER`, `INODE`, `LAPTOP_IP`, `$S`, `$X`, and that you set the short names again in this shell. |
| `verify` fails `evidence-integrity` | You are pointing at the wrong folder, or a file was changed: re-download your evidence. |

## 15. Cleanup instructions

```bash
exit                                   # leave the analyst shell
docker compose down --remove-orphans
```

Delete the large working files once you have submitted: `rm work/laptop.raw work/unalloc.bin`. To remove the image as well: `docker image rm ghcr.io/kernalguard/cyberlab-ir-workstation:0.5.0`. To start over: `docker compose run --rm reset` (backs up your work first).

## 16. Reflection questions

1. Across Labs 1–4, which skill did you use most, and which surprised you?
2. The breach followed fixes being postponed. How would you present the risk of a postponed fix to a board so that it is taken seriously?
3. Where in this lab did you change your mind about a conclusion, and what evidence caused it?
4. What would you do differently if this were a real organisation and real donors?
