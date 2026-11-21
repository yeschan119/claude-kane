"""kane 훅 공용 유틸 — 페이로드 읽기, 게이트 상태, 훅 결정 출력."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 게이트 상태는 프로젝트가 아니라 사용자 홈에 둔다 — 레포를 더럽히지 않고 커밋에 섞이지 않게.
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
    """git 레포 안이면 최상위 경로로 맞춘다 — 게이트를 연 위치와 검사 위치가 하위 폴더로 갈려도 같은 키가 되게."""
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
    """PreToolUse 결정(deny|ask)을 출력한다. 사유는 Claude 와 사용자 모두에게 보인다."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
