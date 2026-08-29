# Free models on a trivial task — measured, 28/08/2026

The premise of the cheap tiers is that a colour change does not need a good
model. That is a claim, so it was measured rather than assumed.

## The test

Every OpenRouter model whose id ends in `:free` (16 of 396 at the time) was
given the same task, at `temperature: 0`, with a system prompt asking for the
corrected code and nothing else:

> Change the button colour from red to blue. Keep everything else identical.
>
> `.btn { background: #e23b3b; padding: 8px 16px; border-radius: 6px; }`

An answer counts as correct when some hex in the reply has its blue channel
above both others by a clear margin, **and** the padding and border-radius came
back untouched. The first version of that check looked for the literal word
`blue` and a narrow set of hex patterns; it failed `#3b82f6` and `#007bff`,
which are obviously blue, and reported six false failures. Reading the number
instead of matching the text is the difference between measuring the models and
measuring the ruler.

## Result

| model | s | tokens | verdict |
|---|---:|---:|---|
| `poolside/laguna-s-2.1:free` | 3.0 | 113 | correct |
| `inclusionai/ling-3.0-flash-fin:free` | 1.5 | 159 | correct |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1.4 | 200 | correct |
| `minimax/minimax-m2.7:free` | 3.6 | 214 | correct |
| `minimax/minimax-m3:free` | 1.3 | 250 | correct |
| `liquid/lfm-2.5-2.6b:free` | 0.8 | 275 | correct |
| `cohere/north-mini-code:free` | 2.8 | 278 | correct |
| `nvidia/nemotron-3-super-120b-a12b:free` | 3.2 | 302 | correct |
| `nvidia/nemotron-3.5-lightning:free` | 2.8 | 484 | correct, but talked |
| `dots-studio/dots-3-note-preview:free` | 4.8 | 474 | wrong |
| `thinkingmachines/inkling{,-small}:free` | — | — | 403 |
| `poolside/laguna-xs-2.1:free` | — | — | 429 |
| `z-ai/glm-5.2:free` | — | — | 429 |
| `google/gemma-4-{26b-a4b,31b}-it:free` | — | — | 429 |

Nine of the ten that answered got it right, including a 2.6-billion-parameter
model. **On a task this size, competence is not the variable.** Cost is, and
the spread there is 4×.

## Three things this changes in the design

**A reasoning model on a trivial task is the same waste as Opus on a trivial
task, one floor cheaper.** `nemotron-3.5-lightning` spent 484 tokens writing out
a thinking process to replace a hex value; `laguna-s` spent 113 doing it. When
the answer is already in the request, thinking is pure cost. Those models are
listed under `evitar_em_trivial` in `mapeamento.json` and are skipped in the two
cheap tiers even when they are the only free option left.

**A free tier is a queue, not a service.** Four of sixteen were unavailable in
this run, and a different four half an hour earlier — `poolside/laguna-xs-2.1`
answered in 0.6 s in the first run and returned 429 in the second. Every free
tier in `mapeamento.json` is therefore a fall-through list, not a single id. One
model per tier would be an agent that does not work half the time.

**DeepSeek is not free, and it looks like it is.** Its own API has always been
billed, and the `deepseek/deepseek-chat-v3.1:free` that OpenRouter used to serve
is gone: on 28/08/2026 no `deepseek` id in `/api/v1/models` ended in `:free`.
`ia-team`'s OpenRouter adapter was still advertising that retired id in its
`doctor` line. DeepSeek stays in the map marked `paga`, so it is never chosen
automatically.

## Reproducing

The measurement script is not in the repository — it needs an OpenRouter key,
and the results are perishable. What matters is the method, which is three
lines: fetch `/api/v1/models`, keep the ids ending in `:free`, send each one the
same edit and compare tokens. Re-run it when the free list changes, which it
does often.
