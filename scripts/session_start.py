"""SessionStart hook — injects the dev rules, the gate command path, and project lessons (.claude/lessons.md) into the session."""
import json
from pathlib import Path

from common import read_payload, resolve_project_dir

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
LESSONS_RELATIVE_PATH = Path(".claude") / "lessons.md"
# Load only recent lessons so a growing file doesn't eat the session context.
MAX_LESSON_LINES = 200


def read_recent_lessons(project_dir):
    try:
        lines = (Path(project_dir) / LESSONS_RELATIVE_PATH).read_text().splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-MAX_LESSON_LINES:])


def build_context(project_dir):
    rules = (PLUGIN_ROOT / "rules" / "RULES.md").read_text()
    gate_command = f'python3 "{PLUGIN_ROOT / "scripts" / "gate.py"}"'
    parts = [
        "[kane] Apply the rules below for this entire session.",
        rules,
        f"Gate command: {gate_command} <design|danger|testfile> <on [minutes]|off|status>",
        f"Rules folder (RULES.md, STYLE.md; pass to subagents): {PLUGIN_ROOT / 'rules'}",
    ]
    lessons = read_recent_lessons(project_dir)
    if lessons:
        parts.append(f"[Project lessons — {LESSONS_RELATIVE_PATH}] Don't repeat these mistakes.\n{lessons}")
    return "\n\n".join(parts)


def main():
    project_dir = resolve_project_dir(read_payload())
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": build_context(project_dir)}
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
