# Lab 3 — Web Application Security Assessment

> **Status:** Draft v0.4.0-dev (2026-11-18). The lab stack (gateway, app, database, workstation) was built and tested on macOS Apple Silicon (Docker Desktop): `verify` 14/14 and every weakness validated end to end. The commands in this guide were checked against the `demo` site on Linux x86-64 with the same application code. Windows is **UNTESTED**, and no student has walked through this guide yet.

## 1. Laboratory title

**Lab 3 — Web Application Security Assessment: The Cedarwick Donation Site**

## 2. Course level

**Upper undergraduate** (web security or secure software course, after Labs 0–2). Graduate students also complete the items marked **[Grad]**: deeper log analysis and a remediation design for every finding.

**Undergraduate expectation:** find and validate each weakness within the rules of engagement, show reproducible evidence, rate the risk, and fix one weakness with proof.
**Graduate expectation:** everything above, plus reconstructing your own test from the logs as a defender would, and a prioritised remediation plan that a developer could implement.

## 3. Estimated completion time

**120–150 minutes** for the assessment (sections 8–9), plus **60 minutes** for the report. Graduate students should budget 45 extra minutes.

## 4. Prerequisite knowledge

- **Lab 0 completed** (Docker basics). Labs 1–2 give the story, but are not technically required.
- HTTP basics: requests and responses, methods (GET/POST), status codes (200, 302, 404, 500), headers, **cookies**, HTML forms.
- SQL basics: `SELECT … FROM … WHERE …`. You will learn `UNION` in this lab.
- Base64 is an encoding, not encryption (Lab 1).

## 5. Learning objectives

By the end of this lab you will be able to:

| ID | Objective | Bloom level | Practised in |
|---|---|---|---|
| L3-1 | Explain the scope and rules of an authorised assessment and work strictly within them. | Understand | Section 6, setup step 4 |
| L3-2 | Map a web application's pages, parameters, cookies and roles with a browser and curl. | Apply | Part A |
| L3-3 | Identify and validate SQL injection, broken access control, broken session handling, information leakage and weak authentication. | Analyze | Parts B–E |
| L3-4 | Use gateway, application and database logs to reconstruct what a tester or attacker did. | Analyze | Part F |
| L3-5 | Rate each finding's risk and justify it with evidence and business impact. | Evaluate | Section 10, report |
| L3-6 | Fix a vulnerability in the source code, re-test it, and show the fix did not break the feature. | Create | Part G |
| L3-7 | Write a findings file and an assessment report with reproducible steps and prioritised remediation. | Create | Part H, section 12 |

## 6. Scenario background

After the incident you investigated in Labs 1 and 2, **Cedarwick Neighborhood Aid**'s board is nervous about its **donation website**, `give.cedarwick.test`. Before the site relaunches for the winter appeal, the executive director has hired you to assess it.

You have a **signed authorisation** (the scope letter in `evidence/CASE-BRIEF.txt`). Read it before you test anything. In short:

| | |
|---|---|
| **In scope** | The lab copy of the site only: `http://127.0.0.1:8080` from your computer, `http://gateway:8080` from the lab workstation |
| **Out of scope** | Everything else |
| **Not allowed** | Denial of service; password guessing beyond `wordlist.txt` (one attempt per word per account); changing or deleting other users' data |
| **Data handling** | Quote no more than three donor records in your report |
| **Deliverable** | Validated findings with risk ratings and fixes, and one weakness fixed and re-tested |

> **Professional practice:** an assessment without written authorisation is an attack. Real testers keep their scope letter at hand and stop the moment they are unsure whether something is in scope.

**Do not read `evidence/seed.sql` to find answers.** It is the site's starting data so that the database can be built. A real tester never has it. Every finding must come from testing the site.

> **Everything here is synthetic.** The organisation, people, donors and payments are fictional. No real payment is processed. The site is **intentionally vulnerable** and runs only on your computer.

### What is realistic and what is simplified

| Realistic | Simplified for the lab |
|---|---|
| A small Flask + PostgreSQL site behind an nginx gateway, with the kinds of mistakes found in real small-organisation sites | One page per feature; no JavaScript front end; weaknesses are easy to reach |
| Real request, application and database logs | Logs live in the same place and are easy to read |
| A scope letter and rules of engagement | No change-control process, no production data |

