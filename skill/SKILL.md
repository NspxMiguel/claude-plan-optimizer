---
name: plan-optimizer
description: Pick the right model at the right reasoning effort for the task in front of you, instead of spending the strongest model on everything. USE THIS BEFORE spawning any subagent, before starting a fan-out, and whenever a task looks small — a colour change, a rename, a typo, a one-file edit. Also use when the user says "economiza", "poupa meu plano", "que modelo usar", "ta gastando muito", "usa um modelo menor", "which model", "save my quota", "use a cheaper model", or when a session is burning an expensive model on mechanical work.
---

# Spend the model the task deserves

A colour change does not need the strongest model. That is not a guess: ten free
models were given the same button-colour edit and nine got it right, including
one with 2.6 billion parameters (`docs/MODELOS-GRATIS.md`). On work that size,
competence is not the variable — cost is, and the spread is 4×.

So the question is never "what is the best model available". It is **what is the
cheapest thing that certainly gets this right**.

## Two axes, and they are not the same

> **Difficulty picks the strength. The wallet picks who pays.**

A task being expensive does not mean "spend Opus". Inside a team of agents it
means "spend the strongest one that is *not* billed to the metered plan" —
another vendor's free tier before the plan you are trying to protect. Get these
two confused and you will burn the expensive wallet while congratulating
yourself on routing.

## Ask first, then act

```bash
planopt classifica "<the request>"     # trivial | barata | media | cara
planopt explica    "<the request>"     # and why, feature by feature
planopt escolhe subagente "<request>"  # model + effort for a subagent
planopt candidatos "<request>"         # everyone who can do it, cheapest first
planopt pressao                        # how much of the metered window is left
```

`planopt` never calls a model to decide which model to call — that would be
absurd. It is local, instant, and deterministic.

## What the four tiers mean for you

| tier | what it is | subagent | fan-out |
|---|---|---|---|
| `trivial` | the answer is inside the request | `haiku`, `low` | free tier, or do it inline |
| `barata` | one bounded change, no decision | `haiku`, `medium` | free tier |
| `media` | needs reading and care | `sonnet`, `high` | `haiku` for the reading, `sonnet` to write |
| `cara` | architecture, unknown cause, risk | `opus`, `high` — **one, never a fleet** | `haiku` wide, `opus` alone at the end |

`xhigh` and `max` are never chosen automatically. They multiply thinking tokens,
and no local signal separates "hard" from "very hard" well enough to spend that
on a guess. They stay hand-typed.

## Continuation is not a tier

`continua`, `dale`, `vai`, `ok`, `.`, `b` — in a real corpus these are 22% of
messages, and **their text says nothing about cost**. The work is whatever was
already running. When `planopt` reports a continuation, change nothing: do not
downgrade the model because the message was short. The cheapest sentence to type
can be the continuation of the most expensive task in flight.

The mirror of that rule matters just as much: `ok, agora refaz o backend inteiro`
opens with `ok` and is the most expensive thing in the list. A leading
acknowledgement does not make a request cheap.

## The rules that actually save the plan

**Never fan out in the strong model.** A wide fan-out of readers, searchers and
cataloguers is `haiku` — always. The strong model comes in once, alone, on top of
what the cheap ones already reduced. If a fan-out stage seems to need the strong
model, the fix is a narrower fan-out, not a bigger model.

**Classify before you spawn, not after.** The `model` parameter on a subagent is
enforced; the model of a running session is not. Choosing at spawn time is the
only place the choice is real.

**Reasoning models are the wrong shape for trivial work, even when free.** One
free reasoning model spent 484 tokens writing out a thinking process to replace
a hex value, against 113 for a plain one. When the answer is already in the
request, thinking is pure cost — the same waste as an expensive model, one floor
down. `mapeamento.json` lists these under `evitar_em_trivial`.

**A free tier is a queue, not a service.** Free models return 429 constantly and
unpredictably — in one measurement four of sixteen were down, and a different
four half an hour earlier. Always take the fall-through list, never a single id.

**Escalate on failure, do not pre-escalate on doubt.** If the cheap model gets it
wrong, redo it on the strong one — that costs one cheap attempt. Sending
everything to the strong model to avoid ever redoing anything costs the plan.

## Check the window before a big fan-out

`planopt pressao` reads the same five-hour/seven-day usage the status line
already shows. When it comes back `critica`, treat the metered account (the
main session and its subagents) as reserved for what only Claude can do, and
push everything else — `media` included — to `team`'s free/local targets
first: `ollama`, `groq`, `openrouter`, `gemini`, `antigravity`, `opencode`, or
`codex` on its own account. `planopt candidatos "<request>"` gives the full
fall-through list for the tier; `planopt pressao` gives the one-line version
for whichever tier is loudest right now. This is what makes a Pro-level plan
last like a Max one: not spending less per task, spending it on a different
account when the window is the thing running out.

## When to ignore all of this

When the user names a model, they named it. When the work is genuinely the last
mile of something already expensive, keep the strong model rather than switching
mid-thought and losing the thread. And when `planopt` reports low confidence —
it says so — treat it as no opinion, not as an instruction.
