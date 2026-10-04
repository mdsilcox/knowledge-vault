"""python -m kv check <vault> | sync --vault <vault> | install [--dry-run]"""
import sys

from kv import check, install, sync

COMMANDS = {"check": check.main, "sync": sync.main, "install": install.main}


def run(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 1
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