## 7. Environment requirements

| Item | Requirement |
|---|---|
| Computer | 8 GB RAM, 4 CPU cores, 20 GB free disk |
| Software | Docker Desktop (macOS/Windows) or Docker Engine + Compose (Linux), working as in Lab 0 |
| Docker memory | 4 GB recommended (`verify` fails below 3 GB). The lab uses about 1.3 GB at most. |
| Browser | Any modern browser, with its developer tools (Network and Storage/Application tabs) |
| Download | About 450 MB the first time (four images) |

### How the lab is built

```
Your computer
├── Browser ──► 127.0.0.1:8080 ─┐                (loopback only: nobody else can reach it)
└── Docker                       ▼
    ├── gateway   (nginx)      ─── the only door; writes /logs/gateway.jsonl
    │      │  internal network "labnet" (no route out)
    │      ├── app (Flask)      ─── code from labs/lab3-webapp-assessment/app/ ; /logs/app.jsonl
    │      └── db  (PostgreSQL) ─── logs every SQL statement to /logs/postgres.log
    └── workstation (curl, http, python3)  on internal network "edge": can reach only the gateway
```

## 8. Setup instructions

**Step 1 — Update the lab files.**

```bash
cd cyberlab-platform && git pull
cd labs/lab3-webapp-assessment
```

**Step 2 — Choose your evidence.** Practice uses the `demo` evidence already in `evidence/`. For graded work, unzip your own evidence outside the repository and, in **every new terminal window**:

```bash
export CYBERLAB_EVIDENCE=~/Downloads/lab3-XXXX-XXXX/evidence     # your real path
```

**Step 3 — Download the images and put fresh templates in `work/`:**

```bash
docker compose --profile tools pull
docker compose pull
docker compose run --rm reset
```

**Step 4 — Sign the authorised-use agreement.** Open `work/authorized-use.md`, read it, then fill in your name and the date and type `I AGREE` on the empty last line:

```bash
open -e work/authorized-use.md        # macOS (TextEdit; save as plain text)
nano work/authorized-use.md           # any system (Ctrl+O, Enter to save; Ctrl+X to exit)
```

**Step 5 — Start the site and check everything:**

```bash
docker compose up -d
docker compose ps                     # wait until db, app and gateway show "healthy" (about 20 s)
docker compose run --rm verify
```

`verify` must end with `OVERALL: PASS`, including `egress-blocked` (no route out), `http:site` (the site answers) and `authorized-use` (you signed).

**Step 6 — Open the site** in your browser: **http://127.0.0.1:8080**. Keep the developer tools open (Network tab).

**Step 7 — Open the workstation shell** in a second terminal (same folder):

```bash
docker compose run --rm workstation
```

Inside it, `$SITE` is `http://gateway:8080`. Keep a cookie jar in your work folder so curl remembers sessions:

```bash
JAR=/work/cookies.txt
rows() { sed 's/<tr>/\n<tr>/g' | grep '^<tr><td>' | sed 's/<[^>]*>/ | /g; s/^ *| *//; s/ | *| / | /g'; }
curl -s $SITE/healthz; echo
```

`rows` prints each row of an HTML results table on its own line (the site writes a whole table on one line). Set `JAR` and `rows` again whenever you open a new workstation shell.

## 9. Investigation tasks

Record every request that shows something in `work/case-notes.md`: time, exact command or browser action, and what it showed. For each weakness you must be able to show **identify** (what you noticed), **validate** (the smallest test that proves it) and **impact** (what an attacker gains).

### Part A — Map the site (L3-2)

1. **Browse** every page you can reach as a visitor. Create an account and log in. Make a small donation with the training card number shown on the form.
2. **Look at what crosses the wire.** In the browser's Network tab, inspect a few requests: method, URL, status, request and response headers, form fields.
3. **Repeat key requests with curl** from the workstation:

   ```bash
   curl -si $SITE/ | head -20
   curl -si $SITE/staff | head -5
   curl -s -c $JAR -b $JAR -d "full_name=Your Name" -d "email=you@example.com" -d "password=CHOOSE-ONE" $SITE/register -o /dev/null -w "%{http_code} %{redirect_url}\n"
   curl -s -b $JAR $SITE/account | grep -i "receipt"
   ```

