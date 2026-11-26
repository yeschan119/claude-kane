---
name: verify
description: Use after finishing an implementation, bug fix, refactor, or config change and before saying "done". Confirms input·output·exceptions·logs·regression with real execution evidence and rules PASS/FAIL/INCOMPLETE.
argument-hint: "[what to verify]"
---

# /kane:verify — post-implementation verification

Target: `$ARGUMENTS` (if empty, this session's changes)

This is the closing step that turns "should work" into "verified". Do not redesign.
If the change is large or needs separation from the implementing context, hand it to the `kane:verifier` agent.

## 1. Fix the scope
- Use `git status`·`git diff --stat` to separate files changed this time from files that were already dirty.
- Restate the original request and acceptance criteria in 1–2 sentences.

## 2. Check items

| # | Item | What to check |
|---|---|---|
| 1 | Input | normal values · empty/None · boundary values · wrong type·format |
| 2 | Output | return shape·key names match consumer expectations; shape of an empty result |
| 3 | Exceptions | failure paths handled, not swallowed, message reveals the cause |
| 4 | Logs | failure paths carry context; no sensitive data |
| 5 | Regression | existing normal cases you didn't change still behave the same (before/after comparison) |
| 6 | Consumers | other callers of this code don't break with it (search call sites) |

## 3. Run
- Find and run the repo's test·lint·build·run commands (README·package.json·Makefile·CI config). **Do not invent commands that don't exist.**
- Keep commands and their actual output as evidence. A path that only passed static checks is "unverified".
- Construct at least 1 counterexample (empty input·boundary value·failure response). Keep verification scripts in the scratchpad and don't commit them.
- Verification that needs approval (production DB·remote server·deployed environment) is not done directly; report that it is needed.

## 4. Verdict · report

| Verdict | Condition |
|---|---|
| PASS | acceptance criteria and key counterexamples actually run and passed |
| FAIL | defect·regression confirmed — attach the raw output |
| INCOMPLETE | key verification remains due to missing environment·approval·data — what couldn't be done and why |

Report as a `# · Item · Expected · Result · Status` table + a one-sentence verdict + remaining risks, written in the user's language.
Fixing a failure to make it pass is not verification. If passing requires changing an existing test assertion, stop and report.
