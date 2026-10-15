# clingo_asp: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how clingo
(Answer Set Programming) expresses it. Runner: [run.py](run.py), which turns the instance
into facts, grounds them with the submission, solves through the clingo Python API and
reads the declared outputs back from the shown atoms.

## Submission file

One ASP program, `model.lp`, in plain clingo syntax. No other file is staged, so it
cannot `#include` one; `#script` is unavailable (see [Traps](#traps)).

## Entrypoint

There is no function. The runner prepends the instance facts to the program text, adds
both as the `base` program, grounds `base` once, and solves. Write ordinary rules,
constraints, `#show` and optimisation statements; no `#program` sections are needed.

## Instance

Every JSON field becomes ground facts, **index positions first, value last**, with
0-based indices and one index per list level:

| JSON | Facts |
| --- | --- |
| `"n": 12` | `n(12).` |
| `"demand": [250, 255]` | `demand(0,250). demand(1,255).` |
| `"rules": [[3,1],[2]]` | `rules(0,0,3). rules(0,1,1). rules(1,0,2).` (ragged is fine) |
| `"flag": true` | `flag(true).` (the constants `true` / `false`) |
| `"word": "AB"` | `word("AB").` plus `word_char(0,"A"). word_char(1,"B").` |
| `"words": ["AB","C"]` | `words(0,"AB"). words(1,"C").` plus `words_char(0,0,"A"). words_char(0,1,"B"). words_char(1,0,"C").` |

- **Names**: the first character after any leading underscores is lowered, because a
  capital starts an ASP variable: `N` gives `n/1`, `NUM_CELLS` gives `nUM_CELLS`, `_SHIP`
  gives `_sHIP`. A name with characters other than letters, digits and `_`, or two fields
  that collide after lowering, is refused (`error`).
- **Strings** arrive whole as quoted string terms and, in addition, one `<pred>_char`
  fact per character: the string's list indices, then the 0-based character position,
  then the one-character string. An empty string gives no `_char` facts. A field whose
  name equals another field's `_char` predicate is refused.
- **Empty lists give no facts at all**, so the predicate may be absent.
- Only integers, Booleans and strings are accepted as leaves; a float, `null` or nested
  object is refused (`error`).
- Extra fields such as `name` and `note` also arrive (`name/1`, `name_char/2`, ...), so do
  not reuse those predicate names for your own rules.

## Outputs

Each declared output is read from the **shown** atoms of the predicate with the same name,
lowered the same way as instance fields (output `A` is carried by `a`), again index
positions first and value last:

- scalar `length` -> exactly one atom `length(V)`;
- list `queens` -> `queens(I,V)` for every `I` in `0..len-1`;
- 2-D `matrix` -> `matrix(I,J,V)`, and so on for deeper nesting.

Indices must be integers, **0-based and contiguous** at every level, and all atoms of
one output must have the same arity. The value must be an integer or the constant `true`
/ `false` (a Boolean may also be `0`/`1`). The runner rebuilds the nested list. Shown
atoms of other predicates are ignored, so `#show name/k.` for each declared output is
the usual form, but extra shown predicates do no harm.

## Objective

Use clingo's own `#minimize { ... }.` or `#maximize { ... }.` (integer weights, any
priority levels). See [Solving](#solving) for how the runner reaches and enumerates the
optimum.

## Solving

- The runner creates `clingo.Control(["0"])` (all models) and sets
  `solve.opt_mode = optN`; every other clingo setting is the default. It grounds once
  and makes one asynchronous `solve` call.
- With an objective, models whose `optimality_proven` is false are skipped; only proven
  optimal models are reported. Without one, every answer set is a candidate.
- Nothing is added to the program between models: clingo enumerates answer sets itself,
  and the runner drops a model whose declared outputs repeat ones already reported
  (other shown atoms and hidden atoms do not count). It stops at `limit` once enough
  distinct ones are out.
- When clingo has no further model the search is exhausted: `complete` if something was
  reported, `unsat` if no model was found at all, and `timeout` if models with a cost
  were found but none was proven optimal.
- The time budget is `execution_timeout`, counted from before grounding and checked
  while waiting for each model: an expired wait cancels the search and reports
  `timeout`. A grounding that overruns is caught by a backstop timer at
  `execution_timeout` + 5 s, also `timeout`.

## Compilation

No separate step. Grounding runs inside the execution budget (`execution_timeout`, with
a 5 s backstop timer); `compilation_timeout` does not apply.

## Environment

Image `dcp-eval/clingo_asp:v1`: clingo 5.8.2 (pip wheel) on Python 3.12.11. Pure ASP
only; the image installs nothing else (no JSON or other library is reachable from ASP,
and the runner does all JSON reading and writing). There is no `clingo` binary on
`PATH`: the wheel provides the Python module, and `python -m clingo model.lp` is its
command line for ad hoc runs. The evaluator runs the container with no network, a
read-only root file system, user 65534, `HOME=/tmp`, a 512 MiB writable `/tmp` and
`/input` read-only. For an ad hoc run, override the entrypoint: `docker run --rm
--network none --entrypoint sh dcp-eval/clingo_asp:v1 -c 'python -m clingo ...'`.

## Traps

- **No `#script`**: this wheel has no Python or Lua scripting, and `#script (python)`
  raises "python support not available". String handling goes through the `_char` facts.
- **A scalar output shown twice** (`x(1). x(2).`) is an `error` ("several values but no
  index"): make it functional.
- **Index gaps or a non-integer index** (`queens(1,_)` without `queens(0,_)`, or a
  constant as index) are an `error`; shift to 0-based.
- **Two arities under one output name** (`x/1` and `x/2` both shown) are an `error`.
- **Strings with a tab or a non-ASCII character** cannot be loaded: the runner escapes
  strings with JSON rules (`\t`, `\uXXXX`), which clingo does not accept.
- Shown atoms of predicates that are not declared outputs are ignored: an extra `#show`
  neither adds an output nor fails the run.

## Example

The pilot fixture [tests/fixtures/model_clingo.lp](../../tests/fixtures/model_clingo.lp)
(instance fields `n`, `optimize`, arriving as `n/1` and `optimize/1`; outputs `x`, `y`,
shown as `x/1`, `y/1`):

```prolog
val(0..N) :- n(N).
1 { xv(X) : val(X) } 1.
1 { yv(Y) : val(Y) } 1.

% The tiny reference is an equality when not optimizing and a lower bound when it is.
:- xv(X), yv(Y), n(N), optimize(false), X + Y != N.
:- xv(X), yv(Y), n(N), optimize(true), X + Y < N.

x(X) :- xv(X).
y(Y) :- yv(Y).

#minimize { X + Y : xv(X), yv(Y), optimize(true) }.

#show x/1.
#show y/1.
```