4. Build a **site map** table in your notes: page, method, parameters, who may use it (visitor / donor / staff), and anything that looks interesting.

### Part B — Passwords and authentication (L3-3)

1. **Password policy.** What is the shortest password the registration form accepts? Test lengths from 0 upwards with new e-mail addresses:

   ```bash
   for n in 0 1 2 3 4 5 6 7 8; do
     p=$(printf '%*s' "$n" '' | tr ' ' 'a')
     code=$(curl -s -o /dev/null -w "%{http_code}" -d "full_name=Policy Test" -d "email=policy$n@example.com" -d "password=$p" $SITE/register)
     echo "length $n -> $code"
   done
   ```

   A `302` means the account was created. Compare the result with current guidance (NIST SP 800-63B recommends at least 8 characters, a check against common and breached passwords, and no composition rules).

2. **Staff accounts.** There is a staff login at `/staff/login`. You do not know any staff usernames yet. Part E will reveal them; come back to step 3 then.

3. **(After Part E) Guess within the rules.** The scope letter allows **one attempt per word in `wordlist.txt` per staff account**, nothing more:

   ```bash
   for user in <usernames from Part E>; do
     for word in $(cat /evidence/wordlist.txt); do
       code=$(curl -s -o /dev/null -w "%{http_code}" -d "username=$user" -d "password=$word" $SITE/staff/login)
       [ "$code" = "302" ] && echo "VALID: $user / $word"
     done
   done
   ```

   Which account falls? Why does a single weak staff password matter so much on this site?

### Part C — Sessions (L3-3)

1. **Look at your session cookie.** In the browser (Storage/Application → Cookies) or in `$JAR`. What is it called and what does its value look like?

   ```bash
   grep cw_session $JAR | awk '{print $6, $7}'       # curl marks HttpOnly cookies with a #HttpOnly_ prefix
   ```

2. **Decode it.** The value looks random, but try base64 (URL-safe alphabet, padding removed):

   ```bash
   python3 -c 'import base64,sys; t=sys.argv[1]; print(base64.urlsafe_b64decode(t + "=" * (-len(t) % 4)))' '<cookie value>'
   ```

   What does the server keep in it? Is anything protecting it from being changed (a signature, an expiry)?

