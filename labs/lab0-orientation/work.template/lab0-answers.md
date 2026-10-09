# Lab 0 — Answer Sheet

Evidence variant: `demo` (Lab 0 uses one shared practice dataset)

Answer in your own words. Paste the **exact command** you used under each answer.

## Part A — Docker basics
1. In one or two sentences, what is the difference between an *image* and a *container*?
2. What architecture did `verify` report (for example `aarch64` or `x86_64`)? What does that tell you about your computer?
3. How much memory does Docker have available, according to `verify`?

## Part B — Navigating evidence
4. How many files are in `/evidence` (including subfolders)? Command:
5. What does the `file` command say `documents/report.txt` really is? Why can't you trust a file extension?
6. What is the name of the file inside `documents/report.txt`, and how did you list it without extracting it to `/evidence`?

## Part C — Searching logs
7. How many failed login attempts appear in `logs/auth.log`? Command:
8. Which IP address made them? Is that address on the shop's local network? How can you tell?
9. List the usernames that were tried and how many times each.

## Part D — Hashing and integrity
10. Run `sha256sum -c MANIFEST.sha256` inside `/evidence`. Result?
11. Run `sha256sum -c transfer/sender_hashes.sha256` inside `/evidence`. Which file fails?
12. Compare the two results. What is the most likely explanation, and what would you write in your case notes? (Hint: look at the numbers inside the failing file.)

## Part E — Read-only evidence
13. Paste the error you got when you tried to create a file in `/evidence`. Why is this protection important in forensics?

## Part F — Troubleshooting drill
14. For each of the three staged problems, paste the error message and explain the fix in one sentence.

## Reflection
15. Which step was hardest, and what would you do differently next time?
