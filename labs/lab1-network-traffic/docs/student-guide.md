# Lab 1 — Network Traffic Analysis and Threat Identification

> **Status:** Draft v0.1.0 (2026-11-17). Every TShark command in Parts A–E was run against the `demo` capture on Linux x86-64 with TShark 4.2.2. The Lab 1 image was built and `verify` passed 10/10 on macOS Apple Silicon (Docker Desktop, TShark 4.4.19), where the Part D decode and the check-in count were confirmed. Windows is **UNTESTED**, and no student has walked through this guide yet.

## 1. Laboratory title

**Lab 1 — Network Traffic Analysis and Threat Identification: The Cedarwick Workstation Alert**

## 2. Course level

**Introductory undergraduate** (first cybersecurity or networking-security course). Graduate students complete the same tasks plus the graduate items marked **[Grad]** in sections 9–12.

**Undergraduate expectation:** find and document the indicators correctly, with commands someone else can repeat.
**Graduate expectation:** everything above, plus correlation across protocols, a stated confidence for each conclusion, alternative explanations you ruled out, and a report a manager could act on.

## 3. Estimated completion time

**90–120 minutes** for the investigation (sections 8–9), plus **45–60 minutes** to write the report. Graduate students should budget 30 extra minutes.

## 4. Prerequisite knowledge

- **Lab 0 completed.** You can start the lab with `docker compose`, move around the shell, and verify hashes.
- Basic networking: what an IP address, a port, a MAC address, DNS, TCP and HTTP are. If any of these are new, read the one-page refresher your instructor posts before starting.
- No prior Wireshark or TShark experience is needed. You will learn TShark (the command-line version of Wireshark) in this lab.

## 5. Learning objectives

By the end of this lab you will be able to:

| ID | Objective | Bloom level | Practised in |
|---|---|---|---|
| L1-1 | Verify the integrity of a packet capture and summarise it with `capinfos` and TShark statistics. | Apply | Part A |
| L1-2 | Write TShark display filters to isolate DNS, HTTP and TLS traffic by host, protocol and field. | Apply | Parts B–D |
| L1-3 | Distinguish algorithmically generated domains and NXDOMAIN bursts from normal DNS activity. | Analyze | Part B |
| L1-4 | Identify periodic command-and-control check-ins and estimate their interval from timestamps. | Analyze | Part C |
| L1-5 | Reconstruct an HTTP upload and decode its payload to assess what data left the network. | Analyze | Part D |
| L1-6 | Separate malicious indicators from benign look-alikes and justify each conclusion with evidence. | Evaluate | Part E |
| L1-7 | Produce a findings file and a timeline-based incident report with reproducible filter commands. | Create | Part F, section 12 |

## 6. Scenario background

**Cedarwick Neighborhood Aid** is a small nonprofit that runs a food pantry and a donor-funded rent assistance program. It has one office network, about ten staff computers, and an outside IT contractor.

On **10 October 2026** the endpoint protection console raised a *low-confidence* alert: "suspicious outbound connection" somewhere on the staff workstation segment. The alert did not say which computer. The contractor exported **one hour of traffic** from a mirror port on the office switch and has hired you to answer three questions:

1. **Is any computer compromised?** If so, which one?
2. **What did it communicate with, and how?**
3. **Did any data leave the network?** If so, what, when and how much?

The executive director needs to know whether she has to notify donors. Your report will be part of that decision, so every claim must point to evidence (a frame number, a filter, a decoded value) that someone else can check.

Read `/evidence/CASE-BRIEF.txt` before you start. It contains the network map.

> **Everything in this capture is synthetic.** All names, addresses, domains and "donor records" are fictional. Domains use reserved names (`.test`, `.example`, `example.org` …) and addresses come from private and documentation ranges. **Do not look any of them up on the internet**: they don't exist, and looking up indicators from a real case can alert an attacker.

### What is realistic and what is simplified

| Realistic | Simplified for the lab |
|---|---|
| Normal office noise: DNS, HTTPS to many sites, intranet pages, NTP, DHCP, ARP | Only one hour, one segment, about 10 hosts |
| Malware behaviours you will meet in real work: generated domain names, periodic check-ins, data staged and uploaded | The malware talks plain HTTP so you can read it. Real malware usually uses HTTPS, and you would see only metadata. |
| Benign traffic that *looks* suspicious | The upload is base64, not encrypted |