3. **Does logout end the session?** Copy your cookie value, log out in the browser, then:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" -b "cw_session=<old value>" $SITE/account
   ```

   `200` means the old token still works after logout.

4. **Validate the impact.** Build a cookie that claims to be a different kind of user, encode it the same way, and request the staff dashboard:

   ```bash
   python3 -c 'import base64,json,sys; print(base64.urlsafe_b64encode(json.dumps(json.loads(sys.argv[1]), separators=(",",":")).encode()).decode().rstrip("="))' '{"kind":"…","id":…,"n":…}'
   curl -s -b "cw_session=<forged value>" $SITE/staff
   ```

   What does the staff dashboard show? Record the **staff notice** code. Stay read-only: do not change anything as staff.

### Part D — Access control on receipts (L3-3)

1. **Your own receipt.** After your donation, the site sends you to `/receipts/<number>`. Note the number.
2. **Someone else's receipt.** Change the number by one. What happens? What personal data is shown? This is an **IDOR** (insecure direct object reference): the server checks *that* you are logged in, not *whose* receipt it is.
3. **Measure the impact.** How many receipts can one donor account read? Which receipt is the **largest gift**, how much, and whose e-mail address is on it? Write a short loop rather than clicking:

   ```bash
   last=<your receipt number>
   for n in $(seq 100001 $((last - 1))); do
     page=$(curl -s -b $JAR $SITE/receipts/$n)
     amount=$(printf '%s' "$page" | grep -o 'Amount</dt><dd>\$[0-9,.]*' | sed 's/.*\$//; s/,//g')
     echo "$n $amount"
   done | sort -k2 -n | tail -3
   ```

   Then open the top receipt and record its number, amount and donor e-mail.

### Part E — Errors and injection (L3-3)

1. **Verbose errors.** While logged in as a donor, request a receipt number that is not a number:

   ```bash
   curl -s -b $JAR $SITE/receipts/x | sed 's/&#34;/"/g' | grep -E 'File "|Error|Python' | head -20
   ```

   What does the error page reveal? Note the **path of the application's source file**, the software versions, and anything about the database.

2. **Find the injection point.** As staff (Part C), the donor search at `/staff/donors?q=` looks up names. Try a normal search, then a single quote:

   ```bash
   STAFF="cw_session=<your forged staff cookie>"
   curl -s -b "$STAFF" -G $SITE/staff/donors --data-urlencode "q=son" | rows
   curl -s -b "$STAFF" -G $SITE/staff/donors --data-urlencode "q='" | sed 's/&#39;/'"'"'/g' | grep -iE "LINE|ILIKE|error" | head -5
   ```

   The error shows the **SQL text** around your input. Which path and parameter are injectable?

3. **Validate.** A search that should match nothing, made always true. The `-- ` (dash, dash, space) turns the rest of the site's SQL into a comment:

   ```bash
   curl -s -b "$STAFF" -G $SITE/staff/donors --data-urlencode "q=zzzz" | rows | wc -l
   curl -s -b "$STAFF" -G $SITE/staff/donors --data-urlencode "q=zzzz' OR 1=1-- " | rows | wc -l
   ```

   Why does the difference between the two counts prove injection? Why did you need the `-- `?

4. **Extract with UNION.** The results table has **four columns** (ID, name, e-mail, since). A `UNION SELECT` lets you add rows of your own, as long as they also have four columns of compatible types. Template:

   ```bash
   curl -s -b "$STAFF" -G $SITE/staff/donors --data-urlencode "q=zzzz' UNION SELECT <4 values> FROM <table>-- " | rows
   ```

   - List the tables: PostgreSQL describes itself in `information_schema.tables` (columns `table_name`, `table_schema`; the site's tables are in schema `public`). Which table does the site **never show** in any page?
   - Read that table (find its columns in `information_schema.columns`). Record the **code** it holds.
   - List the **staff** accounts (username, role). How many are there? Now go back to Part B step 3.

   Read only. Do not use `INSERT`, `UPDATE`, `DELETE` or `DROP`: they are out of scope.

### Part F — What did the logs see? (L3-4)

The lab keeps three logs in `/logs` (read-only in the workstation).

```bash
ls -la /logs
tail -3 /logs/gateway.jsonl | jq .
tail -3 /logs/app.jsonl | jq .
grep -c "ILIKE" /logs/postgres.log
```

1. **Gateway log.** Count your requests by status code, and find the requests that returned `500`:

   ```bash
   jq -r .status /logs/gateway.jsonl | sort | uniq -c
   jq -r 'select(.status==500) | .uri' /logs/gateway.jsonl | head
   ```

   The gateway logs the **session cookie** of every request. Find your forged staff cookie in it. Why is logging session tokens itself a security problem?

2. **Application log.** Which events show your IDOR test (`receipt_view` with `owner_match:false`) and your injection (`donor_search`)?

   ```bash
   jq -c 'select(.event=="receipt_view" and .owner_match==false) | {ts, path, user}' /logs/app.jsonl | head -3
   jq -c 'select(.event=="donor_search") | {ts, q, results}' /logs/app.jsonl | tail -3
   ```

3. **Database log.** Find your UNION query as the database received it:

   ```bash
   grep "UNION" /logs/postgres.log | tail -2
   ```

4. **[Grad]** Write three detection rules a defender could run on these logs (for example: many `receipt_view` with `owner_match:false` from one session; a `donor_search` containing `'` or `UNION`; a staff session whose cookie never appeared in a `login_ok`). For each, say how many of your own requests it would have caught and how many false alarms it might raise.

### Part G — Fix one weakness and prove it (L3-6)

You will fix the **SQL injection**. The site's source is on your computer at `labs/lab3-webapp-assessment/app/app.py`, mounted read-only into the app container.

1. **Find the vulnerable code** in `app.py` (search for the donor search route). Explain in your notes why it is injectable.
2. **Fix it** with a **parameterised query**: the SQL text stays fixed and the user's input is passed separately to `execute()`. psycopg uses `%s` placeholders, for example:

   ```python
   rows = db().execute("SELECT … WHERE full_name ILIKE %s OR email ILIKE %s ORDER BY id", (pattern, pattern)).fetchall()
   ```

   (Build `pattern` with the `%` wildcards in Python; never paste user input into the SQL string.) Edit with any editor on your computer, then restart only the app:

   ```bash
   docker compose restart app
   ```

