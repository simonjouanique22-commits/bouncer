#!/usr/bin/env python3
"""Checks for hooks/bouncer.py.  python3 tests/check.py         -> logic, no model call
                                  python3 tests/check.py --live  -> plus three real triages by Haiku
(python3 tests/eval.py scores the triage itself on labelled messages.)"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "bouncer.py"
tmp = Path(tempfile.mkdtemp())
busy_tx, idle_tx, odd_tx = tmp / "busy.jsonl", tmp / "idle.jsonl", tmp / "odd.jsonl"
task = {"type": "user", "message": {"role": "user", "content": "Refactor the payment module"}}
tool = {"type": "assistant", "message": {"role": "assistant", "stop_reason": "tool_use",
        "content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": "payment.py"}}]}}
stop = {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "[Request interrupted by user]"}]}}
busy_tx.write_text("\n".join(json.dumps(e) for e in (task, tool)), encoding="utf-8")
idle_tx.write_text("\n".join(json.dumps(e) for e in (task, tool, stop)), encoding="utf-8")
odd_tx.write_text('{"kind": "turn", "payload": {}}\nnot json at all\n', encoding="utf-8")  # a format we do not know


def hook(event, prompt="", tx=busy_tx, fake=None, note="rephrased", drop=(), drop_only=False, sid="s1", **env):
    e = {**os.environ, "CLAUDE_PLUGIN_DATA": str(tmp), "CLAUDE_PLUGIN_OPTION_LANGUAGE": "en", **env}
    e.pop("BOUNCER_FAKE", None)
    if fake is not None:
        e["BOUNCER_FAKE"] = json.dumps({"analysis": "a", "urgent": fake, "drop": list(drop), "drop_only": drop_only,
                                        "why": "test.", "note": note})
    data = {"session_id": sid, "hook_event_name": event, "prompt": prompt, "transcript_path": str(tx)}
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       capture_output=True, env=e)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    o = r.stdout.decode("utf-8")
    return json.loads(o) if o.strip() else None


def st(sid="s1"):
    return json.loads((tmp / f"{sid}.json").read_text(encoding="utf-8"))


accents = "après, regarde le README stp ✨"  # non-ASCII on purpose: encodings differ on Windows
# A turn starts; a message that can wait is held, one needed now gets in, with or without a note.
assert hook("UserPromptSubmit", "Refactor the payment module") is None and st()["busy"]
o = hook("UserPromptSubmit", accents, fake=False)
assert o["decision"] == "block" and st()["held"][0]["original"] == accents, o
o = hook("UserPromptSubmit", "stay on Python 3.9 please", fake=True)
assert "additionalContext" in o["hookSpecificOutput"] and len(st()["held"]) == 1, o
o = hook("UserPromptSubmit", "this one is clear as is", fake=True, note="")
assert o == {"systemMessage": "⚡ Let through now. test."}, o  # no note: nothing added
o = hook("UserPromptSubmit", "an idea for later on", fake=False, note="")
assert "Note for Claude" not in o["reason"] and len(st()["held"]) == 2, o
# Fast paths: a held message sent again, a short message.
o = hook("UserPromptSubmit", "an idea for later on", fake=False)
assert "twice" in o["systemMessage"] and len(st()["held"]) == 1, o
o = hook("UserPromptSubmit", "no, stop", fake=False)
assert "short" in o["systemMessage"], o
# Withdrawing a waiting message, alone or with a new request.
o = hook("UserPromptSubmit", "forget what I said about the README", fake=False, drop=[1], drop_only=True)
assert o["decision"] == "block" and "Taken out of the line" in o["reason"] and st()["held"] == [], o
hook("UserPromptSubmit", accents, fake=False)
o = hook("UserPromptSubmit", "instead of the README look at the docs", fake=False, drop=[1])
assert "Taken out" in o["reason"] and [h["original"] for h in st()["held"]] == ["instead of the README look at the docs"], o
o = hook("UserPromptSubmit", "drop it and keep Python 3.9", fake=True, drop=[9])  # out of range: ignored
assert len(st()["held"]) == 1 and "Taken out" not in o["systemMessage"], o
# A failing triage lets the message through and warns once per session.
broken = {"CLAUDE_CODE_EXECPATH": str(tmp / "missing")}
o = hook("UserPromptSubmit", "is this going to work fine", **broken)
assert o and "could not triage" in o["systemMessage"], o
assert hook("UserPromptSubmit", "and what about this message", **broken) is None
# Commands, answered without the model.
o = hook("UserPromptSubmit", "/bouncer:status")
assert o["decision"] == "block" and "In line (1)" in o["reason"] and "Today:" in o["reason"], o
assert o["hookSpecificOutput"]["suppressOriginalPrompt"] is True and st()["busy"], o
o = hook("UserPromptSubmit", "/bouncer:release")
assert "decision" not in o and "instead of the README" in o["hookSpecificOutput"]["additionalContext"] and st()["held"] == [], o
assert "Nobody in line" in hook("UserPromptSubmit", "/bouncer:release")["reason"]
hook("UserPromptSubmit", accents, fake=False)
o = hook("UserPromptSubmit", "/bouncer:clear")
assert "Line cleared (1)" in o["reason"] and st()["held"] == [], o
assert "paused" in hook("UserPromptSubmit", "/bouncer:pause")["reason"] and st()["paused"]
assert hook("UserPromptSubmit", "a long message that is not triaged", fake=False) is None  # paused: passes
assert "back on duty" in hook("UserPromptSubmit", "/bouncer:resume")["reason"] and not st()["paused"]
assert "Unknown command" in hook("UserPromptSubmit", "/bouncer:dance")["reason"]
hook("UserPromptSubmit", accents, fake=False)
o = hook("UserPromptSubmit", "Bouncer status")  # plain-text form, delivered mid-task
assert o["decision"] == "block" and "In line (1)" in o["reason"], o
o = hook("UserPromptSubmit", "bouncer release")
assert "bouncer command" in o["hookSpecificOutput"]["additionalContext"] and st()["held"] == [], o
o = hook("UserPromptSubmit", "bouncer, can you dance for me", fake=True, note="")
assert o == {"systemMessage": "⚡ Let through now. test."}, o  # not a command: triaged as usual
assert "en pause" in hook("UserPromptSubmit", "/bouncer:pause", CLAUDE_PLUGIN_OPTION_LANGUAGE="fr")["reason"]
hook("UserPromptSubmit", "/bouncer:resume")
# French notices on request.
o = hook("UserPromptSubmit", "on reste bien en Python 3.9", fake=True, note="", CLAUDE_PLUGIN_OPTION_LANGUAGE="fr")
assert o["systemMessage"].startswith("⚡ Transmis tout de suite"), o
# The end of the task hands held messages over, once.
hook("UserPromptSubmit", accents, fake=False)
o = hook("Stop")
assert o["decision"] == "block" and accents in o["reason"] and st()["held"] == [], o
assert o["reason"].count("Triage note") == 1 and "1 held message" in o["systemMessage"], o
assert hook("Stop") is None and not st()["busy"]
# Housekeeping: abandoned sessions purged, log capped.
old = tmp / "old-session.json"
old.write_text("{}")
os.utime(old, (time.time() - 8 * 86400,) * 2)
assert hook("UserPromptSubmit", "a brand new task for you", fake=False) is None and st()["busy"]  # idle: passes
assert not old.exists()
(tmp / "log.txt").write_text("2000-01-01 00:00:00 x y\n" * 20000, encoding="utf-8")  # about 480 KB
hook("UserPromptSubmit", "/bouncer:status")
assert (tmp / "log.txt").stat().st_size < 256_000
# Left alone: interrupted turns, nested calls, system messages, other commands, unknown transcripts.
assert hook("UserPromptSubmit", "after pressing Esc again", tx=idle_tx, fake=False) is None
assert hook("UserPromptSubmit", "x y z w v", fake=False, BOUNCER_CHILD="1") is None
assert hook("UserPromptSubmit", "<task-notification>…", fake=False) is None
assert hook("UserPromptSubmit", "/review the whole thing", fake=False) is None
hook("UserPromptSubmit", "Refactor the payment module", sid="s2")
o = hook("UserPromptSubmit", "a message during an odd transcript", tx=odd_tx, fake=False, sid="s2")
assert o and "does not recognise" in o["systemMessage"], o  # passes, warns once
assert hook("UserPromptSubmit", "another one during it", tx=odd_tx, fake=False, sid="s2") is None
assert hook("UserPromptSubmit", "a message with a bad option", fake=True, note="", sid="s3",
            CLAUDE_PLUGIN_OPTION_TIMEOUT="soon") is None  # not mid-turn for s3; bad option ignored
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
