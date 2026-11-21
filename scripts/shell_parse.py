"""Bash 명령을 '명령 위치' 단위 세그먼트로 나눈다 — 인용문·heredoc 본문 속 글자로 오차단하지 않기 위함."""
import os
import re
import shlex

HEREDOC_START = re.compile(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")
SEPARATOR_CHARS = set(";&|()")
WRAPPER_COMMANDS = {"sudo", "command", "time", "env", "nohup", "exec", "xargs"}
NESTED_SHELLS = {"bash", "sh", "zsh"}
ENV_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def strip_heredoc_bodies(command):
    kept_lines, terminator = [], None
    for line in command.split("\n"):
        if terminator is not None:
            if line.strip() == terminator:
                terminator = None
            continue
        kept_lines.append(line)
        match = HEREDOC_START.search(line)
        if match:
            terminator = match.group(1)
    return "\n".join(kept_lines)


def tokenize(command):
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return command.split()


def is_separator(token):
    return bool(token) and set(token) <= SEPARATOR_CHARS


def unwrap(tokens):
    """선행 환경변수 할당과 sudo 같은 래퍼를 벗기고, (sudo 사용 여부, 실제 명령 토큰)을 돌려준다."""
    used_sudo = False
    while tokens and (ENV_ASSIGNMENT.match(tokens[0]) or os.path.basename(tokens[0]) in WRAPPER_COMMANDS):
        used_sudo = used_sudo or tokens[0] == "sudo"
        tokens = tokens[1:]
    return used_sudo, tokens


def split_segments(command):
    """명령 문자열 → [{'tokens': [...], 'sudo': bool}, ...]. bash -c '...' 안쪽도 펼친다."""
    segments, current = [], []
    for token in tokenize(strip_heredoc_bodies(command)) + [";"]:
        if not is_separator(token):
            current.append(token)
            continue
        used_sudo, tokens = unwrap(current)
        current = []
        if not tokens:
            continue
        if os.path.basename(tokens[0]) in NESTED_SHELLS and "-c" in tokens[1:-1]:
            segments += split_segments(tokens[tokens.index("-c") + 1])
            continue
        segments.append({"tokens": tokens, "sudo": used_sudo})
    return segments


def is_redirect(token):
    return ">" in token and set(token) <= set("<>&0123456789")


def redirect_targets(tokens):
    """`> file`, `>> file`, `&> file` 의 대상. `2>&1` 같은 fd 복제는 제외한다."""
    targets = []
    for index, token in enumerate(tokens[:-1]):
        if is_redirect(token) and not token.endswith("&"):
            targets.append(tokens[index + 1])
    return targets


def positional_args(tokens):
    """명령 이름·플래그·리다이렉션을 뺀 인자."""
    args, skip_next = [], False
    for token in tokens[1:]:
        if skip_next:
            skip_next = False
            continue
        if is_redirect(token):
            skip_next = not token.endswith("&")
            continue
        if token.startswith("-"):
            continue
        args.append(token)
    return args