3. **Re-test (both directions).** From the workstation, run your step E3 and E4 attacks again: they must now return **no extra rows and no SQL error**. Then show the feature still works: a normal search still finds donors.
4. **Keep the evidence.** On your computer: `git diff labs/lab3-webapp-assessment/app/app.py > labs/lab3-webapp-assessment/work/fix.diff`.
5. **[Grad]** For each of the other four weaknesses, write the fix you would make (code-level, a few lines each) and how you would test it. Do not implement them in this lab.

To return to the vulnerable version later: `git checkout labs/lab3-webapp-assessment/app/app.py` and `docker compose restart app`.

### Part H — Fill in `findings.json` (L3-7)

| Item | What to enter | Format example |
|---|---|---|
| `variant` | your pseudonym, or `demo` | `"K7QX-2M4P"` |
| `min_password_length` | shortest password the registration form accepted | `6` |
| `weak_staff_username` | the staff account whose password is in the word list | `"jdoe"` |
| `session_cookie_name` | the session cookie's name | `"sessionid"` |
| `staff_notice_code` | the code on the staff dashboard | `"CW-STAFF-ABCD-1234"` |
| `largest_gift_receipt` | receipt number of the largest gift | `100123` |
| `largest_gift_donor_email` | e-mail on that receipt | `"name@example.org"` |
| `largest_gift_amount` | its amount in dollars | `1234.5` |
| `injectable_path` | the URL path with the injection | `"/search"` |
| `injectable_parameter` | the injectable parameter | `"term"` |
| `hidden_table` | the table the site never shows | `"secret_table"` |
| `hidden_table_code` | the `CW-AUDIT-…` code in it | `"CW-AUDIT-ABCD-1234"` |
| `staff_account_count` | number of staff accounts | `7` |
| `error_source_path` | the application source file shown in the error page | `"/srv/site/main.py"` |

*Format examples are made up; they are not hints.* Validate before submitting:

```bash
cyberlab-findings validate /work/findings.json
```

## 10. Guided questions

Answer in your report, with the request or command that shows each answer.

1. What did your site map show? Which pages and parameters accept input, and which require a role?
2. What is the minimum password length, and how does that compare with NIST SP 800-63B? Which staff account fell to the word list, and what could an attacker do with it?
3. What is in the session cookie? Name three separate problems with it (protection, lifetime, logout).
4. How did you obtain staff access without a password? What did the dashboard reveal?
5. Explain the receipt IDOR. How many receipts could one ordinary donor read, and what personal data do they contain?
6. What did the error page reveal, and how did that help your other tests?
7. Show the injection step by step: the error, the true/false test, the UNION. Why does the UNION need exactly four columns?
8. What is the hidden table, what does it hold, and how many staff accounts are there?
9. Rate each of the five weaknesses (Critical / High / Medium / Low) with one sentence of justification each. Map each to an OWASP Top 10 (2021) category.
10. Which of your actions are visible in each log? What would a defender need to notice you?
11. Show your fix (the diff), the failed attack and the working search. Why does a parameterised query stop injection where escaping quotes by hand might not?
12. **[Grad]** In what order should Cedarwick fix the five weaknesses, and why? Which single change removes the most risk?

## 11. Independent challenge (optional)

1. **One-shot audit.** Write a Python script (the workstation has `requests`) that reproduces your five findings from a fresh account and prints a one-line verdict for each. Keep within the rules (one guess per word per account).
2. **Blind injection.** Without using `UNION` or reading the error page, extract the first character of the hidden code using only true/false searches (a result count of 0 or more). How many requests did it take?
3. **Session fix prototype.** In a copy of `app.py`, replace the cookie with Flask's signed session (`flask.session` and a secret key) and show that a forged cookie is rejected. (Do not submit this as your Part G fix.)
4. **[Grad]** Lab 4 preview: from the three logs alone, write a timeline of your own assessment as if you were the incident responder who found it.

## 12. Required deliverables

