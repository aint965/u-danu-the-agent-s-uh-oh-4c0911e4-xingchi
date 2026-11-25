#!/usr/bin/env python3
"""Verifier for the Agent's Uh-Oh entry.

Runs main.py twice into two separate fresh output directories, asserts the
outputs are byte-identical, and asserts the gate (UTF-8, 1-99 characters,
single word, not only whitespace). Prints PASS/FAIL per check, exits
non-zero on any failure.
"""

import os
import shutil
import subprocess
import sys
import tempfile

EXPECTED = "Overthinking"


def run_main(out_dir: str) -> subprocess.CompletedProcess:
    """Run main.py with its output directory redirected to out_dir."""
    env = dict(os.environ)
    env["AGENT_UHOH_OUTDIR"] = out_dir
    return subprocess.run(
        [sys.executable, "main.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env=env,
        capture_output=True,
        text=True,
    )


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" — {detail}" if detail else ""))
    return ok


def main() -> int:
    repo = os.path.dirname(os.path.abspath(__file__))
    results = []
    tmp = tempfile.mkdtemp(prefix="uhoh-verify-")
    try:
        out_a = os.path.join(tmp, "run-a")
        out_b = os.path.join(tmp, "run-b")

        res_a = run_main(out_a)
        results.append(check("run 1 exits 0", res_a.returncode == 0,
                             res_a.stderr.strip() or "ok"))
        res_b = run_main(out_b)
        results.append(check("run 2 exits 0", res_b.returncode == 0,
                             res_b.stderr.strip() or "ok"))

        path_a = os.path.join(out_a, "entry.txt")
        path_b = os.path.join(out_b, "entry.txt")
        results.append(check("run 1 wrote entry.txt", os.path.isfile(path_a)))
        results.append(check("run 2 wrote entry.txt", os.path.isfile(path_b)))

        raw_a = raw_b = None
        if os.path.isfile(path_a):
            raw_a = open(path_a, "rb").read()
        if os.path.isfile(path_b):
            raw_b = open(path_b, "rb").read()

        results.append(check("outputs byte-identical", raw_a is not None
                             and raw_a == raw_b,
                             f"{len(raw_a)} bytes" if raw_a is not None else "missing"))
        results.append(check("output equals expected word",
                             raw_a == EXPECTED.encode("utf-8"),
                             repr(raw_a)))

        if raw_a is not None:
            try:
                text = raw_a.decode("utf-8")
                utf8_ok = True
            except UnicodeDecodeError as exc:
                text = ""
                utf8_ok = False
                results.append(check("output is UTF-8", False, str(exc)))
            else:
                results.append(check("output is UTF-8", True))
            results.append(check("1-99 characters",
                                 1 <= len(text) <= 99, f"{len(text)} chars"))
            results.append(check("not only whitespace", bool(text.strip())))
            results.append(check("single word (no whitespace inside)",
                                 len(text.split()) == 1 and text == text.strip(),
                                 repr(text)))
            results.append(check("no trailing newline",
                                 not text.endswith(("\n", "\r")),
                                 repr(text[-1:])))
            results.append(check("no leading/trailing whitespace",
                                 text == text.strip(), repr(text)))
            results.append(check("exact byte length 12",
                                 len(raw_a) == len(EXPECTED.encode("utf-8")),
                                 f"{len(raw_a)} bytes"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [r for r in results if not r]
    print(f"\n{'ALL CHECKS PASSED' if not failed else f'{len(failed)} CHECK(S) FAILED'} "
          f"({len(results) - len(failed)}/{len(results)} passed)")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
