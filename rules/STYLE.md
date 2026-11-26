# kane code style (not injected into the session — read during design·review)

## Names
- Make the role obvious. Functions start with a verb (`createUser`), classes are nouns (`OrderRepository`), booleans use `is/has/can`.
- No vague names like `qty`·`tmp`·`data`·`val`·`cnt` — say what the value is of (`sold_quantity`). The name must match the actual value.
- Pull meaningful numbers·strings (weights·thresholds·ratios·upper/lower bounds) into named constants and state their intent·unit.

## Structure
- One responsibility per class, one action per function. Separate business logic from I/O·external APIs·DB access.
- Don't merge code that only looks alike by accident — if it has no reason to change together, it isn't duplication. Don't put a rule·formula in two places.
- Split files by feature and create no circular dependencies. Inject dependencies via constructor·parameters and keep external libraries behind a thin adapter.
- Don't put keys in responses·return values that no current consumer reads. Refactor in ways that change behavior only when the reason is clear.

## Exceptions
- Logic that can fail (external API·file·DB·network) handles its failure cases. Don't swallow exceptions.
- Catch only at a level that can handle it; otherwise pass it up. Messages should reveal the cause.
- Separate user-facing errors from internal debugging errors.

## Logs
- On failures·exceptions, leave the context needed to find the cause. Match the level to the purpose (debug·info·warn·error).
- No personal data·tokens·passwords. Don't duplicate logs with the same meaning in multiple places.
