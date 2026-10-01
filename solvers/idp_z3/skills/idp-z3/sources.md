# Sources for `idp-z3`

IDP-Z3's documentation covers the language at the level of a tutorial and says
little about the Python engine's behaviour, so most of what this skill and the
runner rely on was established by experiment against the pinned versions, and
by reading the installed library's source. Each entry says which.

- <https://docs.idp-z3.be/en/stable/FO-dot.html>, <https://docs.idp-z3.be/en/stable/summary.html>,
  <https://docs.idp-z3.be/en/stable/IDP-Z3.html> — FO(.) reference, syntax summary and
  Python API, consulted 2026-10-01; the prototype's cheat-sheet was adapted from them
- `idp_engine/Idp.tx` in the installed idp-engine 0.12.1 wheel — the textX grammar,
  read directly for type declarations, the `$( )` construct and procedure strings
- `idp_engine/Theory.py` in the same wheel — the source of `Theory.expand`,
  `Theory.optimize` and `Theory._add_assignment`, read directly
- <https://pypi.org/project/idp-engine/0.12.1/> — the version pinned in the image
- `prototype/solvers/kb/idp-z3/docs/notes.md` in this repository's prototype — earlier
  findings (Assignment values are always truthy; quantified variables need commas;
  interpolate with `%`, not f-strings), re-checked where this skill relies on them

## Environment

- idp-engine 0.12.1 pins **z3-solver 4.11.2.0**, much older than the 5.1 used by
  `z3_python`, and also installs `setuptools 70.3.0`.
- It depends on **sli-lib**, a Rust extension built with maturin and shipped only as
  a `cp311-abi3-manylinux_2_28_x86_64` wheel. A platform-restricted `pip download`
  that omits `manylinux_2_28` fails with "No matching distribution found for
  sli-lib"; on Debian bookworm (glibc 2.36) a plain `pip install` resolves it.

## The engine (read from source, then confirmed by experiment)

- **`Theory.expand` blocks on every unknown atom**, so an unconstrained auxiliary
  symbol multiplies the models: `x() + y() = 2` over `{0..2}` with a free
  `aux: () -> V` gives 9 models for 3 distinct `(x, y)`. A leading underscore
  (`_aux`) does **not** exclude a symbol from this; only `propagate`'s docstring
  promises that. `max=0` means unlimited.
- **`expand`'s terminal strings**: `"No models."`, `"\nNo more models."` (missing from
  its own docstring), `"\nMore models may be available.  Change the max argument
  to see them."`, the `timeout_seconds` variants, and `"\nNo model found in N
  seconds. ..."`.
