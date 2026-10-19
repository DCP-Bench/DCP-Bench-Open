---
name: minizinc-gecode
description: MiniZinc constraint modelling language solved by the Gecode constraint solver, from the command line or the minizinc-python API. Use when writing, running or debugging MiniZinc (.mzn) models, listing all or all optimal solutions, or using Gecode through MiniZinc.
license: Apache-2.0
compatibility: Requires MiniZinc 2.9.3 on PATH (bundles Gecode 6.3.0; free, no licence key); the Python API needs minizinc 0.10.0 and Python 3.12 (tested)
metadata:
  domain: constraint-programming
  solver: gecode
  paradigm: cp
---

# MiniZinc with Gecode

MiniZinc is a declarative modelling language: you state variables and constraints, and
MiniZinc flattens them to FlatZinc for a solver. Here the solver is Gecode, a
constraint-programming solver that propagates constraints and searches depth-first. Keep
one idea in mind: the model says *what* must hold, and Gecode decides *how* to search
unless you add a search annotation.

Contents: [Install](#install) · [Quick start](#quick-start) · [Modelling](#modelling) · [Solving](#solving) · [All solutions](#all-solutions) · [Common issues](#common-issues) · [Further reading](#further-reading)

## Install

Gecode ships inside the MiniZinc bundle, so there is nothing else to install for the
command line. The Python package drives the `minizinc` executable, so MiniZinc must be
on `PATH` first.

```bash
minizinc --version                 # tested with MiniZinc 2.9.3
minizinc --solvers                 # lists "Gecode ... default solver"
pip install minizinc               # optional: Python API
python3 -c "from minizinc import Solver; print(Solver.lookup('gecode').version)"
```

Details: [MiniZinc installation](https://docs.minizinc.dev/en/2.9.3/installation.html) ·
[minizinc-python getting started](https://python.minizinc.dev/en/latest/getting_started.html)

## Quick start

```python
from minizinc import Instance, Model, Solver

model = Model()
model.add_string("""
include "globals.mzn";
int: n;
array[1..n] of var 1..n: x;
constraint all_different(x);
constraint x[1] < x[n];
solve satisfy;
""")
instance = Instance(Solver.lookup("gecode"), model)
instance["n"] = 4                  # data is assigned by name, not written into the model
result = instance.solve()
if result.status.has_solution():
    print("x =", result["x"])
else:
    print("no solution:", result.status.name)
```

From the command line the same model is a file, run with `minizinc --solver gecode model.mzn data.dzn`.

## Modelling

Full list: [language specification](https://docs.minizinc.dev/en/2.9.3/spec.html) ·
[global constraints](https://docs.minizinc.dev/en/2.9.3/lib-globals.html) ·
[scheduling globals](https://docs.minizinc.dev/en/2.9.3/lib-globals-scheduling.html)

| Need | Syntax |
|---|---|
| integer variable with domain | [`var 1..10: x;`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| boolean variable | [`var bool: b;`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| array of variables | [`array[1..n] of var 1..n: x;`](https://docs.minizinc.dev/en/2.9.3/spec.html), 2-D: `array[1..n, 1..m] of var 0..5: g;` |
| data parameter | [`int: n;`](https://docs.minizinc.dev/en/2.9.3/spec.html), value from a `.dzn` file or from Python |
| all different | [`all_different(x)`](https://docs.minizinc.dev/en/2.9.3/lib-globals.html) after `include "globals.mzn";` |
| index an array by a variable | `c[x] = 7`, where `c` is a constant array (element) |
| allowed tuples | [`table([x, y], [\| 1, 2 \| 2, 3 \|])`](https://docs.minizinc.dev/en/2.9.3/lib-globals.html) |
| shared resource over time | [`cumulative(s, d, r, cap)`](https://docs.minizinc.dev/en/2.9.3/lib-globals-scheduling.html) |
| no overlap of tasks | [`disjunctive(s, d)`](https://docs.minizinc.dev/en/2.9.3/lib-globals-scheduling.html); one machine's tasks: `disjunctive([s[t] \| t in 1..T where mach[t] = m], [dur[t] \| t in 1..T where mach[t] = m])` ([jobshop](assets/jobshop/model.py)) |
| minimise a maximum | bound each term by a variable (`s[t] + dur[t] <= makespan`), then `solve minimize makespan;` |
| reification | [`b <-> (x < y);`](https://docs.minizinc.dev/en/2.9.3/spec.html) (also `b -> c`, `/\`, `\/`) |
| count of true booleans | [`sum(i in 1..n)(bool2int(b[i]))`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| integer division, modulo | `div`, `mod`; `/` yields a float and is refused in integer context |
| minimise / maximise | [`solve minimize expr;`](https://docs.minizinc.dev/en/2.9.3/spec.html), `solve maximize expr;` |
| satisfaction | [`solve satisfy;`](https://docs.minizinc.dev/en/2.9.3/spec.html) |
| print values | [`output ["x = ", show(x), "\n"];`](https://docs.minizinc.dev/en/2.9.3/spec.html); 2-D: `showJSON(g)` |

Bound every `var`; an unbounded `var int` gets the solver's 32-bit range.

### One-sided bounds

MiniZinc 2.9.3 can flatten a model in which an auxiliary variable is bounded from one side
only, so that the variable doing the bounding drops out of another constraint. Shape:
`bool2int(covered[j]) <= sum(i)(delta[i, j] * bool2int(build[i]))` together with a budget
on `build`. The flattened model then lets `build[i]` take any value, and the solver reports
a solution that breaks the budget. The fix is to state the relation as an equivalence:

```minizinc
constraint forall(j in Regions)(covered[j] <-> exists(i in Sites)(delta[i, j] = 1 /\ build[i]));
```

Use the equivalence whenever the one-sided bound is tight at every solution you may report.
To confirm, compile with `minizinc --solver gecode -c model.mzn` and check that each variable
appears in some constraint.

### Data from Python

`instance["name"] = value` binds a parameter; lists become 1-based arrays. Bind exactly the
parameters the model declares: a key the model does not declare was accepted without error
in the test, so a misspelled name is silent. Encode sets and enumerated types as integers or
booleans.

Arrays must be rectangular (a ragged list raises `TypeError`). For ragged data, flatten into
one 1-based array per field and keep the row positions in Python, as
[assets/jobshop/model.py](assets/jobshop/model.py) does: `job[t]` is the job of task `t`,
`mach[t]` its machine, `dur[t]` its duration. Then `where job[t] = job[t+1]` selects the
precedences inside a job.

## Solving

Status values: [`Status`](https://python.minizinc.dev/en/latest/api.html#minizinc.result.Status)

| Python `Status` | CLI output | Meaning |
|---|---|---|
| `OPTIMAL_SOLUTION` | `==========` after the last solution | optimum proven |
| `SATISFIED` | `----------` with no `==========` | a solution was found; the search stopped early (time limit), so optimality or the rest of the space is unproven |
| `UNSATISFIABLE` | `=====UNSATISFIABLE=====` | the whole search space was explored; no solution |
| `UNKNOWN` | `=====UNKNOWN=====` | the limit was reached before any solution |
| `ALL_SOLUTIONS` | `==========` | all solutions enumerated (see [All solutions](#all-solutions)) |
| `UNBOUNDED`, `ERROR` | | rarely reported; a syntax or type error raises `minizinc.error` instead |

Options: CLI [`--time-limit <ms>`](https://docs.minizinc.dev/en/2.9.3/command_line.html),
`-s`, `-d data.dzn`, `-c`. Python: [`Instance.solve(timeout=...)`](https://python.minizinc.dev/en/latest/api.html#minizinc.instance.Instance.solve), `result.statistics`.

Reading results from Python:

| Need | How |
|---|---|
| a declared variable | `result["x"]` (declare it `var ...: x;`, see below) |
| the objective of an optimisation | `result["objective"]` (always present, whatever the variable is named; `result["value"]` for a variable called `value` raises `KeyError` when it is defined with `=`) |
| all fields of the solution | `result.solution`, an object with one attribute per variable |
| no solution | `result.solution` is `None` (`[]` with `all_solutions=True`); check `result.status.has_solution()` |

A variable defined in its declaration (`var int: t = expr;`) is **not** returned to Python.
Declare it and constrain it instead: `var int: t; constraint t = expr;`.

Search annotations, for example `solve :: int_search(x, input_order, indomain_min, complete) satisfy;`,
override Gecode's default search: [search annotations](https://docs.minizinc.dev/en/2.9.3/mzn_search.html).

### Implied constraints

When Gecode runs out of time, the cause is often weak propagation. Add constraints that every
solution satisfies but Gecode cannot derive. Example: if `x ++ y` is a permutation of `1..n`
and `sum(x) = sum(y)`, then `4 * sum(x) = n * (n + 1)` holds in every solution. Never add a
constraint that removes solutions to gain speed: a narrower model can be fast and still wrong.

## All solutions

| Goal | CLI | Python (`minizinc`) |
|---|---|---|
| every solution of a satisfaction model | `minizinc --solver gecode -a model.mzn` | `instance.solve(all_solutions=True)`, status `ALL_SOLUTIONS`; `result.solution` is a list with one `Solution` per solution, `[]` when there is none (status `UNSATISFIABLE`) |
| the first k solutions | `-n k` | `instance.solve(nr_solutions=k)` |
| all optimal solutions | not by `-a` (it prints one optimum) | two passes, below |

Details: [enumeration in the command line](https://docs.minizinc.dev/en/2.9.3/command_line.html)

**Duplicates.** The CLI enumerates distinct values of the output, so unconstrained auxiliary
variables do not repeat a solution. Python's `all_solutions` enumerates every variable,
auxiliary ones included: a free auxiliary variable doubles the count. Either make auxiliaries
functions of the outputs, or keep only distinct values of the output variables in Python
(example: [assets/python-all-solutions/model.py](assets/python-all-solutions/model.py)).

**All optimal solutions.** Gecode refuses `all_solutions` on an optimisation model
(`NotImplementedError: Solver does not support the -a-o flag`), so:

1. solve `solve minimize objective;` and check the status is `OPTIMAL_SOLUTION`;
2. add `int: best;` and `constraint objective = best;` to the model and change the solve item to `solve satisfy;`;
3. assign `best` the optimum and call `solve(all_solutions=True)`.

Full code: [assets/all-optimal/model.py](assets/all-optimal/model.py).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `Solver does not support the -a-o flag` (or `-n-o`) | `all_solutions` or `nr_solutions` on a minimise or maximise model | two passes, see [All optimal solutions](#all-solutions) |
| `syntax error, unexpected opt, expecting identifier` | `opt` is a reserved word | rename the variable (`best`); other keywords fail the same way |
| `no function or predicate with name 'all_different'` | `include "globals.mzn";` missing | add the include |
| `cannot determine coercion from type float to type var int` | `/` on integers | use `div` |
| `cannot determine coercion from type array[_] of array[int] of int` | ragged list passed from Python | flatten to 1-based arrays, see [Data from Python](#data-from-python) |
| `lower bound of empty array undefined` | a `where` comprehension selects no element, e.g. a machine count `M` above the machines in use | use `M = max(mach)`, or guard the loop with `where exists(t in 1..T)(mach[t] = m)` |
| `KeyError` on `result["value"]` (or another name) | the objective is read by a name other than `objective`, or the variable is defined with `=` | read `result["objective"]`; it is present whatever the variable is called |
| `KeyError` when reading `result["t"]` | `t` is defined with `=` in its declaration | declare `var int: t;` and `constraint t = ...;` |
| `TypeError` iterating `result.solution` | a plain `solve` found no solution, so `result.solution` is `None` | check `result.status.has_solution()` first; with `all_solutions=True` the list is empty instead |
| `Warning: model inconsistency detected` then `UNSATISFIABLE` | the domains and constraints contradict each other directly, e.g. `x > 5` with `var 0..3` | fix the model; it is not a solver fault |
| objective reported as `2147483646` | a variable without bounds, so the solver used the 32-bit range | bound every variable |
| repeated solutions from Python `all_solutions` | auxiliary variables | see [Duplicates](#all-solutions) |
| `=====UNKNOWN=====` on a larger instance | propagation too weak | see [Implied constraints](#implied-constraints) |
| a solution that breaks a constraint you wrote | one-sided bound flattened away | see [One-sided bounds](#one-sided-bounds) |

## Further reading

- MiniZinc handbook, 2.9.3: [docs.minizinc.dev/en/2.9.3](https://docs.minizinc.dev/en/2.9.3/) (start with [Tutorial](https://docs.minizinc.dev/en/2.9.3/part_2_tutorial.html) and [Efficiency](https://docs.minizinc.dev/en/2.9.3/efficient.html))
- Global constraint catalogue: [lib-globals](https://docs.minizinc.dev/en/2.9.3/lib-globals.html)
- minizinc-python API: [python.minizinc.dev/en/latest/api.html](https://python.minizinc.dev/en/latest/api.html)
- Gecode documentation and reference: [gecode.org/doc-latest](https://www.gecode.org/doc-latest/) ([Modeling and Programming with Gecode](https://www.gecode.org/doc-latest/MPG.pdf))
- Examples: the `assets/` folder; each subfolder is one pattern, runnable on its own.
