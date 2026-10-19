# Sources for `pysat`

Tested with python-sat 1.9.dev15, Python 3.12.11, a Linux container.

Existing skills: not searched in this refactor (the refactor brief did not ask for it). The text was rewritten from an earlier pysat skill, and its claims were re-run.

- <https://pysathq.github.io/> — PySAT home page and documentation entry point
- <https://pysathq.github.io/installation/> — installation, `pblib` extra
- <https://pysathq.github.io/usage/> — usage overview
- <https://pysathq.github.io/docs/html/api/formula.html> — `CNF`, `WCNF`, `IDPool`
- <https://pysathq.github.io/docs/html/api/card.html> and <https://pysathq.github.io/docs/html/api/pb.html> — `CardEnc`, `PBEnc`
- <https://pysathq.github.io/docs/html/api/integer.html> — `pysat.integer`, the finite-domain layer
- <https://pysathq.github.io/docs/html/api/solvers.html> — solver names and limited solving
- <https://pysathq.github.io/docs/html/api/examples/rc2.html> — RC2 and `RC2Stratified`
- <https://github.com/pysathq/pysat/tree/master/examples> — upstream examples (the examples here are written from scratch)
- Licence: python-sat is MIT-licensed (package metadata in the image)

Verified by running inside that container:

- **Every example in `assets/` runs and prints its expected output**; the Quick start and the all-solutions snippet in `SKILL.md` were run as written.
- **Brute-force cross-checks** in the examples agree: all-solutions (9 solutions), all-optimal (2 optimal covers), minimise (cost 7), maximise (profit 24), scheduling (makespan 11).
- **`pysat.integer` is the framework's own integer layer.** `Integer(name, lb, ub, encoding=...)` and `IntegerEngine(vars=..., vpool=...)` clausify direct, order or coupled encodings; `add_linear(..., reified=True)` returns a selector literal.
- **Encoding restrictions**: `equals()` raises `Direct encoding is disabled` on `order`; `ge()` raises `Order encoding is disabled` on `direct`; `add_not_equal` on the left side requires `direct` or `coupled`.
- **Expressions are not Integers**: `add_alldifferent`, `add_equal` and `add_not_equal` fail on a `LinearExpr`; `add_linear` takes it.
- **`PBEnc` accepts negative weights**, and `PBEnc.equals`/`leq` produce clauses that respect them.
- **`CNF.weighted()` makes every clause soft** (weight 1, no hard clauses), so a constraint becomes optional. `WCNF().extend(cnf.clauses)` makes them hard.
- **`RC2Stratified` returns `None` on unsatisfiable hard clauses**, and returns `None` with `rc2.interrupted` set when `rc2.interrupt()` fires during `compute(expect_interrupt=True)`.
- **Glucose 4.2 honours `interrupt()`**: a 14-into-13 pigeonhole returned `None` 0.15 s after a 1 s timer.
- **CaDiCaL (`cadical195`) does not honour `interrupt()`**: the same pigeonhole ran past 120 s. `clear_interrupt()` raises `NotImplementedError`. Lingeling's `solve_limited` raises `NotImplementedError`.
- **Integer domain encodings**: `Integer.decode` reads `model[abs(lit) - 1]`, so a model from RC2 must be padded to the pool's top variable before decoding.
- **`Integer.ge(v)` and `le(v)`**: `ge` gives the literal for `x >= v` and `le` gives `-ge(v+1)`, both only for order or coupled; out-of-range values raise. `add_linear(x >= 3)` is a constraint on any encoding (measured on direct, order and coupled).
- **Reified `add_linear` returns `None`** when the bounds entail the constraint (measured: an entailed `x + 2 <= y` gave `None`, an impossible one gave a literal). In an early draft of the jobshop asset, keeping the other literal of such a clause made the model unsatisfiable, so the clause is skipped instead.
- **`Solver.get_model()` length**: 36 entries with `pool.top` 37 when the last pool id is in no clause, so pad before `decode`.
- **Unit-weight makespan softs** `[-makespan.ge(t)]`, `t` from `lb+1` to `ub`, give `makespan - lb` as the cost. Measured: ft06 optimum 55 in about 3 s with the greedy horizon 68 (assets/jobshop, schedule checked independently).
- **Horizon and clause counts** for reified no-overlap on ft06 at horizons 197, 80, 68 and 55 (table in pysat-api.md), measured with `clausify()` in the image.
- **Colour-count objective** (one-hot colours, `x -> y_k`, soft `[-y_k]` weight 1) returned 3 on a triangle with a 4-cycle tail.
- **Blocking on Integer solutions**: `equals` literals created before `clausify()` enumerate 92 eight-queens placements (the tester's n-queens-all model, re-run in the image: 92 lines of output).
- **Pigeonhole timings** for `Integer` plus `add_alldifferent` under Glucose 4.2 (12/11 4.5 s up to 15/14 70.9 s) were measured in an earlier run of this skill and kept as a reference.

Independent toy test (add-solver toy problems, solved from the skill alone by a tester agent; models and runner output kept in the refactor scratch folder, not in the skill):

| Problem | Instances | Passed |
|---|---|---|
| cryptarithm | 3 | 3 |
| graph-colouring | 3 | 3 |
| jobshop | 2 | 2 |
| knapsack | 2 | 2 |
| knapsack-all-optimal | 3 | 3 |
| n-queens | 3 | 3 |
| n-queens-all | 2 | 2 |
| **Total** | **18** | **18** |

Run order: the first run scored 17/18 (jobshop/ft06 timed out after 120 s with horizon 197). One repair round on jobshop only brought it to 18/18 (75 s). That run used the skill before this round's changes; a fresh tester has not yet run the updated skill.

Refactored from an earlier integration skill; examples verified inside the same container.
