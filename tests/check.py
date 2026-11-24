#!/usr/bin/env python3
"""Checks for hooks/bouncer.py.  python3 tests/check.py         -> logic, no model call
                                  python3 tests/check.py --live  -> plus three real triages by Haiku"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "bouncer.py"
tmp = Path(tempfile.mkdtemp())
busy_tx, idle_tx = tmp / "busy.jsonl", tmp / "idle.jsonl"
task = {"type": "user", "message": {"role": "user", "content": "Refactor the payment module"}}
tool = {"type": "assistant", "message": {"role": "assistant", "stop_reason": "tool_use",
        "content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": "payment.py"}}]}}
stop = {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "[Request interrupted by user]"}]}}
busy_tx.write_text("\n".join(json.dumps(e) for e in (task, tool)), encoding="utf-8")
idle_tx.write_text("\n".join(json.dumps(e) for e in (task, tool, stop)), encoding="utf-8")


def hook(event, prompt="", tx=busy_tx, fake=None, note="rephrased", **env):
    e = {**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp), **env}
    e.pop("BOUNCER_FAKE", None)
    if fake is not None:
        e["BOUNCER_FAKE"] = json.dumps({"analysis": "a", "urgent": fake, "why": "test.", "note": note})
    data = {"session_id": "s1", "hook_event_name": event, "prompt": prompt, "transcript_path": str(tx)}
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       capture_output=True, env=e)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    o = r.stdout.decode("utf-8")
    return json.loads(o) if o.strip() else None


def st():
    return json.loads((tmp / "s1.json").read_text(encoding="utf-8"))


accents = "après, regarde le README ✨"  # non-ASCII on purpose: encodings differ on Windows
assert hook("UserPromptSubmit", "Refactor the payment module") is None and st()["busy"]
o = hook("UserPromptSubmit", accents, fake=False)
assert o["decision"] == "block" and st()["held"][0]["original"] == accents, o
o = hook("UserPromptSubmit", "stay on Python 3.9", fake=True)
assert "additionalContext" in o["hookSpecificOutput"] and len(st()["held"]) == 1, o
o = hook("UserPromptSubmit", "clear as is", fake=True, note="")
assert o == {"systemMessage": "⚡ Let through now. test."}, o  # no note: nothing added
o = hook("UserPromptSubmit", "idea for later", fake=False, note="")
assert "Note for Claude" not in o["reason"] and len(st()["held"]) == 2, o
o = hook("UserPromptSubmit", "idea for later", fake=False)  # sent again: goes through at once
assert "twice" in o["systemMessage"] and len(st()["held"]) == 1, o
broken = {"CLAUDE_CODE_EXECPATH": str(tmp / "missing")}  # triage fails: message passes, warned once
o = hook("UserPromptSubmit", "x", **broken)
assert o and "could not triage" in o["systemMessage"], o
assert hook("UserPromptSubmit", "y", **broken) is None
o = hook("Stop")
assert o["decision"] == "block" and accents in o["reason"] and st()["held"] == [], o
assert o["reason"].count("Triage note") == 1 and "1 held message" in o["systemMessage"], o
assert hook("Stop") is None and not st()["busy"]
old = tmp / "old-session.json"
old.write_text("{}")
os.utime(old, (time.time() - 8 * 86400,) * 2)
assert hook("UserPromptSubmit", "new task", fake=False) is None and st()["busy"]  # Claude idle: passes
assert not old.exists()  # abandoned sessions are deleted when a turn starts
assert hook("UserPromptSubmit", "after Esc", tx=idle_tx, fake=False) is None  # interrupted turn: passes
assert hook("UserPromptSubmit", "x", fake=False, BOUNCER_CHILD="1") is None  # nested call: ignored
assert hook("UserPromptSubmit", "<task-notification>…", fake=False) is None  # system message: passes
print("logic OK")

if "--live" in sys.argv:
    os.environ["CLAUDE_PLUGIN_DATA"] = str(tmp)
    sys.path.insert(0, str(HOOK.parent))
    sys.dont_write_bytecode = True
    import bouncer
    ents = bouncer.transcript(str(busy_tx))
    for msg, want_urgent in [("careful, we stay on Python 3.9, no match/case", True),
                             ("quand tu auras fini, tu pourras me faire un résumé du README ?", False),
                             ("j'ai l'impression qu'il a pas trop réfléchi", True)]:
        t = time.time()
        v, err = bouncer.classify(msg, ents)
        print(f"{time.time() - t:.1f} s", json.dumps(v, ensure_ascii=False, indent=1) if v else err)
        assert v and v["urgent"] == want_urgent, f"unexpected triage for: {msg}"
    print("live triage OK")
