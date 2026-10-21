"""Repository-owned lint and test entrypoint; CI never mutates source."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = [["Ruff lint", ["-m", "ruff", "check", "."]]]
FORMAT_CHECK = ["Ruff format", ["-m", "ruff", "format", "--check", "."]]
TESTS = [
    ["Public boundary", ["conformance/check_public_boundary.py"]],
    [
        "Conformance",
        [
            "-m",
            "unittest",
            "conformance.test_conformance",
            "conformance.test_package_v2",
            "conformance.test_public_boundary",
        ],
    ],
    ["Public client tests", ["-m", "unittest", "discover", "-s", "tests", "-v"]],
    [
        "Synthetic 0.1 contract",
        [
            "conformance/validate.py",
            "spec/schemas/package-0.1.0.schema.json",
            "examples/synthetic/valid/package-0.1.0.json",
        ],
    ],
    [
        "Synthetic 0.2 contract",
        [
            "conformance/validate.py",
            "spec/schemas/package-0.2.0.schema.json",
            "examples/synthetic/valid/package-0.2.0.json",
        ],
    ],
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline repository verification.")
    parser.add_argument("--preflight", action="store_true", help="Only run lint and format checks")
    parser.add_argument(
        "--fix-style", action="store_true", help="Apply safe Ruff fixes before preflight"
    )
    parser.add_argument(
        "--check-format", action="store_true", help="Check full-tree Ruff formatting"
    )
    args = parser.parse_args()
    if args.fix_style and not args.preflight:
        parser.error("--fix-style requires --preflight")

    env = os.environ.copy()
    # The installed project and runtime are supplied by each repository.
    if args.fix_style:
        for command in (
            [sys.executable, "-m", "ruff", "check", "--fix", "."],
            [sys.executable, "-m", "ruff", "format", "."],
        ):
            if subprocess.run(command, cwd=ROOT, env=env, check=False).returncode:
                return 1

    commands = [FORMAT_CHECK, *(PREFLIGHT if args.preflight else PREFLIGHT + TESTS)]
    failures = []
    for label, args_list in commands:
        command = [sys.executable, *args_list]
        print(f"==> {label}", flush=True)
        if subprocess.run(command, cwd=ROOT, env=env, check=False).returncode:
            failures.append(label)
    if failures:
        print("Failed checks: " + ", ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
