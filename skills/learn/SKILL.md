---
name: learn
description: Extracts the user's corrections and pushback from this session into lesson blocks and appends them to the project's .claude/lessons.md. Use for requests like "record what we learned", "save a lesson", "log feedback" / "배운 거 기록", "교훈 남겨", "피드백 기록".
argument-hint: "[topic] (if omitted, inferred from the session)"
---

# /kane:learn — accumulate lessons

Topic: `$ARGUMENTS`

The kane hook injects `.claude/lessons.md` automatically at session start. Lessons accumulated here change behavior in the next session.

## 1. Find corrections
Find the points in this session where the user corrected, pushed back, or showed frustration (in any language — e.g. "no", "that's not what I meant", "again", "why did you do that", repeating the same request, telling you to revert a result).
**If there are none, write nothing and report that.** Do not invent lessons.

## 2. Numbering — measure from the file
```bash
grep -oE '^## L[0-9]+' .claude/lessons.md 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1
```
Add 1 to the result. If the file doesn't exist, start at L1 and write `# Project Lessons` as the first line.

## 3. Block format (append to the end of the file only)
Write the block content in the user's language; keep the `## L{number}` heading format.
```markdown
## L{number} — {one-line summary} ({YYYY-MM-DD})
- **Situation**: what task was underway and what went wrong
- **Instruction**: what the user actually said (verbatim, not paraphrased)
- **Lesson**: what to do differently next time in the same situation — generalized so it prevents recurrence
- **Applied**: which procedure·file·command changes and how
```

## 4. Rules
- Never change a single character of existing blocks. Do not renumber them.
- If the same lesson already exists, don't create a new one; report its number.
- Do not record passwords·tokens·personal data.
- Report: the added number and summary, and show via `git diff --stat .claude/lessons.md` that only lines were added. Get commit approval separately.
