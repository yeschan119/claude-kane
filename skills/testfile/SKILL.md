---
name: testfile
description: Test-file commit gate — temporarily allows or locks committing test files (test_*.py, *.test.ts, tests/, etc.). User-run only.
argument-hint: "on [minutes] | off | status"
disable-model-invocation: true
---

# /kane:testfile

Arguments: `$ARGUMENTS`

Run `testfile $ARGUMENTS` with the gate command from the session context. With no arguments, `testfile status`. Relay only its output and don't chain it with other commands.

Before opening, the list of test files to commit·line counts·reason must already have been reported to the user. Once the commit is done, recommend `/kane:testfile off`. Default 15 minutes, max 480 minutes.
