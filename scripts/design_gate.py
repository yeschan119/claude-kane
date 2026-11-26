"""PreToolUse design gate — code files inside a git repo cannot be edited before user approval (gate open)."""
import os

from common import emit_decision, find_repository_root, is_gate_open, read_payload, resolve_project_dir
from shell_parse import positional_args, redirect_targets, split_segments

# Docs and harness files may be edited without a design. Only code is blocked.
EXEMPT_PREFIXES = (".claude/", "docs/", ".git/")
EXEMPT_SUFFIXES = (".md",)
ALL_ARGS_WRITE_VERBS = {"rm", "rmdir", "touch", "mkdir", "truncate", "tee", "chmod", "chown"}
DESTINATION_WRITE_VERBS = {"cp", "mv", "install", "ln", "rsync"}
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
MAX_LISTED_PATHS = 5


def is_protected(path, project_dir, cwd):
    if not path:
        return False
    absolute = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    if not absolute.startswith(project_dir + os.sep):
        return False
    relative = absolute[len(project_dir) + 1:]
    return not relative.lower().endswith(EXEMPT_SUFFIXES) and not relative.startswith(EXEMPT_PREFIXES)


def bash_write_targets(command):
    targets = []
    for segment in split_segments(command):
        tokens = segment["tokens"]
        verb = os.path.basename(tokens[0])
        args = positional_args(tokens)
        targets += redirect_targets(tokens)
        if verb in ALL_ARGS_WRITE_VERBS:
            targets += args
        elif verb in DESTINATION_WRITE_VERBS and args:
            targets.append(args[-1])
        elif verb == "sed" and any(t.startswith("-i") or t == "--in-place" for t in tokens):
            has_script_flag = "-e" in tokens or "-f" in tokens
            targets += args if has_script_flag else args[1:]
    return targets


def main():
    payload = read_payload()
    project_dir = resolve_project_dir(payload)
    if not find_repository_root(project_dir) or is_gate_open("design", project_dir):
        return
    tool_input = payload.get("tool_input") or {}
    tool_name = payload.get("tool_name") or ""
    cwd = payload.get("cwd") or project_dir
    if tool_name in EDIT_TOOLS:
        candidates = [tool_input.get("file_path") or tool_input.get("notebook_path") or ""]
    elif tool_name == "Bash":
        candidates = bash_write_targets(tool_input.get("command") or "")
    else:
        return
    blocked = list(dict.fromkeys(p for p in candidates if is_protected(p, project_dir, cwd)))
    if not blocked:
        return
    emit_decision("deny", "[kane] Code edit blocked before approval: " + ", ".join(blocked[:MAX_LISTED_PATHS]) + ". "
                  "First follow the /kane:design procedure (classify mode → investigate → design → approval gate) and get user approval. "
                  "For a simple fix, the user opens it with /kane:design on [minutes]. Claude does not open the gate on its own.")


if __name__ == "__main__":
    main()
