# Paramita 1.2.0 API (Python)

Checked with paramita 1.2.0 on CPython 3.12 with the Cadical300 (CaDiCaL 3.0.0) and
EvalMaxSAT2022 plugins. Calls the examples use are marked in the lists below; the
expression forms are in [SKILL.md](../SKILL.md#modelling) and the encodings in
[modelling.md](modelling.md).

## Imports

```python
from paramita.modelling import (Bool, And, Or, Not, If, Iff, DimacsVariablePool,
                                add_to_container, add_to_weighted_container, to_cnf)
from paramita.solvers import SatSolver, MaxSatSolver, MAXSAT_ANSWER, SolvingBudget
from paramita.containers import CnfFormula, WcnfFormula, SPECIAL_WEIGHTS
from paramita.encoders import PbToCnfEncoder
from paramita.base import PbConstraint      # not `from paramita import PbConstraint`
```

## Expressions (`paramita.modelling`)

| Form | Meaning |
|---|---|
| `Bool(name)` | a variable, identified by its name |
| `~a`, `a & b`, `a \| b` | Not, And, Or; `And(a, b)`/`Or(a, b)` or one list `Or([a, b, c])`; three operands or one bare operand raise TypeError |
| `If(a, b)`, `Iff(a, b)` | implication, equivalence; either side may be a PB comparison |
| `w * a`, `a + b`, `sum(...)`, `e + c`, `-e` | integer expressions over Bools |
| `e1 <= e2`, `<`, `==`, `>=`, `>` | PB comparison (a Boolean expression) |
| `Xor`, `^` | build an expression, but `to_cnf` rejects them |
| Python `True`/`False` (e.g. `sum([]) >= 1`) | not a Paramita expression: `If(a, False)` builds and forces `a` false; skip the constraint instead |

## Pool

- `pool = DimacsVariablePool()`; `pool.get_variable(Bool("x"))` or `pool.get_variable("x")`
  gives the DIMACS id, creating it on first use. Used by all examples.
- `pool.decode_literal(5)` gives `Bool`, `decode_literal(-5)` gives `~Bool`, an unknown id
  gives `None`.
- `pool.new_aux()` gives a fresh `Bool("aux_k")`.

## Encoding

- `add_to_container(expr, to_cnf, container, pool)`: clauses of `expr` into a `SatSolver`
  or `CnfFormula`. Used by all examples.
- `add_to_weighted_container(objective, subject_to, to_cnf, container, pool)`: hard clauses
  for `subject_to` (one expression), soft clauses that **maximise** `objective`; returns the
  objective's constant part (an int). Used by the MaxSAT examples.
- `to_cnf` uses `BestEncoder` for PB constraints. Another encoder:
  `functools.partial(to_cnf, encoder=PbToCnfEncoder.from_name(NAME))`.
- Encoders: `BestEncoder`, `BddEncoder` (weighted and unweighted). `AdderEncoder`,
  `BinaryMergeEncoder`, `CardEncoder`, `SortingNetworksEncoder`, `SwcEncoder`,
  `TotalizerPySatEncoder`, `SeqCounterPySatEncoder`, `KMTotalizerPySatEncoder`,
  `MTotalizerPySatEncoder`, `ITotalizerPySatEncoder` and others handle unweighted
  (cardinality) constraints only; `PairwisePySatEncoder`, `RegularPySatEncoder`,
  `BitwisePySatEncoder` accept only bound 1. The pysat encoders need their plugin
  installed.

## SAT (`SatSolver.from_name("Cadical300")`)

- `add_clause([1, -2])`, `add_clauses([...])`, `num_clauses()`, `max_var()`.
- `solve(assumptions=[...], budget=SolvingBudget(num_conflicts=N))` returns `True`,
  `False`, or `None` (budget reached). `cpu_time_seconds` and `num_propagations` raise on
  CaDiCaL.
- `model()`: one signed literal per variable up to `max_var()`. Used by all examples.
- `core()`: the failed assumptions after an UNSAT call.
- `val_lit(l)` reports the value of `abs(l)` whatever the sign of `l`. Read `model()` when
  the sign matters.
- Incremental: clauses added after a solve apply to the next solve. The all-solutions
  examples rely on this.

## MaxSAT (`MaxSatSolver.from_name("EvalMaxSAT2022")`)

- `add_clause(lits)` or `weight=SPECIAL_WEIGHTS.TOP_WEIGHT`: hard; `add_clause(lits, weight=w)`:
  soft with integer weight `w`.
- `solve()` returns `MAXSAT_ANSWER.UNKNOWN`, `SATISFIABLE`, `UNSATISFIABLE` or `OPTIMAL`.
  No budget of any kind.
- `model()`, `cost()` (weight of falsified soft clauses), `benefit()` (`total_weight() -
  cost()`). `cost()` raises when there is no solution. `model()` gives signed literals, as
  the SAT solver does.
- Not supported: `num_clauses()`, `lower_bound()`, `val_lit()`.
- It may write `c ...` lines to standard output; none appeared in the knapsack example
  here. If a program parses its own output, check stdout.