| File | What it is | Graded by |
|---|---|---|
| `work/findings.json` | Structured answers (Part H) | Auto-checker (40 points) |
| `Lab3-Report-<pseudonym>.pdf` | Assessment report (outline below), including section 10 | Instructor rubric (60 points) |
| `work/fix.diff` | Your Part G patch | Rubric |
| `work/case-notes.md` | Test log with times and commands | Supports the report |
| `work/authorized-use.md` | Your signed agreement | Required |
| `work/lab3-check.json` | Created by `verify`; run it again at the end | Required |

**Report outline** (undergraduate 6–9 pages; graduate 9–14 pages):

1. **Executive summary** for the director: overall risk, the two most urgent fixes, and whether the site should relaunch as is.
2. **Scope, authorisation and method:** what you tested, rules followed, tools.
3. **Findings**, one section each: description, affected page and parameter, steps to reproduce (requests), evidence (screenshots or output), impact, risk rating, OWASP category, recommended fix.
4. **Remediation performed:** the SQL injection fix, the diff, the re-test (attack fails, feature works).
5. **Logging and detection** (Part F). **[Grad]** with your detection rules.
6. **Prioritised recommendations.**
7. **Appendix:** request log from your case notes.

## 13. Submission instructions

1. `cyberlab-findings validate /work/findings.json` in the workstation.
2. On your computer: `git diff labs/lab3-webapp-assessment/app/app.py > labs/lab3-webapp-assessment/work/fix.diff`.
3. `docker compose run --rm verify` once more so `lab3-check.json` is current.
4. Upload the report PDF, `findings.json`, `fix.diff`, `case-notes.md`, `authorized-use.md` and `lab3-check.json` to the LMS.
5. **Do not** upload the logs, `cookies.txt` or any donor data beyond the three records quoted in your report.

Your site's data is unique to your variant; answers copied from someone else will not match it. Follow your course syllabus on AI tools.

## 14. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `[FAIL] authorized-use` | Agreement not signed, or `I AGREE` not on its own line | Re-open `work/authorized-use.md`; fill `Name:` and type `I AGREE` on the last line; save as plain text |
| `[FAIL] http:site … unreachable` | The site is not running yet | `docker compose up -d`, wait for "healthy" in `docker compose ps`, retry |
| `docker compose ps` shows a service restarting or exited | Start-up problem | `docker compose logs <service> --tail 30` and tell your instructor |
| Browser cannot open `127.0.0.1:8080` | Stack not started, or another program uses port 8080 | `docker compose ps`; stop the other program; do **not** change the port binding to another address |
| `/receipts/x` returns `302` instead of an error | You are not logged in | Log in as a donor first (Part A) and use the cookie jar `-b $JAR` |
| `/staff/...` redirects to `/staff/login` | Your staff cookie is wrong | Re-check the JSON you encoded; `kind` must be the staff value and `id` an existing staff ID |
| `UNION` query returns an SQL error | Wrong number or type of columns, or missing `-- ` at the end | Four columns: number, text, text, timestamp (`now()` works for the last); end with `-- ` (dash dash space) |
| After your fix, every search fails | Syntax error in `app.py` | `docker compose logs app --tail 20`; fix the error; `docker compose restart app` |
| You want a fresh site | Data changed during testing | `docker compose down -v`, then `docker compose up -d` (this deletes the site's data and logs) |
| `verify` fails `docker-memory` | Docker has under 3 GB | Docker Desktop → Settings → Resources → Memory = 4 GB |

## 15. Cleanup instructions

```bash
exit                                          # leave the workstation
docker compose down -v                        # stop the site and delete its data and logs
git checkout labs/lab3-webapp-assessment/app/app.py    # optional: restore the vulnerable code
unset CYBERLAB_EVIDENCE
```

Keep the images if you will do Lab 4. `docker compose run --rm reset` gives you fresh templates (your old work is moved to `work/.backup/<timestamp>/`).

## 16. Reflection questions

1. Which weakness surprised you most, and why would its developer not have noticed it?
2. Two weaknesses chained together gave you far more than either alone. Which ones, and what does that teach you about rating risk?
3. Where exactly did you stop yourself because of the rules of engagement? How would that decision look in a real engagement?
4. Your fix took a few lines. Why do weaknesses like this still reach production?
5. Which of your actions would a careful defender have noticed first, and in which log?
