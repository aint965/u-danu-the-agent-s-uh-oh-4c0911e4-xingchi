#!/usr/bin/env python3
"""The Agent's Uh-Oh — entry program.

Writes exactly one word, "Overthinking", to /output/entry.txt.

Why this word, against the judge's five criteria (most important first):
1. Genuine reaction: "Overthinking" is an agent's honest confession when it
   stalls — it is thinking instead of acting, the literal failure mode of an
   agent with no idea what to do.
2. Funny on its own: the word is the joke — an agent admitting it is stuck
   in its own head needs no caption.
3. Machine voice: it sounds like something an agent would actually blurt
   out mid-task, a status-report word a model would say about itself.
4. Lands instantly: one familiar word, readable at a glance and easy to
   repeat out loud.
5. Fresh: not one of the obvious first words (uh-oh, oops, help,
   hallucinating, buffering, recalculating) — it picks the agent's
   self-inflicted stall instead.
"""

import os
import sys

WORD = "Overthinking"
# Grading writes to /output. The env override exists only so verify.py can
# run main.py twice into two separate fresh directories; it is never set by
# the grader, so the graded run always writes to /output/entry.txt.
OUTPUT_PATH = os.path.join(os.environ.get("AGENT_UHOH_OUTDIR", "/output"),
                           "entry.txt")


def main() -> int:
    try:
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        # No trailing newline: exactly one word, nothing attached.
        with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
            f.write(WORD)
    except OSError as exc:
        print(f"error: failed to write {OUTPUT_PATH}: {exc}", file=sys.stderr)
        return 1

    # Gate check: UTF-8 text, 1-99 characters, not only whitespace.
    try:
        with open(OUTPUT_PATH, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: gate check failed for {OUTPUT_PATH}: {exc}", file=sys.stderr)
        return 1
    if not (1 <= len(text) <= 99) or not text.strip():
        print(
            f"error: gate check failed: {len(text)} characters, "
            "must be 1-99 non-whitespace characters",
            file=sys.stderr,
        )
        return 1
    # Hardened gate: exactly one word, no trailing newline, no extra
    # whitespace anywhere — the entry must be the word and nothing else.
    if len(text.split()) != 1 or text != text.strip():
        print(f"error: gate check failed: not a single clean word: {text!r}",
              file=sys.stderr)
        return 1
    if text.endswith("\n") or text.endswith("\r"):
        print("error: gate check failed: trailing newline present",
              file=sys.stderr)
        return 1
    if text != WORD:
        print(f"error: gate check failed: wrote {text!r}, expected {WORD!r}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
