---
name: paramita
description: Paramita SAT and MaxSAT framework for Python (paramita 1.2.0) - Bool variables, propositional operators and pseudo-Boolean constraints from paramita.modelling, integers encoded as Booleans, satisfiability and all-solutions enumeration with CaDiCaL, and optimisation as MaxSAT with EvalMaxSAT2022. Use when writing, debugging or explaining Paramita models, or when the user has chosen Paramita for a SAT, MaxSAT or pseudo-Boolean problem.
license: Apache-2.0
compatibility: Requires Python 3.12 (tested) and paramita 1.2.0 with the Cadical300 and EvalMaxSAT2022 plugins built from paramita-plugins (CMake and a C++ compiler). No licence key, no size limit.
metadata:
  domain: constraint-programming
  solver: paramita
  paradigm: sat
---

# Paramita (Python)

Paramita is a SAT and MaxSAT framework. A model is propositional: `Bool` variables,
logical operators and pseudo-Boolean (PB) constraints `Σ wᵢ·bᵢ ⋈ k`. There are no
integer or finite-domain variables: an integer is a sum of Bools, so the modelling
work is choosing the encoding. `to_cnf` turns each expression into clauses (PB
encoder `BestEncoder` by default). Satisfiable problems go to CaDiCaL; optimisation
goes to EvalMaxSAT as a weighted problem. Call signatures: [references/api.md](references/api.md).
Encodings and modelling advice: [references/modelling.md](references/modelling.md).

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install paramita
python3 -c "import importlib.metadata as m; print('paramita', m.version('paramita'))"
```

The solver plugins are not in the wheel. Build them from
[paramita-plugins](https://codeberg.org/paramita/paramita-plugins) at commit
`a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb` (tested), into the install prefix paramita
searches ([plugin docs](https://ulog.udl.cat/static/doc/paramita/)):

```bash
git clone https://codeberg.org/paramita/paramita-plugins && git -C paramita-plugins checkout a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb
P="$PWD/paramita-plugins"; PREFIX="$HOME/.local/paramita"
paramita plugins build cmake -j 4 -i "$PREFIX" "file://$P#sat-solvers/cadical-3.0.0"
paramita plugins build cmake -j 4 -i "$PREFIX" "file://$P#maxsat-solvers/mse22-EvalMaxSAT2022"
paramita plugins build cmake -j 4 -i "$PREFIX" "file://$P#pb-to-cnf-encoders/pblib"
```

The pysat encoders (`file://$P#pb-to-cnf-encoders/pysat`) are optional and are not used
below. They build a `libpairwise.so` of the same name as pblib's, so install them to a
second search path. If the
EvalMaxSAT build fails while configuring, its `FindZLIB.cmake` is downloading zlib from
zlib.net; use a system zlib or the zlib 1.3.2 GitHub release (SHA-256
`bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16`).

Verify: `SatSolver.from_name("Cadical300")` and `MaxSatSolver.from_name("EvalMaxSAT2022")`
must both construct without an error.

## Quick start

```python
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf
from paramita.solvers import SatSolver

a, b, c = Bool("a"), Bool("b"), Bool("c")
constraints = [a | b, ~a | ~c, sum([a, b, c]) == 2]

pool = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, solver, pool)

if solver.solve():
    true = {abs(lit) for lit in solver.model() if lit > 0}
    print({name: pool.get_variable(v) in true for name, v in [("a", a), ("b", b), ("c", c)]})
else:
    print("unsatisfiable")
```

Prints `{'a': False, 'b': True, 'c': True}`. Every model is a standalone program: it builds, solves
and prints. Worked examples, each with a README (problem, what it shows, run, expected output):

