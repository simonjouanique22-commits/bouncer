# Changelog

## 0.4.0 — 2026-11-24

- **Commands**: status, release, clear, pause and resume. Type `bouncer status` while Claude works (Claude Code keeps slash commands until the task is over), or `/bouncer:status` between tasks. All but release are answered at once, without calling the model.
- **Short messages skip the triage**: three words or fewer get in at once.
- **The triage sees the line**: “forget my question” takes a waiting message out of it, and a follow-up to a waiting message joins it.
- **Fewer notes**, and an ambiguous message no longer stops Claude: it carries on with what is not affected and asks at the end.
- **Options**: triage model, time limit, language of notices (English or French), set with `/plugin configure`.
- **Steps aside** and warns once when it does not recognise Claude Code’s transcript.
- The log stays under 256 KB.
- **Tests**: a set of 29 labelled messages (`tests/eval.py`) and a script for real sessions (`tests/e2e.py`). On the test set, compared with 0.3.0: messages wrongly held 1 → 0, messages wrongly let in 4 → 0, unneeded notes 15 → 2 or 3, median triage 5.8 s → 4.3 s.
- Releases are published by GitHub for every `vX.Y.Z` tag. Automated checks run on Linux and Windows; macOS is checked locally.

## 0.3.0 — 2026-11-24

- The bouncer mascot, drawn in code, with one expression per plugin state.
- A new README: banner, animated demo, entry tickets, decision flow.
- New plugin icon.

## 0.2.0 — 2026-11-24

- First published version, in English.
- Windows support (file locking, encodings, `python` when `python3` is missing).
- A held message sent again gets in at once.
- Triage failures are shown once per session instead of passing silently.
- MIT license.