- **`expand` treats a z3 `unknown` like `unsat`** (`if solver.check() == sat: ...
  else: break`) and only reports a timeout if wall-clock time actually ran out, so
  a fast `unknown` would be reported as exhaustion. Not reproduced: on the
  nonlinear cases tried (three cubes summing to 33, `x*y` equal to a large
  semiprime) z3 used the full budget before answering `unknown` ("incomplete
  (theory arithmetic)"). The runner checks `solver.check()` itself regardless.
- **`Theory.optimize` raises the same `AssertionError("Optimization requires
  satisfiable specification")` for an unsatisfiable theory and for a timeout**,
  and takes no timeout. Driving `theory.optimize_solver` (a `z3.Optimize`)
  directly separates them: `unsat` versus `unknown`.
- **`Theory.optimize` silently returns a wrong optimum for an unbounded
  objective.** Maximizing `x()` subject to `x() > 0` asserts 11: the witness value
  1 plus its `for i in range(0, 10)` "strict inequality" loop, each `val < s`
  check succeeding, then stopping without a warning. Checked directly.
- `theory.solver` is an incremental `z3.Solver`; `theory._add_assignment(solver)`
  adds the GIVEN/EXPANDED/DEFAULT values (structure data, a pinned optimum) and
  must be called before checking. `theory.assignments` also holds whole
  constraint sentences (`'x() + y() = 2'`, an `AComparison` whose `symbol_decl`
  is `x`), so output terms are selected as `AppliedSymbol`s by `sentence.decl.name`.
- `IDP.from_str` succeeds on a vocabulary whose `<: Int` types are uninterpreted;
  "Expected an interpretation for type X" is raised only by `Theory()`. That is
  what lets the runner parse once to read the declarations, then bind the data.
- A `TypeDeclaration` for `type A <: Int` has `interpretation None` and `super_set`
  ℤ; `type B := {1..4}` has an interpretation and `super_set` ℤ but `is_subtype`
  False; a constructor type has `super_set` None.
- Every vocabulary contains the built-ins `abs`, `relevant`, `goal_symbol`,
  `Concept`, `true`, `false`. Redeclaring `abs` fails with `IndexError: list index
  out of range`. `a`, `S`, `T`, `V`, `min`, `sum`, `type`, `minimize` and uppercase
  names all work as symbols — checked one by one. No dataset field or declared
  output collides with a built-in.
- `procedure` blocks are run only by an explicit `IDP.execute()`, never by
  parsing, `Theory()` or solving; inside one, RestrictedPython rejects `import os`.

## Bugs found while building the runner

- **z3 `Optimize` answers `sat` for an unbounded objective, and
  `model().eval(objective)` gives the witness model's finite value.** The first
  version of the runner reported `x = 1` as the optimum of `maximize x()` with
  `x() > 0`. It now requires `lower(handle)` and `upper(handle)` to be finite and
  equal, and reports "The objective is unbounded: between oo and oo" (or
  `-1*oo`) as an error.
- `${n-1}` was originally left in the text and produced an FO(.) parse error that
  never mentioned the placeholder; the runner now rejects any leftover `${...}`
  with its own message.

## FO(.) syntax (each checked on 0.12.1)

- Type ranges must be integer literals: `type Row := {1..n()}` in a vocabulary and
  `Row := {1..n}.` in a structure are both "Expected IDPFLOAT or INT". This is why
  the runner provides `${name}` and data-sized types.
- A bare `type Row` (no `<: Int`) is not numeric even when the structure gives it
  integers: arithmetic on it fails with "ℤ value expected (Row found: queens(r1))".
  `type Row <: Int` interpreted later as `Row := {1..6}.` works.
- Structure syntax: 2-D needs tuple parentheses, `cost := {(0,0)->1, (0,1)->2}.`
  (bare `0,0->1` is a parse error); negative values are fine; a predicate takes
  the set of its true tuples, `flag := {0, 1}.` or `{}` — `{0->true}` fails with
  "Can't use function enumeration for predicates 'flag' (yet)"; a proposition
  takes `p := true.`. Several structure blocks merge into one `Theory`.
- Operators: `=<`, `>=`, `~=` work; `!=`, `==` and a missing final `.` are parse
  errors. `x() <= 2.` is reverse implication and fails loudly with "𝔹 value
  expected (ℤ found: 2)". `?=1`, `?=<2`, `?>=2`, `#{ v in V: p(v) }`,
  `sum{{ e | v in V: g }}` (single-brace `sum{` is a parse error), `max{ e | ... }`,
  `if c then a else b`, definitions with `<-`, Python's `and`/`or`/`not` and
  `abs()` work; `sum{{ cost(t, p) | t in Task, p in Person: x(t, p) }}` over two
  variables works.
- `$` is already FO(.) syntax, but only as `$( expr )` (a symbol computed from an
  expression) — so `${name}` cannot collide with anything valid.
- Procedure strings are double-quoted with no escapes: the grammar's
  `f?"(\.|[^"])*"` matches a literal dot, not a backslash escape, so a string can
  never contain `"`; `print('x')` and `print("{\"a\"}")` are parse errors.

## Arithmetic (each value observed directly)

- Constants are folded in Python, symbols go to z3, and the two disagree for a
  negative divisor: `7 / -2 = -4`, `7 % -2 = -1`, but with `x() = 7`,
  `x() / -2 = -3` and `x() % -2 = 1`. Instance data bound through a structure is
  folded like a constant: `a := 7. b := -2.` gives `a() / b() = -4`,
  `a() % b() = -1`. For a positive divisor both agree (`-7 / 2 = -4`).
- `x() / y()` fails with "Domain error: ¬(y() = 0) is not a tautology. Please add
  appropriate guards." even when the theory states `y() = 2`; an implication
  guard, an `if y() ~= 0 then ... else ...` term, or a divisor type without 0 are
  all accepted. `%` by a symbol has no such check.

## Performance

- A generated structure for a `[1000]int` field parses in 0.36s, `Theory()` takes
  0.29s and a check 0.22s; a 60x9 table parses in 0.42s. The runner parses twice
  (to read the declarations, then with the data), which this makes cheap.

## End to end against this repository's evaluator

- `assignment_costs` (data-sized `Task`/`Person`, minimize): all 5 instances accepted,
  about 0.9s each.
- `csplib_054_n_queens` (`${n}`-sized `Row`, function output): all 6 instances
  accepted with 3 solutions each, about 1.1s each.
- `capital_budget` (1-D arrays and a scalar, maximize): all 5 instances accepted.
- `huey_dewey_louie` (three propositions as Boolean outputs): accepted.
