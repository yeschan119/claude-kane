"""Open/close kane timed gates — usage: gate.py <design|danger|testfile> <on [minutes] | off | status>"""
import sys
import time

from common import gate_file, read_gate_expiry, resolve_project_dir

GATE_LABELS = {"design": "Design approval gate", "danger": "Dangerous command gate", "testfile": "Test file commit gate"}
# Irreversible commands and test commits open briefly; the design bypass opens for a working session.
DEFAULT_MINUTES = {"design": 30, "danger": 15, "testfile": 15}
MAX_MINUTES = 480


def open_gate(gate_name, project_dir, minutes):
    if not 1 <= minutes <= MAX_MINUTES:
        raise SystemExit(f"x minutes must be between 1 and {MAX_MINUTES}: {minutes}")
    expiry = int(time.time()) + minutes * 60
    path = gate_file(gate_name, project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{expiry}\n")
    print(f"🔓 {GATE_LABELS[gate_name]} open for {minutes} min (expires {time.strftime('%H:%M', time.localtime(expiry))})"
          f" — when done, /kane:{gate_name} off")


def close_gate(gate_name, project_dir):
    gate_file(gate_name, project_dir).unlink(missing_ok=True)
    print(f"🔒 {GATE_LABELS[gate_name]} locked")


def print_status(gate_name, project_dir):
    remaining = read_gate_expiry(gate_name, project_dir) - int(time.time())
    if remaining > 0:
        print(f"🔓 {GATE_LABELS[gate_name]} open — {remaining // 60}m {remaining % 60}s left")
    else:
        print(f"🔒 {GATE_LABELS[gate_name]} locked")


def main(argv):
    if len(argv) < 2 or argv[0] not in GATE_LABELS or argv[1] not in ("on", "off", "status"):
        raise SystemExit(__doc__)
    gate_name, action = argv[0], argv[1]
    project_dir = resolve_project_dir({})
    if action == "on":
        minutes_text = argv[2] if len(argv) > 2 else str(DEFAULT_MINUTES[gate_name])
        if not minutes_text.isdigit():
            raise SystemExit(f"x minutes must be a number: {minutes_text}")
        open_gate(gate_name, project_dir, int(minutes_text))
    elif action == "off":
        close_gate(gate_name, project_dir)
    else:
        print_status(gate_name, project_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
