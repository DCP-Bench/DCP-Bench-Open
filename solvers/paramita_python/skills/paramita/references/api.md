# Paramita 1.2.0 API used in models

All calls below were run in `dcp-eval/paramita_python:v1`.

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
| `Xor`, `^` | exist, but `to_cnf` rejects them |

## Pool

- `pool = DimacsVariablePool()`; `pool.get_variable(Bool("x"))` or
  `pool.get_variable("x")` gives the DIMACS id, creating it on first use.
- `pool.decode_literal(5)` gives `Bool`, `decode_literal(-5)` gives `~Bool`,
  an unknown id gives `None`.
- `pool.new_aux()` gives a fresh `Bool("aux_k")`.

## Encoding

- `add_to_container(expr, to_cnf, container, pool)`: clauses of `expr` into a
  `SatSolver` or `CnfFormula`.
- `add_to_weighted_container(objective, subject_to, to_cnf, container, pool)`:
  hard clauses for `subject_to`, soft clauses that **maximise** `objective`;
  returns the objective's constant part (an int).
- `to_cnf` uses `BestEncoder` for PB constraints. Another encoder:
  `functools.partial(to_cnf, encoder=PbToCnfEncoder.from_name(NAME))`.
- Encoders in the image: `BestEncoder`, `BddEncoder` (weighted and unweighted);
  `AdderEncoder`, `BinaryMergeEncoder`, `CardEncoder`, `SortingNetworksEncoder`,
  `SwcEncoder`, `TotalizerPySatEncoder`, `SeqCounterPySatEncoder`, `KMTotalizerPySatEncoder`,
  `MTotalizerPySatEncoder`, `ITotalizerPySatEncoder` and others for unweighted
  (cardinality) constraints only; `PairwisePySatEncoder`, `RegularPySatEncoder`,
  `BitwisePySatEncoder` accept only bound 1.

## SAT (`SatSolver.from_name("Cadical300")`)

- `add_clause([1, -2])`, `add_clauses([...])`, `num_clauses()`, `max_var()`.
- `solve(assumptions=[...], budget=SolvingBudget(num_conflicts=N))` returns
  `True`, `False`, or `None` (budget reached). `cpu_time_seconds` and
  `num_propagations` raise on CaDiCaL.
- `model()`: one signed literal per variable up to `max_var()`.
- `core()`: the failed assumptions after an UNSAT call.
- `val_lit(l)` reports the value of `abs(l)` whatever the sign of `l`.
- Incremental: clauses added after a solve apply to the next solve.

## MaxSAT (`MaxSatSolver.from_name("EvalMaxSAT2022")`)

- `add_clause(lits)` or `weight=SPECIAL_WEIGHTS.TOP_WEIGHT`: hard;
  `add_clause(lits, weight=w)`: soft with integer weight `w`.
- `solve()` returns `MAXSAT_ANSWER.UNKNOWN`, `SATISFIABLE`, `UNSATISFIABLE` or
  `OPTIMAL`. No budget of any kind.
- `model()`, `cost()` (weight of falsified soft clauses), `benefit()`
  (`total_weight() - cost()`). `cost()` raises when there is no solution.
- Not supported: `num_clauses()`, `lower_bound()`, `val_lit()`.
- Writes `c ...` lines to standard output (the DCP runner keeps them off the
  protocol channel).
