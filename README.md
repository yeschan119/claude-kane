# claude-kane

> A Claude Code harness: design-approval gate, destructive-command guard, verification & review workflow, and lesson memory — plus pstack's engineering skills, playbooks and principles, run behind the same approval gate.

Install it once and every repo gets the same development rules and safety rails. Unlike feature-heavy orchestration plugins, it keeps only what you actually use every day — **DRY · KISS · YAGNI**.

## Install

```
/plugin marketplace add yeschan119/claude-kane
/plugin install kane@claude-kane
```

Requirements: `python3` (3.8+), `git`. No extra packages.

To ship it with a team repo, add the following to `.claude/settings.json`. Trusting the folder brings up the install prompt.

```json
{
  "extraKnownMarketplaces": {
    "claude-kane": { "source": { "source": "github", "repo": "yeschan119/claude-kane" } }
  },
  "enabledPlugins": { "kane@claude-kane": true }
}
```

## What's inside

| Type | Name | What it does |
|---|---|---|
| Rules | `rules/RULES.md` | Work gates, DRY·KISS·YAGNI, verification & done criteria, git & risky operations, reporting, reply language (the user's). Injected at session start |
| | `rules/STYLE.md` | Detailed naming, structure, exception and logging standards. Not injected; read by designer and reviewer |
| Skills | `/kane:design` | Mode classification → investigation → design → **approval gate** → implementation → verification → completion report. `on/off/status` controls the gate |
| | `/kane:verify` | Checks input, output, exceptions, logs and regressions with execution evidence and returns PASS / FAIL / INCOMPLETE |
| | `/kane:review` | Inspects branch/PR changes for intent, quality, layering and data; verdict based on net change (read-only) |
| | `/kane:learn` | Accumulates user corrections in `.claude/lessons.md`. Auto-injected in the next session |
| | `/kane:danger` | Turns the dangerous-command gate on/off (user only) |
| | `/kane:testfile` | Turns the test-file commit gate on/off (user only) |
| | `/kane:hud` | Turns the HUD statusline on/off: `branch` / `Model · 5h·wk usage · session · ctx%`. Backs up and restores the previous `statusLine` (user only) |
| | `/kane:poteto-mode` and 58 more | pstack's engineering skills, playbooks and principles — see [Engineering skills](#engineering-skills-from-pstack) |
| Agents | `investigator` · `designer` · `verifier` · `reviewer` | Investigation · per-mode design · separate-lane verification · review |
| | `poteto-agent` · `comment-sicko` | pstack delegate wrapper · read-only comment reviewer |
| Hooks | `session_start.py` | Injects rules, gate commands and project lessons |
| | `bash_guard.py` | Blocks irreversible commands and test-file commits, enforces `gh pr create --base`, asks for confirmation on commit, push, PR, rm, sudo, package installs and migrations |
| | `design_gate.py` | Blocks edits to code files inside a git repo until approval (`.md`, `.claude/`, `docs/` excluded) |
| Statusline | `statusline.py` · `hud.py` | HUD renderer from Claude Code's statusline stdin (no token or network access) · `/kane:hud` on/off |

## How it works

**Design gate** — locked by default. Claude follows the `/kane:design` procedure, shows a design, gets approval, then opens the gate. The command that opens the gate always triggers a confirmation prompt. For a simple fix, open it yourself with `/kane:design on 30` and lock it again with `/kane:design off` when done.

**Block vs. confirm**

| Level | Command | How to allow |
|---|---|---|
| Block | `push --force`·`push +ref`, `reset --hard`, `clean`, `commit --amend`, branch/tag deletion, `checkout --`/`restore`, `rm -rf`, `docker down -v`·`prune`, `DROP`/`TRUNCATE` | `/kane:danger on [min]` |
| Block | Test files (`test_*.py`, `*_test.py/go`, `*.test/spec.[jt]s(x)`, `tests/`) included in a commit | `/kane:testfile on [min]` |
| Block | `gh pr create` without `--base` | Specify `--base` |
| Confirm | `git commit/push/merge/rebase/reset/switch/checkout/pull…`, `gh pr create/merge`, `docker up/down…`, `rm`, `chmod`, `sudo`, package installs, migrations | Approve in the confirmation prompt |

Decisions are based on where a command **appears**. Text like `rm -rf` inside a commit message or heredoc body is not blocked just for being there.

**Gate state** is stored in `~/.claude/kane/gates/`, not in the repo, and relocks automatically once it expires (default 15–30 min, max 480 min). So nothing is left behind in the repo.

**Lessons** accumulate in the project's `.claude/lessons.md`, and the latest 200 lines are injected each session. Commit this file to share it with your team.

## Engineering skills (from pstack)

kane bundles every skill, playbook, principle and agent from [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT, Lauren Tan), taken from its Claude Code build. Names are kept; only the plugin prefix changed (`/pstack:x` → `/kane:x`, `setup-pstack` → `setup-models`). Not included: the Cursor-only `automations/benny` pack and the bundled test suites of `statechart` and `poteto-mode/scripts/watch-pr`.

**Approval still comes first.** `/kane:poteto-mode` and its playbooks stop at the kane ④ approval gate and ask for commit, push and PR one by one. Say "never-block" / "묻지 말고 진행" to run a task end to end the pstack way (irreversible actions still stop). See `rules/RULES.md`.

Start with `/kane:poteto-mode <task>`. Model roles: `/kane:setup-models` (writes `~/.claude/rules/kane-models.md`). Cursor names are mapped by [`docs/harness/claude-code.md`](./docs/harness/claude-code.md); guide: [`docs/guide/`](./docs/guide/README.md).

<details>
<summary>Playbooks used by /kane:poteto-mode</summary>

| playbook | for |
|---|---|
| [investigation](./skills/poteto-mode/playbooks/investigation.md) | a read-only question. how does x work, why was y built this way, are we sure. |
| [bug fix](./skills/poteto-mode/playbooks/bug-fix.md) | reproduce a defect, root-cause it, and fix with runtime evidence. |
| [perf](./skills/poteto-mode/playbooks/perf-issue.md) | trace a measured slowness and improve it against a baseline. |
| [hillclimb](./skills/poteto-mode/playbooks/hillclimb.md) | sustained, scientific improvement of one metric against a target, looping hypotheses with before/after measurement and one commit per accepted win. |
| [runtime forensics](./skills/poteto-mode/playbooks/runtime-forensics.md) | diagnose a live symptom (leak, idle-cpu spin, glitch) from instrumentation. |
| [trace forensics](./skills/poteto-mode/playbooks/trace-forensics.md) | diagnose a captured profiling artifact (cpuprofile, trace, spindump, heap snapshot). |
| [feature](./skills/poteto-mode/playbooks/feature.md) | new or changed behavior, built from a named data shape. |
| [refactoring](./skills/poteto-mode/playbooks/refactoring.md) | a behavior-preserving change to structure or shape. |
| [prototype](./skills/poteto-mode/playbooks/prototype.md) | a throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it. |
| [visual parity](./skills/poteto-mode/playbooks/visual-parity.md) | pixel-exact ui equivalence between two implementations. |
| [authoring a skill](./skills/poteto-mode/playbooks/authoring-a-skill.md) | writing or editing a SKILL.md. |
| [eval](./skills/poteto-mode/playbooks/eval.md) | test how a skill or prompt change affects agent behavior, blinded. |
| [babysit](./skills/poteto-mode/playbooks/babysit.md) | drive a pr or a stack to merge-ready: conflicts, review threads, ci. |
| [shipping](./skills/poteto-mode/playbooks/shipping.md) | independently verify a green stack, then land the contiguous verified run bottom-up through github by default or origin when available. |
| [autonomous run](./skills/poteto-mode/playbooks/autonomous-run.md) | drive a long task to completion without stopping. |
| [autopilot-full](./skills/poteto-mode/playbooks/autopilot-full.md) | run independent prs to merged with one owner per pr. a swarm verifies each code-ready head, and every later change to the patch gets a fresh check. |
| [autopilot-stack](./skills/poteto-mode/playbooks/autopilot-stack.md) | autopilot-full without the merge. build and verify prs for the operator to review and land, stacking a pr only on a pr it builds on. |
| [session pickup](./skills/poteto-mode/playbooks/session-pickup.md) | resume or take over a prior agent's in-flight work. |
| [pause safely](./skills/poteto-mode/playbooks/pause-safely.md) | suspend in-flight work cleanly so it can be resumed later. |
| [multi-phase plan](./skills/poteto-mode/playbooks/multi-phase-plan.md) | work that spans phases or stacked PRs. |
| [worktree cleanup](./skills/poteto-mode/playbooks/worktree-cleanup.md) | reclaim disk by pruning merged or abandoned worktrees and stale ios simulators, safety-gated. |
| [opening a pr](./skills/poteto-mode/playbooks/opening-a-pr.md) | open a ready pr from small ordered commits with a conventional commits title and a briefing-style body. invoked at the end of every other playbook. |

</details>

<details>
<summary>Skills</summary>

| skill | use it when |
|---|---|
| [`/kane:poteto-mode`](./skills/poteto-mode/SKILL.md) | default entry point for any non-trivial task. |
| [`/kane:poteto-help`](./skills/poteto-help/SKILL.md) | you're new to kane, or unsure which skill, playbook, or principle fits. finds out what you're trying to do, answers that part, and hands you a prompt to type. runs only when you type `/poteto-help`. |
| [`/kane:in-your-own-words`](./skills/in-your-own-words/SKILL.md) | you want the agent to play back your goal and the problem before it starts. runs only when you type `/in-your-own-words`. |
| [`/kane:sharpen`](./skills/sharpen/SKILL.md) | you want a prompt made deeper, not bigger, before you send it: what a top professional would do that you didn't ask for, the raw material they'd start from, their methods and tools, and an outside check that the result is right. hands back the rewritten prompt, which asks the agent to prototype any choice an experiment can settle and leaves product and preference choices to you. doesn't do the task. runs only when you type `/sharpen`. |
| [`/kane:reframe`](./skills/reframe/SKILL.md) | you can't name what you're building, so you can't ask an agent for it clearly. starts from your files and your own words. if they could describe more than one problem, it lists the two or three it could be, with the sign that tells each apart, and picks the likeliest. then it gives 8 to 12 expert terms ranked by how much they'd change what you build, each tied to the part of your description it names and to a real project whose link it checked. borrows terms from 2 or 3 neighboring fields that solved the same problem under other names, says where each analogy breaks, then rewrites your description with the new words. runs only when you type `/reframe`. |
| [`/kane:how`](./skills/how/SKILL.md) | you want a walkthrough of how a subsystem works. |
| [`/kane:why`](./skills/why/SKILL.md) | you want to know why something was built this way. answers from the record, not the code: the commits and pr discussions that introduced it and each later change, and other sources when that trail is thin. cites what the authors wrote, marks its own inferences, and says what the record does not answer. |
| [`/kane:recall`](./skills/recall/SKILL.md) | you're starting or resuming work and want your recent context on a topic rebuilt from your own chat history and the shared record, handed back as a tight current-state brief. |
| [`/kane:ketchup`](./skills/ketchup/SKILL.md) | you want what changed in this chat since your last message, in plain words and small visuals, with every item waiting on you listed and decidable from the reply alone, even when that makes the reply long. |
| [`/kane:ketchup-video`](./skills/ketchup-video/SKILL.md) | you want the `/ketchup` catch-up as a short subtitled video of slides, with the calls waiting on you as text under it. |
| [`/kane:blast-radius`](./skills/blast-radius/SKILL.md) | you have a small-looking change and want to know what else it could break, with the one fact it's safe because of proven by running code, not asserted. |
| [`/kane:architect`](./skills/architect/SKILL.md) | you're about to write code that crosses a function boundary and want the caller's usage, types, and module shape settled first. |
| [`/kane:arena`](./skills/arena/SKILL.md) | you want N parallel attempts at the same thing, then to grab the best parts of each. |
| [`/kane:swarm`](./skills/swarm/SKILL.md) | you want N parallel workers across different slices or races, then one aggregated report. |
| [`/kane:interrogate`](./skills/interrogate/SKILL.md) | you have a diff and want different models to try to break it, keeping only findings a run proves. |
| [`/kane:automate-me`](./skills/automate-me/SKILL.md) | you want your own `-mode` skill, drafted from how you've actually worked. |
| [`/kane:make-bot-ui`](./skills/make-bot-ui/SKILL.md) | you want a page or dashboard whose buttons wake a Grok Bot over a webhook, including the sender-key handoff and Tailscale. |
| [`/kane:setup-models`](./skills/setup-models/SKILL.md) | you want to pick which models kane uses per role. detects your models and writes a config rule. |
| [`/kane:reflect`](./skills/reflect/SKILL.md) | a long task landed and you want the recipe captured as a skill edit. |
| [`/kane:correct`](./skills/correct/SKILL.md) | you keep correcting agents for the same mistakes. mines history for mistake classes, fixes each at the highest level that works (architecture, then types, lint, and ci, then tests, with docs last), and keeps a table pairing each rule with what enforces it. |
| [`/kane:teach`](./skills/teach/SKILL.md) | you want to actually understand a change or subsystem, not just have it summarized. runs how + why and weaves one plain explanation, built up diagram by diagram. |
| [`/kane:tdd`](./skills/tdd/SKILL.md) | you're fixing a bug and there's a cheap local test path. write the failing test first, then the fix. |
| [`/kane:benchmark-checklist`](./skills/benchmark-checklist/SKILL.md) | you ran a benchmark or measured a speedup or regression. vets the number (limiter, tuning, errors, repeat runs, end-to-end relevance) before you report or act on it. |
| [`/kane:no-comments`](./skills/no-comments/SKILL.md) | strip comments before review; spawns Comment Sicko, fixes accepted findings, offers encodings for claimed constraints. |
| [`/kane:typescript-best-practices`](./skills/typescript-best-practices/SKILL.md) | you're reading or editing typescript. grounds the type-system-discipline principle in syntax. |
| [`/kane:figure-it-out`](./skills/figure-it-out/SKILL.md) | no bundled playbook fits. designs a rigorous, auditable playbook for the task. |
| [`/kane:show-me-your-work`](./skills/show-me-your-work/SKILL.md) | you want a reviewable decision trail. logs decisions to a tsv you can commit. |
| [`/kane:create-verification-skill`](./skills/create-verification-skill/SKILL.md) | your project has no scripted way to prove app behavior. generates a project-local verify skill with a feature map, for any language or platform. |
| [`/kane:maintain-verification-skill`](./skills/maintain-verification-skill/SKILL.md) | your verify skill's feature map has drifted from the app. source wave + one live pass, at most one PR of proven corrections. |
| [`/kane:create-formal-verification-skill`](./skills/create-formal-verification-skill/SKILL.md) | tests can't reach the case that breaks a race, retry, state machine, parser, or unsafe code. verifies one property with the tool that fits and generates a project-local skill to recheck it on every change. |
| [`/kane:maintain-formal-verification-skill`](./skills/maintain-formal-verification-skill/SKILL.md) | code your formal verification covers has changed since it was last checked. updates the model, harness, or properties to match the code, reruns, and says whether each failure is drift in the verification or a bug in the code. |
| [`/kane:statechart`](./skills/statechart/SKILL.md) | someone who owns the behavior needs to see it, not read a spec. checks a tla+ model, draws what the user sees as a mermaid statechart, marks each state that breaks a rule, and gives the shortest path to each one. |
| [`/kane:unslop`](./skills/unslop/SKILL.md) | you're cleaning up writing. removes AI tells. |
| [`/kane:bro`](./skills/bro/SKILL.md) | you want the last message restated in plain human language, no jargon. |
| [`/kane:technical-writing`](./skills/technical-writing/SKILL.md) | layered doc standard (Diátaxis + Google developer style + STE + Global English) for docs, RFCs, readmes, PR descriptions, commit messages. |

</details>

<details>
<summary>Principles</summary>

| principle | group | rule |
|---|---|---|
| [laziness-protocol](./skills/principle-laziness-protocol/SKILL.md) | core | Bias toward deletion and the smallest change that solves the problem. |
| [foundational-thinking](./skills/principle-foundational-thinking/SKILL.md) | core | Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious. |
| [redesign-from-first-principles](./skills/principle-redesign-from-first-principles/SKILL.md) | core | Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on. |
| [attack-the-premise](./skills/principle-attack-the-premise/SKILL.md) | core | Apply when two or more fixes that share one premise have failed the same gate. Write the premise down and test it directly before you write another fix that assumes it. |
| [subtract-before-you-add](./skills/principle-subtract-before-you-add/SKILL.md) | core | Remove dead weight, redundant validators, and stub references first, then build on the simpler base. |
| [minimize-reader-load](./skills/principle-minimize-reader-load/SKILL.md) | core | Count layers between question and answer, and hidden state in the reader's head; collapse one-caller wrappers and shrink mutable scope. |
| [outcome-oriented-execution](./skills/principle-outcome-oriented-execution/SKILL.md) | core | Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; don't preserve smooth intermediate states with throwaway compatibility code. |
| [experience-first](./skills/principle-experience-first/SKILL.md) | core | Choose user delight over implementation convenience; ship fewer polished features over more rough ones. |
| [exhaust-the-design-space](./skills/principle-exhaust-the-design-space/SKILL.md) | core | Build 2-3 competing prototypes and compare side by side before committing. |
| [build-the-lever](./skills/principle-build-the-lever/SKILL.md) | core | Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun. |
| [model-the-domain](./skills/principle-model-the-domain/SKILL.md) | architecture | Encode the domain in a structure instead of scattered conditionals. |
| [boundary-discipline](./skills/principle-boundary-discipline/SKILL.md) | architecture | Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions. |
| [type-system-discipline](./skills/principle-type-system-discipline/SKILL.md) | architecture | Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, exhaust variants, derive from authoritative schemas. |
| [make-operations-idempotent](./skills/principle-make-operations-idempotent/SKILL.md) | architecture | Converge to the same end state regardless of partial prior runs. |
| [migrate-callers-then-delete-legacy-apis](./skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md) | architecture | Migrate callers and delete the old API in the same wave instead of preserving compatibility layers. |
| [separate-before-serializing-shared-state](./skills/principle-separate-before-serializing-shared-state/SKILL.md) | architecture | Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant. |
| [prove-it-works](./skills/principle-prove-it-works/SKILL.md) | verification | Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'. |
| [fix-root-causes](./skills/principle-fix-root-causes/SKILL.md) | verification | Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate. |
| [sequence-verifiable-units](./skills/principle-sequence-verifiable-units/SKILL.md) | verification | Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer. |
| [test-behavior-not-implementation](./skills/principle-test-behavior-not-implementation/SKILL.md) | verification | Apply when you write, change, or keep a test. Assert what the code's users can observe, so the test fails when that behavior breaks and keeps passing when only the internals change. |
| [explain-the-number](./skills/principle-explain-the-number/SKILL.md) | verification | Apply before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result. Find what limits it, and rule out that it measured something other than the work you think. |
| [guard-the-context-window](./skills/principle-guard-the-context-window/SKILL.md) | delegation | Route bulk to subagents; keep summaries in the main thread, not raw payloads. |
| [never-block-on-the-human](./skills/principle-never-block-on-the-human/SKILL.md) | delegation | Proceed, present the result, let the human course-correct after the fact; reserve confirmation for irreversible actions. |
| [encode-lessons-in-structure](./skills/principle-encode-lessons-in-structure/SKILL.md) | meta | Encode the rule as a lint, metadata flag, runtime check, or script instead of more text. |

</details>

Agents: `kane:poteto-agent` (delegate wrapper spawned by `poteto-mode`; reads it in full first) · `kane:comment-sicko` (read-only comment reviewer, used by `/kane:no-comments`).

## Session cost

| Item | Tokens | Measurement |
|---|---|---|
| Fixed per session | ~6,800 (estimate) | Sum of the two rows below; before pstack was added, `claude -p` measured ~2,200 (27,283 → 29,463) |
| └ Skill & agent list | ~5,600 | `claude --plugin-dir . plugin details kane` (0.1.5; was ~1,060 before pstack) |
| └ Rule injection (SessionStart) | ~1,200 | Only `RULES.md` is injected; agents read `STYLE.md` when needed. Grows by the size of `.claude/lessons.md` if present |
| Per invocation | 40 ~ 5,300 | Per skill/agent (see `plugin details`) |

## Release

The version lives in two places, `plugin.json` and `marketplace.json`, and they must match.

1. Bump `version` in both files together, then commit and push (if the version is unchanged, installs won't see an update)
2. `claude plugin validate .`
3. Check with `claude plugin tag . --dry-run`, then `claude plugin tag . --push` — this is rejected if the two versions differ
4. On the installed side: `/plugin marketplace update claude-kane` → `/plugin update kane@claude-kane` → restart

Tags are named `kane--v<version>`.

## Disabling

To disable it in a single repo, add `"enabledPlugins": { "kane@claude-kane": false }` to `.claude/settings.json`. To remove it completely, run `/plugin uninstall kane@claude-kane`.

## Recommended plugins

kane covers only rules and safety rails. Below are plugins worth pairing with it when needed. Each is installed separately.

<details>
<summary><b>superpowers</b> — development technique skills</summary>

Skills for brainstorming, writing and executing plans, TDD, systematic debugging, verification before completion, requesting and receiving code review, git worktrees, and parallel subagent work.

- Repo: [obra/superpowers](https://github.com/obra/superpowers)
- Install:
  ```
  /plugin install superpowers@claude-plugins-official
  ```

</details>

<details>
<summary><b>andrej-karpathy-skills</b> — behavioral guidelines to reduce LLM coding mistakes</summary>

A single guideline skill that reduces the LLM coding mistakes Andrej Karpathy pointed out (over-abstraction, out-of-scope edits, hidden assumptions, etc.). Lightweight.

- Repo: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
- Install:
  ```
  /plugin marketplace add forrestchang/andrej-karpathy-skills
  /plugin install andrej-karpathy-skills@karpathy-skills
  ```

</details>

<details>
<summary><b>playground</b> — interactive HTML playgrounds</summary>

Builds a single HTML file with a control panel and live preview. You can copy the result as a prompt and hand it back to Claude.

- Repo: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- Install:
  ```
  /plugin install playground@claude-plugins-official
  ```

</details>

<details>
<summary><b>oh-my-claudecode</b> — multi-agent orchestration</summary>

19 agents and 40 skills (autopilot, ralph, team, deep-interview, etc.). Use it to push large tasks through to completion automatically.

- Repo: [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- Install:
  ```
  /plugin marketplace add Yeachan-Heo/oh-my-claudecode
  /plugin install oh-my-claudecode@omc
  ```

</details>

<details>
<summary><b>eli5</b> — explanations pitched to the audience</summary>

A skill that explains topics, code or errors with vocabulary, analogies and depth adjusted to the audience — "to a 5-year-old", "to a manager", "to a senior developer". Triggers automatically on phrases like "ELI5" or "explain this to ~".

- Repo: [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5)
- Install (copy the skill folder):
  ```
  git clone https://github.com/DreambigOu/ELI5.git
  cp -r ELI5/skills/eli5 ~/.claude/skills/eli5
  ```

</details>

<details>
<summary><b>understand-anything</b> — turn a codebase into an interactive knowledge graph</summary>

Analyzes a codebase with multiple agents and builds a knowledge graph you can explore, search and query. Analyze with `/understand`, view the graph with `/understand-dashboard`, and use `/understand-chat`, `/understand-explain` and `/understand-onboard` for questions, file explanations and onboarding guides.

- Repo: [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)
- Install:
  ```
  /plugin marketplace add Egonex-AI/Understand-Anything
  /plugin install understand-anything
  ```

</details>

<details>
<summary><b>oh-my-mermaid</b> — the whole codebase as Mermaid architecture diagrams</summary>

Analyzes a codebase to generate Mermaid architecture docs (`.omm/`) and lets you browse the diagrams in a browser viewer. Generate with `/omm-scan` inside Claude Code and view with `omm view` in the terminal. Use `omm config language ko` for Korean docs.

- Repo: [oh-my-mermaid/oh-my-mermaid](https://github.com/oh-my-mermaid/oh-my-mermaid)
- Install (terminal):
  ```
  npm install -g oh-my-mermaid && omm setup
  ```

</details>

<details>
<summary><b>visual-skills</b> — writing AI video & image prompts</summary>

Two skills, `video` and `image`. Based on directing, camera and editing rules, they write copy-ready prompts in each model's syntax — Seedance, Kling, Veo, Nano Banana, GPT Image and more.

- Repo: [smixs/visual-skills](https://github.com/smixs/visual-skills)
- Install:
  ```
  /plugin marketplace add smixs/visual-skills
  /plugin install visual-skills@visual-skills
  ```

</details>

Things to watch when combining them:

- superpowers and oh-my-claudecode also have planning, verification and review procedures that overlap with kane's `/kane:design`, `/kane:verify` and `/kane:review`. Use only one side's procedure per task.
- oh-my-claudecode is heavy (lots of session context and hooks) and has autonomous execution modes. kane's hooks keep working and still block dangerous commands, but we recommend enabling it at project scope only in repos that need it.
- understand-anything and oh-my-mermaid scan the entire codebase, so they use a lot of tokens on large repos. Try them on a small repo first.

## Recommended skills

External skills that pair well with Claude. Each is installed separately; after installing, restart Claude Code or run `/reload-plugins`.

<details>
<summary><b>find-skills</b> — find and install the skills you need</summary>

Ask something like "is there a skill that does X?" and it searches the public skill directory ([skills.sh](https://skills.sh)), shows candidates, and installs the one you pick. Uses the Skills CLI (`npx skills`) under the hood.

- Repo: [vercel-labs/skills](https://github.com/vercel-labs/skills)
- Install:
  ```
  npx skills add vercel-labs/skills --skill find-skills
  ```
- Usage:
  - Ask Claude things like "find me a skill for handling PDFs" or "is there a skill for X".
  - Directly: `npx skills find <query>` to search · `npx skills add <owner/repo>` to install · `npx skills update` to update
  - Installs into the current project by default; add `-g` to install for your whole user account. For unfamiliar skills, review the contents first and install at project scope.

</details>

<details>
<summary><b>claude-mem</b> — memory across sessions</summary>

While you work, a separate agent records observations, and at the start of the next session a summary index is injected. Details are searched and loaded only when needed, saving tokens. Memory is stored locally in `~/.claude-mem`.

- Repo: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- Install (inside Claude Code):
  ```
  /plugin marketplace add thedotmack/claude-mem
  /plugin install claude-mem
  ```
  Or from the terminal: `npx claude-mem install`. Don't use `npm install -g claude-mem` — it installs only the library and doesn't register the hooks.
- Usage:
  - After installing, just work as usual; records build up automatically and memory is injected from the next session in the same project.
  - Ask something like "how did we fix that auth bug last time?" and the `mem-search` skill finds past records.
  - Browse records, sessions and settings at `/viewer` on the worker address printed at startup.
  - Installation asks you to log in and choose a memory provider (paid observer trial, your own API key, or an Anthropic plan). Anonymous usage telemetry is on by default; turn it off with `npx claude-mem telemetry disable`.
  - kane's `/kane:learn` explicitly records only lessons from user corrections, while claude-mem automatically records all of your work.

</details>

<details>
<summary><b>impeccable</b> — commands for polishing UI design</summary>

A design skill that helps avoid the generic look typical of AI-generated screens. Works best when you point it at an existing page or component to fix. Includes 24 commands and a design-check hook that runs automatically when UI files are edited.

- Repo: [pbakaus/impeccable](https://github.com/pbakaus/impeccable) · Docs: [impeccable.style/docs](https://impeccable.style/docs)
- Install:
  ```
  npx impeccable install
  ```
  The installer asks for project or global scope and whether to install the design hook. To add it as a plugin, run `/plugin marketplace add pbakaus/impeccable` and install from `/plugin`. Update with `npx impeccable update`.
- Usage:
  - Once per project, run `/impeccable init` → generates `PRODUCT.md`. To capture an existing design in `DESIGN.md`, use `/impeccable document`.
  - Format: `/impeccable <command> <target>`, e.g. `/impeccable critique the pricing cards`, `/impeccable polish settings`
  - Common commands: `critique` (UX score review) · `audit` (technical quality report) · `polish` (pre-launch finishing) · `bolder`/`quieter` (adjust intensity) · `harden` (errors, overflow, edge cases)
  - Enter just `/impeccable` for the full command list. Run `npx impeccable detect src/` from the CLI to check in CI as well.

</details>

<details>
<summary><b>frontend-design</b> — build new screens with character</summary>

An official Anthropic skill. When you build a new page or component, it has Claude settle on a design direction first (tone, typography, color, layout), producing polished production code instead of generic default designs.

- Repo: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- Install:
  ```
  /plugin install frontend-design@claude-plugins-official
  ```
- Usage:
  - No need to invoke it; it applies automatically when you ask for a frontend screen. E.g. "Build a SaaS landing page. Minimal and premium in tone."
  - Results improve when you also mention the mood, target users and constraints (framework, accessibility).
  - Use frontend-design for new screens and impeccable for polishing existing ones, so they don't overlap.

</details>

## Plugin commands

Use `claude plugin …` in the terminal and `/plugin …` inside Claude Code. Day to day, five are enough: `list`, `install`, `marketplace update`, `update`, `disable`.

<details>
<summary><b>For users — install & manage</b></summary>

| Command | What it does |
|---|---|
| `claude plugin list` | Installed plugins with version, scope, and enabled state |
| `claude plugin install <name>@<market>` (`i`) | Install. Scope via `-s user\|project\|local` |
| `claude plugin update <name>@<market>` | Update to the latest version. Takes effect after restart |
| `claude plugin uninstall <name>@<market>` (`remove`) | Remove |
| `claude plugin enable <name>` / `disable <name>` | Enable / disable (without removing) |
| `claude plugin configure <name>` | View and set plugin options |
| `claude plugin prune` (`autoremove`) | Clean up auto-installed dependencies no longer needed |
| `claude plugin restore-set-aside <name>` | Restore options/secrets set aside when an organization changes a marketplace source |

</details>

<details>
<summary><b>Marketplaces</b></summary>

| Command | What it does |
|---|---|
| `claude plugin marketplace add <source>` | Register. Source is a GitHub `owner/repo`, URL, or local path |
| `claude plugin marketplace list` | List registered marketplaces |
| `claude plugin marketplace update [name]` | Refresh catalogs. Omit the name to refresh all |
| `claude plugin marketplace remove <name>` (`rm`) | Unregister |

</details>

<details>
<summary><b>For developers — build & publish</b></summary>

| Command | What it does |
|---|---|
| `claude plugin init <name>` (`new`) | Scaffold a new plugin in `~/.claude/skills/<name>/` |
| `claude plugin validate <path>` | Validate `plugin.json`, marketplace, skill and agent formats |
| `claude plugin details <name>` | Component list and estimated token cost (excludes hook injections) |
| `claude plugin eval [target]` | Score plugin behavior against `evals/` cases |
| `claude plugin tag [path]` | Create a `<name>--v<version>` release tag. `--dry-run`·`--push` |
| `claude plugin test [folder]` | Run mod tests |
| `claude --plugin-dir <path>` | Load and run a plugin under development once, without installing |

</details>

<details>
<summary><b>Inside Claude Code — <code>/plugin</code></b></summary>

| Command | What it does |
|---|---|
| `/plugin` | Plugin management screen (browse, install, enable, disable) |
| `/plugin marketplace add <source>` | Register a marketplace |
| `/plugin install <name>@<market>` | Install |
| `/plugin marketplace update <name>` → `/plugin update <name>@<market>` | Update sequence |
| `/plugin uninstall <name>@<market>` | Remove |
| `/context` | See how much of the current session context plugins and others take up |

</details>

## License

MIT. The pstack-derived skills, agents and docs are MIT © 2026 Lauren Tan; see `LICENSE`.