| Pattern | Example |
|---|---|
| satisfy: one solution, one-hot cells | [queens-one](assets/queens-one/README.md) |
| all solutions, blocking clauses over the answer Booleans | [queens-all](assets/queens-all/README.md) |
| maximise (MaxSAT) | [knapsack-max](assets/knapsack-max/README.md) |
| all optimal solutions | [all-optimal](assets/all-optimal/README.md) |
| minimise, instance read from a JSON file | [colouring-json](assets/colouring-json/README.md) |
| infeasible, read from the status | [infeasible](assets/infeasible/README.md) |
| scheduling with deadlines, reading start times | [scheduling](assets/scheduling/README.md) |

## Modelling

Full reference: [Python API](https://ulog.udl.cat/static/doc/paramita/). Calls are in [references/api.md](references/api.md).

| The description says | Expression |
|---|---|
| a and b / a or b / not a | `a & b`, `a \| b`, `~a`; `And`/`Or` take two operands or one list: `Or([a, b, c])` (`Or(a, b, c)` and `Or(a)` raise TypeError) |
| if a then b | `If(a, b)` |
| a exactly when b | `Iff(a, b)` |
| exactly / at least / at most k of these | `sum(bs) == k`, `sum(bs) >= k`, `sum(bs) <= k` |
| weighted capacity, budget | `sum(w * b for w, b in zip(ws, bs)) <= cap` |
| a condition holds when r is chosen (reified) | `If(r, sum(bs) >= 2)`; both ways: `Iff(r, 2*a + b <= 2)` |
| x differs from y (as Bools) | `Iff(a, ~b)`; exactly one of two: `a + b == 1` |

- PB comparisons take negative coefficients and sums on both sides
  (`a + b <= c + r`). Weights are integers.
- `Xor` and `^` build an expression but `to_cnf` rejects it ("Invalid operation when
  converting to NNF+"): write `(a & ~b) | (~a & b)` or `a + b == 1`.
- `Bool("x")` is identified by its name: the same name is the same variable.
  Build names from indices (`Bool(f"x_{i}_{v}")`) and keep them unique per meaning.
- `==` on Bools builds an expression, never a Python bool: do not put Bools in
  sets, dict keys or `if` tests. The converse: `sum([])` is the int 0, so
  `sum([]) == k` and `sum([]) >= k` are Python bools, not expressions. Skip the
  constraint when the list is empty (check `len(bs)` first); never pass such a bool
  into `If` or `~`, because `If(a, False)` silently forces `a` false.
- Integers are 32-bit inside Paramita: a coefficient beyond ±2^31 is a TypeError, and a
  sum whose value leaves that range wraps silently. Scale large data down or split the
  sum.
- `Bool | (PB comparison)`, `If(PB, Bool)` and `If(Bool, PB)` are all accepted by `to_cnf`
  (checked on small cases against brute force). A PB comparison that is a constant in
  Python is not an expression: see Common issues.
- Integers as Booleans (one-hot, unary, binary), global-style constraints as PB
  constraints (all different, element, table, no-overlap, product), symmetry, wide
  ranges and weight shrinking: [references/modelling.md](references/modelling.md).

## Solving

**Satisfaction.** Add every expression with `add_to_container(expr, to_cnf, solver, pool)`,
then `solver.solve()`:

| Result | Meaning |
|---|---|
| `True` | a model; read it with `solver.model()` (one signed literal per variable) |
| `False` | proven unsatisfiable |
| `None` | the conflict budget ran out before an answer (only with a budget, see below) |

```python
true = {abs(lit) for lit in solver.model() if lit > 0}
value = pool.get_variable(a) in true          # abs(lit) ignores the sign; read the list
```

**All solutions.** After each model, add a clause that differs from it in at least one
answer Boolean, and solve again; `False` means the list is complete. Block only the
answer variables: auxiliary variables make duplicates of the same answer.
See [queens-all](assets/queens-all/README.md).

**Optimisation (MaxSAT).** `add_to_weighted_container(objective, subject_to, to_cnf, ms, pool)`
with `ms = MaxSatSolver.from_name("EvalMaxSAT2022")` **maximises** the linear objective and
returns the objective's constant part; the optimum is `constant + ms.benefit()`. To
minimise, pass the negated objective and negate the result. `subject_to` must be one
expression: wrap a list with `And(list)`. `ms.solve()` returns `MAXSAT_ANSWER.OPTIMAL`,
`SATISFIABLE`, `UNSATISFIABLE` or `UNKNOWN`; only `OPTIMAL` is a proven result.
See [knapsack-max](assets/knapsack-max/README.md) and
[colouring-json](assets/colouring-json/README.md).

**All optimal solutions.** Solve for the optimum, then add `objective == optimum` as a
hard constraint to a **fresh** solver and enumerate the answer Booleans as above. See
[all-optimal](assets/all-optimal/README.md).

**Time limits.** CaDiCaL takes only `SolvingBudget(num_conflicts=N)`: call `solve` in
rounds of N conflicts and check the clock between them. EvalMaxSAT takes no budget at all:
run it in a child process and kill that process at the deadline; a child that has not
finished is a timeout, not a result.

**Recursion.** The default PB encoder recurses once per term. A single sum of about 5000
Bools segfaults on the default 8 MB stack (2000 was fine). Run under `ulimit -s unlimited`
(or a larger stack), or split the sum into smaller ones.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `RuntimeError: Invalid operation when converting to NNF+` | `Xor` or `^` in an expression | Expand: `(a & ~b) \| (~a & b)` |
| `TypeError` from `And`/`Or` | three operands, or one bare operand | `Or([a, b, c])`, or nest two-operand calls |
| `TypeError` on a coefficient | outside the 32-bit range | scale the data, or split the sum |
| A sum wraps and the answer is wrong | a constraint or objective value beyond 32 bits | scale down or split; read big numbers from the model bits in Python |
| Segmentation fault on a wide sum | the recursive PB encoder overflows the stack | `ulimit -s unlimited`, or split the sum |
| A Bool in a set, a dict key or an `if` test misbehaves | `==` on Bools builds an expression, and a Bool is not a Python bool | keep Booleans as expressions; map them to ids with `pool.get_variable` |
| `sum([]) == k` gives a Python `bool` | an empty sum is the int 0 | skip empty sums (see Modelling) |
| A constraint silently forces a Bool false, e.g. `If(a, sum([]) >= 1)` makes `a` false | `sum([]) >= 1` is Python `False`, and `If` with a Python bool on one side is not a dropped constraint | build the constraint only when the list is non-empty |
| A unary chain gives too small a value (e.g. a makespan of 0) | an end time that is always at least `t` (end >= t with `t` at most the duration) was left out of the clauses instead of asserted | assert such a fact as a unit clause (`m[t]`, `s[b][t]`), not as an `If` with a constant |
| EvalMaxSAT proof takes minutes on a scheduling-sized model (a 6x6 job shop took about 3 minutes to prove optimal) | MaxSAT has no budget, and a large horizon with many unary bits makes the proof long | tighten the horizon to a feasible makespan upper bound, use the unary makespan from [modelling.md](references/modelling.md#precedence-and-makespan), run in a child process with a deadline, and treat anything not `OPTIMAL` as unresolved |
| `SyntaxError` at the top of the file | a comment such as `# ... encoding: ...` in lines 1-2 is a Python coding declaration | move encoding notes below line 2 |
| EvalMaxSAT run never returns | no budget exists for it | run it in a child process and kill at the deadline |
| Enumeration returns duplicates | blocking clauses cover auxiliary variables | block only the answer Booleans |
| Optimum or direction looks wrong | objective not negated for a minimise, or the constant part not added | `optimum = constant + ms.benefit()`; negate for minimise |

## Further reading

- Paramita 1.2.0 documentation (tutorials, Python API reference): <https://ulog.udl.cat/static/doc/paramita/>
- Plugin sources, pinned commit: <https://codeberg.org/paramita/paramita-plugins>
- [references/api.md](references/api.md): the calls used in the examples.
