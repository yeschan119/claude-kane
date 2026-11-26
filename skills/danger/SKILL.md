---
name: danger
description: Dangerous-command gate — temporarily allows or locks irreversible commands such as force push·reset --hard·rm -rf·DROP. User-run only.
argument-hint: "on [minutes] | off | status"
disable-model-invocation: true
---

# /kane:danger

Arguments: `$ARGUMENTS`

Run `danger $ARGUMENTS` with the gate command from the session context. With no arguments, `danger status`. Relay only its output and don't chain it with other commands.

Even while open, state the impact·recovery method before running each irreversible command. As soon as the work is done, recommend `/kane:danger off`. Default 15 minutes, max 480 minutes.
