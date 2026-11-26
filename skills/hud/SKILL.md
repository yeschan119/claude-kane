---
name: hud
description: kane HUD statusline — turns on/off a two-line statusline (branch / model · 5h·daily·weekly usage · session time · context %). User-run only.
argument-hint: "on | off | status"
disable-model-invocation: true
---

# /kane:hud

Arguments: `$ARGUMENTS`

Run `python3 "<rules folder>/../scripts/hud.py" $ARGUMENTS` (the rules folder path is in the session context). With no arguments, `status`. Relay only its output and don't chain it with other commands.

- `on` changes `statusLine` in the user's `settings.json` and backs up the previous value; `off` restores it. Tell the user which statusline it replaced.
- Usage (5h·day·wk) shows only when Claude Code provides `rate_limits` (Pro/Max plans); no token or network access.
- `day` is today's share of the daily allotment (weekly limit ÷ 7): `(wk% now − wk% at today's first render) × 7`, reset at local midnight or a weekly reset. Usage before the day's first render isn't counted; it can exceed 100%.
