# claude-kane

> A minimal Claude Code harness: design-approval gate, destructive-command guard, verification & review workflow, and lesson memory. Nothing else.

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
| Agents | `investigator` · `designer` · `verifier` · `reviewer` | Investigation · per-mode design · separate-lane verification · review |
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

## Session cost

| Item | Tokens | Measurement |
|---|---|---|
| Fixed per session | ~2,200 | `claude -p` input tokens with vs. without the plugin (27,283 → 29,463) |
| └ Skill & agent list | ~1,060 | `claude --plugin-dir . plugin details kane` |
| └ Rule injection (SessionStart) | ~1,100 | Difference of the two above. Only `RULES.md` is injected; agents read `STYLE.md` when needed. Grows by the size of `.claude/lessons.md` if present |
| Per invocation | 220 ~ 1,500 | Per skill/agent (see `plugin details`) |

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

MIT
