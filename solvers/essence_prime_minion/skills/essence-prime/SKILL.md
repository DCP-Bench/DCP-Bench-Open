---
name: essence-prime
description: Write and run Essence' constraint models with Savile Row 1.11.1 and the Minion solver (given/find/letting, matrices, globals, minimising/maximising, parameter files, solution files, enumeration, branching). Also covers DCP-Bench Open submissions for the essence_prime_minion integration (.eprime model, instance fields bound as given).
compatibility: Savile Row 1.11.1 with bundled Minion, Java 15+. DCP-Bench use needs the repository and the Docker image dcp-eval/essence_prime_minion.
---

# Essence' with Savile Row and Minion

Essence' is a typed CP modelling language. Savile Row translates a model plus a parameter file into Minion input, runs Minion and writes the solution as Essence' text. Details: [references/language.md](references/language.md) (syntax, operators, globals), [references/examples.md](references/examples.md) (tested models), [sources.md](sources.md).

## File shape

```
language ESSENCE' 1.0
$ one-line statement of the problem
given n : int(1..20)                          $ parameters, values come from the param file
letting c = 5                                 $ named constants
find q : matrix indexed by [int(1..n)] of int(1..n)   $ decision variables
branching on [q]
such that
$ a comment line per constraint block
allDiff(q),
$ next block
forAll i : int(1..n) . q[i] != c
```

- Header `language ESSENCE' 1.0` (ASCII apostrophe). Comments start with `$`.
- Order: header, `given`, `letting`, `find`, `where`, objective, `branching on`, `such that`. Constraints are separated by commas; no trailing comma.
- Parameter file: the header plus `letting n = 6` lines (ints, bools, matrix literals `[[1,2],[3,4]]`). A matrix literal is rectangular and has exactly as many entries as the declared index domain.
- Every `find` variable needs a finite domain: `int(lo..hi)`, `bool`, or `matrix indexed by [D1, D2] of Base`. Matrices are 1-based by default.

## Run

```
savilerow model.eprime model.param -run-solver                  # one solution (or the optimum)
savilerow model.eprime model.param -run-solver -all-solutions   # enumerate (satisfaction)
savilerow model.eprime model.param -run-solver -num-solutions 5
```

Add `-timelimit S` (Savile Row only) and `-solver-options "-cpulimit S"` (caps Minion). Run in a writable directory: Minion writes hidden temp files there. In the image the command is `/opt/savilerow/savilerow`; plain `java -jar savilerow.jar ... -minion-bin bin/minion` also works.

- Output files are `<param>.solution` (or `.solution.000001`, ... when several), `<param>.info`, `<param>.minion`. Override with `-out-solution`, `-out-info`, `-out-prefix`.
- A solution file is `language ESSENCE' 1.0`, `$` info lines, then `letting NAME be VALUE` for each `find`: ints `5`, bools `true`, matrices `[1, 2, 3]`, 2-D as nested rows over several lines. Variables come out in alphabetical order.
- No solution file and `SolverSatisfiable:0` in the info file means unsatisfiable. `SolverTimeOut:0` means the search finished, `1` means Minion hit its limit.
- Optimisation: `-all-solutions` and `-num-solutions` are ignored; only the best solution is written, after the search finished.
- Errors print `ERROR: ...` and exit nonzero. Parse errors name the line.

## Objective and enumeration

`minimising EXPR` or `maximising EXPR`, one per model, on its own line, before `such that`. EXPR is an int expression (a variable or a sum). To list all optimal solutions, find the optimum, then re-solve without the objective and with `EXPR = optimum` added.

## Modelling rules

- Open with a `$` line stating the problem. Start each conceptual constraint block with a `$` comment taken from the problem statement (`$ all rows must have different values`), not naming the global used. Name variables in the problem's vocabulary.
- Prefer globals: `allDiff`, `gcc`, `atleast`, `atmost`, `table`, `cumulative`, `alldifferent_except`. Use quantifiers over decompositions by hand.
- Tight domains from the data. Add `where` on parameters only to validate input.
- Put matrices of the same shape in one `find`, not many scalars.

## Pitfalls

