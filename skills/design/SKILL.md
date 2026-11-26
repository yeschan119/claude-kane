---
name: design
description: Use before writing code when a request changes code (feature-add, feature-change, bug-fix). Triggers — "add", "build", "change", "fix", "doesn't work", "error", "bug", "implement" / "추가해", "만들어", "수정해", "바꿔", "고쳐", "안 돼", "에러 나", "버그", "구현해". Classify mode → investigate → design → approval gate → implement → verify → completion report. Also return to this procedure when a kane hook blocks an edit. Arguments on/off/status operate the design gate.
argument-hint: "<task request> | on [minutes] | off | status"
---

# /kane:design — implement after design approval

Arguments: `$ARGUMENTS`

## 0. Parse arguments
- If the first token is `on`·`off`·`status` followed by nothing but a number, it is a **gate operation**. Run `design <on [minutes]|off|status>` with the gate command from the session context and relay only its output. Do not chain it with other commands via `&&`.
- Otherwise it is a **task request**. Follow the procedure below. With no arguments, show only the mode table and usage, then wait for a request.

## 1. Procedure

| Step | What to do | Owner |
|---|---|---|
| ① Classify | One of feature-add·feature-change·bug-fix + rationale (quote the request). If ambiguous, ask once with options | main |
| ② Investigate | Entry point·call path·related files (max 5)·duplicate implementations·consumers·existing verification means | `kane:investigator` (main does it directly if 2–3 files) |
| ③ Design | Per-mode deliverables | `kane:designer` |
| ④ Approve | Output the template below, then **stop and wait** | main |
| ⑤ Implement | Right after approval, open the gate with `design on 240` and implement only the approved scope | main |
| ⑥ Verify | Run the approved verification plan | `kane:verifier` (separate lane) |
| ⑦ Done | Completion report, then `design off` | main |

Classification: make something broken work = bug-fix · make something working behave differently (including formulas) = feature-change · build something new = feature-add.
If the mode is clear, don't ask; run ②③ and get approval once at ④.

## 2. Approval gate template (④ — required before writing code)

Write the template in the user's language.

```
### ④ Approval gate — <mode>
> <this direction in one sentence>

| Item | Content |
|---|---|
| Investigation summary | |
| Implementation direction | |
| Rationale | existing structure·maintainability·testability·DRY/KISS/YAGNI |
| Trade-off | pros / cons / rejected alternatives |
| Impact scope | changed files · API · DB · other consumers |
| Verification plan | only commands that actually exist in the repo. If none, "none" |

OK to proceed in this direction?
```

Write "N/A" instead of leaving a cell blank. Only **the exact direction presented** is approved — do not widen scope during implementation.

## 3. Completion report (⑦)

Write the report in the user's language.

```
### ⑦ Done — <one-line result>
| Item | Content |
|---|---|
| Changed files | |
| Verification | command run → result (what couldn't be run and why) |
| Impact scope | |
| Remaining risks | if none, "no known remaining risks" |
```

If verification wasn't run, don't write "done". Commit·push·PR do not come with the completion report — get each approved separately.

## 4. Gate rules
- The gate opens at only two points: right after ④ approval (Claude opens it and the user allows it in the confirmation prompt), or when the user runs `/kane:design on [minutes]`.
- Even if opened via bypass, still record the one-line ① classification before working. Run `design off` when finished.
