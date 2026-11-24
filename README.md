# bouncer

A Claude Code plugin that decides which of your messages may interrupt Claude while it works.

You send a message while Claude is busy. bouncer has a quick look at it:

- **Needed now** (a correction, a constraint, "stop", an answer to Claude's question): it gets in at Claude's next step, with a short note when its link to the task is not obvious.
- **Can wait** (a new task, an unrelated question): it is held, then handed to Claude once the task is done.
- **Changed your mind?** Send a held message again and it gets in at once.
- **Doubt, ambiguity or error**: the message gets in as usual. A held message is never lost: if the task is interrupted, it is added to your next message.

Claude always receives your original words. bouncer only adds a note; it never rewrites your message.

Works in the terminal, in VS Code and in the desktop app.

## Install

```
/plugin install bouncer --marketplace simonvoltalis/bouncer
```

On Claude Code versions older than 2.1.275:

```
/plugin marketplace add simonvoltalis/bouncer
/plugin install bouncer@bouncer
```

## Requirements

- Claude Code, signed in (tested with 2.1.331).
- Python 3.9 or later on your PATH (`python3`, or `python` on Windows).

## Privacy and cost

- Each message you send mid-task is judged by Claude Haiku, through your own Claude Code account. The request holds your message and a short extract of the recent work: your messages, Claude's messages, and the names of the tools Claude used with a file path or a description. Never full commands, file contents or tool results. Nothing is sent anywhere else.
- Each triage is a small Haiku request, counted in your usage. It takes 4 to 8 seconds, and only happens for messages sent while Claude is working.
- Held messages are stored in clear text in the plugin's data folder until they are handed over. Files left by abandoned sessions are deleted after 7 days.
- A log of decisions, with no message content, is kept in the same folder: `~/.claude/plugins/data/bouncer-bouncer/log.txt`.

## Limits

- Claude Code only hands a mid-task message over between two of Claude's actions. During a long command, your message waits.
- When held messages are handed over at the end of a task, Claude Code may show a "stop hook" notice. That is expected: it is how the plugin keeps Claude going.
- To know whether Claude is working, bouncer reads Claude Code's session transcript, whose format is not a public API. If bouncer misbehaves after a Claude Code update, disable it.
- Windows is covered by the automated checks but has not been tried in a real session yet.

## Turn it off

```
claude plugin disable bouncer@bouncer
```

## Development

- `python3 tests/check.py`: logic checks, no model call (also run on Linux, macOS and Windows on every push).
- `python3 tests/check.py --live`: plus three real triages.
- The model and timeouts are constants at the top of `hooks/bouncer.py`.

## License

MIT
