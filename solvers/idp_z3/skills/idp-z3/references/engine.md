# Engine behaviour and driving z3 directly

What `idp_engine` does underneath, read from `idp_engine/Theory.py` in idp-engine
0.12.1 and confirmed by experiment. The documentation says little about it.

## Contents
- [Theory.expand](#theoryexpand)
- [Theory.optimize](#theoryoptimize)
- [Driving z3 directly](#driving-z3-directly)
- [Parsing and declarations](#parsing-and-declarations)
- [Environment](#environment)

## Theory.expand

- **It blocks on every unknown atom**, so an unconstrained auxiliary symbol multiplies
  the models: `x() + y() = 2` over `{0..2}` with a free `aux: () -> V` gives 9 models for
  3 distinct `(x, y)`. A leading underscore (`_aux`) does **not** exclude a symbol from
  this (only `propagate`'s docstring promises that). An auxiliary symbol fixed by an
  equation (`aux() = x() + 1.`) or a definition gives 3 models again.
- `max=0` means unlimited; so does `timeout_seconds=0`.
- Its terminal strings: `"No models."`, `"\nNo more models."` (missing from its own
  docstring), `"\nMore models may be available.  Change the max argument to see
  them."`, the `timeout_seconds` variants, and `"\nNo model found in N seconds. ..."`.
- **It treats a z3 `unknown` like `unsat`** (`if solver.check() == sat: ... else:
  break`) and reports a timeout only if wall-clock time actually ran out, so a fast
  `unknown` would read as exhaustion. Not reproduced: on the nonlinear cases tried (three
  cubes summing to 33, `x*y` equal to a large semiprime) z3 used the full budget before
  answering `unknown` ("incomplete (theory arithmetic)"). When exhaustion must be
  certain, check with z3 yourself (below).
- With `complete=False` (the default) a term the theory leaves free may have value
  `None` in the model, and models are not enumerated over its values. In a test, a
  Boolean no sentence mentioned read `None` in both models; with `complete=True` it read
  `false` in one model and `true` in the next. Pass `complete=True` when every declared
  symbol needs a value or when every value combination should count as a model.

## Theory.optimize

- `theory.optimize(term, minimize)` builds a `z3.Optimize`, asserts the optimum as a
  given value and returns the theory, so `.expand()` then yields only optimal models.
- **It raises the same `AssertionError("Optimization requires satisfiable
  specification")` for an unsatisfiable theory and for z3 giving up**, and takes no
  timeout.
- **It silently returns a wrong optimum for an unbounded objective.** Maximising `x()`
  subject to `x() > 0` asserts 11: the witness value 1 plus its
  `for i in range(0, 10)` "strict inequality" loop, each `val < s` check succeeding,
  then stopping without a warning. z3's `Optimize` itself answers `sat` for an unbounded
  objective, and `model().eval(objective)` gives the witness model's finite value.
- The CLI's `minimize(T, S, term=...)` / `maximize(...)` return the first model of
  `Theory(...).optimize(...).expand()`.

## Driving z3 directly

For a time limit, a clean infeasible/unknown split, or certain exhaustion, use the z3
solvers IDP-Z3 builds for the theory ([schedule-makespan](../assets/schedule-makespan/README.md)):

```python
import z3
theory = Theory(*kb.get_blocks("T, S"))
term = lambda code: theory.assignments[code].sentence.translate(theory)   # "start(2)" -> z3 expr

opt = theory.optimize_solver              # z3.Optimize with the grounded theory
theory._add_assignment(opt)               # the structure's values; private, used by Theory.optimize
opt.set("timeout", 10_000)
h = opt.minimize(term("makespan()"))
status = opt.check()                      # unsat = infeasible, unknown = gave up
low, high = opt.lower(h), opt.upper(h)    # proven only if both are integers and equal
```

- `theory.solver` is an incremental `z3.Solver`; call `theory._add_assignment(solver)`
  before checking it, as with the optimiser.
- **All optimal solutions, or all solutions without repeats from auxiliary symbols**:
  on `theory.solver`, add `term("makespan()") == best`, then loop: `check()`; on `sat`,
  read the output terms with `model.eval(t, model_completion=True)` and add
  `z3.Or([t != value ...])` over the output terms only. `unsat` is exhaustion; `unknown`
  is not.
- `theory.assignments` also holds whole constraint sentences (`'x() + y() = 2'`), so to
  collect every ground term of one symbol select the entries whose `sentence` is an
  `AppliedSymbol` with `sentence.decl.name == "start"`.

## Parsing and declarations

- `IDP.from_str` succeeds on a vocabulary whose `<: Int` types are uninterpreted;
  "Expected an interpretation for type X" is raised only by `Theory()`. So you can parse
  once to read the declarations (`kb.vocabularies["V"].symbol_decls`), then append a
  structure and parse again; parsing twice is cheap. A file with no `theory` block fails
  to parse (`StopIteration`); an empty `theory T: V { }` is enough.
- A `TypeDeclaration` for `type A <: Int` has `interpretation None` and `super_set` ℤ;
  `type B := {1..4}` has an interpretation and `super_set` ℤ but `is_subtype` False; a
  constructor type has `super_set` None.

## Environment

- idp-engine 0.12.1 pins **z3-solver 4.11.2.0** and also installs `setuptools 70.3.0`.
- It depends on **sli-lib**, a Rust extension shipped only as a
  `cp311-abi3-manylinux_2_28_x86_64` wheel. A platform-restricted `pip download` that
  omits `manylinux_2_28` fails with "No matching distribution found for sli-lib"; on
  Debian bookworm (glibc 2.36) a plain `pip install` resolves it.
- The package requires Python `>=3.11,<3.15` and is licensed LGPL-3.
