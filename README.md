<p align="center">
  <img src="assets/banner.png" width="100%" alt="bouncer, a Claude Code plugin. Not on the list? Wait in line. “stay on Python 3.9, no match/case”: in. “actually, only from 1 to 15”: in. “what’s the capital of Australia?”: later.">
</p>

<p align="center">
  <img src="assets/stickers.svg" width="780" alt="your words, untouched · never loses a message · fails open · made with Claude">
</p>

<p align="center">
  <b>You hand Claude a long task. Two minutes in, a thought hits you.</b><br>
  Send it now and you might knock the work off course. Keep it for later and you’ll forget it.<br>
  <b>bouncer</b> stands at the door: what matters gets in now, the rest waits in line until the task is done.
</p>

<p align="center">
  <img src="assets/demo.svg" width="100%" alt="Animated demo: Claude works on a task behind a door guarded by bouncer. ‘stay on Python 3.9’ is stamped IN and goes straight to Claude. ‘what’s the capital of Australia?’ is stamped LATER and waits in line. ‘only from 1 to 15’ is stamped IN. When the task is done, bouncer reads his list and hands the held message over.">
</p>

## Who gets in

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/let-in.svg" width="150" alt="Thumbs up"><br>
      <b>Needed now: gets in</b><br>
      <sub>A correction, a constraint, “stop”, an answer to Claude’s question. Claude gets it at its next step.</sub><br><br>
      <code>stay on Python 3.9, no match/case</code><br>
      <sub>⚡ Let through now.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/held.svg" width="150" alt="Raised hand"><br>
      <b>Can wait: held</b><br>
      <sub>A new task, an unrelated question. It waits outside instead of interrupting.</sub><br><br>
      <code>what’s the capital of Australia?</code><br>
      <sub>⏸ Held until the task is done.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/handover.svg" width="150" alt="Reading the list"><br>
      <b>Task done: handed over</b><br>
      <sub>Before Claude stops, bouncer hands it the held messages, and Claude takes care of them.</sub><br><br>
      <code>▶ handing over 1 held message</code><br>
      <sub>“Canberra. And the refactor is done.”</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/resent.svg" width="150" alt="Shrug"><br>
      <b>Changed your mind? Send it again</b><br>
      <sub>A held message sent a second time gets straight in.</sub><br><br>
      <code>what’s the capital of Australia?</code> ×2<br>
      <sub>⚡ Let through now: you sent it twice.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/error.svg" width="150" alt="Crooked glasses"><br>
      <b>Something broke: it gets in anyway</b><br>
      <sub>If the triage fails, your message goes through as usual, and you are told once.</sub><br><br>
      <code>⚠ bouncer could not triage this message</code><br>
      <sub>It went through as usual.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/idle.svg" width="150" alt="Coffee break"><br>
      <b>Claude isn’t working: off duty</b><br>
      <sub>Messages sent between tasks are left alone.</sub><br><br>
      <code>thanks! now add tests</code><br>
      <sub>A normal message, no triage.</sub>
    </td>
  </tr>
</table>

## How it decides

<p align="center">
  <img src="assets/flow.svg" width="100%" alt="1. You type while Claude works. 2. bouncer takes a look: Claude Haiku reads your message next to the task. 3. If it changes the task, it gets in right away; if it can wait, it waits in line and is handed over when the task is done.">
</p>

- **In, right away** if it changes the work in progress: a correction, a constraint, a detail, an answer to Claude, a request to stop or change course, a “looks good, carry on”. A short note goes with it only when Claude could misread it otherwise.
- **The line** if it can wait for the end: a separate task, an unrelated question, an idea for later, a follow-up to a message already waiting.
- **In, when in doubt.** An ambiguous message gets in with a note that lists the possible readings. Claude carries on with what is not affected and asks you at the end.
- **Short messages skip the triage.** Three words or fewer (“stop”, “no, the other one”) get in at once: no model call, no wait.
- **The line listens.** “Forget my question about Australia” takes that message out of the line, and nothing else happens.
- **Off duty** when Claude isn’t working: your message is just a message.

Measured on 29 labelled messages (`tests/eval.py`): no message that was needed now got held, every withdrawal hit the right message, and a triage takes about 4 seconds.

## Commands

| While Claude works, type | Between tasks | Effect |
| --- | --- | --- |
| `bouncer status` | `/bouncer:status` | Who is waiting, and today’s numbers. Answered at once, without the model. |
| `bouncer release` | `/bouncer:release` | Lets everyone in now: Claude handles the waiting messages at its next step, then carries on. |
| `bouncer clear` | `/bouncer:clear` | Empties the line without handing the messages over. |
| `bouncer pause` · `bouncer resume` | `/bouncer:pause` · `/bouncer:resume` | Turns the triage off, then back on, for the current session. |

Why two forms: Claude Code keeps slash commands until the task is over, while a plain message reaches bouncer at Claude’s next step.

## Install

**1 · Add the plugin.** In Claude Code:

```
/plugin install bouncer --marketplace simonvoltalis/bouncer
```

