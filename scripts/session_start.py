"""SessionStart 훅 — 개발 규칙, 게이트 명령 경로, 프로젝트 교훈(.claude/lessons.md)을 세션에 주입한다."""
import json
from pathlib import Path

from common import read_payload, resolve_project_dir

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
LESSONS_RELATIVE_PATH = Path(".claude") / "lessons.md"
# 교훈이 쌓여도 세션 컨텍스트를 잡아먹지 않도록 최근 것만 싣는다.
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
        "[kane] 아래 규칙을 이 세션 전체에 적용한다.",
        rules,
        f"게이트 명령: {gate_command} <design|danger|testfile> <on [분]|off|status>",
        f"규칙 폴더(RULES.md·STYLE.md, 서브에이전트에 전달): {PLUGIN_ROOT / 'rules'}",
    ]
    lessons = read_recent_lessons(project_dir)
    if lessons:
        parts.append(f"[프로젝트 교훈 — {LESSONS_RELATIVE_PATH}] 같은 실수를 반복하지 않는다.\n{lessons}")
    return "\n\n".join(parts)


def main():
    project_dir = resolve_project_dir(read_payload())
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": build_context(project_dir)}
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
