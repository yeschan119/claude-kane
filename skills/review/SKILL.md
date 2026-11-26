---
name: review
description: Use to inspect a branch's or PR's changes before merge. Reads the merge-base diff along four axes — intent·quality·layer contract·data — and gives a net-gain verdict. Read-only.
argument-hint: "[branch | PR number] [base branch]"
---

# /kane:review — change review (read-only)

Arguments: `$ARGUMENTS`

## 1. Fix the target
- Given a branch, use that branch; given a PR number, `gh pr view <number> --json headRefName,baseRefName`; otherwise the current branch.
- If no base is given, use the PR's base; failing that, the remote default branch (`git symbolic-ref refs/remotes/origin/HEAD`).
- Set the baseline with `MB=$(git merge-base <base> <branch>)` and look only at `git diff $MB..<branch>`. Do not change the checkout.

## 2. Inspect
Pass `{branch, base, MB, changed file list, commit log, original request}` to the `kane:reviewer` agent.
If the change is small (3 files or fewer), main reviews it directly by the same criteria.

## 3. Report

| Grade | Meaning |
|---|---|
| 🔴 | merging causes outage·data corruption·security problem |
| 🟠 | wrong behavior·high regression likelihood |
| 🟡 | maintainability·rule violation |
| ⚪ | taste·trivial |

After the findings table (`Grade · File:line · Problem · Evidence · Suggested fix`), write a one-sentence verdict, in the user's language.
Base the verdict on **net gain**, not on whether defects exist: does this change leave things better than before merge, is there any 🔴, and what does reverting cost.
Distinguish "do not merge" from "mergeable, N fixes remaining". Fix code or comment on the PR only when the user asks.
