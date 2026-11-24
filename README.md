<p align="center">
  <img src="assets/bouncer.svg" width="260" alt="bouncer, the mascot: a bouncer in a suit, arms crossed">
</p>

<h1 align="center">bouncer</h1>

<p align="center">
  <b>Not on the list? Wait in line.</b><br>
  A Claude Code plugin that decides which of your messages may interrupt Claude while it works.
</p>

<p align="center">
  <a href="https://github.com/simonvoltalis/bouncer/actions/workflows/check.yml"><img src="https://github.com/simonvoltalis/bouncer/actions/workflows/check.yml/badge.svg" alt="checks"></a>
  <img src="https://img.shields.io/badge/Claude_Code-plugin-D7FF3A?labelColor=17131F" alt="Claude Code plugin">
  <img src="https://img.shields.io/badge/license-MIT-C8B6FF?labelColor=17131F" alt="MIT license">
</p>

---

You hand Claude a long task. Two minutes in, a thought hits you. Send it now and you might knock the work off course. Keep it for later and you'll forget it.

**Just send it.** bouncer stands at the door and takes a quick look at every message you send while Claude is busy.

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/let-in.svg" width="150" alt="Thumbs up"><br>
      <b>Needed now: gets in</b><br>
      <sub>A correction, a constraint, “stop”, an answer to Claude’s question. Claude gets it at its next step.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/held.svg" width="150" alt="Raised hand"><br>
      <b>Can wait: held</b><br>
      <sub>A new task, an unrelated question. It waits outside instead of interrupting.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/handover.svg" width="150" alt="Reading the list"><br>
      <b>Task done: handed over</b><br>
      <sub>Before Claude stops, bouncer hands it the held messages, and Claude takes care of them.</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/resent.svg" width="150" alt="Shrug"><br>
      <b>Changed your mind? Send it again</b><br>
      <sub>A held message sent a second time gets straight in.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/error.svg" width="150" alt="Crooked glasses"><br>
      <b>Something broke: it gets in anyway</b><br>
      <sub>If the triage fails, your message goes through as usual, and you are told once.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="assets/states/idle.svg" width="150" alt="Coffee break"><br>
      <b>Claude isn’t working: off duty</b><br>
      <sub>Messages sent between tasks are left alone.</sub>
    </td>
  </tr>
</table>

Claude always receives your own words. bouncer only adds a short note when the link to the task is not obvious. It never rewrites your message, and it never loses one.

## See it at work

```text
❯ refactor the payment module
  ● Edit payment.py

› stay on Python 3.9, no match/case
  ⚡ Let through now. It changes how the code has to be written.

› what's the capital of Australia?
  ⏸ Held until the task is done. Unrelated question, it can wait.
    Need it now? Send it again.

  ● Edit payment.py
  ● Bash pytest -q

  ▶ bouncer: handing over 1 held message(s) to Claude.
  Canberra. And the payment module is refactored, Python 3.9 compatible.
```

## Install

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

Works in the terminal, in VS Code and in the desktop app. You need Claude Code, signed in (tested with 2.1.331), and Python 3.9 or later on your PATH (`python3`, or `python` on Windows).

## How it decides

<details>
<summary>The rules, and what runs where</summary>

<br>

When you send a message while Claude is mid-task, Claude Haiku reads it next to a short summary of the current task and answers four questions, in this order: what does the message say and what does it refer to, does it change what Claude does before the task ends, why, and does Claude need a note to understand it.

- **Gets in now** if it changes the work in progress: a correction, a constraint, a detail, an answer to Claude, a request to stop or change course.
- **Waits** if it can wait for the end: a separate task, an unrelated question, an idea for later.
- **Gets in** whenever there is doubt or the message is ambiguous. In that case the note lists the possible readings instead of picking one.

Under the hood: one Python script on two Claude Code hooks. `UserPromptSubmit` judges messages sent mid-task and holds the ones that can wait. `Stop` keeps Claude going while held messages remain, and hands them over.
</details>

## Privacy and cost

- **What is sent.** Each message you send mid-task goes to Claude Haiku through your own Claude Code account, with a short extract of the recent work: your messages, Claude’s messages, and the names of the tools Claude used with a file path or a description. Never full commands, file contents or tool results. Nothing goes anywhere else.
- **What it costs.** One small Haiku request per message sent while Claude is working, counted in your usage. It takes 4 to 8 seconds.
- **What stays on disk.** Held messages, in clear text in the plugin’s data folder, until they are handed over. Files left by abandoned sessions are deleted after 7 days. A log of decisions, with no message content: `~/.claude/plugins/data/bouncer-bouncer/log.txt`.

## Good to know

- Claude Code only hands a mid-task message over between two of Claude’s actions. During a long command, your message waits.
- When held messages are handed over, Claude Code may show a “stop hook” notice. That is expected: it is how bouncer keeps Claude going.
- To know whether Claude is working, bouncer reads Claude Code’s session transcript, whose format is not a public API. If bouncer misbehaves after a Claude Code update, turn it off.
- Windows is covered by the automated checks but has not been tried in a real session yet.

## Turn it off

```
claude plugin disable bouncer@bouncer
```

## Development

- `python3 tests/check.py` runs the logic checks, with no model call. They also run on Linux, macOS and Windows on every push.
- `python3 tests/check.py --live` adds three real triages.
- The model and timeouts are constants at the top of `hooks/bouncer.py`.
- The mascot is drawn in code: `python3 assets/mascot.py assets` redraws every pose. New expressions are a few lines each.

## License

MIT
