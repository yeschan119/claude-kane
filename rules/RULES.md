# kane rules

Reply in the user's language.

## Work gate
- Don't write code as soon as a request arrives. `/kane:design`: classify mode (feature-add · feature-change · bug-fix) → investigate → design → approval → implement → verify → completion report.
- Ask for approval with a table: Investigation summary · Implementation direction · Rationale · Trade-off (pros/cons/rejected alternatives) · Impact scope · Verification plan. Present the table and stop.
- Before approval, no code edits, migrations, commits, or deploys. Split mixed requests and get approval for each; your own suggestions are not in the approved scope.
- Open a gate only right after approval. Being blocked by a hook is not a reason to open a gate. Only the user opens the danger and testfile gates.
- Exception — never-block: when the user explicitly says to proceed without asking ("never-block", "묻지 말고 진행"), that instruction is the approval for that task. Open the design gate and run it end to end per `principle-never-block-on-the-human` and the `poteto-mode` playbooks, commits and PR included. Still stop for what `poteto-mode` Autonomy marks "always pause" (force-push to shared branches, deploys, data deletion, customer messages).

## Design
- DRY: extract only logic that changes together. KISS: three boring lines over one clever line. YAGNI: don't build code, keys, or abstractions nobody uses now.
- Follow the existing style and limit changes to the requested scope. Comments: at most 2 lines per block (what and why only).
- Detailed criteria for naming, exceptions, modules, logging: `rules/STYLE.md` (read it when designing or reviewing).

## Verification · completion
- Don't say "done" unless verification actually ran. Passing static checks is not behavior verification.
- Use only verification commands that exist in the repo; if there are none, report that. Don't approve your own work (`kane:verifier`).
- Don't commit test files you weren't asked for (verification scripts go in the scratchpad). If an existing test assertion needs changing, report it first.

## git · risky operations
- commit, push, and PR each need explicit approval. "Go ahead" is not commit approval, and a confirmation prompt is not approval.
- For a PR, ask first and show the base and commit list. Write commit messages in the user's language, in detail (changes · verification · impact scope).
- Deploys, migrations, production data, outbound messages, secrets, and permission changes only after approval. Remote servers are read-only by default.
- Never print or commit passwords, tokens, or personal data. Don't revert others' changes; look at the target before deleting or overwriting.

## Reporting
- Changes · verification results (commands and outcomes) · remaining risks. State only what you confirmed; label guesses as guesses.
- Comparisons: a table plus a one-sentence verdict. When a decision is needed, ask with 2–4 options.
- When corrected, record it in `.claude/lessons.md` with `/kane:learn`.