<details>
<summary>Claude Code older than 2.1.275</summary>

```
/plugin marketplace add simonvoltalis/bouncer
/plugin install bouncer@bouncer
```
</details>

**2 · Keep working.** There is nothing to set up. Send messages while Claude works, and watch for ⚡ (let through) and ⏸ (held).

Works in the terminal, in VS Code and in the desktop app. You need Claude Code, signed in (tested with 2.1.331), and Python 3.9 or later on your PATH (`python3`, or `python` on Windows).

## Options

| Option | Default | Effect |
| --- | --- | --- |
| Triage model | `haiku` | `haiku` or `sonnet`. Haiku is the fastest and cheapest. |
| Triage time limit | `12` seconds | From 4 to 30. Past this, the triage gives up and your message gets in. |
| Language of notices | `auto` | `auto` (follows your system), `en` or `fr`. The triage explanations always follow the language of your message. |

Change them with `/plugin configure bouncer@bouncer`, or in `/config`. Turn the plugin off with `claude plugin disable bouncer@bouncer`.

## Behind the door

- **Your words, untouched.** Claude always receives your original message. bouncer can only add a note next to it, capped at 300 characters and marked as an automatic suggestion that your own words override.
- **Never loses a message.** A held message is handed over when the task ends. If the task is interrupted first, it is added to your next message.
- **Fails open.** Error, timeout or doubt: your message gets in as if bouncer weren’t there. The first failure of a session is shown, so a broken setup never goes unnoticed.
- **Sends the minimum.** Only messages sent mid-task are triaged, by Claude Haiku through your own Claude Code account. With them goes a short extract of the recent work: your messages, Claude’s messages, and the names of the tools Claude used with a file path or a description. Never full commands, file contents or tool results. Nothing goes anywhere else.
- **Writes the minimum.** One small state file per session, holding held messages in clear text until they are handed over (abandoned sessions are cleaned up after 7 days), and a log of decisions with no message content: `~/.claude/plugins/data/bouncer-bouncer/log.txt`.
- **Light.** With nothing to sort, each hook takes about 60 ms. A triage is one small Haiku request of about 4 seconds, counted in your usage. The log stays under 256 KB.
- **Knows when it is lost.** If Claude Code changes its transcript format and bouncer can no longer tell whether Claude is working, it says so once and lets every message through.
- **Stays out of subagents.** Their messages and stops are left alone.

## Known limits

- Claude Code only hands a mid-task message over between two of Claude’s actions. During a long command, your message waits.
- When held messages are handed over, Claude Code may show a “stop hook” notice. That is expected: it is how bouncer keeps Claude going.
- To know whether Claude is working, bouncer reads Claude Code’s session transcript, whose format is not a public API. If bouncer misbehaves after a Claude Code update, turn it off.
- Used for real on macOS. Linux and Windows are covered by the automated checks, not by real use yet.
- A note still shows up now and then on a message that was clear enough on its own (2 or 3 out of 29 in the test set).

<details>
<summary><b>What’s in the repository</b></summary>

```
hooks/           bouncer.py (the whole plugin) and hooks.json
commands/        /bouncer:status, release, clear, pause, resume (answered by the hook)
tests/
  check.py       logic checks against fake events, no model call (--live: three real triages)
  eval.py        triage quality on the labelled messages in cases.json
  e2e.py         real Claude Code sessions with messages sent mid-task
assets/          banner, mascot, README visuals and the maker's stamp
  mascot.py      draws the mascot in every pose
  readme.py      builds stickers.svg, flow.svg and the animated demo.svg, fonts embedded
  fonts/         Bricolage Grotesque and JetBrains Mono, with their OFL licenses
.claude-plugin/  plugin and marketplace manifests, icon
.github/         checks on Linux and Windows on every push (macOS locally); a release for every vX.Y.Z tag
CHANGELOG.md     what changed in each version
```

</details>

## Tests

```bash
python3 tests/check.py            # logic, no model call
python3 tests/check.py --live     # plus three real triages by Haiku
python3 tests/eval.py             # triage quality on 29 labelled messages (about a minute)
python3 tests/e2e.py              # real sessions with messages sent mid-task (a few minutes)
python3 assets/mascot.py assets   # redraws the mascot
python3 assets/readme.py          # rebuilds the README visuals
```

Releasing: add the version to `CHANGELOG.md` and to `.claude-plugin/plugin.json`, then push a `vX.Y.Z` tag. GitHub runs the checks and publishes the release with its notes.

## Credits

- **Bricolage Grotesque** © The Bricolage Grotesque Project Authors · **JetBrains Mono** © The JetBrains Mono Project Authors. Both under the [SIL Open Font License 1.1](https://openfontlicense.org), embedded in this README’s visuals; the license texts are in `assets/fonts/`.
- The mascot is drawn in code (`assets/mascot.py`), with no image generator.

<br>

<p align="center">
  <img src="assets/jouanique-industries.webp" width="320" alt="Jouanique Industries"><br>
  <sub>Code and drawings made with the help of Claude (AI).</sub>
</p>
