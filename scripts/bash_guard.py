"""PreToolUse(Bash) 가드 — 비가역 명령 차단, 테스트 파일 커밋 차단, PR --base 강제, 외부 반영 명령 확인."""
import os
import re
import subprocess

from common import emit_decision, is_gate_open, read_payload, resolve_project_dir
from shell_parse import positional_args, split_segments

DESTRUCTIVE_SQL = re.compile(r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)\b|TRUNCATE\s+(TABLE\s+)?[A-Za-z_\"])", re.I)
TEST_FILE_PATH = re.compile(
    r"(^|/)(test_[^/]+\.py|[^/]+_test\.(py|go)|[^/]+\.(test|spec)\.[cm]?[jt]sx?)$|(^|/)(tests?|__tests__)/"
)
GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree"}
GIT_CONFIRM_SUBCOMMANDS = {"commit", "push", "merge", "rebase", "reset", "switch", "checkout",
                           "cherry-pick", "revert", "am", "pull"}
GH_CONFIRM = {"pr": {"create", "merge", "close", "reopen"}, "repo": {"create", "delete", "edit", "rename"},
              "release": {"create", "delete"}}
DOCKER_CONFIRM = {"up", "down", "stop", "restart", "rm", "rmi", "build", "kill"}
PACKAGE_MANAGERS = {"npm", "pnpm", "yarn", "bun", "pip", "pip3", "uv"}
PACKAGE_CONFIRM = {"install", "i", "add", "remove", "uninstall", "update", "upgrade", "publish", "ci"}
ALWAYS_CONFIRM = {"rm", "chmod", "chown"}


def split_git(tokens):
    """git [전역옵션] <서브커맨드> [인자] → (서브커맨드, 인자)."""
    rest = tokens[1:]
    while rest:
        if rest[0] in GIT_OPTIONS_WITH_VALUE:
            rest = rest[2:]
        elif rest[0].startswith("-"):
            rest = rest[1:]
        else:
            return rest[0], rest[1:]
    return "", []


def short_flag_chars(args):
    return "".join(arg[1:] for arg in args if arg.startswith("-") and not arg.startswith("--"))


def find_git_danger(subcommand, args):
    if subcommand == "push" and any(a in ("-f", "--force") or a.startswith("--force") or a.startswith("+") for a in args):
        return "강제 푸시"
    if subcommand == "reset" and "--hard" in args:
        return "git reset --hard"
    if subcommand == "clean":
        return "git clean"
    if subcommand == "commit" and "--amend" in args:
        return "git commit --amend"
    if subcommand in ("branch", "tag") and ({"-d", "-D", "--delete"} & set(args)):
        return f"git {subcommand} 삭제"
    if subcommand == "checkout" and ("--" in args or "." in args):
        return "git checkout 으로 변경분 폐기"
    if subcommand == "restore" and ("--staged" not in args or "--worktree" in args):
        return "git restore 로 변경분 폐기"
    if subcommand == "stash" and args[:1] in (["drop"], ["clear"]):
        return "git stash 삭제"
    return None


def find_danger(tokens):
    verb = os.path.basename(tokens[0])
    args = tokens[1:]
    if verb == "git":
        return find_git_danger(*split_git(tokens))
    if verb == "rm":
        flags = short_flag_chars(args)
        is_recursive = "r" in flags.lower() or "--recursive" in args
        if is_recursive and ("f" in flags or "--force" in args):
            return "rm -rf"
    if verb in ("docker", "docker-compose"):
        if "prune" in args:
            return "docker prune"
        if "down" in args and ({"-v", "--volumes"} & set(args)):
            return "docker down -v (볼륨 삭제)"
    return None


