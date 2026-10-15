---
name: clingo-asp
description: clingo, an answer set programming (ASP) system with a Python API. Writes rules, choice rules and constraints, grounds and solves them, enumerates answer sets and finds proven optimal ones. Use when writing, debugging or explaining ASP programs, or when the user has chosen clingo for a combinatorial or logic problem.
license: Apache-2.0
compatibility: Requires Python 3.10+ and the clingo package (tested with clingo 5.8.2, MIT licence); no other software, no licence key.
metadata:
  domain: constraint-programming
  solver: clingo
  paradigm: asp
---

# clingo (Python)

clingo grounds a logic program first (every variable is replaced by the values it can take), then searches for answer sets, the stable models of the program. The modeller's main idea: write rules that describe what a valid answer looks like, and let the search find them. Ground size, not search, is usually the bottleneck.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [Optimisation](#optimisation)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- [Runnable examples](#runnable-examples)

## Install

```bash
pip install clingo
python3 -c "import clingo; print(clingo.__version__)"
```

Tested with clingo 5.8.2 on Python 3.12. The package is a CFFI wheel with no licence key or account. Details: [clingo installation](https://potassco.org/clingo/) and the [Python API](https://docs.potassco.org/clingo/python-api/current/).

## Quick start

```python
import clingo

ctl = clingo.Control()
ctl.add("base", [], """
colour(red;green).
node(1..3).
edge(1,2). edge(2,3).
1 { paint(N,C) : colour(C) } 1 :- node(N).
:- edge(A,B), paint(A,C), paint(B,C).
#show paint/2.
""")
ctl.ground([("base", [])])
with ctl.solve(yield_=True) as handle:
    for model in handle:
        print(sorted(str(atom) for atom in model.symbols(shown=True)))
    print("satisfiable:", handle.get().satisfiable)
```

Output: one list of `paint(...)` atoms, then `satisfiable: True`.

## Modelling

Full list: [language reference](https://potassco.org/guide/language/). Every `#` directive is a clingo extension to plain ASP.

| Need | Syntax |
|---|---|
| fact | `p(1).` |
| rule | `q(X) :- p(X).` |
| integrity constraint (must not hold) | `:- p(X), q(X).` |
| choice with bounds | `1 { assign(N,C) : colour(C) } 1 :- node(N).` |
| negation as failure | `not in(A)` |
| integer range | `node(1..N).` |
| arithmetic | `+ - *`, `/` (truncates: `-7/2` is `-3`), modulo `\` (`7\2` is `1`) |
| sum / count / min / max | `#sum { W,I : take(I), weight(I,W) } > C`, `#count`, `#min`, `#max` |
| minimise / maximise | `#minimize { W,I : take(I), weight(I,W) }.`, `#maximize { ... }.` |
| priority levels | `#minimize { 5@2,1 : x(1); 1@1,2 : x(2) }.` (level 2 first) |
| constant | `#const n = 5.` or `Control(["-c", "n=5"])` |
| output | `#show p/2.` shows only `p/2` atoms |

Facts and rules:

- Names starting with a capital are **variables**. Predicates and constants are lowercase. `_SHIP(1).` is a parse error, and so is `-c N=5`; use `_ship`, `n`.
- Every variable must appear in a positive body literal, or the program is unsafe (see [Common issues](#common-issues)).
- Strings are constants in double quotes. The escapes `\"`, `\\` and `\n` parse; `\t` and `\uXXXX` do not. Strings have no built-in length or character access; to inspect characters, write one fact per character.
- Uppercase data (letters, codes) works as strings: `letter("S").`, `val("S",9)`. Read them back with `atom.arguments[0].string`; `str(atom)` shows them in quotes. Strings compare with `<`, as in `L1 < L2`. The cryptarithm example uses this.
- With no `#show` directive every atom is shown. Once one `#show` appears, only the listed signatures are shown. `#show.` alone hides everything.
- Bounds of a choice go outside the braces: `L { ... } U`.

Aggregate elements are **sets of tuples**. Elements with the same tuple count once. With `b(1,5). b(2,5). b(3,7).`:

```prolog
s(S) :- S = #sum { V : b(I,V) }.    % 12: the tuple 5 is counted once, not twice
t(S) :- S = #sum { V,I : b(I,V) }.  % 17: the index makes each tuple unique
c(N) :- N = #count { V : b(I,V) }.  % 2 distinct values, not 3
```

Add a distinguishing term (an index, a position or the name) to every element whose values may repeat. The same holds for weights in `#minimize` and `#maximize`. Negative weights are fine in a sum compared with `!=`, as in the cryptarithm example: `:- #sum { W*D,L : val(L,D), weight(L,W) } != 0.`

A `#sum` or `#count` aggregate cannot be compared with another aggregate: `:- #sum{...} != #sum{...}.` is a parse error. Bind each side first:

```prolog
total_a(S) :- S = #sum { V : a(V) }.
total_b(S) :- S = #sum { V : b(V) }.
:- total_a(A), total_b(B), A != B.
```

## Solving

Settings: [command-line options](https://potassco.org/guide/options) · [Python API](https://docs.potassco.org/clingo/python-api/current/)

| Want | Setting |
|---|---|
| one model (default) | `ctl.configuration.solve.models = 1` |
| every model | `ctl.configuration.solve.models = 0` |
| one model per shown answer | `ctl.configuration.solve.project = "show"` |
| optimisation with proof | `ctl.configuration.solve.opt_mode = "optN"` |
| threads | `clingo.Control(["-t", "4"])` |
| random seed | `ctl.configuration.solver.seed = "7"` or `Control(["--seed=7"])` |

Set options before grounding; pass them to `clingo.Control(...)` or assign them to `ctl.configuration` in a variable. Reading a value back from a temporary `Control` (`clingo.Control(...).configuration...`) crashed the interpreter (exit 139) with clingo 5.8.2 (Python module); keep the object in a variable.

Solve result, from `handle.get()` after the loop ([`SolveResult`](https://docs.potassco.org/clingo/python-api/current/)):

| Attribute | Meaning |
|---|---|
| `satisfiable` | at least one model found |
| `unsatisfiable` | no model exists (proven) |
| `exhausted` | the search finished, so no further models exist |
| `interrupted` | stopped early by `cancel()` or a time limit |
| `unknown` | neither satisfiable nor unsatisfiable (for example, interrupted before any result) |

Reading models: `model.symbols(shown=True)` returns the shown atoms; `atom.name` and `atom.arguments` split them (`atom.number` on an integer argument, `atom.string` on a string, `str(atom)` for the text). `model.contains(clingo.parse_term("q(3)"))` tests one atom. Build terms with `clingo.Function`, `clingo.Number`, `clingo.String` or `clingo.parse_term`. The constants `true` and `false` arrive as `Function` symbols with no arguments.

One model with the default `models = 1`, then check the result:

```python
with ctl.solve(yield_=True) as handle:
    digits = None
    for model in handle:            # at most one iteration with models = 1
        digits = {a.arguments[0].string: a.arguments[1].number for a in model.symbols(shown=True)}
    result = handle.get()
if not result.satisfiable:
    print("no solution")
```

Time limit, run in a background thread and cancelled after `seconds`:

```python
handle = ctl.solve(async_=True, yield_=True)
handle.wait(seconds)
handle.cancel()
result = handle.get()     # result.interrupted is True if the limit hit
```

Errors: a syntax error raises `RuntimeError: parsing failed` from `ctl.add`; an unsafe rule or a grounding error raises `RuntimeError: grounding stopped because of errors` from `ctl.ground`. The detailed message goes to stderr, for example `<block>:1:1-14: error: unsafe variables in: ...`. ASP programs written as Python strings report line and column inside that string.

## Optimisation

Objectives are ordinary `#minimize` or `#maximize` statements. Clingo reports the cost of each model in `model.cost`, a list with one entry per priority level. For `#maximize` the cost is the **negated** value.

Without `opt_mode`, clingo stops at the first model it finds, and that model is not proven optimal (`optimality_proven` is False). Set `opt_mode = "optN"` and clingo keeps improving the model and proves the optimum. With the default `models = 1`, the last model yielded is then the proven optimum:

```python
ctl.configuration.solve.opt_mode = "optN"    # models = 1 is the default
with ctl.solve(yield_=True) as handle:
    best = None
    for model in handle:                     # improving models; the last one is optimal
        best = model
    result = handle.get()
optimal = result.exhausted and best is not None and best.optimality_proven
# best.cost[0] is the optimum; negate it for #maximize
```

`models = 0` with `optN` also yields every optimal model, and it has to search for all of them. On a 6x6 job shop (ft06, optimum 55) an independent run with `models = 0` timed out at 120 s, while `models = 1` with `optN` proved the optimum in about 23 s. Use `models = 0` only when every optimal model is wanted (see [All solutions](#all-solutions)); then keep the models whose `optimality_proven` is true.

If the solve is interrupted by a time limit, the last model may be unproven. Check `optimality_proven`: an unproven model is only the best found so far.

Worked, runnable examples: [assets/maximise](assets/maximise/README.md), [assets/minimise](assets/minimise/README.md), [assets/scheduling](assets/scheduling/README.md).

### Scheduling at scale

The [scheduling example](assets/scheduling/README.md) gives each task one start time in `time(0..H)` and forbids overlaps pairwise. Grounding and search both grow with the number of tasks and with `H`. Ways to keep them small:

- **Horizon.** The sum of all durations is always a valid makespan bound for one machine or a job shop, since everything can run in sequence. A smaller `H` shrinks the domains but can exclude the optimum; use it only when a feasible makespan at or below `H` is known.
- **Tighter domains.** Limit each start to times where the task still ends inside the horizon:

  ```prolog
  1 { start(T,S) : time(S), S + D <= H } 1 :- task(T), dur(T,D), h(H).
  ```

- **Models.** Use `opt_mode = "optN"` with `models = 1`, as above. In that measurement, `models = 0` was the cause of the timeout; the domain limit alone did not change the 120 s run.

Measured: the 6x6 job shop (36 tasks, optimum 55) solved to a proven optimum in about 23 s with this encoding, and grounding took about 1 s. No larger instance was measured, so expect longer solves beyond that size.

## All solutions

Set `models = 0` and `project = "show"`. Without projection, clingo lists every combination of auxiliary atoms separately: the subset example in [assets/all-solutions](assets/all-solutions/README.md) reports 20 models without projection and 4 with it.

```python
ctl.configuration.solve.models = 0
ctl.configuration.solve.project = "show"
with ctl.solve(yield_=True) as handle:
    answers = [sorted(str(a) for a in m.symbols(shown=True)) for m in handle]
    result = handle.get()        # result.exhausted is True when enumeration finished
```

All **optimal** solutions: combine `opt_mode = "optN"`, `models = 0` and `project = "show"`, and keep only the models with `optimality_proven`. See [assets/all-optimal](assets/all-optimal/README.md). Details: [enumeration and optimisation](https://potassco.org/guide/basics/).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `RuntimeError: parsing failed` on a name or string | A name starts with a capital (for example `letter(S)` or `_SHIP`), or a string uses `\t` or `\uXXXX` | Lowercase the name (`_ship`), or write the data as a string (`letter("S")`); use a real tab, or escape only `\"`, `\\`, `\n` |
| Sum or count is smaller than expected, with no error | Aggregate elements are sets of tuples, so repeated values count once: `#sum { V : b(I,V) }` gives 12 for values 5, 5, 7 | Add a distinguishing term: `#sum { V,I : b(I,V) }` gives 17 |
| Optimum search times out, or enumerates many models | `models = 0` with `optN` searches for every optimal model | `opt_mode = "optN"` with the default `models = 1`; use `models = 0` only for all optima |
| Last model has `optimality_proven` False | No `opt_mode`, or the run was interrupted by a time limit | Set `opt_mode = "optN"`; treat an interrupted result as a bound, not an optimum |
| Scheduling model too slow to finish | Horizon far above a feasible makespan, unrestricted start domains, or `models = 0` | Use the sum of durations as `H`, limit `S + D <= H`, and `models = 1` with `optN` |
| `grounding stopped because of errors`, "unsafe variables" | A variable appears only in the head, a negative literal or a comparison | Bind it with a positive body literal, for example `p(X), not q(X)` |
| parse error on `:- #sum{...} != #sum{...}` | Aggregate compared with another aggregate | Bind each aggregate to a variable first |
| `info: tuple ignored: #inf@0` on stderr | A `#max` or `#min` over an empty set, during grounding | Add an unconditional element: `#max { 0,none ; E,T : end(T,E) }`; the optimum is unchanged |
| Duplicate solutions in an enumeration | Auxiliary atoms differ between models with the same shown answer | `project = "show"` |
| Enumeration never finishes | Grounding is too large, or a rule has an unbounded domain | Constrain variables in the body; use aggregates instead of listing combinations |
| Output has extra atoms | Another `#show` line, or no `#show` at all | List only the signatures to report |
| `python support not available` | `#script(python)` in a program | Not supported in the pip wheel; express the logic in rules |
| Interpreter exits with code 139 | Reading a configuration value from a temporary `Control` | Keep the `Control` in a variable first |

## Further reading

- Python API: [clingo documentation](https://docs.potassco.org/clingo/python-api/current/)
- Language and guide: [Potassco guide](https://potassco.org/guide/) (chapters: [language](https://potassco.org/guide/language/), [basics](https://potassco.org/guide/basics/))
- Command-line options: [clingo options](https://potassco.org/guide/options)

## Runnable examples

Each folder under `assets/` is a standalone program with its README.

| Example | Pattern |
|---|---|
| [satisfy](assets/satisfy/README.md) | one model: graph colouring with a bounded choice and a constraint |
| [all-solutions](assets/all-solutions/README.md) | every model, with projection |
| [all-optimal](assets/all-optimal/README.md) | every optimal model, `optN` with proof check |
| [maximise](assets/maximise/README.md) | knapsack with `#maximize` |
| [minimise](assets/minimise/README.md) | vertex cover with `#minimize` |
| [infeasible](assets/infeasible/README.md) | pigeonhole: no model, `unsatisfiable` |
| [cryptarithm](assets/cryptarithm/README.md) | uppercase letters as strings, weighted `#sum` with negative weights, one model read in a loop |
| [scheduling](assets/scheduling/README.md) | single machine: start times, non-overlap, `#max` makespan |