- A quantifier body extends as far right as possible: `sum i : D . a[i] <= c` is a sum of booleans and fails with "'And' contains something other than a relation". Write `(sum i : D . a[i]) <= c`. Likewise `forAll i : D . A /\ B` puts both under the quantifier.
- No if-then-else, no `element`, no `negativeTable`. Use `(c -> A) /\ (!c -> B)`, an index `M[idx]` with a decision variable, or `table` with a complement built by a comprehension.
- Division floors and `%` follows it (`(-3)/2 = -2`, `(-3)%2 = 1`). `**` is right associative.
- An out-of-range index or division by zero makes the containing constraint false, not an error.
- Bool converts to int in arithmetic, int does not convert to bool.
- Global arguments must be one-dimensional: slice (`M[i,..]`) or `flatten`. `atleast/atmost(X, Counts, Vals)` but `gcc(X, Vals, Counts)`.
- Parameter-only positions (set `in`, `table` tuples, quantifier and sum bounds, `where`) take no decision variables.
- No strings or floats. Ragged data must be padded with a length parameter.
- Savile Row compiles slowly for large grids; keep matrix dimensions small and quantifier bounds fixed.

## Search

- `branching on [x, M, [M[i,i] | i : int(1..n)]]` fixes variable order (flatten order for matrices). Branch first on the structural decisions the rest follows from, then the rest.
- `heuristic static|sdf|conflict|srf` (Minion only), placed before the constraints. Try `sdf` (smallest domain first) when the default stalls.
- Implied constraints on sums, tighter domains and a sorted symmetric copy help more than extra branching.
- An optimisation that cannot be proven within the time limit yields no result here: tighten the objective's domain and add implied bounds.

## Using this skill in DCP-Bench Open

Applies only to the `essence_prime_minion` integration; all above still holds. Full rules: [references/dcp-binding.md](references/dcp-binding.md).

- Submission: one `.eprime` file, no parameter file. Never read files. Do not hardcode instance data.
- Each instance field is a `given` of the same name; the file runs on several instances. `given n : int(1..)` and `given w : matrix indexed by [int(1..n)] of int(0..)` bind from the instance. A `given` that is not an instance field makes Savile Row fail (`execution_error`); an instance field no `given` names is ignored.
- Outputs: `find` variables named exactly as the declared outputs, with the declared shape. Ints, bools and (nested) matrices only. Matrices are 1-based: the reference's index 0 is `M[1]`. Output values are matched to the reference's, so an output must be constrained to exactly the reference value (an expression result needs its own `find` with an equality).
- Field binding: int, bool or rectangular list bind unchanged; a nonempty list of lists also binds `<field>_len` (row lengths). A ragged list of rows (one item shape, one scalar type) binds padded with 0/false plus `<field>_len`. Equal-length rows with different column types bind as `<field>_1`, `<field>_2`, ... Floats, strings, empty lists and other shapes are refused with an `error` naming the field.
- Objective: `minimising EXPR` or `maximising EXPR` alone on its line, in the direction of the problem, never bounded by a known answer. `such that` appears once, after the objective: the runner appends `, <constraint>` to it.
- How `run.py` solves: satisfaction enumerates solutions distinct on the declared outputs up to the solution limit. Optimisation first solves once and emits nothing unless Minion finished the search, so an unproven optimum is `execution_timeout`; then it re-solves with the objective fixed and enumerates distinct outputs. Other `find` variables are not compared.
- Workflow:
  1. `python -m generation.brief PROBLEM` prints output names and shapes, the direction and every instance field with its shape.
  2. Write `MODEL.eprime`, with `given` for each field you use.
  3. `python -m evaluation.check MODEL.eprime --problem PROBLEM --solver essence_prime_minion` (stronger: `--instance-count 3 --solution-limit 5`). The JSON has `accepted`, `reason`, `detail`. Instance ids are 1-based.
  4. By `reason`: `execution_error` Savile Row message in `detail` (parse error, a `given` with no instance field, an unbindable field); `invalid_output` wrong names, shapes or non-integer values; `invalid_solution` a constraint is missing or too weak, or an output is not fully pinned; `no_solution`/`suboptimal_solution` overconstrained or wrong direction; `execution_timeout` weak search or unproven optimum, add `branching`, tighter domains, a global.
  5. Repeat a bounded number of times; do not edit the reference or evaluator.
- The comment rule above is required by `skills/model-generator/references/acceptance.md`: opening problem line and a statement-worded comment on every constraint block.
