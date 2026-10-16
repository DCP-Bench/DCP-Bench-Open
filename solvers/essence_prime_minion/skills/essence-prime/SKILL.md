---
name: essence-prime
description: Essence' constraint modelling language run with Savile Row and its bundled Minion CP solver (given/find/letting, matrices, globals, minimising/maximising, .param files, solution files, -all-solutions, branching). Use when writing, running or debugging .eprime models, or when the user has chosen Essence', Savile Row or Minion.
license: Apache-2.0
compatibility: Requires Savile Row (tested 1.11.1, Linux tarball with Minion bundled) and Java 15+ on PATH; free, no licence key. Examples that read JSON use Python 3 (standard library only).
metadata:
  domain: constraint-programming
  solver: minion
  paradigm: cp
---

# Essence' with Savile Row and Minion

Essence' is a typed CP modelling language. Savile Row reads a model (`.eprime`) plus a parameter file (`.param`), reformulates it, writes Minion input, runs Minion and turns its answer back into Essence' text (`letting NAME be VALUE`). Keep in mind: **everything is finite and ground before search** (every domain and index range comes from constants or parameters), and the model is compiled fresh for each parameter file.

Contents: [Install](#install) · [Quick start](#quick-start) · [File shape](#file-shape) · [Run and read results](#run-and-read-results) · [Objective and enumeration](#objective-and-enumeration) · [Modelling rules](#modelling-rules) · [Pitfalls](#pitfalls) · [Search and performance](#search-and-performance) · [Common issues](#common-issues) · [Further reading](#further-reading) · Language reference: [references/language.md](references/language.md)

Examples (each runs with its README's command): [satisfy](assets/send-more-money/README.md) · [all solutions](assets/queens-all/README.md) · [maximise](assets/knapsack/README.md) · [all optimal](assets/all-optimal/README.md) · [minimise](assets/vertex-cover/README.md) · [infeasible](assets/pigeonhole/README.md) · [scheduling](assets/scheduling/README.md) · [job shop, no-overlap](assets/jobshop/README.md) · [JSON data, ragged lists](assets/json-input/README.md)

## Install

```bash
curl -fLO https://www-users.york.ac.uk/peter.nightingale/savilerow/savilerow-1.11.1-linux.tgz
mkdir savilerow && tar -xzf savilerow-1.11.1-linux.tgz -C savilerow --strip-components=1
export PATH="$PWD/savilerow:$PATH"          # the `savilerow` launcher script; Minion is in savilerow/bin/
java -version && savilerow -help | head -1  # "Savile Row 1.11.1 ..."
```

If the launcher's directory is not on `PATH` (a container image that unpacks the tarball elsewhere, for instance), the bare `savilerow` command is `not found`: run `DIR/savilerow` with its full path, or put `DIR` on `PATH`. The commands below use the bare name.

The tarball bundles Minion (plus Chuffed and Kissat for other back ends). The `savilerow` script runs `java -Xmx8G -jar savilerow.jar` and passes `-minion-bin bin/minion` itself; on a smaller machine call the jar directly with a lower heap: `java -Xmx2g -Djava.library.path=DIR/lib -jar DIR/savilerow.jar model.eprime p.param -run-solver -minion-bin DIR/bin/minion`. Releases and macOS builds: [Savile Row releases](https://www-users.york.ac.uk/peter.nightingale/savilerow/releases.html).

## Quick start

```bash
cat > hello.eprime <<'EOF'
language ESSENCE' 1.0
$ n distinct values from 1..n, the first larger than the last
given n : int(1..10)
find x : matrix indexed by [int(1..n)] of int(1..n)
such that
allDiff(x),
x[1] > x[n]
EOF
printf "language ESSENCE' 1.0\nletting n = 4\n" > hello.param
savilerow hello.eprime hello.param -run-solver -solutions-to-stdout   # prints: letting x be [2, 3, 4, 1]
savilerow hello.eprime -params "letting n = 4" -run-solver            # inline data; writes hello.eprime.solution
```

## File shape

```
language ESSENCE' 1.0
$ one-line statement of the problem
given n : int(1..20)                          $ parameters, values come from the .param file
letting c = 5                                 $ named constants
find q : matrix indexed by [int(1..n)] of int(1..n)   $ decision variables
branching on [q]
such that
$ a comment line per constraint block
allDiff(q),
forAll i : int(1..n) . q[i] != c
```

- Header `language ESSENCE' 1.0` (ASCII apostrophe). Comments start with `$`.
- Order: header, `given`, `letting`, `find`, `where`, `branching on`, `heuristic`, objective, `such that`. Verified: `branching on` or `heuristic` after `minimising` is a parse error. Constraints are separated by commas; **no trailing comma**, and one `such that`.
- Parameter file: the header plus one `letting n = 6` per `given` (ints, `true`/`false`, matrix literals `[[1,2],[3,4]]`); order does not matter, so a size may come after the matrix it sizes. A matrix literal is rectangular and has exactly as many entries as the declared index domain, else `Index domains do not match for the matrix F`.
- Every `find` needs a finite domain: `int(lo..hi)`, `bool`, or `matrix indexed by [D1, D2] of Base`. Matrices are 1-based by default.
- Full syntax, operators and globals: [references/language.md](references/language.md).

## Run and read results

```
savilerow model.eprime data.param -run-solver                    # one solution, or the optimum
savilerow model.eprime data.param -run-solver -all-solutions -S0 # enumerate (satisfaction only)
savilerow model.eprime data.param -run-solver -num-solutions 5 -S0
```

Options: [manual section 4.5](https://arxiv.org/abs/2201.03472), `savilerow -help`.

- **Where results go.** By default `<param>.solution` (or `<param>.solution.000001`, ... for several), `<param>.info`, `<param>.minion`; with no param file the prefix is the model name. `-solutions-to-stdout` prints them instead, separated by `----------`; `-out-solution`, `-out-info` rename the files. Run in a writable directory: Minion also writes hidden temp files there.
- **Solution text**: `language ESSENCE' 1.0`, `$` info lines (nodes, time, `SolverTimeOut`), then `letting NAME be VALUE` per `find`, in alphabetical order: ints `5`, bools `true`, matrices `[1, 2, 3]`, 2-D as nested rows over several lines; a matrix not indexed from 1 carries its domain, `[1, 2, 3;int(0..2)]`. A parser is in [the JSON example](assets/json-input/solve.py). `-mode ReadSolution` and `-param-to-json` convert files.
- **Status lives in the info file** (`<param>.info`), not in the exit code:

| Info line | Meaning |
|---|---|
| `SolverSatisfiable:1` | a solution was written |
| `SolverSatisfiable:0` + `SolverTimeOut:0` | proven infeasible: exit code 0, no solution file, nothing on stdout ([example](assets/pigeonhole/README.md)) |
| `SolverTimeOut:0` | Minion finished: an optimum written is **proven**, an enumeration is complete |
| `SolverTimeOut:1` | Minion hit its limit: the solution written is the best found, **not** proven optimal |
| `SavileRowTimeOut:1` | Savile Row ran out of time before Minion started |

- **Time limits**: `-timelimit S` limits Savile Row's translation only; once Minion runs it is not stopped (measured: a Golomb-ruler run with `-timelimit 2` ran Minion for 100 s). Cap Minion with `-solver-options "-cpulimit S"`; give both.
- **Errors** print `ERROR: ...` and exit nonzero; parse errors name the line and column. Some warnings are harmless and do not change the exit code: `Number of givens in model file does not match number of lettings` (the param file sets other names too), `interval 1..0 is out of order`, and, for an **empty** matrix (`letting edges = []` where the domain is `int(1..0)`), `Index domains do not match for the matrix edges`. An empty matrix gives exit 0 and a correct solution with those warnings on stderr. The `-all-solutions` warning recommending `-S0` is not harmless: see below.

## Objective and enumeration

`minimising EXPR` or `maximising EXPR`, one per model, on its own line, after any `branching on`/`heuristic` and before `such that`. EXPR is an int expression (a variable or a sum). Only the best solution is written, and only after the search finished or hit its limit; `-all-solutions` and `-num-solutions` are ignored with a warning on an optimisation model.

- **Pass `-S0` when enumerating.** The default `-S1` lets Savile Row delete "unused" `find` variables by fixing them to one value, and a variable whose only constraints are unary counts as unused (they fold into its domain). Measured: `find x : int(1..3)` with `x != 2` gives 1 solution under `-S1`, 2 under `-S0`; an unconstrained `find` is likewise pinned. With `-S0`, every `find` is enumerated, so a free auxiliary variable repeats each solution once per value: pin it to a function of the others or leave it out.
- **All optimal solutions**: solve, check `SolverTimeOut:0`, read the optimum, then re-solve **without** the objective line and with `(EXPR) = optimum` appended after the last constraint, using `-all-solutions -S0` ([example](assets/all-optimal/README.md)). Parenthesise EXPR: `sum i : D . e = v` would put `= v` inside the sum. To read the optimum of an expression, add `find best` with `maximising best` and `best = (EXPR)`. That wrapper is needed only for an expression objective: when the objective is already one variable (`maximising total`), read it directly and fix it in pass 2 (`total = optimum`), which enumerates the same solutions.

## Modelling rules

- Items listed together in a clue (`X, the chef, and the police officer`) are distinct unless the statement says otherwise.
- Prefer globals: `allDiff`, `gcc`, `atleast`, `atmost`, `table`, `cumulative`, `alldifferent_except`. Use quantifiers over decompositions by hand.
- Tight domains from the data (`int(0..sum(values))`). Add `where` on parameters only to validate input.
- Put matrices of the same shape in one `find`, not many scalars.
- Every size that varies between data sets must be a `given` (or a `letting` computed from givens); a matrix declared with one data set's numbers fails on the next with `Index domains do not match for the matrix F`.
- Ragged data (lists of different lengths) has no direct form: pad rows to the longest with a value outside the real range and pass a row-length matrix; read row `i` only up to `len[i]`, since padding can equal a real value ([example](assets/json-input/README.md)). No strings or floats: map names to integers before writing the param file.
- No-overlap on a machine (one task at a time): post each pair of tasks as an either-or, `(a < b /\ mach[a] = mach[b]) -> ((s[a] + d[a] <= s[b]) \/ (s[b] + d[b] <= s[a]))` over a flat task list; a precedence within a job is an implication on its job index. Solved job shop with 9 tasks to proven optimum ([example](assets/jobshop/README.md)). For a resource with a shared capacity, use `cumulative` instead.
- Symmetric designs (round-robin, periodic schedules): fix the first period to canonical values. A set of rows: `M[r,..] <=lex M[r+1,..]` orders them.
- No square root: the nearest integer to sqrt(s) is `letting R = sum([d | d : int(0..DMAX), (2*d-1)**2 <= 4*s, 4*s < (2*d+1)**2])` (verified for s = 0, 2, 10, 13, 24). `^` does not parse; use `**`.

## Pitfalls

- A quantifier body extends as far right as possible: `sum i : D . a[i] <= c` is a sum of booleans and fails with `'And' contains something other than a relation`. Write `(sum i : D . a[i]) <= c`. Likewise `forAll i : D . A /\ B` puts both under the quantifier.
- `abs(x)` does not parse; write `|x|`. No if-then-else, no `element`, no `negativeTable`: use `(c -> A) /\ (!c -> B)`, an index `M[idx]` with a decision variable, or `table` with a complement built by a comprehension.
- Division floors and `%` follows it (`(-3)/2 = -2`, `(-3)%2 = 1`). `**` is right associative.
- An out-of-range index or division by zero makes the enclosing constraint false, not an error.
- Bool converts to int in arithmetic, int does not convert to bool.
- Global arguments must be one-dimensional: slice (`M[i,..]`) or `flatten`. `atleast/atmost(X, Counts, Vals)` but `gcc(X, Vals, Counts)`.
- `sum(M)` and `max(M)` need a 1-D matrix: write `sum(flatten(M))` for 2-D. `forAll i : D1, j : D2` with different domains does not parse: nest the quantifiers.
- Parameter-only positions (set `in`, `table` tuples, quantifier and sum bounds, `where`) take no decision variables.
- Reserved words cannot be names (`find max` fails with `Parsed keyword 'max'`, `find where` with `Parsed 'find' keyword.`); rename, e.g. `max_`. List: [references/language.md](references/language.md#declarations).
- A sequence generated by a recurrence and cut at a bound needs its index domain wider than the bound, or the model is unsatisfiable.
- A quantifier over a large domain (primality over 1..10000) exhausts Savile Row's memory (a 1.2 GB heap in one measured setup; the launcher's default is 8 GB). Precompute the set as a `letting` list and quantify over that.
- Savile Row compiles slowly for large grids and reads the whole model before search, so a large instance can time out before Minion starts (`SavileRowTimeOut:1`); keep matrix dimensions small and quantifier bounds fixed.

## Search and performance

- `branching on [x, M, [M[i,i] | i : int(1..n)]]` fixes variable order (flatten order for matrices). A comprehension is one entry of the list, so wrap it: `[[e | i : D]]`. Branch first on the structural decisions the rest follows from, then the rest. Branch on few-valued variables that fix the objective.
- `heuristic static|sdf|conflict|srf` (Minion only) goes before `such that` and before the objective. Try `sdf` (smallest domain first) when the default stalls, and `conflict` too: it solved one scheduling model where `sdf` and `srf` did not. On others neither helped; value-symmetry breaking did.
- Restrict decisions to a precomputed admissible set: `letting S = [i | i : int(1..N), cond]` and `x in toSet(S)`. Grid paths: branch on a Boolean cell matrix, not on position arrays. Long sequences: try a position model (variable = value at each position) early.
- Boolean incidence matrices (`x[i,s]` bool) propagate much better than weighted sums such as `sum i : D . toInt(x[i] = s) * i`. Products of decision variables in an objective prove poorly; keep the objective linear where you can.
- Symmetric models (partitions, interchangeable items, large symmetric Boolean matrices): order the entries within each set, and add implied totals (sums, sum of squares halved).
- Implied constraints on sums, tighter domains and a sorted symmetric copy help more than extra branching. Scheduling optimisations: a `cumulative` per resource, with the implied bounds, proved what `sdf` and bounds alone did not ([example](assets/scheduling/README.md)).
- An optimum that is not proven within the limit comes back with `SolverTimeOut:1`: tighten the objective's domain and add implied bounds rather than only raising the limit.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `'And' contains something other than a relation` | quantified `sum` compared without parentheses | [Pitfalls](#pitfalls): `(sum i : D . e) <= c` |
| `Parsed entry in list` on `branching on` | bare comprehension in the list | `branching on [[e \| i : D]]` |
| `Index domains do not match for the matrix F` | param matrix size differs from the `given` domain (an error when F is not empty) | size it from a `given` ([Modelling rules](#modelling-rules)). An empty `F = []` for a `int(1..0)` domain is only a warning: exit 0, correct solution ([Run](#run-and-read-results)) |
| `savilerow: not found` | launcher directory not on `PATH` | run it by full path or add its directory to `PATH` ([Install](#install)) |
| `Expected one-dimensional matrix in sum function` | `sum(M)` on 2-D | `sum(flatten(M))` |
| `Parsed keyword 'max'` / `Parsed 'find' keyword.` | reserved word as a name | rename (`max_`) |
| parse error at `branching on` / `heuristic` | placed after the objective | move before `minimising` |
| `-all-solutions` lists too few solutions | default `-S1` fixed a variable | add `-S0` ([enumeration](#objective-and-enumeration)) |
| `-all-solutions` repeats the same values | a free auxiliary `find` under `-S0` | pin it or remove it |
| optimisation returns one solution only | expected: enumeration is ignored there | [all optimal](assets/all-optimal/README.md) pattern |
| no solution file, exit 0 | infeasible, or a limit hit | read `SolverSatisfiable` / `SolverTimeOut` in `.info` |
| run goes past `-timelimit` | that limit stops Savile Row only | add `-solver-options "-cpulimit S"` |
| Java `OutOfMemoryError` | large quantifier domain or heap too small | precompute sets; adjust `-Xmx` |

## Further reading

- Savile Row manual: `savilerow-manual.pdf` in the tarball, or [arXiv:2201.03472](https://arxiv.org/abs/2201.03472) (2.1 expressions, 2.2 declarations, 2.4 objective, 2.5 branching, 4.3-4.5 files and options).
- Language definition: [Essence' description, arXiv:1601.02865](https://arxiv.org/abs/1601.02865).
- Releases: <https://www-users.york.ac.uk/peter.nightingale/savilerow/releases.html>; example models ship in the tarball's `examples/`.
