---
name: cvc5-python
description: cvc5, an SMT solver with a Python API (pip package cvc5, module cvc5.pythonic, Z3-style) for finite-domain combinatorial models. Covers integer and Boolean variables, Distinct, sums and cardinality, table, element, lexicographic, cumulative, no-overlap and routing encodings, satisfiability, enumeration and optimisation by tightening. Use when writing, debugging or explaining cvc5 models in Python, or when the user has chosen cvc5 for a constraint or scheduling problem.
license: Apache-2.0
compatibility: Requires Python 3.10+ and the cvc5 pip package (tested with cvc5 1.4.2 on Python 3.12, Linux x86-64; no NumPy needed). cvc5 is free with no key or size limit.
metadata:
  domain: constraint-programming
  solver: cvc5
  paradigm: smt
---

# cvc5 (Python)

cvc5 is an SMT solver. Its `cvc5.pythonic` API builds integer, Boolean and array formulas
with the same operators as Z3. It has **no global constraints**: no cumulative, table,
element or circuit, and no `PbEq`, `AtMost` or `Max`. Encode them with `Distinct`, `If`,
`Or`, `And` and `Sum`. It has **no optimiser**: minimise or maximise by asking for a
better value until the solver answers `unsat`. Integers are unbounded unless you bound them.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Optimisation](#optimisation)
- [Choosing an encoding](#choosing-an-encoding)
- [Performance](#performance)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/<example>/`, one folder per pattern (table under [Quick start](#quick-start))

## Install

```bash
pip install cvc5
python -c "import cvc5; from cvc5 import pythonic; print(cvc5.__version__)"
```

The package is [cvc5 on PyPI](https://pypi.org/project/cvc5/). API details:
[cvc5 Python API, pythonic](https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html).

## Quick start

```python
from cvc5.pythonic import *

x, y = Ints("x y")
s = SolverFor("QF_LIA")
s.add(x >= 0, x <= 10, y >= 0, y <= 10, x + y == 7, x - y == 1)
if s.check() == sat:
    m = s.model()
    print(m.eval(x, model_completion=True).as_long(), m.eval(y, model_completion=True).as_long())  # 4 3
```

| Example | Pattern | Run |
|---|---|---|
| [satisfy-magic-square](assets/satisfy-magic-square/README.md) | satisfy, `Distinct`, sums | `python model.py` |
| [all-solutions-queens](assets/all-solutions-queens/README.md) | all solutions, no-goods | `python model.py` |
| [maximise-knapsack](assets/maximise-knapsack/README.md) | maximise by tightening, JSON data | `python model.py` |
| [minimise-jobshop](assets/minimise-jobshop/README.md) | no-overlap, minimise | `python model.py` |
| [cumulative-schedule](assets/cumulative-schedule/README.md) | cumulative by time point | `python model.py` |
| [table-element-lex](assets/table-element-lex/README.md) | table, element, lex order | `python model.py` |
| [routing-tour](assets/routing-tour/README.md) | permutation, subtour elimination | `python model.py` |
| [infeasible-pigeonhole](assets/infeasible-pigeonhole/README.md) | infeasible | `python model.py` |

## Modelling

Full list: [cvc5 pythonic API](https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html)

| Need | API |
|---|---|
| integer variables (no domain: add bounds) | `Int("x")`, `Ints("x y")` or `Ints(["x", "y"])` |
| Boolean variables | `Bool("b")`, `Bools(["b0", "b1"])` |
| all different | `Distinct(xs)`: needs at least two arguments |
| linear sum over integers | `Sum([...])`, Python `sum(...)` also works |
| cardinality, weighted count | `Sum([If(b, w, 0) for b, w in ...]) <= k` (`Sum` over Booleans raises `TypeError`) |
| conditional value | `If(c, a, b)` |
| logic | `And`, `Or`, `Not`, `Implies`, `Xor`; `And`/`Or` need at least two arguments |
| Boolean as an equivalence | `b == (x > 3)` (tested: reifies both ways) |
| maximum / minimum | no `Max`: fold with `If(a > b, a, b)` |
| table (allowed tuples) | `Or([And(x == a, y == b) for a, b in allowed])` |
| element `row[i]` with variable `i` | `If` chain: `If(i == 0, row[0], If(i == 1, row[1], row[2]))` |
| lexicographic `xs <= ys` | recursive: `Or(x0 < y0, And(x0 == y0, lex_le(rest)))` ([table-element-lex](assets/table-element-lex/README.md)) |
| no-overlap of intervals | pairwise `Or(end_a <= start_b, end_b <= start_a)` ([minimise-jobshop](assets/minimise-jobshop/README.md)) |
| cumulative resource | per time point `Sum([If(And(s <= t, t < s + d), r, 0), ...]) <= cap` ([cumulative-schedule](assets/cumulative-schedule/README.md)) |
| circuit / tour | successor variables with `Distinct`, positions with `Implies(succ[i] == j, pos[j] == pos[i] + 1)` ([routing-tour](assets/routing-tour/README.md)) |
| quantifiers | `ForAll([i], body)`, `Exists([i], body)`; tested on small bounded cases only |

Build constraints with the Python operators; they produce cvc5 terms, not Python booleans.
Pass them to `Solver.add`, as separate arguments: `s.add(c1, c2)` or `s.add(*constraints)`.
A Python list in `add` raises `SMTException` (see [Common issues](#common-issues)).

## Solving

Status: `Solver.check()` returns `sat`, `unsat` or `unknown` (compare with the names `sat`,
`unsat`, `unknown` from the module). `s.reason_unknown()` gives an `UnknownExplanation`,
for example `UnknownExplanation.TIMEOUT`.

| `check()` | Meaning |
|---|---|
| `sat` | a model exists; read it with `s.model()` |
| `unsat` | proven: no model exists |
| `unknown` | undecided; `reason_unknown()` says why (tested: `TIMEOUT`) |

Reading values: `m.eval(x, model_completion=True).as_long()` for integers and
`is_true(m.eval(b, model_completion=True))` for Booleans. `m[x]` also works. `s.model()`
raises `RuntimeError: cannot get value unless after a SAT or UNKNOWN response.` after `unsat`,
so test the status first.

Options: [cvc5 options](https://cvc5.github.io/docs/cvc5-1.4.2/options.html). Set them with `s.set(name, value)`.

| Setting | Effect, as measured |
|---|---|
| `SolverFor("QF_LIA")` | linear integer logic. Faster than a plain `Solver()` on the models in [Performance](#performance). Use it for linear models |
| `SolverFor("QF_NIA")` | nonlinear integer logic, needed for products of variables |
| `s.set("tlimit-per", ms)` | time limit per `check()`, in milliseconds; a run stopped by it returns `unknown` / `TIMEOUT` (measured: 60 s limit ended at 60.00 s) |
| `s.set("arith-prop", "none")` | slower on n-queens n=40 (33 s against 13 s); keep the default |
| `s.set("arith-brab", False)` | no measurable change on the tested models |
| `s.set("sat-random-seed", n)` | accepted; effect on speed not measured |
| `incremental`, `produce-models` | accepted; `model()` worked without `produce-models` in testing |

`s.set("timeout", ms)` is rejected (see [Common issues](#common-issues)). Do not set the global
`tlimit` option: it hung in testing. Use `tlimit-per`.

## All solutions

No enumeration call exists. Loop over `check()` and block the assignment of the **decision**
variables only. An auxiliary variable in the no-good gives each solution once per value of
the auxiliary. Example: [all-solutions-queens](assets/all-solutions-queens/README.md).

```python
solutions = []
while s.check() == sat:
    m = s.model()
    values = [m.eval(v, model_completion=True).as_long() for v in q]
    solutions.append(values)
    s.add(Or([v != x for v, x in zip(q, values)]))
```

Check that the last `check()` returned `unsat`, not `unknown`, before reporting the list as complete.

## Optimisation

cvc5 has no optimiser. Tighten: solve, record the value, add `objective > best` (or
`< best` for minimisation), solve again. The last `check()` returning `unsat` proves the
optimum. Returning `unknown` means the best value is only a bound. Examples:
[maximise-knapsack](assets/maximise-knapsack/README.md) and
[minimise-jobshop](assets/minimise-jobshop/README.md). For all optimal solutions, first find
the optimum, then add `objective == best` and enumerate as in [All solutions](#all-solutions).

## Choosing an encoding

Measured on puzzles and designs between 10 and 400 variables, default logic, 180 s limit.

- **Boolean atoms and clauses beat integer sums on combinatorial designs.** Replacing `Int`
  variables, `Distinct` and `Sum(If(...))` counts by one-hot Booleans with exactly-one and
  at-most-one clauses solved what timed out otherwise: a Steiner system on 13 points
  (clauses plus one degree sum, 7 s), a word-design code (12 s), a round-robin schedule
  (10 s), n-queens 14 to 16 (1 s). A permutation with a cost, such as a rehearsal order,
  was fast as pairwise order Booleans plus transitivity clauses (5 s) and timed out as
  `Distinct` over slot variables.
- **Costs and capacities: 0/1 integer variables with linear rows.** A warehouse location
  model went from 157 s with `If` sums to 4.7 s with `x[t][w] <= open[w]` and plain linear
  capacity and cost rows.
- **Products of variables: case-split over a constant.** `Or([And(d == a, p == a * t) for a
  in range(1, 10)])` made a three-factor digit puzzle solve in 3 s after the product form
  timed out. A square test is an `Or` over the constant squares up to the bound.
- **Large products: bit-vectors.** `BitVec`, `ZeroExt` to double width and `BV2Int` solved
  products of four factors near 10^9 that timed out as integers. `<=` on bit-vectors is
  signed: give a constant bound one extra bit, or it reads as negative and the model is
  silently unsat.
- **Write counters and definitions as clauses.** A sequential counter over 200 Booleans
  written as `v == Or(prev, And(lit, prev_j))` made `check()` run for more than 800 s, past
  `tlimit-per`. The same counter as four implication clauses (`v -> prev or lit`,
  `v -> prev or prev_j`, `prev -> v`, `lit and prev_j -> v`) solved in seconds. Use it for
  at-most-k windows and cardinalities; one clause per forbidden subset also worked.
- **Bit-vectors under integer outputs need `bv-solver=bitblast-internal`.** A model on
  `BitVec` letters with `ULE` bounds and `Distinct` solved a 10-letter cryptarithm in 0.3 s
  with a bit-vector blocking clause, but the default `bv-solver=bitblast` stalled for
  170 s once a no-good over `BV2Int` outputs was added. With `SolverFor("ALL")` and
  `s.set("bv-solver", "bitblast-internal")` it took 13 to 17 s. `solve-int-as-bv` fails on an
  incremental solver (`solveIntAsBV not supported with incremental solving`).
- **Tours and routes: prune arcs before encoding.** With Int arcs, degree rows and an order
  encoding, the optimality proof of a 12-city tour took 74 to 102 s and 20 cities timed out.
  Computing in Python, from the distance matrix only, an assignment lower bound (Hungarian
  method, reduced costs as arc coefficients), a tour upper bound (nearest neighbour plus 2-opt)
  and a 1-tree bound that drops arcs which cannot be on a tour within the upper bound made all
  instances solve in under 3 s, up to 30 cities. Cheapest-in and cheapest-out bounds alone did
  not help.
- **Redundant totals help.** Adding a derived equality (the cells of a magic hexagon sum to
  n(n+1)/2, the line sums of a heterosquare lie between the sum of the smallest and of the
  largest values) made two timeouts solve.
- **Tightening for optimisation is the weak spot.** Every step ends in an unsat proof over
  all the objective terms; weighted sums of 100 conditional terms timed out on a 10x10 grid.
  The second solution of a satisfaction problem is the same kind of proof and can stall when
  the instance is a pigeonhole in disguise.

## Performance

Measured with cvc5 1.4.2, with `tlimit-per` set to 60 s per `check()`.
Times are wall-clock for one run of a script, model building included (building
took under 0.02 s in every case). These are the measurements behind the advice above.

| Model | Config | Result | Time |
|---|---|---|---|
| pigeons 7 into 6 holes (`Distinct`, bounded ints) | `Solver()` | unsat | 0.70 s |
| pigeons 7 into 6 holes | `SolverFor("QF_LIA")` | unsat | 0.57 s |
| pigeons 8 into 7 holes | `Solver()` | unsat | 7.8 s |
| pigeons 8 into 7 holes | `SolverFor("QF_LIA")` | unsat | 5.8 s |
| pigeons 9 into 8 holes | either | unknown, TIMEOUT | 60 s |
| magic square 4x4 | `Solver()` | sat | 0.31 s |
| magic square 4x4 | `QF_LIA` | sat | 0.23 s |
| magic square 4x4 | `QF_LIA`, `arith-prop` none | sat | 0.47 s |
| n-queens 8 | either | sat | under 0.05 s |
| n-queens 20 (`Distinct` on rows and diagonals) | `Solver()` | unknown, TIMEOUT | 60 s |
| n-queens 20 | `QF_LIA` | sat | 1.1 s |
| n-queens 40 | `QF_LIA` | sat | 13.0 s |
| n-queens 40 | `QF_LIA`, `arith-brab` off | sat | 13.0 s |
| n-queens 40 | `QF_LIA`, `arith-prop` none | sat | 32.9 s |
| job shop ft06 (6 jobs x 6 machines), horizon 55 | `Solver()`, `QF_LIA`, `QF_LIA` with `arith-prop` none | sat | 0.07 to 0.15 s |
| job shop ft06, horizon 54 | `Solver()`, `QF_LIA`, `QF_LIA` with `arith-brab` off | unsat | 0.12 to 0.14 s |

Takeaways. Set `QF_LIA` for linear models: the default logic timed out on 20-queens where
`QF_LIA` solved it in 1.1 s. Pairwise no-overlap disjunctions were fast on this job shop;
measure before trying other encodings at larger sizes. Pigeonhole-style models hit the
limit quickly at 9 into 8; add redundant bounds or reformulate.

Nonlinear integer arithmetic (`QF_NIA`, products of two or more variables): cvc5 decided
the small cases tested (`a*b == 143` sat with `a = 13, b = 11`; `a*a == 2` unsat;
`a*b == 7` with bounds unsat). For a product of two primes near 10^6 it returned
`unknown` with reason `TIMEOUT` after 20 s. The solver can return `unknown` on nonlinear
problems, so treat it as incomplete. Do not expect a definite answer on large products.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `RuntimeError: unrecognized option: timeout.` | `s.set("timeout", ...)` is not a cvc5 option | `s.set("tlimit-per", ms)` |
| `RuntimeError: unrecognized option: <name>.` | misspelt option name | list them with `cvc5.Solver().getOptionNames()` |
| `TypeError: unsupported operand type(s) for +: 'BoolRef' and 'BoolRef'` | `Sum` over Boolean terms | `Sum([If(b, 1, 0) for b in bs])` |
| `NameError: name 'PbEq' is not defined` (also `AtMost`, `AtLeast`, `PbLe`) | no pseudo-Boolean helpers in `cvc5.pythonic` | `Sum([If(b, w, 0) ...]) == k` |
| `NameError: name 'Max' is not defined` | no `Max` | `If`-fold |
| `SMTException: True, False or SMT Boolean expression expected. Received [...] of type <class 'list'>` | a Python list passed to `add` | `s.add(*constraints)` |
| `RuntimeError: invalid kind 'AND', expected Terms with kind AND must have at least 2 children` (`'OR'` likewise) | `And` or `Or` with one argument | pass the constraint directly; `Or([...])` needs two or more |
| `RuntimeError: invalid kind 'DISTINCT', ... must have at least 2 children` | `Distinct` with one argument | skip the constraint when there are fewer than two terms |
| `SMTException: At least one of the arguments must be an SMT expression` | `Distinct([])` | skip the constraint |
| `RuntimeError: LogicInfo::setLogicString(): cannot parse logic string: NOTALOGIC` | unknown logic name in `SolverFor` | use a standard name, e.g. `QF_LIA`, `QF_NIA` |
| `RuntimeError: cannot get value unless after a SAT or UNKNOWN response.` | `model()` read after `unsat` | test `check() == sat` first |
| `RuntimeError: ... solver is already fully initialized` | `s.set(...)` or a logic change after the first `add` | set options and the logic before the first `add` |
| `RuntimeError: A non-linear term was asserted to arithmetic in a linear logic.` | `x * y` under `SolverFor("QF_LIA")` | use `QF_NIA` or the default `Solver()`, or case-split the product |
| a bit-vector bound makes the model unsat with no error | `<=` on `BitVec` is signed, the constant's top bit is set | widen by one bit |
| `if x == 3:` takes the wrong branch | `==` builds a term; `bool()` on it returned `False` with no error | `s.add(x == 3)`, or test a model value with `is_true(m.eval(...))` |
| `check()` returns `unknown`, `TIMEOUT` | hard search, or nonlinear terms | `QF_LIA` for linear models, redundant bounds, a stronger encoding, a larger `tlimit-per` |
| enumeration repeats a solution | auxiliary variable in the no-good | block only the decision variables |
| optimum not proven | the last `check()` returned `unknown`, not `unsat` | treat the value as a bound; raise `tlimit-per` or strengthen the model |
| `model()` gives 0 for a variable | the variable is not in the formula | create it in the formula, or ignore it |

## Further reading

- cvc5 Python API (pythonic): <https://cvc5.github.io/docs/cvc5-1.4.2/api/python/pythonic/pythonic.html>
- cvc5 options: <https://cvc5.github.io/docs/cvc5-1.4.2/options.html>
- cvc5 on PyPI: <https://pypi.org/project/cvc5/>
