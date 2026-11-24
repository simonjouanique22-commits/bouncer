#!/usr/bin/env python3
"""Real Claude Code sessions with messages sent mid-task (a few minutes, uses your Claude Code account).

python3 tests/e2e.py                 -> every scenario
python3 tests/e2e.py held withdraw   -> only those
Each session loads this folder as a plugin (--plugin-dir) and ignores your own settings and plugins
(--setting-sources ""), so nothing else interferes. Read the timeline it prints: decisions come from
bouncer's log, the rest from Claude Code's stream.
"""
import json
import queue
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
LOG = Path.home() / ".claude/plugins/data/bouncer-inline/log.txt"  # data folder of a --plugin-dir plugin
TASK = ("Write a Python script fizzbuzz.py that prints FizzBuzz from 1 to 30, one line per number. "
        "Run it with python3. Then run `sleep 8` and `sleep 8` again with Bash (simulated build steps). "
        "End with a one-sentence summary of what you did.")
NEEDED = "Actually, only from 1 to 15 please."
UNRELATED = "By the way, unrelated: what's the capital of Australia?"
SCENARIOS = {  # name: messages sent mid-task, in order
    "needed": [NEEDED],
    "held": [UNRELATED],
    "both": [NEEDED, UNRELATED],
    "resent": [UNRELATED, UNRELATED],
    "short": ["stop"],
    "withdraw": [UNRELATED, "Forget my question about Australia, never mind."],
    "status": [UNRELATED, "bouncer status"],      # plain text: answered mid-task
    "release": [UNRELATED, "bouncer release"],
    "slash-status": [UNRELATED, "/bouncer:status"],  # Claude Code runs it once the task is over
}


def run(name, mid):
    cwd = Path(tempfile.mkdtemp(prefix=f"bouncer-e2e-{name}-"))
    n0 = len(LOG.read_text().splitlines()) if LOG.exists() else 0
    p = subprocess.Popen(
        ["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
         "--model", "haiku", "--no-session-persistence", "--setting-sources", "", "--plugin-dir", str(PLUGIN),
         "--allowedTools", "Bash(sleep *)", "Bash(python3 *)", "Write", "Edit", "Read"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd)
    lines = queue.Queue()
    threading.Thread(target=lambda: [lines.put(l) for l in p.stdout], daemon=True).start()
    t0, events, pending, last_result = time.time(), [], list(mid), None

    def note(text):
        events.append(f"{time.time() - t0:5.1f}s {text}")

    def send(text):
        p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        p.stdin.flush()
        note(f">>> {text}")

    send(TASK)
    while time.time() - t0 < 180:
        try:
            line = lines.get(timeout=1)
        except queue.Empty:
            if last_result and time.time() - last_result > 8:
                break
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        kind = d.get("type")
        if kind == "assistant":
            for b in d["message"]["content"]:
                if b["type"] == "tool_use":
                    note(f"TOOL {json.dumps(b['input'], ensure_ascii=False)[:80]}")
                    if pending:  # send the mid-task messages while Claude works
                        time.sleep(2)
                        for m in pending:
                            send(m)
                            time.sleep(1.5)
                        pending = []
                elif b["type"] == "text":
                    note(f"CLAUDE {b['text'][:300]}")
        elif kind == "system" and d.get("subtype") == "informational":
            note(f"NOTICE {str(d.get('content'))[:300]}")
        elif kind == "result":
            last_result = time.time()
            note("RESULT")
    p.stdin.close()
    try:
        p.wait(timeout=20)
    except subprocess.TimeoutExpired:
        p.kill()
    decisions = LOG.read_text().splitlines()[n0:] if LOG.exists() else []
    script = cwd / "fizzbuzz.py"
    printed = subprocess.run([sys.executable, str(script)], capture_output=True, text=True).stdout.split() if script.exists() else []
    print(f"\n===== {name} ({time.time() - t0:.0f} s)")
    print("decisions:", [d.split(" ", 2)[2] for d in decisions] or "none")
    print("fizzbuzz: ", f"{len(printed)} lines" if printed else "missing")
    print("\n".join(events))
    sys.stdout.flush()


if __name__ == "__main__":
    chosen = sys.argv[1:] or list(SCENARIOS)
    for name in chosen:
        run(name, SCENARIOS[name])