def find_confirm(segment):
    tokens = segment["tokens"]
    verb = os.path.basename(tokens[0])
    args = positional_args(tokens)
    if segment["sudo"]:
        return "sudo"
    if verb in ALWAYS_CONFIRM:
        return verb
    if verb == "git":
        subcommand, git_args = split_git(tokens)
        if subcommand in GIT_CONFIRM_SUBCOMMANDS:
            return f"git {subcommand}"
        if subcommand in ("branch", "tag", "remote") and [a for a in git_args if not a.startswith("--show")]:
            return f"git {subcommand} 변경"
        if subcommand == "stash" and git_args[:1] not in (["list"], ["show"]):
            return "git stash"
    if verb == "gh" and len(args) >= 2 and args[1] in GH_CONFIRM.get(args[0], set()):
        return f"gh {args[0]} {args[1]}"
    if verb in ("docker", "docker-compose") and DOCKER_CONFIRM & set(args):
        return "docker " + " ".join(sorted(DOCKER_CONFIRM & set(args)))
    if verb in PACKAGE_MANAGERS and args[:1] and args[0] in PACKAGE_CONFIRM:
        return f"{verb} {args[0]}"
    if any("migrat" in a.lower() for a in tokens) or verb == "alembic":
        return "DB 마이그레이션"
    if verb.endswith("gate.py") or (len(tokens) > 1 and tokens[1].endswith("gate.py")):
        if "on" in tokens:
            return "kiss 게이트 열기 — 사용자가 직접 확인해야 한다"
    return None


def is_pr_create_without_base(tokens):
    if os.path.basename(tokens[0]) != "gh" or positional_args(tokens)[:2] != ["pr", "create"]:
        return False
    return not any(t in ("--base", "-B") or t.startswith("--base=") for t in tokens)


def run_git(project_dir, *git_args):
    try:
        result = subprocess.run(["git", "-C", project_dir, *git_args], capture_output=True, text=True, timeout=5)
        return result.stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def added_paths(name_status_output):
    """--name-status 출력에서 삭제(D)를 뺀 경로. 테스트 파일을 커밋에서 '빼는' 정리는 막지 않는다."""
    paths = []
    for line in name_status_output.splitlines():
        fields = line.split("\t")
        if len(fields) >= 2 and not fields[0].startswith("D"):
            paths.append(fields[-1])
    return paths


def find_test_files_entering_commit(tokens, project_dir):
    subcommand, args = split_git(tokens)
    if subcommand == "add":
        explicit = [a for a in args if TEST_FILE_PATH.search(a)]
        if explicit:
            return explicit
        if {"-A", "--all", ".", "-u", "--update", ":/", "*"} & set(args):
            status = run_git(project_dir, "status", "--porcelain")
            return [line[3:] for line in status.splitlines() if "D" not in line[:2] and TEST_FILE_PATH.search(line[3:])]
    if subcommand == "commit":
        staged = added_paths(run_git(project_dir, "diff", "--cached", "--name-status"))
        if "-a" in args or "--all" in args or "a" in short_flag_chars(args):
            staged += added_paths(run_git(project_dir, "diff", "--name-status"))
        return [p for p in staged if TEST_FILE_PATH.search(p)]
    return []


def main():
    payload = read_payload()
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not command:
        return
    project_dir = resolve_project_dir(payload)
    segments = split_segments(command)

    if not is_gate_open("danger", project_dir):
        dangers = [d for d in (find_danger(s["tokens"]) for s in segments) if d]
        if DESTRUCTIVE_SQL.search(command):
            dangers.append("DROP/TRUNCATE SQL")
        if dangers:
            emit_decision("deny", f"[kiss] 비가역 명령 기본 차단: {', '.join(dangers)}. 영향·복구 방법을 사용자에게 "
                                  "설명하고, 사용자가 /kiss:danger on [분] 으로 연 뒤에만 실행한다.")
            return

    if any(is_pr_create_without_base(s["tokens"]) for s in segments):
        emit_decision("deny", "[kiss] gh pr create 에 --base 가 없다. 생략하면 기본 브랜치로 올라간다 — base 를 명시한다.")
        return

    if not is_gate_open("testfile", project_dir):
        test_files = []
        for segment in segments:
            if os.path.basename(segment["tokens"][0]) == "git":
                test_files += find_test_files_entering_commit(segment["tokens"], project_dir)
        if test_files:
            listed = ", ".join(sorted(set(test_files))[:10])
            emit_decision("deny", f"[kiss] 테스트 파일이 커밋에 들어간다: {listed}. 지시받지 않은 검증 스크립트는 "
                                  "커밋에서 빼고, 꼭 필요하면 이유를 보고한 뒤 사용자가 /kiss:testfile on 으로 연다.")
            return

    confirms = [c for c in (find_confirm(s) for s in segments) if c]
    if confirms:
        emit_decision("ask", f"[kiss] 외부 반영·되돌리기 어려운 명령: {', '.join(dict.fromkeys(confirms))}")


if __name__ == "__main__":
    main()
