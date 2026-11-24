#!/usr/bin/env python3
"""Triage quality on labelled messages (real Haiku calls, about a minute).

python3 tests/eval.py            -> score on tests/cases.json
python3 tests/eval.py -v         -> plus every verdict
Exit code 1 if a message that should get in was held (the costly mistake).
"""
import inspect
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "hooks"))
sys.dont_write_bytecode = True
os.environ.setdefault("CLAUDE_PLUGIN_DATA", tempfile.mkdtemp())
import bouncer  # noqa: E402

CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
TAKES_HELD = "held" in inspect.signature(bouncer.classify).parameters


def entries(case):
    """A tiny fake transcript: the task, the agent's last words, one tool call."""
    tool = {"type": "tool_use", "name": "Edit", "input": {"file_path": case.get("file", "main.py")}}
    agent = [{"type": "text", "text": case["last"]}] if case.get("last") else []
    return [{"type": "user", "message": {"role": "user", "content": case["task"]}},
            {"type": "assistant", "message": {"role": "assistant", "stop_reason": "tool_use", "content": agent + [tool]}}]


def run(case):
    t = time.time()
    held = case.get("held", [])
    args = (case["message"], entries(case)) + ((held,) if TAKES_HELD else ())
    v, err = bouncer.classify(*args)
    return case, v, err, time.time() - t


def main():
    verbose = "-v" in sys.argv
    with ThreadPoolExecutor(6) as pool:
        results = list(pool.map(run, CASES))
    held_wrongly, let_wrongly, notes_extra, ambiguous_missed, drop_wrong, errors, secs = [], [], [], [], [], [], []
    for case, v, err, dt in results:
        secs.append(dt)
        if not v:
            errors.append(f"{case['id']}: {err}")
            continue
        note = (v.get("note") or "").strip()
        drop = sorted(int(i) for i in v.get("drop", []) if isinstance(i, int)) if TAKES_HELD else None
        if case["urgent"] and not v["urgent"]:
            held_wrongly.append(case["id"])
        if not case["urgent"] and v["urgent"]:
            let_wrongly.append(case["id"])
        if case["note"] == "none" and note:
            notes_extra.append(case["id"])
        if case["note"] == "ambiguous" and "mbigu" not in note.lower():
            ambiguous_missed.append(case["id"])
        if TAKES_HELD and "drop" in case and drop != sorted(case["drop"]):
            drop_wrong.append(f"{case['id']} (got {drop})")
        if verbose:
            print(f"- {case['id']}: urgent={v['urgent']} drop={drop} {dt:.1f}s\n  why: {v['why']}\n  note: {note or '-'}")
    n = len(CASES)
    secs.sort()
    print(f"\n{n} cases · median {secs[n // 2]:.1f} s · slowest {secs[-1]:.1f} s")
    print(f"held but needed now : {len(held_wrongly)}  {held_wrongly}")
    print(f"let in but could wait: {len(let_wrongly)}  {let_wrongly}")
    print(f"unneeded notes       : {len(notes_extra)}  {notes_extra}")
    print(f"ambiguity not flagged: {len(ambiguous_missed)}  {ambiguous_missed}")
    if TAKES_HELD:
        print(f"wrong withdrawals    : {len(drop_wrong)}  {drop_wrong}")
    print(f"errors               : {len(errors)}  {errors}")
    sys.exit(1 if held_wrongly or errors else 0)


if __name__ == "__main__":
    main()
