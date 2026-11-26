"""Split a Bash command into segments by command position — so text inside quotes or heredoc bodies is not mistaken for a command."""
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
    """Strip leading env assignments and wrappers like sudo; return (whether sudo was used, the real command tokens)."""
    used_sudo = False
    while tokens and (ENV_ASSIGNMENT.match(tokens[0]) or os.path.basename(tokens[0]) in WRAPPER_COMMANDS):
        used_sudo = used_sudo or tokens[0] == "sudo"
        tokens = tokens[1:]
    return used_sudo, tokens


def split_segments(command):
    """Command string → [{'tokens': [...], 'sudo': bool}, ...]. Also expands the inside of bash -c '...'."""
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
    """Targets of `> file`, `>> file`, `&> file`. Excludes fd duplication like `2>&1`."""
    targets = []
    for index, token in enumerate(tokens[:-1]):
        if is_redirect(token) and not token.endswith("&"):
            targets.append(tokens[index + 1])
    return targets


def positional_args(tokens):
    """Arguments excluding the command name, flags, and redirections."""
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