## 7. Environment requirements

| Item | Requirement |
|---|---|
| Computer | 8 GB RAM, 4 CPU cores, 20 GB free disk (same as Lab 0) |
| Software | Docker Desktop (macOS/Windows) or Docker Engine + Compose (Linux), working as in Lab 0 |
| Docker memory | 4 GB recommended. The lab itself is limited to 512 MB. |
| Download | About 300 MB the first time (the TShark image), plus the 17 MB evidence |
| Optional | **Wireshark** installed on your computer (wireshark.org) if you want a graphical view. Everything graded can be done with TShark alone. |

### How the lab is built

```
Your computer
└── Docker
    └── container "workstation"        ← normal user, no network, all privileges dropped
        ├── /evidence  (read-only)     ← the capture, case brief and manifest
        └── /work      (writable)      ← your notes, findings.json, exported files
                                          = the labs/lab1-network-traffic/work folder on your computer
```

The container has **no network at all**. TShark only *reads* the capture file. Nothing you do can send traffic anywhere.

## 8. Setup instructions

**Step 1 — Update the lab files.** In the `cyberlab-platform` folder you cloned for Lab 0:

```bash
git pull
cd labs/lab1-network-traffic
```

(If you downloaded a ZIP for Lab 0, download a fresh ZIP and unzip it.)

**Step 2 — Choose your evidence.**

- **Practice / self-study:** use the `demo` evidence already in `evidence/`. Do nothing.
- **Graded work:** your instructor gives you **your own evidence folder** (your *variant*). Its indicators are different from the demo's and from your classmates'. Unzip it somewhere outside the repository, then tell the lab where it is **in every new terminal window**:

  ```bash
  export CYBERLAB_EVIDENCE=~/Downloads/lab1-XXXX-XXXX/evidence     # use your real path
  ```

  Windows (WSL): copy the folder into your WSL home first, for example `~/lab1-evidence`, and use that path.

**Step 3 — Download the image and check your environment:**

```bash
docker compose pull
docker compose run --rm verify
```

You should see `OVERALL: PASS` and, among other lines, these two:

```
[PASS] tools                10 required tools found
[PASS] evidence-integrity   all 2 files match MANIFEST.sha256
```

