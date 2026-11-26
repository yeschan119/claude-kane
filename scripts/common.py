"""Shared utilities for kane hooks — reading the payload, gate state, emitting hook decisions."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Gate state lives in the user's home, not the project — so it never dirties the repo or slips into a commit.
GATE_ROOT = Path.home() / ".claude" / "kane" / "gates"


def read_payload():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def find_repository_root(path):
    try:
        result = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"],
                                capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def resolve_project_dir(payload):
    """Inside a git repo, normalize to the top level — so the key matches even if the gate was opened and checked from different subfolders."""
    start = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return os.path.realpath(find_repository_root(start) or start)


def gate_file(gate_name, project_dir):
    project_key = hashlib.sha1(project_dir.encode()).hexdigest()[:12]
    return GATE_ROOT / project_key / f"{gate_name}.unlock"


def read_gate_expiry(gate_name, project_dir):
    try:
        return int(gate_file(gate_name, project_dir).read_text().strip())
    except (OSError, ValueError):
        return 0


def is_gate_open(gate_name, project_dir):
    return read_gate_expiry(gate_name, project_dir) > time.time()


def emit_decision(decision, reason):
    """Emit a PreToolUse decision (deny|ask). The reason is shown to both Claude and the user."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
