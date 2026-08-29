# claude-plan-optimizer

Picks the right model at the right reasoning effort for the task in front of it,
so the strongest model stops being spent on changing a colour.

```
$ planopt explica "muda a cor do botao pra azul"
Faixa: barata   (-1)

Por quê:
  +1  pede obra, não conversa
  -2  edição mecânica: a resposta está no próprio pedido

$ planopt candidatos "muda a cor do botao pra azul"
  ollama       local          (padrão do agente)
  groq         gratis         openai/gpt-oss-20b
  openrouter   gratis         poolside/laguna-s-2.1:free
```

## Why it exists

Ten free models were given the same button-colour edit. Nine got it right —
including one with 2.6 billion parameters. On a task that size competence is not
the variable; cost is, and the spread between the cheapest and the most wasteful
answer was 4× in tokens ([the measurement](docs/MODELOS-GRATIS.md)).

So the useful question is not "which model is best available" but **which is the
cheapest that certainly gets this right** — and answering it needs no model at
all, which is the whole point: a classifier that calls an LLM to decide which LLM
to call has already lost.

## How it decides

Four tiers — `trivial`, `barata`, `media`, `cara` — from a scored set of local
signals: unknown-cause defects, open scope, architecture decisions, risk,
distinct product areas touched, and the discounts that make a request cheap
(a named file and line, a mechanical edit, a plain question).

The cut points are not taste. They come from a sweep over 120 hand-labelled real
requests, choosing the bands where the classifier can commit without risk:

| band | share of requests | what it means |
|---|---|---|
| score ≤ 0 | 23% | provably cheap — **none was actually expensive** |
| score ≥ 5 | 25% | 83% genuinely medium or expensive |
| in between | 52% | the text does not decide — so nothing is changed |

That middle band is deliberate. A router that has an opinion about everything is
wrong about everything; this one stays quiet where it does not know.

### Two rules that shape the whole design

**Errors are not symmetric.** Sending easy work to a big model wastes tokens.
Sending hard work to a small one produces a plausible wrong answer that nobody
notices until later. So ties break upward — except at the entrance to the most
expensive tier, where breaking upward *is* the waste this project exists to
remove. Measured on the labelled corpus: **zero expensive tasks routed to a small
model.**

**Continuations are not classifiable.** `continua`, `dale`, `ok`, `.`, `b` — 22%
of real messages — say nothing about cost, because the work is whatever was
already running. They are detected and excluded rather than guessed at. The
mirror case matters too: `ok, agora refaz o backend inteiro` starts with `ok` and
is the most expensive request in the set.

## Enforced or advisory — the honest table

Claude Code's session model **cannot be changed programmatically**. No hook
output field sets it, there is no `$CLAUDE_MODEL`, and a `UserPromptSubmit` hook
cannot rewrite the prompt. Any tool claiming to "switch your model mid-session"
is lying. What is real:

| surface | mechanism | strength |
|---|---|---|
| subagents | `model` and `effort` per invocation | **enforced** — and this is where the tokens actually go |
| agent CLIs (`ia-team`) | the flags go straight into argv | **enforced** |
| session start | `claude --model X --effort Y` | enforced, once |
| running session | a hook line saying what this deserves | advisory |
| the narrow guard | block only when an expensive model meets a provably cheap task | interrupts, then it is up to you |

The status line does double duty as the sensor: it is the only place Claude Code
reports `model.id` and the five-hour usage percentage on every frame, so it
writes them down and the hook reads them. Without it the hook cannot tell that
the expensive model is the one changing a colour.

## Install

```bash
git clone https://github.com/NspxMiguel/claude-plan-optimizer
cd claude-plan-optimizer && ./install.sh
```

Adds `planopt` to `~/.local/bin`, installs the skill, and appends the hook to
`settings.json` without touching anything already there. An existing status line
is kept, not replaced.

## Use

```bash
planopt classifica "<request>"          # the tier
planopt explica    "<request>"          # the tier, and every signal that fired
planopt escolhe subagente "<request>"   # model + effort for that target
planopt candidatos "<request>"          # everyone who can do it, cheapest first
planopt modo aviso|guarda|mudo          # how loud the hook is
planopt idioma pt|en
```

Three modes. `aviso` speaks up and never interrupts. `guarda` also interrupts, in
exactly one case: an expensive model meeting a confidently cheap task. `mudo`
classifies and records without saying anything, for measuring against your own
requests before changing how you work.

## Free tiers are queues, not services

Every free target is a fall-through list, never one id. In one measurement four
of sixteen free models were unavailable, and a different four half an hour
earlier. One model per tier is an agent that does not work half the time.

Two related traps the mapping encodes:

- **Reasoning models are wrong for trivial work even when free.** One spent 484
  tokens writing a thinking process to replace a hex value, against 113 for a
  plain model. That is the same waste as an expensive model, one floor down.
- **DeepSeek is not free**, and it looks like it is. Its own API has always been
  billed, and OpenRouter's `deepseek-*:free` is gone. It stays in the map marked
  as paid so it is never picked automatically.

## Language

Portuguese and English from the first line printed. The system language decides
the default, `PLANOPT_LANG` forces one, and `planopt idioma` persists a choice.

## Layout

```
planopt/classificador.py   the scoring, the bands, the asymmetry
planopt/lexico.py          the signals, pt + en in one pattern each
planopt/mapeamento.json    tier -> model + effort, per target. Data, editable.
planopt/estado.py          config, and the status-line-to-hook bridge
bin/planopt                the CLI, the hook, the status line
skill/SKILL.md             what an agent should do with all of this
docs/MODELOS-GRATIS.md     the measurement the cheap tiers rest on
```

## Licence

MIT.