If you see `FAIL`, stop and go to [Troubleshooting](#14-troubleshooting).

**Step 4 — Put fresh templates in your work folder:**

```bash
docker compose run --rm reset
```

`work/` now contains `findings.json`, `case-notes.md` and `chain-of-custody.md`. Open them with a text editor on your computer and keep them open while you work.

**Step 5 — Open the analyst shell:**

```bash
docker compose run --rm workstation
```

Inside the container, set two shortcuts. You will use them in almost every command:

```bash
PCAP=/evidence/cedarwick-ws-segment.pcapng
alias ts='tshark -r "$PCAP" -t ud'        # -t ud = show times as UTC dates
```

You need to set them again each time you open a new workstation shell.

## 9. Investigation tasks

**Work like an examiner:** after each command that shows you something useful, add a row to the *Working log* in `case-notes.md`: the time (`date -u +%H:%M`), the exact command, and what it showed. Your report must let someone else repeat your steps.

### TShark in two minutes

| You want to… | Use |
|---|---|
| See packets that match a condition | `ts -Y '<display filter>'` |
| Print only certain fields | `ts -Y '<filter>' -T fields -e <field> -e <field>` |
| Run a statistics report | `tshark -r "$PCAP" -q -z <report>` |
| Count or rank results | pipe into `sort | uniq -c | sort -rn` |

Display filters use the same syntax as Wireshark: `ip.addr == 10.20.30.12`, `dns`, `http.request`, `tcp.port == 443`, combined with `&&`, `||` and `!`. Field names: in Wireshark, click a field and look at the status bar, or search the Wireshark *Display Filter Reference*.

### Part A — Integrity and first look (L1-1)

1. **Verify before you analyze.**

   ```bash
   cd /evidence
   sha256sum -c MANIFEST.sha256
   cd /work
   ```

   Copy the two hashes into the integrity table in `case-notes.md`, and fill in the *Received (UTC)* and *Handled by* columns of `chain-of-custody.md`.

2. **What is in the file?**

   ```bash
   capinfos "$PCAP"
   ```

   Record the first and last packet times, the number of packets and the duration. (The lab container runs in UTC, so the times shown are UTC.)

3. **Which protocols, and who talks the most?**

   ```bash
   tshark -r "$PCAP" -q -z io,phs              # protocol hierarchy
   tshark -r "$PCAP" -q -z endpoints,ip        # every IP address, busiest first
   tshark -r "$PCAP" -q -z conv,ip | head -40  # busiest conversations
   ```

   Using the network map in `CASE-BRIEF.txt`, sort the addresses you see into: *internal servers*, *staff workstations*, *external*. Which external address ranges appear? Does anything in the conversation list surprise you? Write down your first impressions. You will test them later.

> Busiest is **not** the same as suspicious. Large HTTPS transfers are normal. Keep an open mind until you have evidence.

### Part B — DNS: who is asking for what? (L1-2, L1-3)

Every connection to a named site starts with a DNS lookup, so DNS is often the fastest way to find odd behaviour.

1. **All lookups, per workstation:**

   ```bash
   ts -Y 'dns.flags.response == 0' -T fields -e ip.src -e dns.qry.name | sort | uniq -c | sort -k2,2 -k1,1rn | less
   ```

   Most names will look like ordinary sites. Scroll through and note any names that look **random** (long strings of letters and digits with no meaning).

2. **Failed lookups (NXDOMAIN = "no such domain"):**

   ```bash
   ts -Y 'dns.flags.rcode == 3' -T fields -e ip.dst | sort | uniq -c | sort -rn
   ts -Y 'dns.flags.rcode == 3' -T fields -e _ws.col.Time -e ip.dst -e dns.qry.name
   ```

   One or two failures from a person mistyping an address is normal. **Bursts** of failures for random-looking names, repeating on a schedule, are a classic sign of malware using a **domain generation algorithm (DGA)**: it tries many generated names until one resolves to its server.

3. **Follow one burst to the end.** Pick the host with the suspicious failures and list *all* its lookups in time order, including the answers:

   ```bash
   ts -Y 'dns && ip.addr == <host-ip>' -T fields -e _ws.col.Time -e dns.flags.response -e dns.qry.name -e dns.flags.rcode -e dns.a
   ```

   Which generated name **did** resolve, and to what address? How often does the burst repeat? Does the host use the same names each time?

4. **Rule out the look-alikes.** Not every random-looking name is malicious. For each odd name you noted, check **how many hosts** looked it up:

   ```bash
   ts -Y 'dns.qry.name == "<name>"' -T fields -e ip.src | sort | uniq -c
   ```

   A random-looking name used by many hosts, with successful answers, is probably a content delivery network (CDN). A single failed lookup next to a similar real name is probably a typo. Record each ruled-out item in the *Benign look-alikes* table.

### Part C — HTTP check-ins (L1-2, L1-4)

1. **What HTTP requests were made, by whom, to where?**

   ```bash
   ts -Y 'http.request' -T fields -e _ws.col.Time -e ip.src -e http.request.method -e http.host -e http.request.uri | less
   ```

2. **User-Agents.** Every HTTP client announces itself with a `User-Agent` header. List them with counts:

   ```bash
   ts -Y 'http.request' -T fields -e ip.src -e http.user_agent | sort | uniq -c | sort -rn
   ```

   Which User-Agent is used by only one host? Does it match the browsers the other workstations use, or look out of date? Ask yourself why an office PC would send that.

3. **Isolate the suspect's requests to the address you found in Part B:**

   ```bash
   ts -Y 'http.request && ip.dst == <server-ip>' -T fields -e frame.number -e _ws.col.Time -e http.request.method -e http.host -e http.request.uri
   ```

   Note the **first** request (time and frame number), the request pattern (path and parameters), and how many **check-ins** (GET requests) there are. Count with `| wc -l`, and make sure your filter counts only GET requests.

4. **How regular are the check-ins?** `frame.time_delta_displayed` is the time since the previous *displayed* packet, so with a filter that shows only the check-ins it gives the gap between check-ins:

   ```bash
   ts -Y 'http.request.method == "GET" && ip.dst == <server-ip>' -T fields -e frame.time_delta_displayed > /work/gaps.txt
   awk 'NR>1 {s+=$1; n++} END {printf "%d gaps, mean %.1f s\n", n, s/n}' /work/gaps.txt
   tail -n +2 /work/gaps.txt | sort -n | awk '{a[NR]=$1} END {print "median", a[int((NR+1)/2)], "s; min", a[1], "s; max", a[NR], "s"}'
   ```

   Human browsing is irregular. A program on a timer produces gaps that cluster tightly around one value, sometimes with a few seconds of deliberate *jitter*. Report the interval as a whole number of seconds.

5. **[Grad]** Is there **another** host with periodic traffic? Compare its timing, destination, protocol and User-Agent with the suspect's. Explain in your report why it is, or is not, part of the incident.

### Part D — Did data leave? (L1-5)

1. **Find uploads.** Uploads usually use `POST`:

   ```bash
   ts -Y 'http.request.method == "POST"' -T fields -e frame.number -e _ws.col.Time -e ip.src -e http.host -e http.request.uri -e http.content_type -e http.content_length
   ```

   Most POSTs here are staff submitting intranet forms. Which one is different, and why (destination, content type, size)? Note its **frame number**, **time**, **URI** and **Content-Length** (the size in bytes of the body).

2. **Read the whole exchange.** Find the TCP stream number, then follow it:

   ```bash
   ts -Y 'frame.number == <frame>' -T fields -e tcp.stream
   tshark -r "$PCAP" -q -z follow,http,ascii,<stream> | less
   ```

   The body is a block of letters, digits, `+` and `/`, possibly ending with `=`. That is **base64**, an encoding (not encryption) that turns any data into plain text.

3. **Decode it into your work folder** (never into `/evidence`):

   ```bash
   ts -Y 'frame.number == <frame>' -T fields -e http.file_data | xxd -r -p > /work/upload.b64
   head -c 80 /work/upload.b64; echo        # should now be base64 text
   base64 -d /work/upload.b64 > /work/upload-decoded.txt
   file /work/upload-decoded.txt
   head /work/upload-decoded.txt
   wc -l /work/upload-decoded.txt
   ```

   TShark prints the body as hexadecimal, and `xxd -r -p` turns the hex back into the original bytes. If `head` on `upload.b64` still shows only hex digits (0–9, a–f), check that you used the right frame number.

4. **Assess the data.** What kind of records are they? How many **records** (rows, not counting a header line)? What fields would matter to the executive director's notification decision? Record a SHA-256 of `upload-decoded.txt` in your case notes (`sha256sum /work/upload-decoded.txt`), because it is now a derived exhibit.

> **Handling rule:** the records are fictional, but treat them as if they were real personal data. Do not paste more than three example rows into your report. Describe the rest.

### Part E — Pin down the host and build the timeline (L1-6)

1. **Hardware address.** IP addresses on a DHCP network can change. The MAC address identifies the network card:

   ```bash
   ts -Y 'ip.src == <host-ip>' -T fields -e eth.src | sort -u
   ts -Y 'dhcp || arp.src.proto_ipv4 == <host-ip>' -T fields -e _ws.col.Time -e eth.src -e _ws.col.Info | head
   ```

2. **Timeline.** In the *Timeline* table of `case-notes.md`, put every suspicious event in time order with its frame number: the first generated-domain burst, the first successful resolution, the first check-in, the upload, any later activity. Times are UTC.

3. **Ruled-out list.** Make sure the *Benign look-alikes* table has at least **three** entries, each with the evidence that makes it benign.

4. **Before you conclude**, check that your story holds up. Does the same host appear in the DNS, check-in and upload evidence? Do the times line up (lookup → connection)? Is there anything that does **not** fit?

### Part F — Fill in `findings.json` (L1-7)

`work/findings.json` is graded automatically against your variant's answers, so **format matters**.

| Item | What to enter | Format example |
|---|---|---|
| `variant` | your pseudonym from the evidence folder, or `demo` | `"K7QX-2M4P"` |
| `suspicious_host_ip` | the compromised workstation's IP | `"10.20.30.199"` |
| `suspicious_host_mac` | its MAC address | `"02:00:5e:00:00:01"` |
| `c2_domains` | **every** generated domain the host looked up, including the one that resolved | `["abc.test", "def.example"]` |
| `c2_resolving_domain` | the generated domain that resolved | `"def.example"` |
| `c2_server_ip` | the address it resolved to | `"192.0.2.1"` |
| `c2_user_agent` | the full User-Agent string, copied exactly | `"Mozilla/4.0 (…)"` |
| `first_beacon_utc` | time of the **first HTTP check-in** (GET), to the second | `"2026-10-10T18:00:00Z"` |
| `beacon_interval_s` | typical gap between check-ins, whole seconds | `60` |
| `checkin_count` | number of check-in GET requests (do not count the upload) | `12` |
| `exfil_utc` | time of the upload request | `"2026-10-10T18:00:00Z"` |
| `exfil_uri` | the upload's URI, path and query string | `"/path/x?id=1"` |
| `exfil_bytes` | the upload's `Content-Length` | `1234` |
| `exfil_record_count` | decoded data rows, **excluding** the header | `10` |
| `scan_open_ports` | optional challenge (section 11); leave `[]` if skipped | `["10.20.30.1:443"]` |

*The format examples are made up. They are not hints.* Convert TShark's `2026-10-10 18:00:00.123456` to `2026-10-10T18:00:00Z` (keep the seconds, drop the fraction, add `T` and `Z`). Numbers have no quotes; text has quotes; leave anything you could not find as `null`.

Check that the file is valid JSON before you submit:

```bash
cyberlab-findings validate /work/findings.json
```

`PASS` means the file is well-formed. If you see `FAIL`, the message names the problem. For JSON syntax errors, `jq . /work/findings.json` points to the line (usually a missing comma or quote).

## 10. Guided questions

Answer these in your report (section 12). Cite a frame number or command for each.

1. What are the first and last packet times, and how many packets are in the capture? Did the evidence match its manifest?
2. Which protocols make up most of the traffic? Is that what you would expect from an office?
3. Which host produced the suspicious DNS failures? Describe the pattern: how many names, how often, and what made them look generated.
4. Which generated name resolved, and to what address? Why would malware use many names instead of one?
5. Which User-Agent was unusual, and what about it stood out?
6. When did check-ins start, how often did they happen, and how many were there? Show how you measured the interval.
7. What was uploaded, when, to where, and how large was it? How many records, and what kinds of personal data fields did they contain?
8. What MAC address belongs to the compromised host, and why record it in addition to the IP?
9. Name three things that looked suspicious but were benign, and the evidence for each.
10. Base64 is not encryption. Why might malware use it anyway?
11. What should Cedarwick do in the next 24 hours? Give three concrete actions, in priority order.
12. **[Grad]** For each of your three main conclusions (which host, what C2, what left), state your confidence (high / medium / low) and the strongest alternative explanation you considered.

## 11. Independent challenge (optional)

1. **Internal reconnaissance.** Some time after the upload the suspect host probed other machines on the office network. Find it:
   - ARP requests sent by the host in a short time (`arp.opcode == 1`)
   - TCP connection attempts (`tcp.flags.syn == 1 && tcp.flags.ack == 0`) from the host to internal addresses. Look at the **source port**: a scanner often reuses one.
   - which of those attempts were answered with `SYN/ACK` (port open) rather than `RST` (port closed)

   Enter the open services in `scan_open_ports` as `"ip:port"` strings. Watch out: the host also makes ordinary connections to internal servers during the hour, and those are **not** part of the scan.
2. **TLS metadata.** Without decrypting anything, list the server names (`tls.handshake.extensions_server_name`) each host visited over HTTPS. Does the suspect host's HTTPS traffic look different from its neighbours'?
3. **Wireshark cross-check.** Open the capture in Wireshark on your computer (*File → Open*, then the `evidence` folder). Use *Statistics → Conversations* and *Statistics → I/O Graph* with your check-in filter. Include one screenshot that shows the periodic pattern, with a caption.
4. **[Grad]** Write three detection ideas the contractor could deploy (a DNS rule, a proxy/User-Agent rule, a rule for regular connection timing). For each, estimate how many **false positives** it would have raised in this capture.

## 12. Required deliverables

| File | What it is | Graded by |
|---|---|---|
| `work/findings.json` | Your structured answers (Part F) | Auto-checker (40 points) |
| `Lab1-Report-<pseudonym>.pdf` | Incident report (outline below), including answers to section 10 | Instructor, using the rubric (60 points) |
| `work/case-notes.md` | Working log with timestamps, timeline, ruled-out table | Supports the report score |
| `work/chain-of-custody.md` | At least: received, verified at start, verified at end | Supports the report score |
| `work/lab1-check.json` | Created by `verify`. Run it again at the end. | Required for grading |

**Report outline** (undergraduate 4–6 pages; graduate 6–10 pages):

1. **Executive summary** — five sentences or fewer, for the executive director: what happened, which computer, whether data left, what to do now.
2. **Scope and evidence** — what you received, hashes, time range, tools and versions (`tshark --version | head -1`).
3. **Method** — how you approached the capture, in the order you did it.
4. **Findings** — one subsection per finding (compromised host, C2 behaviour, data exfiltration), each with the filter you used, the frame numbers, and the observed values.
5. **Timeline** — a UTC table of the key events.
6. **Benign activity ruled out** — at least three items.
7. **Conclusions and recommendations** — answers to the three client questions. **[Grad]** with confidence levels and alternatives.
8. **Appendix** — the commands from your working log that support each finding.

## 13. Submission instructions

1. In the workstation shell, run `cyberlab-findings validate /work/findings.json` one last time.
2. Leave the container (`exit`) and run `docker compose run --rm verify`, so `lab1-check.json` is current and shows the evidence was **unchanged at the end** of your analysis. Add that result to your chain of custody.
3. Export your report to PDF.
4. Upload to the Lab 1 assignment in the course LMS: the report PDF, `findings.json`, `case-notes.md`, `chain-of-custody.md`, `lab1-check.json`.
5. **Do not** upload the evidence, `upload-decoded.txt`, or any other exported file unless your instructor asks for them.

Your graded variant is yours alone. Discuss *methods* with classmates if your course policy allows, but your indicators will not match theirs, and identical answers from different variants are easy to spot. Follow your course syllabus on the use of AI tools.

## 14. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `pull access denied` / `manifest unknown` for `cyberlab-net-analysis` | The Lab 1 image is not published yet, or you typed the name wrong | Tell your instructor. Meanwhile: `docker compose build workstation` (needs internet once, a few minutes). |
| `[FAIL] evidence-integrity` | Your evidence folder is incomplete or changed, or `CYBERLAB_EVIDENCE` points to the wrong folder | Check the path with `echo $CYBERLAB_EVIDENCE` (on your computer, not inside the container). Unzip your bundle again. Write the problem in your chain of custody. **Do not analyze changed evidence.** |
| `verify` checks the demo instead of your variant | `CYBERLAB_EVIDENCE` is not set in this terminal window | `export CYBERLAB_EVIDENCE=…` again, then rerun. |
| `tshark: The file "" doesn't exist` | You opened a new shell and lost the shortcuts | Run the two lines in Step 5 again. |
| `tshark: … isn't a valid display filter` | Filter typo: single `=`, missing quotes around text, wrong field name | Use `==`, put text values in double quotes inside the single-quoted filter (`'http.host == "x.test"'`). |
| A command prints nothing | The filter is valid but matches nothing | Remove conditions one at a time until something appears. Check the IP or name for typos. |
| `base64: invalid input` | You decoded the hex form, or included HTTP headers | Use the `xxd -r -p` step in Part D. Check `head -c 80 /work/upload.b64` first. |
| `Permission denied` writing a file | You tried to write into `/evidence` or another read-only place | Write to `/work/…` only. |
| `[FAIL] writable:/work … EACCES` (Linux) | Your user ID is not 1000 | `export CYBERLAB_UID=$(id -u) CYBERLAB_GID=$(id -g)` before `docker compose` |
| Commands are slow | Each TShark command re-reads the 17 MB file. This is normal. | Save results you will reuse to a file in `/work` and work from that. |
| Wireshark on your computer shows local times | Wireshark's default display | *View → Time Display Format → UTC Date and Time of Day* |

## 15. Cleanup instructions

When you have submitted:

```bash
exit                                    # leave the workstation shell, if you are in it
docker compose down --remove-orphans    # remove lab containers and networks
docker ps -a                            # should list no cyberlab-lab1 containers
unset CYBERLAB_EVIDENCE
```

Keep your graded evidence bundle until grades are final, then delete it. Keep the image if you will do later labs. Lab 4 reuses it.

To start over, run `docker compose run --rm reset`. Your previous work is moved to `work/.backup/<timestamp>/`, not deleted.

## 16. Reflection questions

1. Which single piece of evidence first convinced you a host was compromised? Would it have been enough on its own?
2. Which benign look-alike nearly fooled you, and what would you check first next time?
3. The malware used plain HTTP. If it had used HTTPS, which of your findings could you still have made, and which would have been lost?
4. How confident are you that **no other** host is compromised? What would you need to be more confident?
5. What would you do differently if you had to repeat this investigation on a full day of traffic?
