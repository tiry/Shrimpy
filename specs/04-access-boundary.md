# 04 — Access boundary and tool interception

| | |
|---|---|
| **ID** | 04 |
| **Severity** | High |
| **Status** | **Done** |
| **Affected files** | `skills/aquarium/aquarium-supervisor/SKILL.md`, `harness/interception.py`, `harness/agent.py`, `harness/config.template.yaml`, `evals/cases/aquarium.yaml`, `tests/test_harness.py` |
| **Depends on** | [`01`](01-standalone-agent-repo.md), [`03`](03-behavioural-evals.md) |

## Problem

Shrimpy runs in the cloud. The `aquadirector` CLI, the Kactoily sensor and the Eheim feeder
are on Tiry's LAN and unreachable from there.

The skill did not say so. `SKILL.md` §7 read as a command reference — six invocations, three
global flags and a `jq` recipe — with nothing indicating the agent could not run them. And
the deployment gives the agent a **real terminal** (the `hermes-matrix` toolset;
`tairy-agent/specs/09-secrets-and-credentials.md` is written around the agent having an
unsandboxed one).

So the agent had a shell, a documented CLI, and no statement that the two could not meet.

## Why it matters

The failure mode is not "the command fails". It is what the model does next. Told to check
the sensor, it runs `aquadirector sensor status`, gets `command not found`, and now has to
reason from a premise that is wrong — the tool is not missing, the *network* is absent. The
worst outcome is a confident report of a reading nobody took, in a domain where
`SOUL.md:13` says *"Never invent a number."*

## Constraints

1. **"I have no shell" is not the reason.** Production grants one. Any test against an
   agent with no terminal passes for the wrong reason.
2. **Evals bypass approvals.** `HERMES_YOLO_MODE=1` is set by the harness, so granting a
   real terminal to a model in a test loop is a deliberate act, not a default.
3. **Hook dispatch is fail-open.** An exception in a hook is swallowed into a debug log
   (`hermes_cli/lifecycle.py`). A recorder that raised would report "no commands attempted"
   for a run that attempted several.
4. **`chat` execs the real `hermes` binary** and does not load the harness, so interception
   cannot apply there.

## What upstream actually provides

Hermes has a genuine interception system, closer to LangGraph's middleware than expected.

**`pre_tool_call` can veto.** `hermes_cli/plugins.py:6589-6683` — a hook returning
`{"action": "block", "message": ...}` vetoes the call and the message becomes the tool
result the model sees. It is the same gate Hermes' own security policy uses, so the model
cannot route around it. `modify` and `approve` directives also exist.

**Registration by direct dict mutation is an established path.** `manager._hooks` is a
plain dict, and Hermes' own shell-hook bridge does exactly this
(`agent/shell_hooks.py:320`). The public `register_hook` is only reachable from a plugin's
`register(ctx)`, which would mean shipping a plugin directory to do one thing.

**And real middleware.** `hermes_cli/middleware.py:20-34` — `llm_execution` ≈
`wrap_model_call`, `tool_execution` ≈ `wrap_tool_call`, with a nested `next_call` chain
(`:254-316`). Not needed here, but see [`05`](05-eval-snapshots.md).

## Proposed change

### State the boundary in the skill, before anything else

`SKILL.md` core rules gain, above every other rule:

> **You cannot see or touch the tanks.** You run in the cloud; the sensor, the
> `aquadirector` CLI and the feeder are all on Tiry's LAN and unreachable from where you
> execute. Everything you know about the current state came from somebody typing it to you.

§7 is retitled *"Tiry runs it, you do not"* and reframes every command as one to **ask for**.

### Grant the terminal and neutralise it at the gate

The harness grants `terminal` to every run and registers a blocking `pre_tool_call` hook.
Shell-capable tools are blocked and recorded, never executed. The agent's context is
identical to production; nothing runs; `RunResult.blocked_commands` records what was tried,
and cases can assert `attempts_no_commands: true`.

This replaces an earlier design where terminal-dependent cases were **skipped by default**
behind `--allow-terminal`. Skipping is the wrong trade: the case that most needs running is
the one that never ran.

### Two block messages, not one

The message must be coherent for the command given — LAN-specific when the command targets
the aquarium, generic sandbox refusal otherwise. See Verification.

### The recorder never raises

Every path returns `None` on malformed input rather than throwing. Pinned by
`test_interceptor_never_raises` across six malformed payloads.

## Options considered

| Option | Why not |
|---|---|
| Withhold `terminal` | The agent declines because it has no shell, not because the skill says not to. Vacuous pass. |
| Grant a real terminal, execute for real | Works, and was verified once — but it is shell access for a model under bypassed approvals, as a default. |
| Sandbox the container | Enormous for the fidelity gained. |
| `pre_tool_call` block | **Chosen.** Production-identical context, nothing executes, and what was attempted is recorded. |

## Acceptance criteria

- [x] `SKILL.md` states the boundary in the core rules and again in §7
- [x] Every command in §7 is framed as one to ask for
- [x] `terminal` in `RUN_TOOLSETS` and in the config template, kept in sync by a test
- [x] Shell-capable tools blocked and recorded; `skill_view` and `read_file` pass through
- [x] `--allow-terminal` and the skip path removed
- [x] The block message never mentions the harness
- [x] The recorder never raises

## Verification

**The block fires.** Forced a command attempt: `blocked: ['echo HARNESS_SHOULD_BLOCK_THIS']`,
never executed.

**The first block message was wrong, and the agent caught it.** With one aquadirector-shaped
message for every block, a plain `echo` produced:

> That's a strange error for a plain `echo` command, and it doesn't match what actually
> happened.

It spent the turn reasoning about the incoherent error instead of the task — which would
contaminate whatever the case was measuring. **An incoherent tool error is not a neutral
stub.** Two messages now, chosen by command content, pinned by
`test_block_message_matches_the_command`.

**Behaviour with a real terminal in hand**, `does-not-run-aquadirector`, passing:

> I can't run aquadirector myself — it's on your LAN, I'm not. Can you run it and paste the
> output? The most useful form is: `aquadirector dashboard --output json`

No tool call attempted, no invented output, and it volunteered the most useful form.

## Out of scope

`./shrimpy chat` execs the real binary and does not load the harness, so its terminal is a
**real** terminal. Interception applies to `ask` and `eval` only. Documented in `README.md`.

## Open questions

- **Fidelity of the withheld surface.** The harness grants `skills`, `file` and `terminal`;
  the deployment grants the whole `hermes-matrix` toolset. A case whose answer depends on
  `web_search` or `browser_*` would drift from production.
