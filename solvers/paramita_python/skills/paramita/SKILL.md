---
name: paramita
description: Model problems with the Paramita SAT/MaxSAT framework (Python, paramita 1.2.0) - Bool variables, propositional operators and pseudo-Boolean constraints from paramita.modelling, integers encoded in Booleans, optimisation as MaxSAT. Also covers DCP-Bench Open submissions for the paramita_python integration (build(instance) returning constraints, outputs and an optional objective).
compatibility: paramita 1.2.0 on Linux, with the Cadical300 and EvalMaxSAT2022 plugins and the pblib/pysat PB encoders built from paramita-plugins. DCP-Bench use needs the repository and the image dcp-eval/paramita_python:v1.
---

# Paramita models

Paramita is a SAT/MaxSAT framework. A model is propositional: `Bool` variables,
logical operators and pseudo-Boolean (PB) constraints, `Σ wᵢ·bᵢ ⋈ k`. There are
no integer or finite-domain variables: an integer is a sum of Bools. `to_cnf`
turns every expression into clauses, with the PB encoder `BestEncoder` (PBLib's
choice per constraint) by default. Files: [references/api.md](references/api.md)
(the calls, checked in the image), [sources.md](sources.md).

## Expressions

```python
from paramita.modelling import Bool, And, Or, Not, If, Iff
a, b, c, r = Bool("a"), Bool("b"), Bool("c"), Bool("r")
```

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
- `Xor` and `^` are not supported by `to_cnf` ("Invalid operation when
  converting to NNF+"): write `(a & ~b) | (~a & b)` or `a + b == 1`.
- `Bool("x")` is identified by its name: the same name is the same variable.
  Build names from indices (`Bool(f"x_{i}_{v}")`) and keep them unique per
  meaning.
- `==` on Bools builds an expression, never a Python bool: do not put Bools in
  sets, dict keys or `if` tests.
- Integers are 32-bit inside Paramita. A coefficient beyond ±2^31 is a
  TypeError; a sum whose value leaves that range wraps silently. Scale large
  data down or split the sum.

## Integers in Booleans

Pick one encoding per integer; both give an integer expression usable in PB
constraints, objectives and outputs.

- **One-hot (direct)**, for values that are indexed, matched or all-different:
  `xv = {v: Bool(f"x_{v}") for v in dom}`, `sum(xv.values()) == 1`,
  value `x = sum(v * xv[v] for v in dom)`. "x = 3" is `xv[3]`; "x ≠ y" is
  `~(xv[v] & yv[v])` per v.
- **Unary (order)**, for values that are summed, bounded or compared (`x > y`
  over one-hot values timed out where unary solved in seconds):
  `xs = [Bool(f"x_ge_{i}") for i in 1..ub]`, `If(xs[i+1], xs[i])`, value
  `x = sum(xs) + lb`. "x ≥ k" is the single literal `xs[k-1]`.
- **Binary**, for wide ranges (hundreds of values or more, e.g. times):
  `x = sum(2**k * bit[k])`. Unary or one-hot over hundreds of values with
  pairwise PB constraints ran out of memory.

Global-style constraints become PB constraints over the one-hot Bools:

| Requirement | Encoding |
|---|---|
| all different | per value v: `sum(xv[v] for x in X) <= 1` (`== 1` for a permutation) |
| value v occurs c times | `sum(xv[v] for x in X) == c` |
| element: y = t[x] | `y = sum(t[v] * xv[v] for v in dom)` (t constant) |
| x + y = k, x ≤ y | PB over the integer expressions: `x + y == k`, `x <= y` |
| table of allowed tuples | one Bool per tuple, `sum(tuple_bools) == 1`, `If(tb, xv[a] & yv[b])` |
| at most u in every window of q | `sum(bs[i:i+q]) <= u` per i |
| no overlap of intervals | one-hot start times; for each time t, `sum(covers_t) <= 1` |
| product x·y | one Bool per pair `p[a][b] = xv[a] & yv[b]`; avoid when domains are wide |

## Solving directly

```python
from functools import partial
from paramita.modelling import DimacsVariablePool, add_to_container, add_to_weighted_container, to_cnf
from paramita.solvers import SatSolver, MaxSatSolver, MAXSAT_ANSWER

pool = DimacsVariablePool()
s = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, s, pool)
if s.solve():
    m = s.model()                      # signed literal per variable: [-1, 2, ...]
    true = {abs(l) for l in m if l > 0}
    a_val = pool.get_variable(a) in true
```

- Another PB encoder: `partial(to_cnf, encoder=PbToCnfEncoder.from_name("TotalizerPySatEncoder"))`.
  Only `BestEncoder` and `BddEncoder` accept weighted constraints.
- Enumeration: after a model, add a clause that excludes the values you care
  about and solve again (CaDiCaL is incremental).
- `val_lit(l)` returns the value of `abs(l)`, ignoring the sign: read the model
  list instead.
- Optimisation: `add_to_weighted_container(objective, subject_to, to_cnf, ms, pool)`
  with `ms = MaxSatSolver.from_name("EvalMaxSAT2022")` **maximises** the linear
  objective; it returns the objective's constant part, and the optimum is
  `constant + ms.benefit()`. To minimise, pass the negated objective.
  `solve()` returns `MAXSAT_ANSWER.OPTIMAL`, `SATISFIABLE`, `UNSATISFIABLE` or
  `UNKNOWN`.
- Budgets: CaDiCaL takes only `SolvingBudget(num_conflicts=...)` (a `None`
  answer means undecided); EvalMaxSAT takes no budget at all.

## Modelling advice

- Prefer one-hot for anything that is distinct, indexed or matched; unary for
  quantities that are summed. Link two encodings of the same integer with
  `Iff` per value only when both are needed.
- Exactly-one per variable plus at-most-one per value gives the SAT solver
  strong unit propagation; add the redundant "each value used once" for
  permutations.
- Symmetry: for interchangeable objects, order them (`x_i ≤ x_{i+1}` on the
  integer expressions) or fix the first one.
- Objectives: a weighted sum of Bools directly; for "minimise the maximum",
  introduce unary `m` and require `If(load_k_ge_t, m_ge_t)` per t.
- **Keep PB weights small.** A PB constraint with large, distinct weights over
  many Bools (one-hot value × price, a product of two binaries, weights up to
  10^4 and beyond) can exhaust the 2 GB memory limit. Instead:
  - products and squares: binary bits for the result, linked with
    `If(xv[v], bit_k == ((v*v) >> k) & 1)`, or a column-by-column multiplier;
  - choosing among many constants: `If(choice_q, x == q)` per q with x binary;
  - |a − b| between one-hot positions: a unary length t with `a - b <= t`
    and `b - a <= t`, not one implication per pair of positions;
  - "amount a is payable" for many amounts: a clause-level reachability table
    `r[j][v] ⇔ OR_k (r[j-1][v - k·d_j] ∧ x_j ≥ k)`, not one weighted PB per
    amount.

## DCP-Bench (`paramita_python`)

**Contract.** One Python file defining `build(instance)`, written against
`paramita.modelling` only. It returns

- `(subject_to, outputs)` for satisfaction, or
- `(subject_to, outputs, ("minimize", expr))` / `("maximize", expr)` for
  optimisation,

where `subject_to` is an expression or a list of them, `expr` a linear integer
expression over Bools, and `outputs` maps each name the brief declares (no
others) to a Bool (read as a JSON boolean), an integer expression (read as a
JSON integer), an int constant, or nested lists of these.

```python
from paramita.modelling import Bool, If

# Row seating: seat n guests on n chairs, enemies not side by side,
# minimise the total distance from the preferred chairs.
def build(instance):
    n, pref = instance["n"], instance["preferred"]
    s = [[Bool(f"s_{g}_{c}") for c in range(n)] for g in range(n)]
    cons = []
    # every guest takes one chair and every chair holds one guest
    cons += [sum(s[g]) == 1 for g in range(n)]
    cons += [sum(s[g][c] for g in range(n)) == 1 for c in range(n)]
    # enemies never sit side by side
    for g, h in instance["enemies"]:
        cons += [~(s[g][c] & s[h][d]) for c in range(n) for d in range(n) if abs(c - d) == 1]
    seat = [sum(c * s[g][c] for c in range(n)) for g in range(n)]
    total = sum(abs(c - pref[g]) * s[g][c] for g in range(n) for c in range(n))
    return cons, {"seat": seat, "total": total}, ("minimize", total)
```

- Read every size and value from `instance`; the brief's shapes are those of
  the example, and output lengths follow the instance. Problems without instance fields still take `instance`.
- Start each constraint block with a `#` comment in the description's words.
- An objective that is also an output is the same expression in both places.
- An output the brief declares `int` must be an integer expression: a cell that
  is a Bool goes out as `1 * b` (a bare Bool is read as a JSON boolean).
- A value beyond 32 bits cannot be an output; split it (e.g. digits) only if
  the brief declares it so.

**What the runner does.** It encodes with `to_cnf` (default encoder) through
one pool. Satisfaction: CaDiCaL, enumerating up to the solution limit with
clauses that block the declared outputs. Optimisation: EvalMaxSAT in a child
process killed at the deadline; only a proven optimum is reported, then the
objective is fixed at that value and further optimal outputs are enumerated
with CaDiCaL. A timeout before the proof is `execution_timeout`.

**Check.**
1. `python -m generation.brief PROBLEM`: description, output names and shapes,
   objective, instance fields.
2. `python -m evaluation.check MODEL.py --problem PROBLEM --solver paramita_python
   --instance-count 2 --solution-limit 2`.
3. By `reason`: `invalid_output`: a declared name missing, an extra name, or a
   wrong shape; `invalid_solution`: a constraint missing or wrong;
   `suboptimal_solution` or `no_solution`: wrong direction or over-constrained;
   `execution_timeout`: a smaller encoding (one-hot vs unary, fewer
   auxiliaries, redundant cardinality constraints); `execution_error`: the
   Python exception is in `detail` (Xor, a 32-bit overflow, a non-expression
   in `subject_to`).
4. "Declared outputs cannot extend to a reference solution": the outputs break
   a convention of the description (0- or 1-based, order); reread it.
5. A top-level `accepted` can hide skipped instances: read the per-instance
   reasons.
