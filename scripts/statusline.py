"""Statusline — renders the kane HUD from the JSON Claude Code passes on stdin.

Line 1: branch:<name> (omitted outside a git repo)
Line 2: Model: <name> | 5h:<n>%(<reset>) wk:<n>%(<reset>) | session:<duration> | ctx:<n>%
"""
import json
import subprocess
import sys
import time
from datetime import datetime

# Percent thresholds for color: below WARN green, below DANGER yellow, otherwise red.
WARN_PERCENT = 70
DANGER_PERCENT = 85
GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
# resets_at above this is treated as epoch milliseconds rather than seconds.
EPOCH_MS_THRESHOLD = 10_000_000_000


def read_stdin():
    try:
        status = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}
    return status if isinstance(status, dict) else {}


def find_branch(cwd):
    try:
        result = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, timeout=1)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def format_percent(percent):
    rounded = round(percent)
    color = GREEN if rounded < WARN_PERCENT else YELLOW if rounded < DANGER_PERCENT else RED
    return f"{color}{rounded}%{RESET}"


def format_duration(seconds):
    minutes = max(int(seconds // 60), 0)
    days, hours, mins = minutes // 1440, minutes % 1440 // 60, minutes % 60
    if days:
        return f"{days}d{hours}h"
    if hours:
        return f"{hours}h{mins}m"
    return f"{mins}m"


def parse_reset_epoch(resets_at):
    if isinstance(resets_at, (int, float)):
        return resets_at / 1000 if resets_at > EPOCH_MS_THRESHOLD else resets_at
    if isinstance(resets_at, str) and resets_at:
        try:
            return datetime.fromisoformat(resets_at.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def format_limit(label, window):
    percent = (window or {}).get("used_percentage")
    if percent is None:
        return None
    text = f"{label}:{format_percent(percent)}"
    reset_epoch = parse_reset_epoch(window.get("resets_at"))
    if reset_epoch is not None:
        text += f"{DIM}({format_duration(reset_epoch - time.time())}){RESET}"
    return text


def compute_context_percent(context_window):
    if context_window.get("used_percentage") is not None:
        return context_window["used_percentage"]
    usage = context_window.get("current_usage") or {}
    size = context_window.get("context_window_size") or 0
    used = sum(usage.get(key) or 0 for key in
               ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return used * 100 / size if size else None


def build_lines(status):
    cwd = (status.get("workspace") or {}).get("current_dir") or status.get("cwd") or "."
    model = status.get("model") or {}
    parts = [f"Model: {model.get('display_name') or model.get('id') or '?'}"]

    limits = status.get("rate_limits") or {}
    limit_texts = [text for text in (format_limit("5h", limits.get("five_hour")),
                                     format_limit("wk", limits.get("seven_day"))) if text]
    if limit_texts:
        parts.append(" ".join(limit_texts))

    duration_ms = (status.get("cost") or {}).get("total_duration_ms")
    if duration_ms is not None:
        parts.append(f"session:{format_duration(duration_ms / 1000)}")

    percent = compute_context_percent(status.get("context_window") or {})
    if percent is not None:
        parts.append(f"ctx:{format_percent(percent)}")

    branch = find_branch(cwd)
    lines = [f"branch:{branch}"] if branch else []
    return lines + [" | ".join(parts)]


def main():
    print("\n".join(build_lines(read_stdin())))


if __name__ == "__main__":
    main()
